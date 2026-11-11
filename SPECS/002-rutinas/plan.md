# Plan 002 — Rutinas y catálogo de ejercicios

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-10 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-10) |
| **Stack** | El de la spec 006 ([plan 006](../006-sesiones/plan.md), secciones 2 y 12): Django + DRF, PostgreSQL, Vue 3 como app instalable, publicada en Railway |
| **Creado** | 2026-11-10 |

## 1. Resumen técnico

Una app nueva del servidor, `rutinas`, con el catálogo propio de cada usuario (grupos y ejercicios) y sus rutinas. Cada cuenta arranca con los 8 grupos y 40 ejercicios predefinidos. Las rutinas y el catálogo se editan solo con conexión (RNF-002-01), pero viajan en el arranque y se guardan en el celular, para poder **empezar una sesión desde una rutina sin señal** (RF-006-17).

Este plan también cierra el hito B de la spec 006: empezar una sesión desde una rutina (T-006-37).

## 2. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea nombra sus `RF-002-xx`. |
| P2. Nada que nadie pidió | Sí, con una excepción anotada | La única regla nueva es cómo nombrar una segunda copia de una rutina (sección 6), porque la spec choca consigo misma. |
| P3. RNF de seguridad | Sí | Toda vista hereda la base de la API (`config/api.py`): acceso vigente, lo ajeno responde 404. |
| P4. Cada requerimiento tiene su prueba | Sí | Sección 8. |
| P5. Reglas de negocio solas | Sí | Reglas nuevas en `reglas/rutinas.py` y su espejo en JavaScript, con las mismas tablas de bordes. |
| P6. David entiende lo que se entrega | Depende de ti | Bitácora de `tasks.md`. |

## 3. Qué hay hoy y qué cambia

| Pieza | Hoy | Después |
|---|---|---|
| Catálogo | No existe. El ejercicio de una sesión es solo un nombre y un grupo copiados | Tablas `grupo_muscular` y `ejercicio` por usuario |
| Rutinas | No existen. Toda sesión es libre | Tablas `rutina` y `rutina_ejercicio` |
| `sesion` | Sin relación con rutinas | Campo `rutina` opcional; si la rutina se elimina, queda vacío y la sesión conserva su nombre (RF-002-06, RF-006-11) |
| `sesion_ejercicio` | Sin relación con el catálogo | Campo `ejercicio` opcional, que el servidor llena solo al recibirlo (sección 4.3) |
| `/api/arranque/` | Sesión en curso y "última vez" | Además, el catálogo y las rutinas, para trabajar sin señal |
| Pantallas | Inicio, sesión, historial | Además: mis rutinas, editor de rutina, catálogo. Agregar un ejercicio a una sesión sugiere del catálogo |
| Grupos musculares en la pantalla | Lista fija en `SesionEnCurso.vue` | Salen del catálogo del usuario |

## 4. Diseño

### 4.1 Datos

| Tabla | Columnas principales | Reglas |
|---|---|---|
| `grupo_muscular` | `id` (UUID), `usuario`, `nombre`, `clave` | `clave` es el nombre sin mayúsculas ni tildes. Único por (`usuario`, `clave`) (RN-002-08) |
| `ejercicio` | `id` (UUID), `usuario`, `nombre`, `clave`, `grupo` | Único por (`usuario`, `clave`) (RN-002-07). `grupo` con `PROTECT`: la base impide borrar un grupo con ejercicios (RF-002-19) |
| `rutina` | `id` (UUID), `usuario`, `nombre`, `clave`, `dias`, `actualizada` | Única por (`usuario`, `clave`) (RN-002-01). `dias` es un número de 0 a 127 donde cada bit es un día, de lunes a domingo (RN-002-02); la API lo entrega como lista `[1, 4]` (1 = lunes) |
| `rutina_ejercicio` | `rutina`, `ejercicio`, `orden`, `series`, `reps`, `peso` | Único por (`rutina`, `ejercicio`) (RN-002-03). Rangos en la base: series 1-10, reps 1-100, peso 0-500 (RN-002-04 a 06). Una sola fila por ejercicio: todas las series previstas comparten reps y peso (RN-002-09) |

