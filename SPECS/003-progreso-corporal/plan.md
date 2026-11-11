# Plan 003 — Progreso corporal

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-11 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-10) |
| **Stack** | El de la spec 006 ([plan 006](../006-sesiones/plan.md), secciones 2 y 12): Django + DRF, PostgreSQL, Vue 3 como app instalable, publicada en Railway |
| **Creado** | 2026-11-11 |

## 1. Resumen técnico

Una app nueva del servidor, `cuerpo`, con una tabla: un registro de peso por usuario y por día. La estatura y el peso objetivo son dos campos de la cuenta, como la meta semanal de la spec 004.

Todo requiere conexión (RNF-003-02), así que **el servidor calcula el resumen** (peso actual, cambio, IMC, categoría y objetivo) con funciones puras en `reglas/cuerpo.py`. El celular solo valida los datos antes de enviarlos, para avisar sin esperar a la red y sin perder lo escrito.

En la pantalla, Progreso (spec 004) gana dos pestañas: **Entrenamiento** (lo que ya existe) y **Peso**.

## 2. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea nombra sus `RF-003-xx` y `CA-003-xx`. |
| P2. Nada que nadie pidió | Sí, con 2 reglas anotadas | La spec no dice qué pasa si el objetivo es igual al primer registro, ni cómo se redondea el IMC en un empate de medio decimal. Están en la sección 6. |
| P3. RNF de seguridad | Sí | Toda vista hereda la base de la API (`config/api.py`). Cada consulta filtra por tu cuenta. |
| P4. Cada requerimiento tiene su prueba | Sí | Sección 8: cada CA de la spec es una prueba con sus mismos números. |
| P5. Reglas de negocio solas | Sí | `reglas/cuerpo.py` no importa Django. El espejo en JavaScript tiene solo las validaciones de peso, estatura y fecha. |
| P6. David entiende lo que se entrega | Depende de ti | Bitácora de `tasks.md`. |

## 3. Qué hay hoy y qué cambia

| Pieza | Hoy | Después |
|---|---|---|
| Peso corporal | No existe en la versión nueva (la v1.0 lo tenía, con la altura en metros en cada registro) | Tabla `registro_de_peso`: fecha y peso, uno por día y por usuario |
| Cuenta | Meta semanal | Además, `estatura_cm` (100 a 250) y `peso_objetivo` (20,0 a 300,0), ambos opcionales y con `CHECK` en la base |
| Progreso | Solo entrenamiento | Pestañas **Entrenamiento** y **Peso** |
| Gráfica de línea | Valores por sesión | Además, una línea horizontal opcional para el peso objetivo |

## 4. Diseño

### 4.1 Datos

| Tabla / campo | Contenido | Restricciones en la base |
|---|---|---|
| `registro_de_peso` | `usuario`, `fecha`, `peso` (decimal, 1 decimal) | Único por (`usuario`, `fecha`) · peso de 20,0 a 300,0 |
| `cuenta.estatura_cm` | Entero o vacío | De 100 a 250 |
| `cuenta.peso_objetivo` | Decimal o vacío | De 20,0 a 300,0 |

La **fecha es la llave** del registro: como hay uno por día (RN-003-06), la dirección de un registro es su fecha. No hace falta un id aparte.

### 4.2 Contratos

Todas requieren acceso vigente y operan solo sobre datos del usuario.

| Operación | Entrada | Salida | Errores | Cubre |
|---|---|---|---|---|
| `GET /api/peso/` | — | `estatura`, `objetivo`, `registros` (del más reciente al más antiguo: `fecha`, `peso`) y `resumen` (sección 4.3) | — | RF-003-03 a 09 |
| `PUT /api/peso/{fecha}/` | `peso`, `reemplazar` (falso por defecto) | El registro | 400 peso o fecha inválidos · **409 si ya hay un registro ese día y `reemplazar` es falso**, con el peso que había | RF-003-01, 02, 10, 13 |
| `DELETE /api/peso/{fecha}/` | — | — | 404 si no existe | RF-003-11 |
| `PUT /api/peso/estatura/` | `estatura` (entero en cm) | La estatura | 400 fuera de rango o con decimales | RF-003-12, 13 |
| `PUT /api/peso/objetivo/` | `objetivo` (número) o `null` para quitarlo | El objetivo | 400 fuera de rango | RF-003-08 |

