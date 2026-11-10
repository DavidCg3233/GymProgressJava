# Tasks 006 — Sesiones de entrenamiento (y base del proyecto)

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-10) |
| **Creado** | 2026-11-10 |
| **Avance** | 0 de 38 cerradas · 8 con código verificado esperando la línea de David en la bitácora (T-006-01 a 05, 09, 15, 16) |

> **Cómo se usa este archivo**
> - **Una tarea = un commit**, en orden. No se salta de fase.
> - Cada tarea se le entrega a la IA con el prompt de 5 partes (ver `docs/guia-sdd.md`): el **requerimiento** es la tarea con sus IDs; la **condición de calidad** es su "Hecho cuando".
> - La IA entrega el código **con sus pruebas y una explicación corta**. David corre las pruebas, lee el cambio, y escribe en la bitácora una línea con lo que entendió (constitución, P6). Sin esa línea, la tarea no se marca.
> - `[P]` = se puede hacer en paralelo con la anterior. `[D]` = la hace David a mano, no la IA.
> - **Hito A** (fases 0 a 6) entrega la sesión libre completa. **Hito B** (fase 7) espera a la spec 002.

## Fase 0 — Preparar el repositorio

- [ ] **T-006-01** `[D]` Etiquetar y archivar la v1.0.
  - Restaurar los archivos borrados (`git restore app`), crear la etiqueta `v1.0` y mover el proyecto Java a `legacy/` con `git mv`.
  - Hecho cuando: `legacy/` contiene la v1.0 completa y `git tag` lista `v1.0`.
- [ ] **T-006-02** Esqueleto del servidor.
  - Proyecto Django en `backend/` con configuración leída de variables de entorno, `.env.example`, y pytest corriendo una prueba de humo.
  - Cumple: RNF-SEG-03, RNF-MAN-04. Hecho cuando: `pytest` pasa y no hay ningún secreto en el repo.
- [ ] **T-006-03** Base de datos local con Docker Compose.
  - `deploy/docker-compose.yml` con PostgreSQL y Django; migraciones iniciales.
  - Cumple: RNF-MAN-02, RNF-MAN-04. Hecho cuando: un comando levanta todo y la prueba de humo usa PostgreSQL.
- [ ] **T-006-04** `[P]` Esqueleto de la pantalla.
  - Proyecto Vue 3 + Vite en `frontend/`, con Vitest corriendo una prueba de humo y una página de inicio vacía en 375 px.
  - Cumple: RNF-PLA-02. Hecho cuando: `npm test` pasa y la página se ve sin desplazamiento horizontal.
- [ ] **T-006-05** Revisiones automáticas en cada cambio.
  - GitHub Actions: pruebas de servidor y pantalla, `gitleaks`, `pip-audit` y `npm audit`.
  - Cumple: RNF-SEG-03, RNF-SEG-07, RNF-MAN-01. Hecho cuando: un PR de prueba muestra las revisiones en verde.

## Fase 1 — Despliegue temprano y prototipo de riesgo

> Primero se comprueba lo más incierto del plan (sin conexión en iOS), antes de construir sobre ello.

- [ ] **T-006-06** `[D]` Contratar el VPS y el subdominio.
  - Elegir proveedor con el precio vigente (tope: $20.000 COP al mes), crear el servidor, acceso solo por llave SSH, cortafuegos con los puertos 22, 80 y 443, actualizaciones de seguridad automáticas.
  - Cumple: RNF-PLA-05. Hecho cuando: entras por SSH con llave y el subdominio apunta al servidor.
- [ ] **T-006-07** Despliegue con Caddy.
  - Caddy en Docker Compose sirviendo la página vacía por HTTPS, con redirección desde HTTP y HSTS.
  - Cumple: RNF-SEG-02. Hecho cuando: la página abre con candado en tu iPhone usando datos móviles.
- [ ] **T-006-08** Prototipo: una serie en modo avión.
  - App instalable mínima: un botón "confirmar serie" que guarda en IndexedDB, una cola que envía a un endpoint de prueba, y un contador de pendientes.
  - Cumple: valida RNF-006-05, RNF-006-06 y RNF-PLA-03 antes de construir. Hecho cuando: en tu iPhone, instalada en la pantalla de inicio y en modo avión, confirmas 3 series, cierras la app, la abres, quitas el modo avión y las 3 llegan al servidor.
  - **Si falla: parar y replantear RNF-006-05 antes de seguir.**