Decisiones:

- **Identificadores UUID generados en el celular**, igual que en la spec 006, aunque aquí se editen con conexión: una misma forma de trabajar, y guardar dos veces la misma rutina no la duplica.
- **`dias` como bits** y no como tabla aparte: siete días caben en un número, la consulta "rutinas de hoy" es una operación sobre ese número, y funciona igual en SQLite y PostgreSQL.
- **Máximo 20 ejercicios por rutina** (RN-002-03) se valida en las reglas, no en la base.
- **Migración de datos:** las cuentas que ya existen (la tuya en Railway y la de prueba en tu equipo) reciben el catálogo predefinido al aplicar la migración, y sus sesiones ya registradas quedan enlazadas al catálogo por nombre (sección 4.3).

### 4.2 Catálogo predefinido (RF-002-14)

Los 8 grupos y 40 ejercicios de la spec viven en un solo archivo, `rutinas/catalogo_inicial.py`. Se cargan:

- Al crear una cuenta, con una señal de Django (`post_save` del usuario). Así `cuentas` no tiene que saber que existen las rutinas.
- En la migración de datos, para las cuentas que ya existen.

Si el usuario ya tiene un ejercicio con la misma clave, no se duplica. **La plancha** queda en la lista, registrada con peso 0 y los segundos en el campo de repeticiones (decisión de la spec, sección 5).

### 4.3 Enlace entre sesiones y catálogo

Un ejercicio de una sesión sigue guardando **su propia copia** del nombre y el grupo: eso es lo que protege el historial (RF-006-11, RN-004-10). Además, el servidor lo enlaza al catálogo:

1. Al recibir un ejercicio de sesión, busca en el catálogo del usuario uno con la misma clave.
2. Si existe, lo enlaza.
3. Si no, **lo crea en el catálogo** con el grupo que traía (RF-002-09) y lo enlaza.

Esto pasa en el servidor al sincronizar, así que también funciona con ejercicios agregados sin señal. El celular nunca necesita conexión para agregar un ejercicio nuevo a una sesión.

Si el ejercicio del catálogo se elimina después, el enlace queda vacío y la sesión conserva su copia (RF-002-16).

### 4.4 Contratos

Todas requieren acceso vigente y operan solo sobre datos del usuario; lo ajeno responde 404.

| Operación | Entrada | Salida | Errores | Cubre |
|---|---|---|---|---|
| `GET /api/catalogo/` | — | Grupos y ejercicios del usuario | — | RF-002-08, 10 |
| `PUT /api/catalogo/grupos/{id}/` | `nombre` | El grupo | 400 nombre inválido o repetido | RF-002-19 |
| `DELETE /api/catalogo/grupos/{id}/` | — | — | 409 si tiene ejercicios | RF-002-19 |
| `PUT /api/catalogo/ejercicios/{id}/` | `nombre`, `grupo` | El ejercicio | 400 nombre repetido, grupo inexistente | RF-002-09, 15 |
| `GET /api/catalogo/ejercicios/{id}/uso/` | — | Rutinas que lo usan y cuáles quedarían vacías | 404 | RF-002-17, 18 |
| `DELETE /api/catalogo/ejercicios/{id}/` | — | Rutinas eliminadas por quedar vacías | 404 | RF-002-16, 18 |
| `GET /api/rutinas/` | — | Rutinas con sus ejercicios, en orden | — | RF-002-01 |
| `PUT /api/rutinas/{id}/` | `nombre`, `dias`, `ejercicios: [{ejercicio, series, reps, peso}]` en orden | La rutina | 400 con el campo y el motivo | RF-002-01, 03, 04, 05, 20 |
| `POST /api/rutinas/{id}/duplicar/` | `id_copia` | La copia | 404 | RF-002-21 |
| `DELETE /api/rutinas/{id}/` | — | — | 404 | RF-002-06 |
| `PUT /api/sesiones/{id}/` (ya existe) | Nuevo campo opcional `rutina` | — | Una rutina ajena o eliminada se ignora en vez de rechazar la sesión | RF-006-01 |
| `GET /api/arranque/` (ya existe) | — | Además: `catalogo` y `rutinas` | — | RF-006-17 |

