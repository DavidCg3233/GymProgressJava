# Plan 004 — Inicio y progreso

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-10 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-10) |
| **Stack** | El de la spec 006 ([plan 006](../006-sesiones/plan.md), secciones 2 y 12): Django + DRF, PostgreSQL, Vue 3 como app instalable, publicada en Railway |
| **Creado** | 2026-11-10 |

## 1. Resumen técnico

Dos partes con reglas distintas de conexión:

- **Inicio** (RF-004-01, 02, 03, 07, 10): funciona **sin señal** (RNF-004-01). Lo que necesita (rutinas, sesión en curso, últimas 3 sesiones y rutinas hechas hoy) viaja en el arranque y se guarda en el celular, como ya pasa con las rutinas.
- **Progreso** (RF-004-04, 05, 06, 09, 11, 12): **necesita conexión** (RNF-004-02). Lo calcula el servidor con todas tus sesiones; el celular solo lo muestra.

Una app nueva del servidor, `progreso`, que **solo lee** las sesiones y el catálogo: no tiene tablas propias. Todas las cuentas (récord, volumen, semanas, grupos) son funciones puras en `reglas/progreso.py`. La única escritura nueva es la meta semanal, que es un campo de tu cuenta.

## 2. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea nombra sus `RF-004-xx` y `CA-004-xx`. |
| P2. Nada que nadie pidió | Sí, con 3 reglas anotadas | La spec deja 3 huecos que el código necesita cerrar: empates entre grupos, la gráfica de ejercicios de peso corporal y qué sesiones cuentan. Están en la sección 6 para que los apruebes o los cambies. |
| P3. RNF de seguridad | Sí | Toda vista hereda la base de la API (`config/api.py`): acceso vigente, y cada consulta filtra por tu cuenta. |
| P4. Cada requerimiento tiene su prueba | Sí | Sección 8: cada CA de la spec es una prueba con sus mismos datos. |
| P5. Reglas de negocio solas | Sí | `reglas/progreso.py` no importa Django. El espejo en JavaScript tiene solo lo que el celular calcula: la meta (para validar el formulario) y la semana y "hecha hoy" (para el inicio sin señal). |
| P6. David entiende lo que se entrega | Depende de ti | Bitácora de `tasks.md`. |

## 3. Qué hay hoy y qué cambia

| Pieza | Hoy | Después |
|---|---|---|
| Inicio | "Continuar" o "Empezar sesión libre" primero, luego "Hoy toca", Mis rutinas e Historial | Orden de la spec: **Continuar** (si hay) → **rutinas de hoy**, con "Hecha hoy" si ya la hiciste → si no hay rutina hoy, lo dice → sesión libre → **últimas 3 sesiones** → Mis rutinas, Progreso, Historial |
| `/api/arranque/` | Sesión en curso, última vez, catálogo, rutinas | Además: `recientes` (3 sesiones terminadas) y `hechas_hoy` (rutinas con sesión terminada hoy) |
| Cuenta | Sin meta | Campo `meta_semanal` opcional, de 1 a 14, con restricción en la base |
| Progreso | No existe | Pantalla nueva: semana actual frente a la meta, 12 semanas, series por grupo, récords y, al tocar un ejercicio, su gráfica |
| Gráficas | No hay | Un componente propio en SVG (sección 6), sin librería nueva |

## 4. Diseño

### 4.1 Qué cuenta (RN-004-01)

Una sola consulta base, `series_que_cuentan(usuario)`: series **confirmadas** de sesiones **terminadas** del usuario, con su sesión y su ejercicio. Antes de leer se llama a `poner_al_dia`, para que una sesión que pasó las 2 horas cuente como terminada (RN-006-11). Las sesiones eliminadas ya no existen, así que dejan de contar solas.

Los datos de la v1.0 que el récord leía mal (H-08: tomaba el peso de la rutina) no se usan: el récord sale **solo** de series confirmadas, nunca de la rutina (CA-004-04c).

### 4.2 El ejercicio de una serie

Una serie pertenece al ejercicio por su **clave** (`sesion_ejercicio.clave`, el nombre sin mayúsculas ni tildes, RN-002-07). Así:

- "Press inclinado" de una sesión libre y el de una rutina son el mismo ejercicio.
- Un ejercicio eliminado del catálogo sigue teniendo récord y gráfica con el nombre que tenía (RN-004-10).
- El nombre que se muestra es el del catálogo si sigue ahí; si no, el último nombre con que se registró.

**Grupo de una serie (RN-004-09 y 10):** el grupo que el ejercicio tiene **hoy** en el catálogo. Si el ejercicio ya no está en el catálogo, el grupo copiado en la sesión.

### 4.3 Semana y hora local (RN-004-02)

La semana va de lunes a domingo en la hora de Colombia (`America/Bogota`, la que ya usa el servidor). Una sesión pertenece al día local en que **empezó**: la que empieza el domingo 11:30 p. m. y termina el lunes cuenta para la semana del domingo (CA-004-05b).

