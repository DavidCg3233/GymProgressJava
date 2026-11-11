# Tasks 006 — Sesiones de entrenamiento (y base del proyecto)

| | |
|---|---|
| **Plan** | [plan.md](plan.md) (Aprobado el 2026-11-10) |
| **Creado** | 2026-11-10 |
| **Avance** | 0 de 38 cerradas · 30 con código listo esperando la línea de David en la bitácora (T-006-01 a 05, 09 a 33). Hito A completo salvo lo que necesita el VPS o el iPhone: T-006-06 a 08, 34 a 36 |

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

- [ ] **T-006-37** Empezar sesión desde una rutina. **Construida el 2026-11-10 como T-002-13** ([tasks de la 002](../002-rutinas/tasks.md)).
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
| 2026-11-10 | T-006-10 | `7b0168f` · Entrar con usuario o correo, salir, acceso de 7 días renovado con cada uso, cookie HttpOnly + Secure + SameSite=Lax, protección CSRF. 28 pruebas escritas primero | `[DAVID]` |
| 2026-11-10 | T-006-11 | `7663a30` · Bloqueo de 15 minutos tras 5 intentos fallidos, por cuenta (no se evade cambiando mayúsculas ni alternando usuario y correo). 10 pruebas escritas primero | `[DAVID]` |
| 2026-11-10 | T-006-12 | Cuentas por invitación: tope de 5, contraseña temporal que se muestra una sola vez, cambio de contraseña pidiendo la actual, panel del dueño en `/panel/`, sin registro público. 41 pruebas escritas primero | `[DAVID]` |
| 2026-11-10 | T-006-13 | Base de la API: sin acceso responde 401, lo ajeno responde 404, con contraseña temporal responde 403, y toda escritura exige el token CSRF. Una prueba recorre **todas** las operaciones con una segunda cuenta | `[DAVID]` |
| 2026-11-10 | T-006-17 | Modelos `sesion`, `sesion_ejercicio`, `serie` con identificadores UUID del celular y restricciones en la base (rangos, una sola sesión en curso) | `[DAVID]` |
| 2026-11-10 | T-006-18 | Guardar sesión: libre, una sola en curso, terminar con nombre y nota, no reabrir, repetir el envío sin duplicar | `[DAVID]` |
| 2026-11-10 | T-006-19 | Ejercicios y series: confirmar, corregir, agregar, quitar; tabla de bordes CA-006-24a comprobada en el servidor | `[DAVID]` |
| 2026-11-10 | T-006-20 | Cierre a las 2 horas y descarte de sesiones vacías, sin tarea programada | `[DAVID]` |
| 2026-11-10 | T-006-21 | Historial por páginas de 20, detalle y eliminar | `[DAVID]` |
| 2026-11-10 | T-006-22 | Arranque: sesión en curso, "última vez" serie por serie y nota de la última vez | `[DAVID]` |
| 2026-11-10 | T-006-14 | Pantalla de acceso, cambio de contraseña (obligatorio con temporal) y salir | `[DAVID]` |
| 2026-11-10 | T-006-23 a 29 | Pantallas de inicio, sesión en curso e historial. Lógica de la sesión en funciones puras con 28 pruebas; pantallas recorridas a mano en 375 px: entrar, sesión libre, agregar ejercicio, confirmar (1 toque), +0,5 kg y confirmar (2 toques), rechazo de 30,3 kg, recargar a mitad de sesión, nota de la última vez, precarga, terminar con resumen, descartar sesión vacía, historial, detalle, eliminar y salir | `[DAVID]` |
| 2026-11-10 | T-006-30 a 33 | Sin conexión: almacén en el celular (IndexedDB), cola de pendientes, aviso de cambios por enviar, cuenta recordada para abrir sin señal, cierre a las 2 horas en el celular y app instalable con service worker. 39 pruebas nuevas. Comprobado en el navegador apagando el servidor a mitad de sesión: se registraron series, se recargó la app sin servidor, abrió con todo intacto, y al encender el servidor los pendientes se enviaron solos | `[DAVID]` |
| 2026-11-10 | T-006-07 (Railway) | Imagen de producción en dos etapas, Django sirve la pantalla con WhiteNoise, HTTPS obligatorio y Content-Security-Policy, `railway.json`. 17 pruebas nuevas. Comprobado en el equipo: Django solo entrega la app, el service worker queda activo y la copia guardada en el celular lleva la cabecera de seguridad. **Falta publicar:** lo hace David en Railway | `[DAVID]` |
| 2026-11-10 | T-006-12 (dueño en Railway) | Comando `crear_dueno`: crea la primera cuenta de dueño desde variables de entorno al arrancar, con contraseña temporal; nunca la escribe en los registros ni detiene el arranque. 8 pruebas | `[DAVID]` |
| 2026-11-10 | T-006-07 (publicada) | La app quedó publicada en Railway desde `main` (PR #10). David comprobó `/salud/` → `{"estado": "ok"}`. Falta: cuenta de dueño, primera entrada e instalación en el iPhone | `[DAVID]` |
| 2026-11-10 | T-006-03 | `e2dc212` · Docker Compose con PostgreSQL 16. **Verificada en GitHub Actions:** migraciones y 105 pruebas dentro de Docker, incluidas las 3 de PostgreSQL. En el equipo de David sigue sin poder correr (falta WSL) | `[DAVID]` |

### Bloqueos

- **Docker no corre en el equipo de David: falta WSL.** No bloquea el avance, porque GitHub Actions ejecuta lo mismo en cada PR, pero sin WSL no se puede levantar el servidor completo en local. Lo instala David, en una PowerShell **como administrador**: `wsl --install`, y reiniciar. Después: abrir Docker Desktop y, en `deploy/`, `docker compose up`.

### Notas técnicas

- **La revisión "Imagen de producción" atrapó un error antes de Railway:** la app corre con un usuario sin privilegios, pero `/app` era del administrador, así que no podía crear su carpeta de archivos al construir. Corregido. La revisión ahora publica las líneas del error como anotación, visible sin iniciar sesión en GitHub.
- **Railway falló al primer intento** porque construyó `main`, que aún no tenía el `Dockerfile`. Se resuelve al fusionar el PR #10.

- **Cambio de hosting (plan 006, sección 12):** el VPS no cabía en el presupuesto; se publica en Railway. T-006-06 (contratar y asegurar el VPS) queda reemplazada por crear el proyecto en Railway. T-006-07 cambia: ya no hay Caddy.
- **Dos errores encontrados al verificar en el navegador:** (1) la cabecera de seguridad no llegaba a los archivos que entrega WhiteNoise, incluido el `index.html` que el service worker guarda en el celular, así que sin señal la app habría corrido sin esa protección; (2) el manifiesto salía con un tipo de archivo que algunos navegadores no reconocen para instalar la app.

- **Tres errores que encontraron las pruebas de la fase 6, antes de llegar al celular:**
  1. *Grave.* La cola fusionaba dos cambios sobre el mismo dato poniendo el último en el lugar del primero. Eso adelantaba el **cierre** de la sesión al lugar de su **inicio**: el servidor la habría recibido terminada y sin series, la habría descartado, y luego habría rechazado todas las series. Se perdía el entrenamiento entero. Ahora solo se fusionan cambios seguidos; con otros en medio, se conservan los dos en orden.
  2. La app no abría sin señal: lo primero que hacía era preguntarle al servidor si había acceso. Ahora el celular recuerda la cuenta y, sin señal, sigue con ella; con señal, manda el servidor.
  3. `structuredClone` no puede copiar los objetos reactivos de Vue: terminar una sesión habría fallado al actualizar "la última vez".
- **Desviación del plan:** no se usó Dexie. Para guardar tres claves bastan 40 líneas sobre IndexedDB, y es una dependencia menos que auditar.
- **Riesgo aceptado:** sin señal, la app confía en la cuenta que recuerda el celular. Si el acceso venció en el servidor, los datos locales se siguen viendo hasta que vuelva la señal; entonces se pide entrar y nada pendiente se pierde.
- **Al salir de la cuenta** se borra todo del celular. Si hay cambios sin enviar, la app avisa antes.
- **Sin hacer de la fase 6:** T-006-34 (pruebas automáticas con el motor de Safari cortando la red; las simulaciones de Vitest y la prueba manual cubren los mismos casos, pero no el service worker real) y T-006-35 (respaldo diario, va con el VPS). **El service worker solo se activa en la versión publicada**, así que "abrir la app en modo avión desde la pantalla de inicio" solo se puede comprobar en tu iPhone (T-006-08 y T-006-36).
- **Íconos provisionales** en `frontend/public/` (una pesa en los colores de la app), generados por script. Reemplázalos cuando quieras.

- **Las pantallas todavía no funcionan sin conexión.** Si se cae la señal, el cambio se ve en el celular pero no llega al servidor y se pierde al recargar; la pantalla avisa "este cambio no se guardó". Eso es exactamente la fase 6 (T-006-30 a 34: IndexedDB, cola de pendientes y service worker).
- **Probar en tu equipo sin Docker:** `backend/config/settings_local.py` usa SQLite. En `backend`: `.venv\Scripts\python.exe manage.py migrate --settings=config.settings_local`, `createsuperuser` con la misma opción, y `runserver --settings=config.settings_local`. En `frontend`: `npm run dev`. Abrir http://localhost:5173.
- **Dos errores encontrados al probar en el navegador:** (1) el resumen al terminar no aparecía, porque la pantalla de sesión desaparecía antes de avisar; ahora el resumen vive en el estado compartido. (2) Un ejercicio conocido quedaba con el nombre como se escribió ese día; ahora conserva el nombre registrado, pero respeta el grupo que se elija.

- **El PR #6 se fusionó con la revisión del servidor en rojo.** Las pruebas pasaban en PostgreSQL; falló la auditoría de dependencias: Django REST Framework 3.17.2 tiene 3 vulnerabilidades conocidas (CVE-2026-114136, 114137 y 114138), corregidas en 3.18.2. La había dejado fija por debajo de 3.18. Se subió a 3.18.3 en la rama `fix/006-dependencias`. Es RNF-SEG-07 funcionando: la revisión lo detectó; lo que falló fue fusionar sin esperarla.
- **12 errores internos encontrados con pruebas de entradas hostiles** (`test_entradas_hostiles.py`): un identificador de ejercicio que no era UUID, o un nombre o nota que no era texto, hacían fallar al servidor con error 500 en vez de rechazar el dato. Corregido en las reglas de Python y de JavaScript.

- **Hueco de diseño encontrado al construir la API (T-006-19, 20):** el plan decía que el servidor cierra la sesión a las 2 horas. Pero si el celular estuvo sin señal más de 2 horas, al sincronizar el servidor ya la habría cerrado y rechazaría todas las series: se perdía justo lo que RF-006-16 promete conservar. Solución: cada acción lleva la hora en que ocurrió (`momento`) y el servidor decide con esa hora. Quedó escrito en la spec como RN-006-17, 18 y 19. Lo detectaron las pruebas de `test_sincronizacion.py`, escritas antes del código.
- **Segundo error, encontrado por las pruebas:** una sesión de hace días que apenas se sincronizaba se borraba por "vencida y vacía" antes de que llegaran sus series. El margen de 24 horas ahora cuenta desde el último envío del celular, no desde el fin de la sesión.
- **Riesgo aceptado:** el servidor confía en la hora que reporta el celular. Alguien podría falsearla para modificar una sesión suya ya terminada. Solo afecta sus propios datos.
- **T-006-12 quedó completa con T-006-13:** con contraseña temporal la API responde 403 hasta cambiarla.

- **Riesgo aceptado en T-006-11 (RNF-ACC-07):** el bloqueo es por cuenta, como pide RNF-ACC-07. Consecuencia: quien conozca tu nombre de usuario puede dejarte fuera 15 minutos fallando 5 veces a propósito. La alternativa (bloquear por cuenta y dirección de red) evita eso, pero deja pasar a quien cambie de red. **Decidido por David el 2026-11-10: se queda por cuenta.** Que alguien moleste 15 minutos es menos grave que darle intentos ilimitados para adivinar la contraseña.
- **Pendiente de T-006-12:** el servidor ya avisa cuando hay que cambiar una contraseña temporal, pero todavía no impide usar el resto de la app hasta cambiarla. Eso se hace cumplir en T-006-13, con la base de permisos de la API.
- **Primera cuenta del dueño:** se crea una sola vez en el servidor con `python manage.py createsuperuser`. Las demás, desde `/panel/`.

- **El PR #3 se fusionó antes de que terminaran las revisiones.** Pasaron después, sobre `main`. Para que no dependa de la suerte: esperar los tres vistos verdes antes de pulsar *Merge* (se puede volver obligatorio en GitHub: Settings → Branches → regla de protección de `main` con *Require status checks to pass*).
- **T-006-15 se adelantó** a las fases 0 a 2 porque no depende de nada y David pidió empezar por las pruebas unitarias (TDD).
- **PostgreSQL no carga en Windows fuera de Docker:** el Control de aplicaciones de Windows bloquea la librería del conector (`psycopg`). No se toca esa configuración de seguridad. Consecuencia: en el equipo, `pytest` corre con SQLite en memoria; las pruebas que dependen de PostgreSQL se marcan `@pytest.mark.postgres` y corren dentro de Docker Compose (T-006-03).
- El equipo tiene Python 3.14; el servidor usará la imagen de Python 3.12 del plan. Django 5.2 funciona en ambos.
