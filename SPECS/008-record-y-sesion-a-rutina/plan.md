# Plan 008 — El récord manda y la sesión se vuelve rutina

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-13 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-13) |
| **Stack** | El de siempre. Sin librerías nuevas y **sin cambios en la base de datos** |
| **Creado** | 2026-11-13 |

## 1. Resumen técnico

Cuatro piezas, todas sobre lo que ya existe:

1. **Récords en el celular.** El arranque trae el récord de cada ejercicio, que ya calcula Progreso (spec 004). El celular lo guarda y lo actualiza solo al confirmar una serie mejor, también sin señal.
2. **Referencia y precarga.** Una regla pura decide la referencia de un ejercicio en una rutina (lo previsto, o el récord si lo supera). La sesión se precarga con ella. Las rutinas guardadas **no se tocan**: la referencia se calcula al mostrar (RN-008-04).
3. **Sesión → rutina.** Un servicio del servidor arma la rutina con reglas puras y la guarda con el servicio de rutinas que ya existe, con sus validaciones y su transacción. Primero devuelve una **vista previa** de los cambios y solo guarda cuando se confirma.
4. **Series y buscador.** Numeración seguida y "Deshacer" en el modelo de la sesión, y un buscador propio en lugar de la lista nativa del navegador.

## 2. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea nombra sus `RF-008-xx`. |
| P2. Nada que nadie pidió | Sí | Nada fuera de la spec. |
| P3. RNF de seguridad | Sí | El servicio nuevo hereda la base de la API: una sesión o una rutina ajena responde 404. |
| P4. Cada requerimiento tiene su prueba | Sí | Sección 7. |
| P5. Reglas de negocio solas | Sí | `supera`, `referencia`, `ejercicios de una sesión`, `actualizar rutina`, `renumerar` y `sugerencias` son funciones puras, en Python y en JavaScript donde aplica, con las mismas tablas. |
| P6. David entiende lo que se entrega | Depende de ti | Bitácora de `tasks.md`. |

## 3. Qué hay hoy y qué cambia

| Pieza | Hoy | Después |
|---|---|---|
| Récord | Solo en Progreso, con conexión | También en el arranque y guardado en el celular; se actualiza sin señal |
| Editor de rutina | Agrega con 3 × 10 × 0 kg | Agrega con el récord y lo muestra; cada ejercicio muestra su referencia |
| Precarga de la sesión | Lo de la última vez, serie por serie | La referencia; la última vez queda como pista debajo |
| Ejercicio agregado en vivo | Última vez | Récord |
| Quitar una serie | Deja un hueco en la numeración | Renumera, y "Deshacer" durante 5 s |
| "Quitar" | En la misma columna que "Confirmar", a 28 px de alto | A la izquierda del pie de la serie, a 16 px o más, con 44 px de alto |
| Buscador de ejercicios | `datalist` nativo (se traba en Safari del iPhone) | Lista propia de hasta 6 sugerencias |
| Resumen e historial | Solo lectura | "Guardar como rutina" |
| Base de datos | — | **Sin cambios.** Ninguna migración |

## 4. Diseño

### 4.1 Reglas puras

En `backend/reglas/progreso.py` (ya tiene `mejor_serie`) y su espejo `frontend/src/reglas/progreso.js`:

| Función | Regla | En JS |
|---|---|---|
| `supera(a, b)` | RN-008-02: más peso supera; con igual peso, más reps | Sí |
| `mejor_serie(series)` | RN-004-03 (ya existe en Python) | Sí, nuevo espejo |
| `referencia(previsto, record)` | RN-008-03: el récord solo si supera lo previsto | Sí |

En `backend/reglas/sesion_a_rutina.py`, solo en Python porque lo hace el servidor:

| Función | Regla |
|---|---|
| `ejercicios_de_sesion(ejercicios)` | RN-008-05: un ejercicio por clave, en orden; series confirmadas sumadas (máximo 10); mejor serie |
| `rutina_nueva(ejercicios)` | RN-008-05, 06: previstos para una rutina nueva; más de 20 se rechaza diciendo cuántos sobran |
| `actualizar_rutina(previstos, de_la_sesion)` | RN-008-07: suma al final, mejora si supera, no quita; devuelve los previstos y la lista de cambios |

