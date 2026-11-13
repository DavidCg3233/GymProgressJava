# Tasks 008 — El récord manda y la sesión se vuelve rutina

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-13) |
| **Creado** | 2026-11-13 |
| **Avance** | 16 de 17 con código y pruebas (T-008-01 a 16). Falta T-008-17, que es de David. Ninguna cerrada hasta que David escriba su línea en la bitácora |

> Mismas reglas que en las demás specs:
> - **Una tarea = un commit**, en orden, con TDD: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - **Nada sube a producción** hasta que T-008-15 (huella de la base) y T-008-16 (recorrido) muestren que no se pierde información, y las cuatro revisiones automáticas estén en verde.

## Fase 1 — Reglas (sin pantalla ni base de datos)

- [x] **T-008-01** "Supera", mejor serie y referencia, en Python y JavaScript.
  - Cumple: RN-008-01, 02, 03. Hecho cuando: CA-008-02b y 02c, más la tabla de "supera" (2 × 18 vs 1 × 20, 10 × 20 vs 10 × 18, empates, peso corporal), pasan en los dos lados con los mismos casos.
- [x] **T-008-02** Reglas de sesión → rutina.
  - `reglas/sesion_a_rutina.py`: ejercicios de una sesión, rutina nueva, actualizar rutina con su lista de cambios.
  - Cumple: RN-008-05, 06, 07. Hecho cuando: CA-008-06a y 07a pasan como pruebas sin base de datos, más los bordes (ejercicio repetido, 11 series, 21 ejercicios, sesión sin series confirmadas).
- [x] **T-008-03** Renumerar y sugerencias.
  - `sesion/series.js`.
  - Cumple: RN-008-08, 10. Hecho cuando: CA-008-08a y 10a pasan, más tildes ("pajaros" encuentra "Pájaros") y el tope de 6.

## Fase 2 — Servidor

- [x] **T-008-04** Récords en el arranque.
  - Cumple: RF-008-05, RNF-008-02. Hecho cuando: el arranque trae el récord de cada ejercicio con series confirmadas, nada de otra cuenta, y un ejercicio eliminado del catálogo conserva su récord con su clave.
- [x] **T-008-05** Sesión → rutina nueva, con vista previa.
  - `POST /api/sesiones/{id}/a-rutina/` con `modo: nueva`.
  - Cumple: RF-008-06, RN-008-05, 06. Hecho cuando: CA-008-06a y 06b pasan por la API; la vista previa no guarda nada; una sesión en curso responde 409.
- [x] **T-008-06** Sesión → actualizar una rutina.
  - `modo: actualizar`.
  - Cumple: RF-008-07, RN-008-07. Hecho cuando: CA-008-07a pasa por la API, con la lista de cambios en la vista previa; pasar de 20 ejercicios se rechaza sin cambiar nada.
- [x] **T-008-07** Permisos de sesión → rutina.
  - Cumple: RNF-ACC-06. Hecho cuando: con dos cuentas, ni la sesión ni la rutina de la otra se pueden usar (404), y sin acceso responde 401.

## Fase 3 — Celular

- [x] **T-008-08** Récords guardados y actualizados sin señal.
  - Cumple: RF-008-05, RNF-008-02. Hecho cuando: CA-008-05a pasa en las pruebas del estado, en modo avión.
- [x] **T-008-09** Precarga con la referencia y la pista de la última vez.
  - Cumple: RF-008-03, 04. Hecho cuando: CA-008-03a, 03b y 04a pasan en el modelo; CA-006-04a y 05a quedan reescritos como sus reemplazos.
- [x] **T-008-10** Quitar con renumeración y deshacer.
  - Cumple: RF-008-08, 09, RN-008-09. Hecho cuando: CA-008-08a y 09a pasan en el modelo y en el estado, y la cola envía en el orden de plan 4.4 (probado con el servidor simulado y su regla de números únicos).

## Fase 4 — Pantallas

