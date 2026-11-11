# Tasks 004 — Inicio y progreso

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-10) |
| **Creado** | 2026-11-10 |
| **Avance** | 16 de 18 con código y pruebas (T-004-01 a 16). Faltan T-004-17 y 18, que son de David. Ninguna cerrada hasta que David escriba su línea en la bitácora |

> Mismas reglas que en las specs 006 y 002:
> - **Una tarea = un commit**, en orden, con TDD: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - Todo se fusiona a `main` solo con las cuatro revisiones automáticas en verde.

## Fase 1 — Reglas (sin pantalla ni base de datos)

- [x] **T-004-01** Reglas de progreso en Python.
  - `reglas/progreso.py`: récord, peso corporal, serie más pesada, volumen, inicio de semana, sesiones por semana, cumple, validar meta, ordenar grupos.
  - Cumple: RN-004-02 a 09; plan, secciones 5 y 6. Hecho cuando: CA-004-04a, 04b y 09a pasan como pruebas con sus mismos números, sin base de datos.
- [x] **T-004-02** Las reglas que usa el celular, en JavaScript.
  - `reglas/progreso.js`: inicio de semana, cumple, validar meta y rutinas hechas hoy.
  - Hecho cuando: la misma tabla pasa en Vitest, caso por caso y mensaje por mensaje.

## Fase 2 — Servidor

- [x] **T-004-03** Meta semanal en la cuenta.
  - Campo `meta_semanal` con `CHECK` de 1 a 14, migración, `PUT /api/progreso/meta/`. La meta se lee en `GET /api/progreso/` (T-004-05): solo Progreso la usa.
  - Cumple: RF-004-11, RN-004-08. Hecho cuando: fijar, cambiar y quitar funcionan; 0, 15 y "4" se rechazan en la API y en la base.
- [x] **T-004-04** Qué cuenta y récords.
  - App `progreso`, consulta base `series_que_cuentan` (plan 4.1 y 4.2), y `records` en `GET /api/progreso/`.
  - Cumple: RF-004-04, RN-004-01, 03, 04, 10. Hecho cuando: CA-004-04a, 04b y 04c pasan por la API; un ejercicio eliminado del catálogo sigue con su récord; una sesión en curso no cuenta y una cerrada sola a las 2 horas sí.
- [x] **T-004-05** Sesiones por semana y meta.
  - `semanas` y `meta` en `GET /api/progreso/`.
  - Cumple: RF-004-05, 11, RN-004-02, 07, 08; regla nueva 3. Hecho cuando: CA-004-05a y 05b pasan, y una sesión sin series confirmadas no suma.
- [x] **T-004-06** Series por grupo muscular.
  - `grupos` en `GET /api/progreso/`.
  - Cumple: RF-004-06, RN-004-09, 10; regla nueva 1. Hecho cuando: CA-004-06a pasa; cambiar un ejercicio de grupo mueve sus series; un ejercicio eliminado cuenta en el grupo que tenía.
- [x] **T-004-07** Progreso vacío.
  - Cumple: RF-004-12. Hecho cuando: CA-004-12a pasa por la API (`vacio: true`, sin semanas ni récords).
- [x] **T-004-08** Evolución de un ejercicio.
  - `GET /api/progreso/evolucion/?clave=…`.
  - Cumple: RF-004-09, RN-004-05, 06; regla nueva 2. Hecho cuando: CA-004-09a pasa por la API (32,5 y 755); peso corporal grafica reps; clave desconocida responde 404.
- [x] **T-004-09** Permisos de progreso.
  - Cumple: RNF-ACC-06. Hecho cuando: con dos cuentas, las series de la otra no aparecen en ninguna cifra, y sin acceso todo responde 401 (403 con contraseña temporal).
- [x] **T-004-10** Arranque con recientes y rutinas hechas hoy.
  - Cumple: RF-004-07, 10; plan 4.5. Hecho cuando: el arranque trae las 3 sesiones más recientes y las rutinas hechas hoy en hora de Colombia.

## Fase 3 — Pantalla

- [x] **T-004-11** Recientes y "hechas hoy" en el celular, también sin señal.
  - Se guardan con el arranque; al terminar una sesión se actualizan sin esperar al servidor.
  - Cumple: RNF-004-01, RF-004-07, 10. Hecho cuando: las pruebas del estado muestran la sesión recién terminada primera y su rutina como hecha, sin servidor; al día siguiente ya no aparece como hecha.
- [x] **T-004-12** Inicio en el orden de la spec.
  - Cumple: RF-004-01, 02, 03, 07, 10. Hecho cuando: CA-004-01a, 02a y 03a se ven en el navegador.
- [x] **T-004-13** Pantalla de Progreso.
  - Semana frente a la meta, editar la meta, 12 semanas, grupos, récords, el "?" de cada indicador y el aviso sin conexión.
  - Cumple: RF-004-04, 05, 06, 11, 12, RNF-004-02, 03. Hecho cuando: CA-004-05a y 12a se ven en el navegador, y sin servidor aparece "Progreso necesita conexión".
- [x] **T-004-14** Gráfica de línea en SVG.
  - Función pura de escalas probada en Vitest; componente que la dibuja y deja tocar cada punto.
  - Cumple: RF-004-09; plan, sección 6. Hecho cuando: las pruebas de escalas pasan (un solo punto, todos iguales, valores grandes).
- [x] **T-004-15** Evolución de un ejercicio.
  - Tocar un récord abre su gráfica, con el selector "Serie más pesada / Volumen".
  - Cumple: RF-004-09. Hecho cuando: CA-004-09a se ve en el navegador al tocar el punto.

## Fase 4 — Cierre

- [x] **T-004-16** Recorrido completo en el navegador contra el servidor local, a 375 px.
- [ ] **T-004-17** `[D]` Probarlo en tu iPhone con la app publicada: inicio en modo avión, y Progreso con señal después de tu próxima sesión real.
- [ ] **T-004-18** `[D]` Pasar la spec 004 a `Implementada` si todos sus criterios están marcados, y actualizar `SPECS/README.md`.

## Bitácora

| Fecha | Tarea | Qué entendí / qué cambió | Quién |
|---|---|---|---|
| 2026-11-10 | T-004-03 | La prueba que vigila los campos de la cuenta falló al agregar la meta: se agregó a la lista permitida porque es una preferencia, no un dato personal. Un commit salió con esa prueba en rojo y se corrigió antes de subir | IA |
| 2026-11-10 | T-004-04 a 08 | Van en un solo commit: las cinco comparten la consulta base de "qué cuenta". Ajuste al plan 4.2: la identidad del ejercicio es la clave del catálogo hoy, para que un renombre junte sus series viejas y nuevas | IA |
| 2026-11-10 | T-004-09 | Las pruebas de permisos pasaron sin código nuevo: la base común de la API ya protegía todo. Quedan como red de seguridad | IA |
| 2026-11-10 | T-004-16 | Recorrido a 375 px contra el servidor local, con 16 sesiones sembradas: CA-004-01a, 02a, 05a (con meta 2), 06a y 09a se ven bien; inicio sin servidor funciona. Se encontró y corrigió: sin servidor, Progreso decía "Algo salió mal" (el proxy responde 5xx, no falla de red); la explicación "?" se apretaba en el encabezado; "Mis rutinas" se partía en dos líneas | IA |

### Notas técnicas