- **`PUT` de rutina reemplaza la rutina completa** en una transacción: nombre, días y la lista entera de ejercicios. Todo o nada (RF-002-05).
- **Un ejercicio inexistente en el catálogo** dentro de una rutina se rechaza con 400. La pantalla crea primero el ejercicio (`PUT /api/catalogo/ejercicios/{id}/`) y luego guarda la rutina (RF-002-09).
- **Eliminar un ejercicio** es una sola operación: lo quita de las rutinas, elimina las que quedan vacías y lo borra del catálogo. La confirmación la pide la pantalla antes, con lo que devuelve `uso` (RF-002-17, 18).
- **Una sesión con una rutina que ya no existe** (eliminada mientras el celular estaba sin señal) se guarda igual, sin enlace. Rechazarla haría perder el entrenamiento.

### 4.5 Empezar una sesión desde una rutina (T-006-37)

Todo pasa en el celular, para que funcione sin señal:

1. La pantalla toma la rutina guardada en el celular.
2. `modelo.nuevaSesionDesdeRutina(rutina, ultimaVez)` crea la sesión con sus ejercicios en orden y, en cada uno, tantas series como las previstas.
3. Cada serie se precarga con "la última vez" o, si no hay, con lo previsto (RF-006-04, 05, ya resuelto en `reglas/precarga.js`).
4. Se envía como una sesión libre más: la sesión con su campo `rutina`, luego cada ejercicio. Las series viajan al confirmarse, como hoy.

Como la sesión copia la rutina al empezar, modificar la rutina después no la toca (RF-002-13).

### 4.6 Pantallas

| Pantalla | Qué tiene | Cubre |
|---|---|---|
| Mis rutinas | Tarjetas con nombre, días y cantidad de ejercicios; botones Empezar, Editar, Duplicar, Eliminar (con confirmación). Acceso desde el inicio | RF-002-01, 06, 21; T-006-37 |
| Editor de rutina | Nombre; siete botones de días; ejercicios con buscador del catálogo, grupo para uno nuevo, series, reps y peso con los controles de la sesión; subir y bajar para ordenar; quitar | RF-002-03, 04, 08, 09, 20 |
| Catálogo | Ejercicios agrupados; renombrar, cambiar de grupo, eliminar (mostrando en qué rutinas está); crear y renombrar grupos | RF-002-15 a 19 |
| Sesión en curso | Agregar ejercicio sugiere del catálogo y toma los grupos de ahí | RF-002-08 |

Para ordenar se usan botones de subir y bajar, no arrastrar: arrastrar en una lista dentro de una página que se desplaza es torpe con el pulgar (RNF-006-04).

Sin conexión, las tres pantallas de edición muestran lo guardado y avisan que para guardar cambios hace falta señal, sin perder lo escrito (RNF-002-01). Empezar una sesión desde una rutina sí funciona sin señal.

## 5. Reglas nuevas (Python y JavaScript, con las mismas tablas)

| Regla | Valor | De dónde sale |
|---|---|---|
| Nombre de rutina | 1 a 50 caracteres | RN-002-01 |
| Días | Lista sin repetidos de números del 1 al 7, o vacía | RN-002-02 |
| Ejercicios por rutina | 1 a 20, sin repetir ejercicio | RN-002-03 |
| Series previstas | 1 a 10 | RN-002-04 |
| Reps y peso previstos | Los mismos de una serie (`reglas/series`) | RN-002-05, 06 |
| Nombre de una copia | Ver sección 6 | RF-002-21 |
| Rutinas de hoy | Las que tienen el bit del día actual | RN-004-11 (la usa la spec 004) |

