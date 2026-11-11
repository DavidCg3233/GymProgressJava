# Tasks 002 — Rutinas y catálogo de ejercicios

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-10) |
| **Creado** | 2026-11-10 |
| **Avance** | 0 de 20 cerradas · 11 con código (T-002-01 a 11): servidor completo |

> Mismas reglas que en la spec 006:
> - **Una tarea = un commit**, en orden, con TDD: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - Todo se fusiona a `main` solo con las cuatro revisiones automáticas en verde.

## Fase 1 — Reglas (sin pantalla ni base de datos)

- [ ] **T-002-01** Reglas de rutina en Python.
  - `reglas/rutinas.py`: nombre (1 a 50), días (lista del 1 al 7 sin repetidos), ejercicios (1 a 20, sin repetir), series previstas (1 a 10), nombre de la copia ("(copia)", "(copia 2)"…, sin pasar de 50), rutinas de un día.
  - Cumple: RN-002-01 a 06, RF-002-03, 21; plan, sección 6. Hecho cuando: la tabla CA-002-RN pasa como prueba, sin base de datos.
- [ ] **T-002-02** Las mismas reglas en JavaScript.
  - Hecho cuando: la misma tabla pasa en Vitest, caso por caso y mensaje por mensaje.

## Fase 2 — Catálogo en el servidor

- [ ] **T-002-03** Modelos del catálogo y de las rutinas, con sus restricciones.
  - `grupo_muscular`, `ejercicio`, `rutina`, `rutina_ejercicio` (plan, 4.1). Únicos por clave, rangos en la base, un grupo con ejercicios no se puede borrar.
  - Cumple: RN-002-03 a 08, RF-002-19. Hecho cuando: pruebas que escriben directo en la base confirman cada restricción.
- [ ] **T-002-04** Catálogo inicial al crear una cuenta.
  - `rutinas/catalogo_inicial.py` con los 8 grupos y 40 ejercicios, y la señal que lo carga.
  - Cumple: RF-002-14, 10. Hecho cuando: una cuenta nueva tiene 8 grupos y 40 ejercicios; dos cuentas no comparten ninguno (CA-002-10a).
- [ ] **T-002-05** Migración de datos para las cuentas que ya existen.
  - Les carga el catálogo y enlaza sus sesiones ya registradas por nombre; si un ejercicio de una sesión no existe en el catálogo, lo crea con el grupo que traía.
  - Cumple: RF-002-14, 09; plan, 4.3. Hecho cuando: una prueba crea una cuenta y una sesión antes de migrar, migra, y encuentra el catálogo completo y la sesión enlazada. Corre también contra PostgreSQL en la revisión automática.
- [ ] **T-002-06** API del catálogo.
  - Listar; crear y renombrar grupos; borrar grupo vacío; crear, renombrar y cambiar de grupo un ejercicio.
  - Cumple: RF-002-08, 09, 15, 19. Hecho cuando: CA-002-09a y 19a pasan, más la prueba de cuenta ajena por operación.
- [ ] **T-002-07** Eliminar un ejercicio del catálogo.
  - `uso` (en qué rutinas está y cuáles quedarían vacías) y el borrado en una sola transacción.
  - Cumple: RF-002-16, 17, 18. Hecho cuando: CA-002-16a y 18a pasan, y las sesiones que lo usaban conservan su copia.

## Fase 3 — Rutinas en el servidor

- [ ] **T-002-08** Guardar y listar rutinas.
  - `PUT` de la rutina completa en una transacción; listado con ejercicios en orden y días como lista.
  - Cumple: RF-002-01, 03, 04, 05, 20. Hecho cuando: CA-002-01a, 03a y la tabla de bordes pasan en la API; un `PUT` con un ejercicio inválido no cambia nada de la rutina anterior.
- [ ] **T-002-09** Duplicar y eliminar rutinas.
  - Cumple: RF-002-06, 21. Hecho cuando: CA-002-06a y 21a pasan; duplicar dos veces da "(copia)" y "(copia 2)".
- [ ] **T-002-10** Enlazar sesiones con rutinas y catálogo.
  - Campo `rutina` opcional en la sesión (una rutina ajena o eliminada se ignora); el servidor enlaza cada ejercicio de sesión al catálogo, creándolo si no existe.
  - Cumple: RF-006-01, RF-002-09, 13; plan, 4.3. Hecho cuando: CA-002-13a pasa; una sesión con una rutina eliminada se guarda igual.