- **Reemplazar (RF-003-02):** la pantalla envía sin `reemplazar`. Si el servidor responde 409, muestra "Ya registraste X kg ese día. ¿Reemplazarlo?" y, si confirmas, reenvía con `reemplazar: true`.
- **Corregir desde el historial (RF-003-10)** es el mismo `PUT` con `reemplazar: true`: ahí ya sabes que existe.
- **"Hoy" es el de Colombia** en el servidor, como en la spec 004. Una fecha mal escrita en la dirección responde 404.

### 4.3 El resumen

`resumen` es `null` si no hay registros (la pantalla invita a registrar el primero, sin ceros ni guiones). Si los hay:

| Campo | Regla | Ejemplo (CA-003-01a) |
|---|---|---|
| `actual` | Peso del registro más reciente (RF-003-03) | 79,0 |
| `cambio` | `{kg, direccion}` frente al registro anterior: `bajo`, `subio` o `igual`. `null` si hay un solo registro (RF-003-04) | 1,0 · `bajo` |
| `imc` | `{valor, categoria}`; `null` si no hay estatura (RF-003-05, CA-003-05a) | 25,8 · Sobrepeso |
| `objetivo` | `{faltan, direccion, alcanzado}`; `null` sin objetivo (RF-003-08, 09) | 4,0 · `bajar` · falso |

El texto orientativo del IMC (RN-003-09) es fijo y lo pone la pantalla.

### 4.4 Pantallas

| Pantalla | Qué muestra | Toques para registrar hoy (RNF-003-01) |
|---|---|---|
| Progreso → pestaña **Peso** | Arriba: campo de peso con la fecha de hoy ya puesta y el botón Guardar. Debajo: peso actual, cambio e IMC en una fila; el objetivo; la gráfica; el historial con Corregir y Eliminar | Inicio → **Progreso** (1) → **Peso** (2) → escribir → **Guardar** (3) |
| Sin estatura | En lugar del IMC: "Agrega tu estatura para ver tu IMC" con su campo (alterno 1a) | — |
| Sin conexión | El mensaje de RNF-003-02, y lo escrito se queda en el campo | — |

**La pestaña elegida se recuerda** en el celular: si entras a Progreso para pesarte, la próxima vez abre en Peso.

## 5. Reglas nuevas

En `backend/reglas/cuerpo.py` y, donde dice, también en `frontend/src/reglas/cuerpo.js` con la misma tabla de pruebas:

| Función | Regla | En JS |
|---|---|---|
| `validar_peso_corporal(valor)` | RN-003-03: de 20,0 a 300,0 con un decimal. "El peso va de 20 a 300 kg, con un decimal." | Sí |
| `validar_estatura(valor)` | RN-003-04: entero de 100 a 250. 1,75 se rechaza con "La estatura va en centímetros, de 100 a 250." | Sí |
| `validar_fecha_de_peso(fecha, hoy)` | RN-003-05: obligatoria y no futura | Sí |
| `imc(peso, estatura_cm)` | RN-003-01: valor exacto, sin redondear | No |
| `imc_para_mostrar(imc)` | RN-003-01: 1 decimal, redondeo hacia arriba en el medio (sección 6) | No |
| `categoria_de_imc(imc)` | RN-003-02: con el valor **exacto** | No |
| `cambio(anterior, actual)` | RF-003-04 | No |
| `hacia_el_objetivo(primero, actual, objetivo)` | RN-003-08 y sección 6 | No |

Todo con `Decimal`: 99,9 ÷ 2,00² da exactamente 24,975 y no 24,974999.

