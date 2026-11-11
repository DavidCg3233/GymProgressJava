# Tasks 007 — Rediseño visual

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-11) |
| **Creado** | 2026-11-11 |
| **Avance** | 0 de 18 |

> Mismas reglas que en las demás specs:
> - **Una tarea = un commit**, en orden, con TDD donde hay lógica: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - Todo se fusiona a `main` solo con las cuatro revisiones automáticas en verde. **Se fusiona por partes** (al final de las fases 2, 3 y 4), para que `main` nunca tenga la app a medias.

## Fase 1 — Base

- [ ] **T-007-01** Fichas de diseño, en claro y en oscuro.
  - `estilos/fichas.css` con las fichas de `DESIGN.md`; `base.css` rehecho sobre ellas; todas las pantallas pasan a los nombres nuevos.
  - Cumple: RF-007-04, RN-007-04. Hecho cuando: una prueba falla si queda una variable `--color-*` vieja o un color escrito a mano en una pantalla; la app se ve con la paleta nueva en los dos temas.
- [ ] **T-007-02** Prueba de contraste de las fichas.
  - Cumple: RNF-007-01. Hecho cuando: la prueba mide cada par de texto en los dos temas y falla con menos de 4,5:1.
- [ ] **T-007-03** Íconos y encabezado.
  - `Icono.vue` con los íconos de `DESIGN.md`; `Encabezado.vue` con título grande y una acción.
  - Cumple: RNF-007-05. Hecho cuando: los íconos se ven sin descargar nada.
- [ ] **T-007-04** `theme-color` según el tema y "Reducir movimiento".
  - Cumple: RNF-007-04, 06. Hecho cuando: la barra de estado acompaña al tema y, con movimiento reducido, nada se anima.

## Fase 2 — Navegación

- [ ] **T-007-05** Destinos y tiempo de la sesión, como funciones puras.
  - `navegacion/destinos.js` y `navegacion/tiempo.js`.
  - Cumple: RN-007-01, 02. Hecho cuando: las pruebas cubren las 4 secciones, las vistas internas (editor → Rutinas) y los bordes del tiempo (0 min, 59 min, 1 h 00 min, 1 h 05 min).
- [ ] **T-007-06** Barra inferior.
  - Cumple: RF-007-01, RNF-007-06. Hecho cuando: CA-007-01a se ve en el navegador y la barra respeta la zona inferior del iPhone.
- [ ] **T-007-07** Sesión a pantalla completa, "Minimizar" y franja.
  - Cumple: RF-007-02, 03. Hecho cuando: CA-007-02a y 02b se ven en el navegador; la prueba de modo avión sigue pasando.
- [ ] **T-007-08** Menú de cuenta.
  - Cumple: RF-007-07, RNF-USA-04. Hecho cuando: CA-007-07a se ve en el navegador, con el aviso de pendientes al salir.
- [ ] **T-007-09** Medidas en WebKit.
  - La prueba de Playwright mide en el Inicio y en la sesión que todo botón mida 44 × 44 con 8 de separación, y que confirmar una serie siga siendo 1 toque.
  - Cumple: RNF-007-02, 03. Hecho cuando: pasa en la revisión automática. **Fin de la fase: se fusiona.**

## Fase 3 — Pantallas

- [ ] **T-007-10** Sesión en curso: fila de serie, paso numérico y ejercicio.
  - Cumple: RF-007-05, 06, RN-007-03. Hecho cuando: CA-007-05a y 06a se ven en el navegador.
- [ ] **T-007-11** Inicio.
  - Hoy toca, esta semana, últimas sesiones y el resumen al terminar.
  - Cumple: RF-004-01 a 10 con el diseño nuevo. Hecho cuando: CA-004-01a, 02a y 03a siguen cumpliéndose.
- [ ] **T-007-12** Progreso, evolución y peso.
  - Cumple: el diseño de gráficas de `DESIGN.md`. Hecho cuando: CA-004-05a, 09a y CA-003-01a se ven en los dos temas.
- [ ] **T-007-13** Rutinas, editor y catálogo.
  - Hecho cuando: crear, editar, duplicar y eliminar una rutina, y renombrar un ejercicio, se ven y funcionan en los dos temas.
- [ ] **T-007-14** Historial y detalle.
  - Hecho cuando: la lista y el detalle se ven en los dos temas, con eliminar y su confirmación.
- [ ] **T-007-15** Acceso y cambiar contraseña.
  - Hecho cuando: entrar y el cambio obligatorio de contraseña se ven en los dos temas. **Fin de la fase: se fusiona.**

## Fase 4 — Cierre

- [ ] **T-007-16** Recorrido completo a 375 px en claro y en oscuro, contra el servidor local, con todos los criterios de la spec.
- [ ] **T-007-17** `[D]` Probarlo en tu iPhone: los dos temas (cámbialo en Ajustes con la app abierta), la barra de estado, una sesión real con "Minimizar".
- [ ] **T-007-18** `[D]` Pasar la spec 007 a `Implementada` si todos sus criterios están marcados, y actualizar `SPECS/README.md`.

## Bitácora

| Fecha | Tarea | Qué entendí / qué cambió | Quién |
|---|---|---|---|

### Notas técnicas