- [ ] **T-002-11** Arranque con catálogo y rutinas.
  - Cumple: RF-006-17. Hecho cuando: `/api/arranque/` trae catálogo y rutinas del usuario, y nada de otra cuenta.

## Fase 4 — Pantalla

- [ ] **T-002-12** Catálogo y rutinas guardados en el celular.
  - Se guardan con el arranque y se actualizan al editarlos; los grupos de la sesión salen del catálogo.
  - Cumple: RF-006-17, RF-002-08. Hecho cuando: pruebas del estado del celular: sin señal, el catálogo y las rutinas siguen disponibles.
- [ ] **T-002-13** Empezar una sesión desde una rutina (cierra T-006-37).
  - `modelo.nuevaSesionDesdeRutina`, con y sin señal.
  - Cumple: RF-006-01, 04, 05, 11; RF-002-13, 20. Hecho cuando: CA-006-01a, 04a, 05a y 11a pasan en el modelo y en el estado del celular, incluido en modo avión.
- [ ] **T-002-14** Pantalla "Mis rutinas".
  - Tarjetas con días y cantidad de ejercicios; Empezar, Editar, Duplicar, Eliminar con confirmación.
  - Cumple: RF-002-01, 06, 21; RNF-USA-04. Hecho cuando: recorrido a mano en 375 px.
- [ ] **T-002-15** Editor de rutina.
  - Nombre, días, ejercicios con buscador del catálogo y grupo para uno nuevo, series/reps/peso, subir y bajar, quitar.
  - Cumple: RF-002-03, 04, 08, 09, 20; RNF-002-01. Hecho cuando: recorrido a mano en 375 px, incluido el aviso sin señal sin perder lo escrito.
- [ ] **T-002-16** Pantalla del catálogo.
  - Cumple: RF-002-15 a 19. Hecho cuando: recorrido a mano: renombrar, cambiar de grupo, eliminar mostrando en qué rutinas está, crear grupo, rechazo al borrar un grupo con ejercicios.
- [ ] **T-002-17** Sugerencias del catálogo al agregar un ejercicio a una sesión.
  - Cumple: RF-002-08. Hecho cuando: escribir "press" en la sesión sugiere los ejercicios del catálogo y toma su grupo.

## Fase 5 — Cierre

- [ ] **T-002-18** Recorrido completo en el navegador contra el servidor local.
  - Crear una rutina, empezarla, registrar series, terminar, empezarla otra vez y ver "la última vez"; modificar la rutina con una sesión en curso (CA-002-13a); eliminar un ejercicio usado en una rutina.
- [ ] **T-002-19** `[D]` Probarlo en tu iPhone con la app publicada, incluida una sesión desde rutina en modo avión.
- [ ] **T-002-20** `[D]` Pasar las specs 002 y 006 a `Implementada` si todos sus criterios están marcados, y actualizar `SPECS/README.md`.

## Bitácora

| Fecha | Tarea | Código | Qué entendí (lo escribe David) |
|---|---|---|---|
| 2026-11-10 | T-002-01 | Reglas de rutina en Python. **Sin rojo previo:** la prueba y el código se escribieron juntos; para compensar, 7 errores introducidos a propósito fueron todos detectados | `[DAVID]` |
| 2026-11-10 | T-002-02 | Las mismas reglas en JavaScript, con rojo previo | `[DAVID]` |
| 2026-11-10 | T-002-03 a 05 | Catálogo por persona, 40 ejercicios predefinidos al crear la cuenta, migración para cuentas existentes. Probada sobre la base local: la cuenta `prueba` recibió el catálogo y sus 3 ejercicios de sesión quedaron enlazados | `[DAVID]` |
| 2026-11-10 | T-002-06 a 09 | API del catálogo y de las rutinas: crear, renombrar, eliminar con aviso, duplicar con numeración | `[DAVID]` |
| 2026-11-10 | T-002-10 y 11 | La sesión recuerda su rutina, cada ejercicio de sesión entra solo al catálogo, el arranque trae catálogo y rutinas | `[DAVID]` |

### Notas técnicas

- **Error encontrado por las pruebas en T-002-03:** la protección "no borrar un grupo con ejercicios" (`PROTECT`) también impedía eliminar una cuenta completa. Se cambió a `RESTRICT`, que mantiene la regla del grupo y permite borrar todo junto.
- **La migración agrega al catálogo los ejercicios que ya registraste** y no están en la lista predefinida. En la base local apareció así "Press Inclinado en maquina".
- **Una rutina inexistente o ajena en una sesión se ignora** en vez de rechazar la sesión: pudo eliminarse mientras el celular estaba sin señal.
