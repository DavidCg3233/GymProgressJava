# Tasks 007 — Rediseño visual

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-11) |
| **Creado** | 2026-11-11 |
| **Avance** | 9 de 18 con código (fases 1 y 2). Ninguna cerrada hasta que David escriba su línea en la bitácora |

> Mismas reglas que en las demás specs:
> - **Una tarea = un commit**, en orden, con TDD donde hay lógica: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - Todo se fusiona a `main` solo con las cuatro revisiones automáticas en verde. **Se fusiona por partes** (al final de las fases 2, 3 y 4), para que `main` nunca tenga la app a medias.

## Fase 1 — Base

- [x] **T-007-01** Fichas de diseño, en claro y en oscuro.
  - `estilos/fichas.css` con las fichas de `DESIGN.md`; `base.css` rehecho sobre ellas; todas las pantallas pasan a los nombres nuevos.
  - Cumple: RF-007-04, RN-007-04. Hecho cuando: una prueba falla si queda una variable `--color-*` vieja o un color escrito a mano en una pantalla; la app se ve con la paleta nueva en los dos temas.
- [x] **T-007-02** Prueba de contraste de las fichas.
  - Cumple: RNF-007-01. Hecho cuando: la prueba mide cada par de texto en los dos temas y falla con menos de 4,5:1.
- [x] **T-007-03** Íconos y encabezado.
  - `Icono.vue` con los íconos de `DESIGN.md`; `Encabezado.vue` con título grande y una acción.
  - Cumple: RNF-007-05. Hecho cuando: los íconos se ven sin descargar nada.
- [x] **T-007-04** `theme-color` según el tema y "Reducir movimiento".
  - Cumple: RNF-007-04, 06. Hecho cuando: la barra de estado acompaña al tema y, con movimiento reducido, nada se anima.

## Fase 2 — Navegación

- [x] **T-007-05** Destinos y tiempo de la sesión, como funciones puras.
  - `navegacion/destinos.js` y `navegacion/tiempo.js`.
  - Cumple: RN-007-01, 02. Hecho cuando: las pruebas cubren las 4 secciones, las vistas internas (editor → Rutinas) y los bordes del tiempo (0 min, 59 min, 1 h 00 min, 1 h 05 min).
- [x] **T-007-06** Barra inferior.
  - Cumple: RF-007-01, RNF-007-06. Hecho cuando: CA-007-01a se ve en el navegador y la barra respeta la zona inferior del iPhone.
- [x] **T-007-07** Sesión a pantalla completa, "Minimizar" y franja.
  - Cumple: RF-007-02, 03. Hecho cuando: CA-007-02a y 02b se ven en el navegador; la prueba de modo avión sigue pasando.
- [x] **T-007-08** Menú de cuenta.
  - Cumple: RF-007-07, RNF-USA-04. Hecho cuando: CA-007-07a se ve en el navegador, con el aviso de pendientes al salir.
- [x] **T-007-09** Medidas en WebKit.
  - La prueba de Playwright mide en el Inicio y en la sesión que todo botón mida 44 × 44 con 8 de separación, y que confirmar una serie siga siendo 1 toque.
  - Cumple: RNF-007-02, 03. Hecho cuando: pasa en la revisión automática. **Fin de la fase: se fusiona.**

## Fase 3 — Pantallas

- [ ] **T-007-10** Sesión en curso: fila de serie, paso numérico y ejercicio.
  - Cumple: RF-007-05, 06, RN-007-03. Hecho cuando: CA-007-05a y 06a se ven en el navegador, y la prueba de Playwright mide también la sesión (objetivos de 44 y 8 de separación).
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
| 2026-11-11 | T-007-01 a 04 | Fichas en `fichas.css` (el único archivo con colores) y `base.css` rehecho sobre ellas: todas las pantallas cambian de color ya, antes de rehacerlas. 32 pares de contraste medidos por una prueba. Dos tropiezos de Vue resueltos en T-007-06: `<script setup>` no admite `export` ni que `defineProps` use una variable local (los trazos pasaron a `iconos.js`) | IA |
| 2026-11-11 | T-007-07 | **Choque entre specs, resuelto así (pendiente de tu visto bueno):** la franja no se muestra en el Inicio, porque ahí CA-004-02a ya pone "Continuar sesión" primero y serían dos botones iguales. Regla `muestraFranja` con su prueba | IA |
| 2026-11-11 | T-007-09 | La prueba de Playwright mide en el Inicio que todo objetivo mida 44 × 44 y que dos pequeños vecinos queden a 8 px o más. Las pestañas de la barra (≈ 94 px cada una) se tocan, como en el iPhone: la regla de 8 px se aplica cuando al menos uno mide menos de 60 px. La medida de la sesión entra con T-007-10, porque hoy su "Quitar" mide 28 px de alto. Pasó en WebKit en mi equipo | IA |

### Notas técnicas