En `frontend/src/sesion/series.js`:

| Función | Regla |
|---|---|
| `renumerar(series)` | RN-008-08: 1, 2, 3… en el mismo orden |
| `sugerencias(catalogo, texto)` | RN-008-10: sin tildes ni mayúsculas, primero las que empiezan, máximo 6 |

### 4.2 Récords en el celular (RF-008-05, RNF-008-02)

- `GET /api/arranque/` agrega `records`: `{clave: {peso, reps}}`, calculados con la misma consulta de Progreso (`series_que_cuentan` + `mejor_serie`).
- El celular los guarda con el resto del arranque.
- **Al confirmar una serie,** si `supera(serie, records[clave])`, reemplaza el récord en el momento y lo guarda en el celular.
- Al volver la señal, el arranque trae los del servidor, que ya incluyen esa serie, como pasa hoy con "la última vez".

### 4.3 Referencia y precarga (RF-008-01 a 04)

- **Editor:** al agregar un ejercicio con récord, propone peso y reps del récord y muestra "Récord: 80 kg × 5". Cada ejercicio ya guardado se muestra con `referencia(previsto, record)`; si el récord manda, se ve "Récord" a su lado. Guardar la rutina guarda lo que se ve.
- **Sesión desde rutina:** cada serie toma la referencia. La última vez de esa serie va en `pista` ("última vez: 30 × 10").
- **Ejercicio en vivo:** la primera serie toma el récord; si no hay, la última vez, como hoy.
- **Serie agregada:** igual que hoy, copia la anterior de esa sesión (RN-006-10).

### 4.4 Quitar y deshacer (RF-008-08, 09)

Las series confirmadas existen en el servidor, y este no admite dos series con el mismo número. Por eso el orden de los envíos importa:

| Acción | En el celular | Envíos, en este orden |
|---|---|---|
| Quitar la 2 de 1, 2, 3 | Quedan 1, 2 (la vieja 3) | Borrar la 2 → la vieja 3 pasa a número 2 |
| Deshacer | Vuelven 1, 2, 3 | La vieja 3 vuelve a 3 → se recrea la 2 con su id y sus valores |

Solo viajan las series confirmadas; las pendientes viven solo en el celular. Todo pasa por la cola de pendientes que ya existe, así que también funciona sin señal y llega en orden.

### 4.5 Sesión → rutina (RF-008-06, 07)

`POST /api/sesiones/{id}/a-rutina/`

| Entrada | Salida | Errores |
|---|---|---|
| `modo`: `nueva` (con `id_rutina`, `nombre`, `dias`) o `actualizar` (con `rutina`); `confirmar`: `false` para la vista previa | Con `confirmar: false`: la lista de cambios. Con `true`: la rutina guardada | 400: nombre repetido, más de 20 ejercicios o sin series confirmadas. 404: sesión o rutina ajena o inexistente. 409 si la sesión sigue en curso |

- Arma los previstos con `reglas/sesion_a_rutina.py` y guarda con `rutinas.servicios.guardar_rutina`: **la misma validación y la misma transacción** que el editor (RF-002-05, todo o nada).
- **Un ejercicio que ya no está en el catálogo** se vuelve a crear con su nombre y grupo, con `asegurar_ejercicio`, como al sincronizar una sesión.
- **La vista previa no guarda nada:** se calcula igual y se descarta.

### 4.6 Pantallas

| Pieza | Cambio |
|---|---|
| `EditorDeRutina.vue` | Récord al agregar; referencia en cada ejercicio; buscador propio |
| `SesionEnCurso.vue` | Buscador propio |
| `FilaDeSerie.vue` | Pista de última vez; "Quitar" a la izquierda del pie, con 44 px de alto |
| `SesionEnCurso.vue` / `TarjetaDeEjercicio.vue` | Aviso "Serie quitada · Deshacer" durante 5 s |
| `BuscadorDeEjercicio.vue` (nuevo) | Campo con `autocorrect="off"`, `autocapitalize="words"` y `spellcheck="false"`, más la lista de sugerencias |
| `GuardarComoRutina.vue` (nuevo) | Hoja con "Rutina nueva / Actualizar una", nombre, días, la vista previa y confirmar |
| `Inicio.vue` (resumen) e `Historial.vue` (detalle) | Botón "Guardar como rutina" |