- [x] **T-008-11** Buscador de ejercicios propio.
  - En la sesión y en el editor.
  - Cumple: RF-008-10, RNF-008-01. Hecho cuando: CA-008-10a se ve en el navegador.
- [x] **T-008-12** Récord y referencia en el editor de rutina.
  - Cumple: RF-008-01, 02. Hecho cuando: CA-008-01a y 02a se ven en el navegador.
- [x] **T-008-13** Fila de serie: pista, "Quitar" lejos de "Confirmar" y "Deshacer".
  - Cumple: RF-008-03, 09, RNF-008-05, RNF-007-02. Hecho cuando: "Quitar" mide 44 px y está a 16 px o más de "Confirmar"; la prueba de Playwright mide la sesión.
- [x] **T-008-14** Guardar como rutina, desde el resumen y desde el historial.
  - Cumple: RF-008-06, 07, RNF-008-03. Hecho cuando: CA-008-06a y 07a se ven en el navegador, con la vista previa, y sin señal avisa sin perder lo escrito.

## Fase 5 — Cierre

- [x] **T-008-15** Huella de la base antes y después.
  - Un script cuenta y resume sesiones, series y rutinas de la base local antes y después del recorrido.
  - Cumple: RNF-008-04. Hecho cuando: solo cambian las rutinas guardadas a propósito y las series quitadas a propósito.
- [x] **T-008-16** Recorrido completo a 375 px, en claro y oscuro, con todos los criterios, y la prueba de modo avión en verde.
- [ ] **T-008-17** `[D]` En tu iPhone: escribir en el buscador sin tirones (RNF-008-01), una sesión real con la referencia, y guardar una sesión como rutina.

## Bitácora

| Fecha | Tarea | Qué entendí / qué cambió | Quién |
|---|---|---|---|
| 2026-11-13 | T-008-03 | Regla agregada al construir: el nombre ya escrito completo no se sugiere a sí mismo (si no, la lista no se cerraría al elegir) | IA |
| 2026-11-13 | T-008-05 a 07 | Un commit: comparten servicio y archivo de pruebas. Al probar apareció algo que faltaba: el servicio pone al día las sesiones antes de mirarlas (una de más de 2 horas cuenta como terminada) | IA |
| 2026-11-13 | T-008-09 | Las pruebas viejas que esperaban la precarga de la última vez (CA-006-04a, 05a y los 30 × 10 de confirmar) se reescribieron a propósito: la regla cambió (spec 008, sección 9) | IA |
| 2026-11-13 | T-008-10 | Un servidor de juguete con la regla de números únicos reproduce los envíos en orden: quitar, deshacer y la mezcla sin señal llegan sin choques | IA |
| 2026-11-13 | T-008-13 | Playwright mide en la sesión los botones (44 px, 8 de aire, "Quitar" lejos de "Confirmar"). Encontró que los campos del número (kg, reps) miden 25 × 24 y recortan "38,5": no caben más anchos en la fila actual; los agranda el rediseño de la fila de serie (T-007-10) | IA |
| 2026-11-13 | T-008-15 | Huella de la base local antes y después del recorrido: 0 filas quitadas y 0 cambiadas entre las que ya existían. Solo se agregó lo hecho a propósito (1 sesión con 2 series, la rutina "Pecho C" con 2 ejercicios). La rutina "Pecho" no cambió aunque el editor mostraba su récord, porque se canceló sin guardar | IA |
| 2026-11-13 | T-008-16 | Recorrido a 375 px contra el servidor local: CA-008-01a/02a (récord en el editor, "subió con tu récord"), 03a (precarga con el récord y pista de la última vez), 06a/06b (rutina nueva y nombre repetido), 07a (actualizar desde el historial: "Queda igual" y "Se agrega"), 08a/09a (quitar, numeración seguida y deshacer, sin rechazos del servidor), 10a (sugerencias con "pr"). Prueba de modo avión en verde | IA |

### Notas técnicas