### 4.4 Contratos

Todas requieren acceso vigente y leen solo datos del usuario.

| Operación | Entrada | Salida | Errores | Cubre |
|---|---|---|---|---|
| `GET /api/progreso/` | — | `vacio`, `meta`, `semanas` (12, de la más antigua a la actual: `inicio`, `sesiones`, `cumple`), `grupos` (`nombre`, `series`), `records` (`clave`, `nombre`, `peso`, `reps`, `fecha`, `peso_corporal`) | — | RF-004-04, 05, 06, 11, 12 |
| `GET /api/progreso/evolucion/?clave=…` | Clave del ejercicio | `nombre`, `peso_corporal`, `puntos`: uno por sesión, en orden de fecha (`fecha`, `pesada`, `reps_de_la_pesada`, `volumen`) | 404 si no tienes series de ese ejercicio | RF-004-09 |
| `PUT /api/progreso/meta/` | `meta`: entero de 1 a 14, o `null` para quitarla | La meta | 400 con el motivo | RF-004-11 |
| `GET /api/arranque/` (ya existe) | — | Además: `recientes` y `hechas_hoy` | — | RF-004-07, 10 |

- **Con `vacio: true`** (no tienes ninguna sesión terminada con series), el resto de campos llega vacío y la pantalla muestra solo la invitación (RF-004-12, CA-004-12a).
- **`cumple`** es `null` mientras no haya meta. Se calcula con la meta **vigente hoy** para todas las semanas (RN-004-08).
- **Los grupos** son todos los de tu catálogo, incluidos los de 0 series, más cualquier grupo que solo exista en sesiones de ejercicios eliminados.
- **La clave va en la consulta (`?clave=`) y no en la ruta**, porque lleva espacios y eñes.

### 4.5 El inicio sin señal (RNF-004-01)

- El arranque trae `recientes` (las 3 sesiones terminadas más recientes: `id`, `nombre`, `inicio`, `rutina`) y `hechas_hoy` (`fecha` local y lista de ids de rutina).
- Se guardan en el celular con el resto del arranque.
- **Al terminar una sesión sin señal**, el celular la pone primera en `recientes` y, si tenía rutina, agrega su id a `hechas_hoy`. No espera al servidor.
- **Si `hechas_hoy.fecha` no es hoy** (abriste la app al día siguiente sin señal), se trata como vacía.
- Se ignoran las sesiones sin ninguna serie confirmada, igual que en el historial.

### 4.6 Pantallas

| Pantalla | Qué muestra | Sin señal |
|---|---|---|
| Inicio (cambia) | Sección 3 | Funciona |
| Progreso (nueva) | Semana actual "3 de 4 esta semana" y la meta para fijarla, cambiarla o quitarla; barras de las 12 semanas, marcando las que cumplieron; series por grupo de esta semana; lista de récords | "Progreso necesita conexión" y un botón para reintentar |
| Evolución de un ejercicio (nueva) | Gráfica con un punto por sesión y el selector "Serie más pesada / Volumen"; al tocar un punto, su fecha y su valor (y las reps de la serie más pesada) | Igual que Progreso |

**RNF-004-03:** cada indicador tiene un botón "?" que despliega una frase de cómo se calcula. Las frases salen de la tabla de la sección 5 de la spec y viven en un solo archivo, `frontend/src/progreso/explicaciones.js`.

## 5. Reglas nuevas

En `backend/reglas/progreso.py` y, donde dice, también en `frontend/src/reglas/progreso.js` con la misma tabla de pruebas:

| Función | Regla | En JS |
|---|---|---|
| `record(series)` | RN-004-03 y 04: mayor peso → más reps → la más antigua. Si todas pesan 0, la de más reps, marcada como peso corporal | No |
| `es_de_peso_corporal(series)` | Todas las series del ejercicio pesan 0 | No |
| `serie_mas_pesada(series)` | RN-004-05 (y su versión de peso corporal, sección 6) | No |
| `volumen(series, peso_corporal)` | RN-004-06: Σ peso × reps; en peso corporal, Σ reps | No |
| `inicio_de_semana(fecha)` | RN-004-02: el lunes de esa semana | Sí |
| `sesiones_por_semana(fechas, hoy)` | RN-004-07: 12 semanas, la actual y las 11 anteriores, con 0 en las vacías | No |
| `cumple(sesiones, meta)` | RN-004-08: `sesiones >= meta`; sin meta, `None` | Sí |
| `validar_meta(valor)` | RN-004-08: entero de 1 a 14 o vacío. Mensaje: "La meta va de 1 a 14 sesiones por semana." | Sí |
| `ordenar_grupos(conteos)` | RN-004-09: de mayor a menor; empates por nombre (sección 6) | No |
| `rutinas_hechas_hoy(hechas, hoy)` | RF-004-10 y sección 4.5: vacía si la fecha no es hoy | Solo JS |