## Fase 2 — Acceso (RNF)

- [ ] **T-006-09** Modelo de cuenta.
  - Usuario propio con nombre para mostrar, usuario único y correo único; Argon2; contraseña de mínimo 10 caracteres.
  - Cumple: RNF-ACC-10, RNF-SEG-01, RNF-SEG-10. Hecho cuando: pruebas de unicidad y de 9 contra 10 caracteres pasan, y la contraseña guardada no es legible.
- [ ] **T-006-10** Entrar y salir.
  - Entrar con correo o usuario; cookie `HttpOnly`, `Secure`, `SameSite=Lax` de 7 días renovada con cada uso; cerrar acceso; protección CSRF.
  - Cumple: RNF-ACC-01 a 04. Hecho cuando: pruebas con reloj simulado: uso el día 6 y el 12 sin contraseña; 7 días sin uso la pide; tras salir, la API responde 401.
- [ ] **T-006-11** Bloqueo por intentos.
  - `django-axes`: 5 fallos seguidos, 15 minutos.
  - Cumple: RNF-ACC-07. Hecho cuando: el sexto intento se rechaza aunque la contraseña sea correcta.
- [ ] **T-006-12** Cuentas por invitación.
  - Panel de administración para crear cuentas y generar contraseña temporal; tope de 5 cuentas; cambio de contraseña obligatorio al primer ingreso y cambio voluntario pidiendo la actual.
  - Cumple: RNF-ACC-05, 08, 09, RNF-PLA-04. Hecho cuando: la sexta cuenta se rechaza y no existe ninguna ruta de registro público.
- [ ] **T-006-13** Base de permisos por dueño.
  - Clase base de la API que filtra todo por el usuario en sesión, y ayudante de pruebas "con la cuenta B, pedir un dato de A".
  - Cumple: RNF-ACC-06, RNF-SEG-06. Hecho cuando: el ayudante existe y una prueba de ejemplo responde "no encontrado".
- [ ] **T-006-14** Pantalla de acceso.
  - Formulario de entrada, mensajes de error en lenguaje del usuario, opción de salir.
  - Cumple: RNF-USA-02, RNF-SEG-09. Hecho cuando: entras y sales desde el iPhone; un error no revela si falló el usuario o la contraseña.

## Fase 3 — Reglas de negocio (sin pantalla ni base de datos)

- [ ] **T-006-15** Reglas en Python.
  - Módulo `reglas`: validar peso, reps, notas y nombre; calcular cierre a las 2 horas; decidir si una sesión se descarta.
  - Cumple: RN-006-02 a 06, 14, 15; RF-006-08, 19, 24. Hecho cuando: las tablas de CA-006-24a y 24b y CA-006-08a pasan como pruebas, sin base de datos.
- [ ] **T-006-16** `[P]` Las mismas reglas en JavaScript.
  - Módulo `reglas` en la pantalla, más "última vez" y "serie agregada sin antecedente".
  - Cumple: lo mismo, más RN-006-08, 10, 11. Hecho cuando: las mismas tablas pasan en Vitest, más CA-006-04a, 05a y 12a.

## Fase 4 — API de sesiones

- [ ] **T-006-17** Modelos y migraciones.
  - `sesion`, `sesion_ejercicio`, `serie` como en el plan (4.2), con restricciones de rango en la base y máximo una sesión en curso por usuario.
  - Cumple: RF-006-02, 11; RNF-MAN-02. Hecho cuando: la base rechaza por sí sola un peso de 500,5 y una segunda sesión en curso.
- [ ] **T-006-18** Guardar sesión.
  - `PUT /api/sesiones/{id}`: crear libre, terminar, nombre, nota.
  - Cumple: RF-006-07, 20, 21, 22. Hecho cuando: CA-006-02a, 20a, 21a y 22a pasan, más la prueba de cuenta ajena.
- [ ] **T-006-19** Guardar ejercicios y series.
  - `PUT` y `DELETE` de ejercicios y series; rechazo si la sesión está terminada.
  - Cumple: RF-006-03, 12, 13, 14, 23, 24. Hecho cuando: CA-006-03a, 13a, 14a y 14b pasan; repetir el mismo `PUT` no duplica; pruebas de cuenta ajena.
- [ ] **T-006-20** Cierre a las 2 horas y sesión vacía.
  - Aplicar las reglas de T-006-15 al leer y al sincronizar.
  - Cumple: RF-006-08, 19. Hecho cuando: CA-006-08a y 19a pasan con reloj simulado.
