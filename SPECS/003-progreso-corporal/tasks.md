# Tasks 003 — Progreso corporal

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-11) |
| **Creado** | 2026-11-11 |
| **Avance** | 0 de 16 |

> Mismas reglas que en las specs 006, 002 y 004:
> - **Una tarea = un commit**, en orden, con TDD: primero la prueba, verla fallar, después el código.
> - La IA entrega cada tarea con pruebas y una explicación corta; David escribe en la bitácora qué entendió. Sin esa línea, la tarea no se cierra.
> - `[D]` = la hace David a mano.
> - Todo se fusiona a `main` solo con las cuatro revisiones automáticas en verde.

## Fase 1 — Reglas (sin pantalla ni base de datos)

- [ ] **T-003-01** Reglas del cuerpo en Python.
  - `reglas/cuerpo.py`: validar peso, estatura y fecha; IMC exacto y para mostrar; categoría; cambio; avance hacia el objetivo.
  - Cumple: RN-003-01 a 05, 08; plan, secciones 5 y 6. Hecho cuando: las tablas CA-003-05b y CA-003-13a pasan como pruebas, y también 25,8 de CA-003-01a, "4,0 por bajar" de CA-003-08a y el alcanzado de CA-003-09a, sin base de datos.
- [ ] **T-003-02** Las validaciones en JavaScript.
  - `reglas/cuerpo.js`: peso, estatura y fecha.
  - Hecho cuando: la tabla CA-003-13a pasa en Vitest, caso por caso y mensaje por mensaje.

## Fase 2 — Servidor

- [ ] **T-003-03** Modelo del registro y campos de la cuenta.
  - App `cuerpo` con `registro_de_peso`; `estatura_cm` y `peso_objetivo` en la cuenta, con migración.
  - Cumple: RN-003-03, 04, 06, 07; plan 4.1. Hecho cuando: la base rechaza un segundo registro del mismo día y los valores fuera de rango, aunque se escriba directo.
- [ ] **T-003-04** Registrar, reemplazar, corregir y eliminar.
  - `PUT` y `DELETE /api/peso/{fecha}/`.
  - Cumple: RF-003-01, 02, 10, 11, 13. Hecho cuando: CA-003-02a, 10a y 11a pasan por la API; sin `reemplazar` responde 409 con el peso que había; mañana y 300,1 se rechazan.
- [ ] **T-003-05** Estatura y peso objetivo.
  - `PUT /api/peso/estatura/` y `PUT /api/peso/objetivo/`.
  - Cumple: RF-003-08, 12, 13. Hecho cuando: fijar y cambiar funcionan; 99, 251 y 1,75 se rechazan; el objetivo se puede quitar.
- [ ] **T-003-06** Historial y resumen.
  - `GET /api/peso/`.
  - Cumple: RF-003-03 a 09. Hecho cuando: CA-003-01a, 05a, 08a y 09a pasan por la API; sin registros `resumen` es `null`.
- [ ] **T-003-07** Permisos del peso.
  - Cumple: RNF-ACC-06; plan, sección 7. Hecho cuando: con dos cuentas y la misma fecha, ninguna ve, corrige ni borra lo de la otra; sin acceso todo responde 401.

## Fase 3 — Pantalla

- [ ] **T-003-08** Línea del peso objetivo en la gráfica.
  - Cumple: RF-003-07. Hecho cuando: las pruebas de escalas incluyen el objetivo dentro del rango, también cuando queda por fuera de los pesos registrados.
- [ ] **T-003-09** Estado del peso en el celular.
  - `estado/cuerpo.js`: cargar, registrar con su 409, corregir, eliminar, estatura y objetivo; mensaje sin conexión.
  - Cumple: RNF-003-02. Hecho cuando: las pruebas muestran el pedido de confirmación ante un 409 y que sin conexión no se pierde lo escrito.
- [ ] **T-003-10** Pestañas Entrenamiento y Peso en Progreso.
  - Cumple: RNF-003-01; plan 4.4. Hecho cuando: la pestaña elegida se recuerda y registrar hoy toma 3 toques.
- [ ] **T-003-11** Registrar el peso.
  - Fecha de hoy puesta, confirmación de reemplazo, estatura la primera vez.
  - Cumple: RF-003-01, 02, 12, 13. Hecho cuando: CA-003-02a y 05a se ven en el navegador.
- [ ] **T-003-12** Resumen, objetivo y gráfica.
  - Cumple: RF-003-03 a 09; RN-003-09. Hecho cuando: CA-003-01a, 08a y 09a se ven en el navegador, con el texto orientativo junto al IMC.
- [ ] **T-003-13** Historial con corregir y eliminar.
  - Cumple: RF-003-06, 10, 11; RNF-USA-04. Hecho cuando: CA-003-10a y 11a se ven en el navegador, con confirmación al eliminar.

## Fase 4 — Cierre

- [ ] **T-003-14** Recorrido completo en el navegador contra el servidor local, a 375 px, incluido sin conexión.
- [ ] **T-003-15** `[D]` Probarlo en tu iPhone con la app publicada: pésate y registra tu peso real.
- [ ] **T-003-16** `[D]` Pasar la spec 003 a `Implementada` si todos sus criterios están marcados, y actualizar `SPECS/README.md`.

## Bitácora

| Fecha | Tarea | Qué entendí / qué cambió | Quién |
|---|---|---|---|

### Notas técnicas