## 6. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| **Nombre de una copia:** "Pecho (copia)"; si ya existe, "Pecho (copia 2)", "(copia 3)"…, recortando el nombre original para no pasar de 50 caracteres | Solo "(copia)" como dice la spec | La spec pide nombres únicos (RN-002-01) y "(copia)" a secas fallaría la segunda vez que duplicas la misma rutina. **Es la única regla que agrega este plan.** |
| Catálogo inicial con una señal de Django | Crearlo dentro de `cuentas` | `cuentas` no debe depender de `rutinas` |
| El servidor enlaza sesiones y catálogo al sincronizar | Que el celular cree el ejercicio en el catálogo antes | Funciona sin señal, y la pantalla de sesión no cambia de forma de trabajar |
| `PUT` de la rutina completa | Operaciones por ejercicio | RF-002-05 pide todo o nada; una rutina tiene como mucho 20 filas |
| Rutinas y catálogo en el arranque | Pedirlos al abrir cada pantalla | Sin señal no habría con qué empezar una sesión desde una rutina |

## 7. Seguridad

Lo mismo que el plan 006, sección 7: base común de la API, validación en el servidor y en la base, y una prueba por operación con una segunda cuenta (RNF-ACC-06). Lo nuevo: el catálogo predefinido se crea por cuenta, así que renombrar o borrar un ejercicio nunca toca el de otra persona (RF-002-10, CA-002-10a).

## 8. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| CA-002-RN (bordes) | Unitaria, misma tabla en los dos lados | `backend/tests/reglas`, `frontend/src/reglas` |
| CA-002-01a, 03a, 06a, 09a, 10a, 13a, 16a, 18a, 19a, 21a | Integración de la API | `backend/tests/rutinas` |
| Rangos y unicidad en la base | Integración, escribiendo directo en la base | `backend/tests/rutinas/test_modelos.py` |
| Catálogo inicial y migración de datos | Integración | `backend/tests/rutinas` |
| Enlace sesión–catálogo | Integración | `backend/tests/sesiones` |
| RNF-ACC-06 (cuenta ajena) | Integración: una por operación | `backend/tests/rutinas/test_permisos.py` |
| Empezar sesión desde rutina, con y sin señal (CA-006-01a, 05a, 13a) | Unitaria del modelo y del estado del celular | `frontend/src/sesion`, `frontend/src/estado` |
| Pantallas | Recorrido a mano en 375 px, en el navegador | Bitácora |

## 9. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| La migración de datos falla en Railway con tu cuenta real | Baja | Se prueba en la revisión automática contra PostgreSQL con una cuenta creada antes de migrar. |
| Una rutina guardada en el celular está desactualizada al empezar sin señal | Media | Es aceptable: la sesión copia la rutina tal como el celular la conocía, y al sincronizar no se pierde nada. |
| Dos ejercicios distintos que solo difieren en tildes ("Remo" y "Remó") quedan como uno | Baja | Es lo que pide RN-002-07. |
| Más memoria en Railway por el arranque más grande | Baja | 5 cuentas, 40 ejercicios y unas pocas rutinas son unos kilobytes. |

## 10. Orden de construcción

1. **Servidor del catálogo:** reglas, modelos, catálogo inicial, migración de datos, API.
2. **Servidor de rutinas:** API de rutinas, duplicar, enlace con sesiones, arranque ampliado.
3. **Pantalla:** catálogo y rutinas guardados en el celular, empezar sesión desde rutina (cierra el hito B de la 006), pantallas de rutinas y catálogo.

El detalle está en [`tasks.md`](tasks.md).