## 6. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| **Regla nueva 1 — objetivo igual al primer registro:** la dirección se decide con el peso actual, y está alcanzado solo si el actual es igual al objetivo | Darlo por alcanzado siempre | RN-003-08 cubre "menor" y "mayor", no "igual". Es el caso de quien quiere **mantener** su peso. |
| **Regla nueva 2 — redondeo del IMC:** cuando la cifra que se quita es justo la mitad, hacia arriba (18,45 → 18,5) | Redondeo bancario, el que usa Python por defecto (18,45 → 18,4, al par más cercano) | Es el que se aprende en el colegio. La tabla de CA-003-05b sale igual con los dos, pero este no sorprende. |
| El servidor calcula el resumen | Calcularlo en el celular | Todo pide conexión (RNF-003-02); así las reglas viven en un solo lugar. |
| La fecha como llave del registro | Un id por registro | Hay uno por día: la fecha ya lo identifica, y reemplazar es natural. |
| Reemplazo con 409 y reenvío | Un endpoint aparte para reemplazar | La confirmación es de la pantalla; el servidor solo se niega a pisar sin permiso. |
| Estatura y objetivo en la cuenta | Tabla de perfil | Son dos números por persona, igual que la meta semanal. |
| Peso dentro de Progreso, con pestañas | Pantalla aparte en el inicio | La spec dice "Abro Progreso", y el inicio ya tiene sus tres botones. |
| Reusar la gráfica de la spec 004, con una línea de referencia | Otra gráfica | Es la misma forma: un valor por fecha. |

## 7. Seguridad

Lo mismo que el plan 006, sección 7. Lo nuevo:

- **El peso y la estatura son datos de salud.** No salen en mensajes de error ni en registros del servidor, y el panel de administración no los muestra en la lista de cuentas.
- Cada operación tiene su prueba con una segunda cuenta (RNF-ACC-06): no ve, no corrige y no borra los registros de otra persona, aunque use la misma fecha.
- La prueba que vigila los campos de la cuenta (`test_la_cuenta_no_tiene_campos_personales_de_mas`) se actualiza a propósito: la estatura es el único dato personal nuevo, y la spec lo justifica (RF-003-12).

## 8. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| CA-003-05b (bordes de categoría), CA-003-13a (bordes de peso, estatura y fecha) | Unitaria, misma tabla en Python y JavaScript donde aplica | `backend/tests/reglas/test_cuerpo.py`, `frontend/src/reglas/cuerpo.test.js` |
| CA-003-01a, 02a, 05a, 08a, 09a, 10a, 11a | Integración de la API | `backend/tests/cuerpo` |
| Rangos y unicidad en la base | Integración, escribiendo directo en la base | `backend/tests/cuerpo/test_modelos.py` |
| RNF-ACC-06 (cuenta ajena) | Integración: una por operación | `backend/tests/cuerpo/test_permisos.py` |
| Línea del objetivo en la gráfica | Unitaria de las escalas | `frontend/src/progreso` |
| Pantalla, 3 toques, sin conexión | Recorrido a mano en 375 px, en el navegador | Bitácora |

## 9. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Pesarte a las 11:30 p. m. con el celular en otro huso horario | Baja | Se usa la fecha de Colombia, como en la spec 004. |
| El IMC preocupa sin necesidad (mucho músculo da "Sobrepeso") | Media | El texto de RN-003-09 se muestra siempre junto al IMC. |
| Un objetivo puesto cuando ya lo cruzaste aparece como alcanzado de una vez | Media | Es lo que dice RN-003-08: se mide desde el primer registro. Si te molesta, se cambia la regla en la spec. |

## 10. Orden de construcción

1. **Reglas:** Python y su espejo en JavaScript.
2. **Servidor:** modelo y campos de la cuenta, registrar, reemplazar, corregir y eliminar, estatura y objetivo, resumen.
3. **Pantalla:** gráfica con objetivo, estado, pestaña Peso.
4. **Cierre:** recorrido en el navegador y prueba en tu iPhone.

El detalle está en [`tasks.md`](tasks.md).