El peso se calcula con `Decimal` en Python para que 32,5 × 8 dé exactamente 260 y no 259,99999.

## 6. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| **Regla nueva 1 — empates en grupos:** dos grupos con las mismas series se ordenan por nombre | Orden del catálogo | La spec pide "de mayor a menor" pero no dice qué pasa con empates; sin una regla, el orden cambiaría entre una carga y otra. |
| **Regla nueva 2 — gráfica de peso corporal:** en un ejercicio de peso corporal, "serie más pesada" grafica las **reps** de la mejor serie, y "volumen" la suma de reps (como ya dice RN-004-06) | Graficar 0 kg | Una línea plana en 0 no muestra nada. Usa la misma definición del récord (RN-004-04). |
| **Regla nueva 3 — sesiones sin series:** una sesión terminada sin ninguna serie confirmada **no cuenta** en sesiones por semana | Contarla | Así lo hace ya el historial: sin series no se muestra. Si contara, abrir y cerrar la app sumaría una sesión a tu meta. |
| Gráfica propia en SVG (~80 líneas, con su función de escalas probada) | Chart.js | Una sola gráfica de línea no justifica una librería de ~70 kB: menos peso para cargar sin señal y una dependencia menos que vigilar (RNF-SEG). Si más adelante hacen falta más gráficas, se cambia. |
| El servidor calcula Progreso | Calcularlo en el celular | Progreso necesita todas tus sesiones; el celular solo guarda la última vez de cada ejercicio. Y la spec ya acepta que Progreso pida conexión. |
| Una app `progreso` sin tablas | Meterlo en `sesiones` | Solo lee; así `sesiones` no crece y las cuentas quedan juntas. |
| Meta como campo de la cuenta | Tabla aparte | Es un solo número por persona. |
| Semana en hora de Colombia para todas las cuentas | Zona horaria por persona | Las 5 cuentas posibles son de personas en Colombia. Si alguien vive en otro país, se agrega después. |

## 7. Seguridad

Lo mismo que el plan 006, sección 7. Lo nuevo:

- **Progreso solo lee**, y toda consulta parte de `usuario=request.user`. Una prueba con una segunda cuenta comprueba que sus series no suman ni en récords, ni en semanas, ni en grupos, ni en evolución (RNF-ACC-06).
- **La clave de `?clave=` nunca se usa para armar SQL**: va como filtro del ORM. Una clave rara o larga responde 404.
- **La meta** se valida en el servidor y en la base (`CHECK` de 1 a 14).

## 8. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| CA-004-04a, 04b, 09a, bordes de meta y semana | Unitaria de las reglas, misma tabla en Python y JavaScript donde aplica | `backend/tests/reglas/test_progreso.py`, `frontend/src/reglas/progreso.test.js` |
| CA-004-04c (el récord no mira la rutina), 05a, 05b (domingo 11:30 p. m.), 06a, 12a | Integración de la API, con sesiones creadas por la API como lo haría el celular | `backend/tests/progreso` |
| RN-004-10 (ejercicio eliminado sigue contando) | Integración | `backend/tests/progreso` |
| Sesión que se cerró sola a las 2 horas cuenta | Integración, con el `Reloj` de pruebas | `backend/tests/progreso` |
| RNF-ACC-06 (cuenta ajena) | Integración: una por operación | `backend/tests/progreso/test_permisos.py` |
| Meta: rangos en la base | Integración, escribiendo directo en la base | `backend/tests/cuentas` |
| CA-004-01a, 02a, 03a, RF-004-07 y 10 sin señal | Unitaria del estado del celular | `frontend/src/estado` |
| Escalas de la gráfica | Unitaria de la función pura | `frontend/src/progreso` |
| Pantallas | Recorrido a mano en 375 px, en el navegador | Bitácora |

## 9. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| Progreso se vuelve lento con años de sesiones | Baja | 5 cuentas × 4 sesiones por semana son ~1.000 sesiones al año: se calcula en milisegundos. Si un día pasa de 1 segundo, se agrega un índice o una caché. |
| "Hecha hoy" queda mal si terminas una sesión en otro dispositivo sin señal | Baja | Se corrige solo en el siguiente arranque con conexión. |
| Cambiar un ejercicio de grupo cambia las series de grupos de esta semana | Es lo que pide la spec | RN-004-09 dice "el grupo que tiene hoy". |
| Un error de redondeo en el volumen | Baja | `Decimal` en el servidor y la prueba de CA-004-09a con 755 exacto. |

## 10. Orden de construcción

1. **Reglas:** Python y su espejo en JavaScript.
2. **Servidor:** meta en la cuenta, `GET /api/progreso/`, evolución, arranque ampliado.
3. **Pantalla:** inicio sin señal con recientes y "hecha hoy", Progreso, gráfica y evolución.
4. **Cierre:** recorrido en el navegador y prueba en tu iPhone.

El detalle está en [`tasks.md`](tasks.md).