- [ ] **T-006-21** Historial y eliminar.
  - `GET` de lista y detalle, `DELETE` de sesión.
  - Cumple: RF-006-09, 10, 15. Hecho cuando: CA-006-10a y 15a pasan, más las pruebas de cuenta ajena.
- [ ] **T-006-22** Arranque (versión del hito A).
  - `GET /api/arranque` con sesión en curso, "última vez" y última nota por ejercicio.
  - Cumple: RF-006-04, 17, 23. Hecho cuando: CA-006-23a pasa y la respuesta no trae datos de otra cuenta.

## Fase 5 — Pantalla, con conexión

- [ ] **T-006-23** Empezar sesión libre y agregar ejercicios.
  - Cumple: RF-006-13, 20. Hecho cuando: en el iPhone empiezas una sesión libre y agregas un ejercicio escribiendo su nombre y grupo.
- [ ] **T-006-24** Confirmar una serie.
  - Fila por serie con peso y reps precargados; confirmar con un toque; estado confirmada o pendiente a la vista.
  - Cumple: RF-006-03, 04, 06; RNF-006-01, 04. Hecho cuando: confirmar sin cambios es 1 toque y se ve la diferencia entre confirmada y pendiente.
- [ ] **T-006-25** Cambiar peso y reps.
  - Controles de subir y bajar de a 0,5 kg y de a 1 rep, sin abrir otra pantalla; rechazo con rango visible.
  - Cumple: RF-006-14, 24; RNF-006-02. Hecho cuando: cambiar y confirmar toma máximo 3 toques; CA-006-24a se cumple en pantalla.
- [ ] **T-006-26** Agregar y quitar series.
  - Cumple: RF-006-12; RN-006-10. Hecho cuando: CA-006-12a se cumple en pantalla.
- [ ] **T-006-27** Notas.
  - Nota por ejercicio (visible la siguiente vez) y nota de sesión.
  - Cumple: RF-006-22, 23. Hecho cuando: CA-006-22a y 23a se cumplen en pantalla.
- [ ] **T-006-28** Terminar y resumen.
  - Terminar, nombre de la sesión libre, resumen de lo hecho; continuar una sesión en curso al abrir.
  - Cumple: RF-006-02, 07, 21. Hecho cuando: CA-006-20a y 21a se cumplen en pantalla.
- [ ] **T-006-29** Historial.
  - Lista por fecha, detalle de solo lectura, eliminar con confirmación.
  - Cumple: RF-006-09, 10, 14, 15; RNF-USA-04. Hecho cuando: CA-006-10a, 14b y 15a se cumplen en pantalla.

## Fase 6 — Sin conexión

- [ ] **T-006-30** Datos locales.
  - Esquema de IndexedDB: copia del arranque, sesión en curso, cola de pendientes. La pantalla lee y escribe solo ahí.
  - Cumple: RF-006-17; RNF-006-06. Hecho cuando: CA-006-03b pasa (cerrar y abrir conserva la sesión).
- [ ] **T-006-31** Cola de pendientes.
  - Envío en orden, reintento al abrir, al volver al frente y al recuperar conexión; un rechazo no bloquea los demás; un 401 conserva la cola.
  - Cumple: RF-006-16; RNF-ACC-02; RNF-006-07. Hecho cuando: pruebas de la cola con red simulada pasan (sin red, con red, 401, 400).
- [ ] **T-006-32** Aviso de pendientes.
  - Cumple: RF-006-18. Hecho cuando: el contador aparece sin conexión y desaparece al sincronizar.
- [ ] **T-006-33** App instalable que abre sin señal.
  - Service worker que guarda la app completa; manifiesto e íconos; el cierre a las 2 horas se aplica en el dispositivo.
  - Cumple: RNF-PLA-03, 06; RNF-006-05; RN-006-12. Hecho cuando: instalada y en modo avión, la app abre y permite empezar y terminar una sesión libre.
- [ ] **T-006-34** Pruebas de flujo completo sin conexión.
  - Playwright con motor WebKit cortando la red.
  - Cumple: CA-006-16a, 17a. Hecho cuando: ambas pasan en las revisiones automáticas.
- [ ] **T-006-35** Respaldo diario.
  - Volcado cifrado de PostgreSQL subido a almacenamiento en la nube; instrucciones de restauración.
  - Cumple: RNF-MAN-06. Hecho cuando: David restaura una copia en su equipo siguiendo las instrucciones.