## 5. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| La referencia se calcula al mostrar, no se guarda | Reescribir las rutinas cuando sube el récord | RN-008-04 y RNF-008-04: nada guardado cambia solo. Además no hay que sincronizar rutinas sin señal |
| Sesión → rutina en el servidor | Armarla en el celular y usar el `PUT` de rutinas | El servidor ya tiene la sesión completa y enlazada al catálogo; el celular puede no tenerla (historial). Una sola fuente de reglas |
| Vista previa con el mismo endpoint (`confirmar: false`) | Calcular la vista previa en el celular | Lo que ves es exactamente lo que se guardará |
| "Deshacer" reenvía la serie en vez de retrasar el borrado | Esperar 5 s para enviar el borrado | Si la app se cierra en esos 5 s, lo de la pantalla y el servidor quedarían distintos |
| Buscador propio | Ajustar el `datalist` | El tirón es del `datalist` en Safari del iPhone; no se arregla desde afuera |

## 6. Seguridad y datos

- **Sin migración:** ninguna tabla cambia (RNF-008-04).
- `a-rutina` filtra sesión y rutina por el usuario; una prueba con una segunda cuenta comprueba el 404 (RNF-ACC-06).
- **Prueba de que no se pierde nada:** antes y después del recorrido completo se toma una huella de la base local (cantidad y contenido de sesiones, series y rutinas). Solo deben cambiar las rutinas que se guardaron a propósito y las series que se quitaron a propósito.

## 7. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| RN-008-02, 03 (tabla de "supera" y referencia), CA-008-02b, 02c | Unitaria, la misma tabla en Python y JavaScript | `backend/tests/reglas`, `frontend/src/reglas` |
| RN-008-05 a 07, CA-008-06a, 07a | Unitaria de las reglas de sesión → rutina | `backend/tests/reglas/test_sesion_a_rutina.py` |
| RN-008-08, 10, CA-008-08a, 10a | Unitaria | `frontend/src/sesion/series.test.js` |
| CA-008-06a, 06b, 07a por la API, cuenta ajena, vista previa que no guarda | Integración | `backend/tests/rutinas/test_sesion_a_rutina.py` |
| Récords en el arranque | Integración | `backend/tests/progreso` |
| CA-008-03a, 03b, 04a, 05a (sin señal), 09a (deshacer y orden de envíos) | Unitaria del modelo y del estado del celular | `frontend/src/sesion`, `frontend/src/estado` |
| CA-008-01a, 02a, buscador, "Quitar" a 16 px | Recorrido en el navegador a 375 px | Bitácora |
| RNF-008-01 (sin tirones en el iPhone) | Prueba de David en su iPhone | Bitácora |
| RNF-008-04 (no se pierde nada) | Huella de la base antes y después | Bitácora |
| Que nada se rompa | Todas las pruebas y la de modo avión (T-006-34) | Revisión automática |

## 8. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Cambiar la precarga rompe pruebas viejas de la 006 (CA-006-04a) | Segura | Se reescriben como CA-008-03a, a propósito, en la misma tarea |
| Un deshacer mal ordenado choca con "ya tiene una serie con ese número" | Media | El orden de 4.4 tiene su prueba con la cola simulada |
| El récord del celular difiere del servidor tras un día sin señal | Baja | El arranque con señal manda, como con "la última vez" |
| El buscador propio no resuelve el tirón | Baja | Lo confirmas en tu iPhone (RNF-008-01); si sigue, se mide qué lo causa |

## 9. Orden de construcción

1. **Reglas** (Python y JS): supera, mejor serie, referencia, sesión → rutina, renumerar, sugerencias.
2. **Servidor:** récords en el arranque; `a-rutina` con vista previa.
3. **Celular:** récords guardados y actualizados sin señal; precarga con referencia y pista; quitar con renumeración y deshacer.
4. **Pantallas:** editor, buscador, fila de serie, guardar como rutina.
5. **Cierre:** huella de la base, recorrido, la prueba de modo avión y tu iPhone.

El detalle está en [`tasks.md`](tasks.md).