- [ ] **T-006-36** `[D]` Recorrido del hito A en el gimnasio.
  - Una sesión libre real, con el iPhone, incluyendo un tramo en modo avión. Medir toques y tiempos.
  - Cumple: RNF-006-01 a 04; RNF-REN-01, 02. Hecho cuando: la lista de chequeo de la bitácora está completa y los bugs encontrados están en `SPECS/issues.md`.

## Fase 7 — Hito B: sesión desde rutina

> **Bloqueada** hasta que la spec 002 esté aprobada y tenga su plan y sus tareas hechas.

- [ ] **T-006-37** Empezar sesión desde una rutina.
  - Copiar ejercicios y series previstas; precargar con "última vez" o, si no hay, con lo previsto; sugerencias del catálogo al agregar un ejercicio.
  - Cumple: RF-006-01, 05, 11. Hecho cuando: CA-006-01a, 04a, 05a y 11a pasan en API y en pantalla.
- [ ] **T-006-38** `[D]` Recorrido final y cierre.
  - Recorrer a mano todos los criterios de aceptación de la spec; pasar la spec a `Implementada`; actualizar `SPECS/README.md` y el README.
  - Hecho cuando: los 23 criterios están marcados y no queda ningún bug abierto de la 006.

## Bitácora

Una línea por tarea: fecha, qué entendí, dónde me trabé.

| Fecha | Tarea | Código | Qué entendí (lo escribe David) |
|---|---|---|---|
| 2026-11-10 | T-006-01 | `c570d5a` · v1.0 en `legacy/`, etiqueta `v1.0` | `[DAVID]` |
| 2026-11-10 | T-006-02 | `98203b4` · 17 pruebas | `[DAVID]` |
| 2026-11-10 | T-006-15 | 64 pruebas de reglas (se escribieron primero y fallaron; luego el código) | `[DAVID]` |

| 2026-11-10 | T-006-04 | `47ff882` · esqueleto Vue + Vite; página comprobada a 375 px sin desplazamiento horizontal | `[DAVID]` |
| 2026-11-10 | T-006-16 | `47ff882` · 76 pruebas en JavaScript (mismas tablas que Python, más la precarga de una serie) | `[DAVID]` |
| 2026-11-10 | T-006-05 | `88c3def` · GitHub Actions con 3 revisiones. **Verificada:** las tres pasaron en `main` (commit `2defea4`, PR #3) | `[DAVID]` |
| 2026-11-10 | T-006-09 | Modelo de cuenta con TDD: 21 pruebas (campos mínimos, unicidad sin distinguir mayúsculas, Argon2, mínimo 10 caracteres) | `[DAVID]` |
| 2026-11-10 | T-006-03 | `e2dc212` · Docker Compose con PostgreSQL 16. **Verificada en GitHub Actions:** migraciones y 105 pruebas dentro de Docker, incluidas las 3 de PostgreSQL. En el equipo de David sigue sin poder correr (falta WSL) | `[DAVID]` |

### Bloqueos

- **Docker no corre en el equipo de David: falta WSL.** No bloquea el avance, porque GitHub Actions ejecuta lo mismo en cada PR, pero sin WSL no se puede levantar el servidor completo en local. Lo instala David, en una PowerShell **como administrador**: `wsl --install`, y reiniciar. Después: abrir Docker Desktop y, en `deploy/`, `docker compose up`.

### Notas técnicas

- **El PR #3 se fusionó antes de que terminaran las revisiones.** Pasaron después, sobre `main`. Para que no dependa de la suerte: esperar los tres vistos verdes antes de pulsar *Merge* (se puede volver obligatorio en GitHub: Settings → Branches → regla de protección de `main` con *Require status checks to pass*).
- **T-006-15 se adelantó** a las fases 0 a 2 porque no depende de nada y David pidió empezar por las pruebas unitarias (TDD).
- **PostgreSQL no carga en Windows fuera de Docker:** el Control de aplicaciones de Windows bloquea la librería del conector (`psycopg`). No se toca esa configuración de seguridad. Consecuencia: en el equipo, `pytest` corre con SQLite en memoria; las pruebas que dependen de PostgreSQL se marcan `@pytest.mark.postgres` y corren dentro de Docker Compose (T-006-03).
- El equipo tiene Python 3.14; el servidor usará la imagen de Python 3.12 del plan. Django 5.2 funciona en ambos.
