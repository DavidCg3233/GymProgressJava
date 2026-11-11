# Plan 006 — Sesiones de entrenamiento (y base del proyecto)

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-10 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-10) |
| **RNF que aplican** | [rnf.md](../rnf.md) completo |
| **Creado** | 2026-11-10 |

> Como es la primera spec que se construye, este plan también decide el **stack de todo el proyecto**. Las specs 002, 003 y 004 lo reutilizan.

## 1. Resumen técnico

Una aplicación web instalable en la pantalla de inicio del iPhone (**PWA**, *Progressive Web App*). La pantalla está hecha en JavaScript, guarda una copia de los datos en el celular y funciona sin conexión; cada cambio hecho sin señal entra a una cola y se envía al servidor cuando la conexión vuelve. El servidor está hecho en Python, valida todo otra vez, guarda en una base de datos relacional y es la única fuente de verdad. Todo corre en un solo servidor Linux pequeño, detrás de HTTPS.

## 2. Stack propuesto

| Capa | Elección | Por qué esta | Alternativa descartada |
|---|---|---|---|
| Servidor | **Python 3.12 + Django 5 (LTS)** | Trae resuelto lo que tu profesor llama "RNF que automatiza el framework": cuentas, contraseñas cifradas, sesiones, protección CSRF, migraciones y un panel de administración. Con eso se cumple la mitad de `rnf.md` sin escribir código propio. | FastAPI: más liviano, pero el acceso, las sesiones y el panel habría que armarlos a mano, y ahí es donde nacen las vulnerabilidades. |
| API | **Django REST Framework** | Validación del lado del servidor declarada por campo (RNF-SEG-04) y permisos por dueño del dato (RNF-SEG-06). Es el estándar, con mucha documentación. | Vistas JSON a mano: menos dependencias, pero la validación queda dispersa. |
| Base de datos | **PostgreSQL 16** | Está en tu plan técnico (rama 4), tiene transacciones y restricciones reales, y escala mucho más allá de 5 cuentas. | SQLite: suficiente para 5 usuarios y más simple de respaldar, pero no es lo que vas a encontrar en un trabajo. |
| Pantalla | **Vue 3 + Vite**, en JavaScript | Componentes en un solo archivo fáciles de leer para quien viene de HTML. Un solo proyecto genera la app instalable. | React: más ofertas de empleo, curva más empinada. Sin framework: menos que aprender, pero el estado de una sesión sin conexión se vuelve difícil de mantener. |
| Sin conexión | **Service worker** con `vite-plugin-pwa` (Workbox) + **IndexedDB** con Dexie | El service worker guarda la app para abrirla sin señal; IndexedDB guarda los datos y la cola de pendientes. Dexie evita escribir la API cruda de IndexedDB. | `localStorage`: no sirve para datos estructurados ni para este volumen. |
| Gráficas | **Chart.js**, versión fija, empaquetada | Ya la conoces de la v1.0. Empaquetada no depende de internet (H-16). | — |
| Servidor web y HTTPS | **Caddy** | Certificado HTTPS automático y renovado solo (RNF-SEG-02), con una configuración de pocas líneas. | Nginx + Certbot: más control, más piezas que mantener. |
| Empaquetado | **Docker Compose** (3 servicios: Caddy, Django, PostgreSQL) | Arranca con un comando (RNF-MAN-04) y es igual en tu equipo y en el servidor. Es tu rama 7. | Instalar todo directo en el servidor: funciona, pero no se puede reproducir. |
| Hosting | **Un VPS Linux pequeño** (1 vCPU, 1 a 2 GB de RAM) | Siempre encendido (cumple los 2 segundos de RNF-REN-01) y es práctica real de Linux y redes, que es hacia donde va tu carrera. | Plataformas con plan gratis: se "duermen" tras un rato sin uso y tardan en despertar, lo que rompe RNF-REN-01. |
| Pruebas | **pytest** (servidor), **Vitest** (lógica de la pantalla), **Playwright** con motor WebKit (flujo completo, incluido sin conexión) | Playwright puede simular "modo avión" y usa el mismo motor de Safari. | — |

### Lo que debes saber antes de aprobar

- **Presupuesto justo.** Un VPS de este tamaño cuesta hoy entre 4 y 7 dólares al mes según el proveedor, y varios subieron precios en 2026. Tu tope de $20.000 COP son unos 5 dólares: cabe en el plan más barato, sin margen. **Verifica el precio en la página del proveedor el día que lo contrates.**
- **Hace falta un dominio.** HTTPS y la instalación en el iPhone exigen un nombre de dominio. Uno propio cuesta alrededor de 10 a 15 dólares al año (fuera del tope mensual); un subdominio gratuito también sirve. **Decidido 2026-11-10: subdominio gratuito.** Se puede pasar a dominio propio después sin tocar código.
- **Son dos lenguajes y cuatro tecnologías nuevas para ti** (Django, Vue, Docker, Caddy). La IA escribe el código, pero la constitución (P6) te obliga a poder explicarlo. Es el costo real de este stack.
- **Límite de iOS que condiciona el diseño:** Safari no envía datos en segundo plano con la app cerrada. La sincronización ocurre cuando la app está abierta o vuelve al frente. Eso ya coincide con RNF-006-07 ("con la app abierta").
- **Por qué es obligatorio instalarla en la pantalla de inicio (RNF-PLA-03):** Safari borra los datos locales de un sitio tras 7 días sin uso; las apps agregadas a la pantalla de inicio llevan su propio contador. Aun así, la regla del diseño es: **el celular nunca es la única copia por más tiempo que el que tarda en volver la señal.**

## 3. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea de `tasks.md` nombra sus `RF-006-xx`. |
| P2. Nada que nadie pidió | Sí | Las tablas y operaciones de este plan salen una a una de la spec; no hay campos "por si acaso". |
| P3. RNF de seguridad | Sí | Ver sección 7. |
| P4. Cada requerimiento tiene su prueba | Sí | Ver sección 8: cada `CA-006-xx` tiene un tipo de prueba asignado. |
| P5. Reglas de negocio solas | Sí | Las reglas viven en un módulo sin dependencias de pantalla ni de base de datos, en el servidor y en la pantalla (sección 4.1). |
| P6. David entiende lo que se entrega | Depende de ti | Cada tarea se entrega con explicación; tú escribes en la bitácora lo que entendiste. |

## 4. Diseño

### 4.1 Componentes

```
iPhone (app instalada)                              Servidor Linux (Docker Compose)
┌─────────────────────────────────────┐            ┌──────────────────────────────────┐
│ Pantallas (Vue)                     │            │ Caddy  ── HTTPS, sirve la app    │
│   Inicio · Sesión · Historial       │            │   │                              │
│        │                            │   HTTPS    │   ▼                              │
│ Reglas (JS puro, con pruebas)       │◄──────────►│ Django                           │
│   rangos · última vez · cierre 2 h  │   JSON     │   API (DRF): valida y autoriza   │
│        │                            │            │   Reglas (Python puro, pruebas)  │
│ Datos locales (IndexedDB)           │            │   Cuentas, sesiones, admin       │
│   copia de rutinas y últimas veces  │            │   │                              │
│   sesión en curso                   │            │   ▼                              │
│   cola de pendientes ───────────────┼── sync ───►│ PostgreSQL                       │
│ Service worker: abre sin señal      │            │ Respaldo diario                  │
└─────────────────────────────────────┘            └──────────────────────────────────┘
```

Las reglas existen dos veces a propósito: en la pantalla para responder al instante y sin señal, y en el servidor porque es el único en el que se confía (RNF-SEG-04). Las mismas tablas de casos de borde de la spec (CA-006-24a) prueban las dos.

### 4.2 Datos

Solo lo que esta spec necesita. Las tablas de rutinas y catálogo se detallan en el plan de la 002; aquí aparecen porque la sesión las referencia.

| Tabla | Columnas principales | Reglas |
|---|---|---|
| `usuario` | la de Django: usuario, correo, contraseña cifrada, nombre para mostrar | Correo y usuario únicos (RNF-ACC-10) |
| `sesion` | `id` (UUID), `usuario`, `rutina` (opcional), `nombre`, `inicio`, `fin` (opcional), `nota`, `actualizado` | `nombre` es una **copia** del nombre de la rutina, o el de la sesión libre (RF-006-11, 21). `rutina` queda vacía si la rutina se elimina. Máximo una sesión sin `fin` por usuario (RF-006-02). |
| `sesion_ejercicio` | `id` (UUID), `sesion`, `ejercicio` (opcional), `nombre`, `grupo`, `orden`, `nota` | `nombre` y `grupo` son **copias** del catálogo en el momento de la sesión (RF-006-11, RN-004-10). |
| `serie` | `id` (UUID), `sesion_ejercicio`, `numero`, `peso`, `reps`, `confirmada`, `actualizado` | `peso` decimal de 0 a 500 en múltiplos de 0,5; `reps` entero de 1 a 100 (RN-006-02, 04), reforzado con restricciones en la base. Único por (`sesion_ejercicio`, `numero`). |

Decisiones de datos:

- **Los identificadores los genera el celular (UUID).** Así una serie creada sin señal ya tiene su identidad definitiva y reenviarla no la duplica.
- **Copias en vez de referencias** para nombre de rutina, ejercicio y grupo: es lo que permite modificar o eliminar una rutina sin tocar el historial.
- **Cierre a las 2 horas sin tarea programada:** una sesión sin `fin` cuyo `inicio` tiene más de 2 horas se trata como terminada con `fin = inicio + 2 h` en el momento en que se lee o se sincroniza (RF-006-08, RN-006-12). Si no tiene series confirmadas, se elimina (RF-006-19).
- **"Última vez"** no se guarda: se calcula al consultar, a partir de las series confirmadas de sesiones terminadas (RN-006-08).
- Todos los cambios de estructura van como **migraciones de Django** versionadas (RNF-MAN-02).

### 4.3 Contratos

Todas requieren acceso. Todas operan solo sobre datos del usuario que hace la petición; un identificador ajeno responde "no encontrado" (RNF-ACC-06).

| Operación | Entrada | Salida | Errores | Cubre |
|---|---|---|---|---|
| `GET /api/arranque` | — | Rutinas, catálogo, "última vez" y última nota por ejercicio, sesión en curso si existe | 401 | RF-006-04, 05, 17, 23 |
| `PUT /api/sesiones/{id}` | Sesión completa: nombre, rutina, inicio, fin, nota | La sesión guardada | 400 validación · 409 si ya hay otra en curso | RF-006-01, 02, 07, 20, 21, 22 |
| `PUT /api/sesiones/{id}/ejercicios/{id}` | Nombre, grupo, orden, nota | El ejercicio guardado | 400 · 409 si la sesión está terminada | RF-006-13, 23 |
| `PUT /api/series/{id}` | Ejercicio, número, peso, reps, confirmada | La serie guardada | 400 · 409 si la sesión está terminada | RF-006-03, 12, 14, 24 |
| `DELETE /api/series/{id}` | — | — | 409 si la sesión está terminada | RF-006-12 |
| `GET /api/sesiones` | Página | Sesiones terminadas, de la más reciente a la más antigua | — | RF-006-09 |
| `GET /api/sesiones/{id}` | — | Sesión con ejercicios y series | 404 | RF-006-10 |
| `DELETE /api/sesiones/{id}` | — | — | 404 | RF-006-15 |

- **Toda escritura de ejercicio o serie lleva `momento`:** la hora en que ocurrió en el celular (RN-006-17). El servidor decide con esa hora, no con la de llegada. Si falta, usa la hora actual.
- **Lo ajeno y lo inexistente responden igual: 404.** No se confirma que un dato de otra persona exista. Por eso quitar una serie ya quitada también da 404, y la cola de pendientes lo toma como "ya estaba hecho".
- **Hito A:** la sesión todavía no tiene el campo `rutina` ni el ejercicio su referencia al catálogo; se agregan con la spec 002. El ejercicio se reconoce por su nombre sin mayúsculas ni tildes.
- **`PUT` con identificador del cliente = operación repetible.** Enviar dos veces la misma serie deja el mismo resultado. Es lo que hace segura la cola de pendientes.
- **Error 400** siempre trae el campo y el rango permitido, en español y sin términos técnicos (RF-006-24, RNF-USA-02, RNF-SEG-09).

### 4.4 Sincronización

1. Cada acción del usuario se aplica primero en IndexedDB y la pantalla responde de inmediato (RNF-REN-02).
2. La misma acción entra a una **cola de pendientes** en IndexedDB, en orden.
3. Con conexión, la cola se envía en orden. Lo que el servidor acepta sale de la cola.
4. Sin conexión, la cola espera. La pantalla muestra cuántos pendientes hay (RF-006-18).
5. La cola se reintenta al abrir la app, al volver al frente y cuando el navegador avisa que hay conexión.
6. Si el acceso venció (401), la cola **no se borra**: se pide la contraseña y se reintenta (RNF-ACC-02).
7. Si el servidor rechaza un pendiente por validación (400), se marca con error y se muestra al usuario; no bloquea los demás.

Conflictos: por la regla de un solo dispositivo por sesión (RN-006-13), no hay ediciones simultáneas que resolver. Si llegaran dos versiones de un mismo registro, gana la de `actualizado` más reciente.

## 5. Estructura del repositorio

**Decidido 2026-11-10:** la v1.0 en Java se mueve a `legacy/`, completa (restaurando los archivos borrados localmente), y se marca con la etiqueta `v1.0` antes de moverla.

```
GymProgress/
├── backend/            # Django: api/, reglas/, cuentas/, tests/
├── frontend/           # Vue: pantallas/, reglas/, datos/ (IndexedDB y cola), tests/
├── deploy/             # docker-compose.yml, Caddyfile, script de respaldo
├── SPECS/  docs/       # como hoy
└── legacy/             # v1.0 en Java
```

## 6. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| App web instalable (PWA), no app nativa | App nativa de iOS | Sin cuenta de desarrollador de Apple ni tienda; RNF-PLA-01. |
| Sesión con cookie del servidor, renovada con cada uso | Tokens guardados por JavaScript | Una cookie `HttpOnly` no puede ser leída por código inyectado; la renovación deslizante cumple RNF-ACC-03 sin código propio. |
| Pantalla y API en el mismo dominio | Dominios separados | Evita abrir permisos entre dominios y simplifica la protección CSRF. |
| Identificadores generados en el celular | Generados por el servidor | Indispensable para crear sin conexión. |
| Cierre a las 2 horas calculado al leer | Tarea programada cada minuto | Una pieza menos que mantener, y funciona igual sin conexión. |
| Cuentas creadas desde el panel de administración de Django | Pantalla propia de invitaciones | RNF-ACC-05 y RNF-ACC-09 resueltos sin construir nada; para 5 cuentas no se justifica más. |

## 7. Seguridad: cómo se cumple cada RNF

| RNF | Cómo |
|---|---|
| RNF-SEG-01 contraseñas ilegibles | Cifrado de una vía de Django con Argon2. |
| RNF-SEG-02 todo cifrado | Caddy redirige a HTTPS y envía HSTS. |
| RNF-SEG-03 sin secretos en el repo | Secretos en un archivo `.env` ignorado por Git; `gitleaks` revisa cada commit. |
| RNF-SEG-04 validación en el servidor | Serializadores de DRF y restricciones en la base. |
| RNF-SEG-05 sin inyección | Consultas solo por el ORM; Vue escapa el texto al pintarlo; cabecera *Content-Security-Policy*. |
| RNF-SEG-06 y RNF-ACC-06 dueño del dato | Toda consulta se filtra por el usuario de la sesión, en una clase base común; hay una prueba por operación con una segunda cuenta. |
| RNF-SEG-07 dependencias | Versiones fijas; `pip-audit` y `npm audit` en cada cambio. |
| RNF-SEG-08 y 09 registros y errores | Modo de depuración apagado; los errores internos devuelven un mensaje genérico. |
| RNF-SEG-10 contraseña de 10 caracteres | Validadores de contraseña de Django. |
| RNF-ACC-02 y 03 acceso 7 días deslizante | Cookie de sesión de 7 días renovada en cada petición; `HttpOnly`, `Secure`, `SameSite=Lax`. |
| RNF-ACC-07 bloqueo tras 5 intentos | `django-axes`: 5 fallos, 15 minutos. |
| RNF-MAN-06 respaldo diario | Volcado diario de PostgreSQL, cifrado, subido a un almacenamiento de objetos en la nube con plan gratuito (decidido 2026-11-10). El proveedor se elige al configurar. Se prueba restaurando una copia. |

## 8. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| CA-006-24a, 24b (bordes de peso, reps y notas) | Unitaria, la misma tabla en los dos lados | `backend/reglas/tests`, `frontend/reglas/tests` |
| CA-006-04a, 05a, 12a (última vez, serie agregada) | Unitaria | `frontend/reglas/tests` y `backend/reglas/tests` |
| CA-006-08a, 19a (cierre a las 2 horas, sesión vacía) | Unitaria con reloj simulado | Ambos lados |
| CA-006-01a, 02a, 03a, 10a, 11a, 13a, 14a, 14b, 15a, 20a a 23a | Integración de la API | `backend/api/tests` |
| RNF-ACC-06 (cuenta ajena) | Integración: una por operación de la sección 4.3 | `backend/api/tests` |
| CA-006-03b, 16a, 17a (cerrar la app, modo avión) | Flujo completo en motor WebKit, cortando la red | `frontend/tests/e2e` |
| RNF-006-01 a 04 (toques, una mano) | Manual, en tu iPhone, con lista de chequeo | Bitácora de `tasks.md` |
| RNF-REN-01, 02 (tiempos) | Manual con cronómetro, 5 intentos | Bitácora de `tasks.md` |

## 9. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| El uso sin conexión en iOS se comporta distinto a lo previsto | Media | Primera tarea técnica: un prototipo mínimo que confirma una serie en modo avión en tu iPhone, **antes** de construir lo demás. Si falla, se replantea RNF-006-05. |
| El VPS más barato sube de precio o no alcanza | Media | El empaquetado en Docker permite cambiar de proveedor sin tocar código. |
| Pérdida de datos en el celular antes de sincronizar | Baja | Cola persistente, aviso visible de pendientes, sincronización en cada apertura. |
| Demasiada tecnología nueva a la vez para David | Alta | Orden de construcción por capas (primero servidor con pruebas, luego pantalla con conexión, al final sin conexión) y explicación por tarea. |
| Mantener un servidor expuesto a internet | Media | Actualizaciones automáticas de seguridad, solo los puertos 80 y 443 abiertos, acceso por llave SSH. Es exactamente lo que estás estudiando en Linux y Redes. |

## 10. Decisiones de aprobación

| # | Decisión | Resultado |
|---|---|---|
| 1 | Stack de la sección 2 | **Aprobado** (2026-11-10): Django + DRF, PostgreSQL, Vue 3, PWA con IndexedDB, Caddy y Docker Compose en un VPS. |
| 2 | Dominio | **Subdominio gratuito** (2026-11-10). |
| 3 | v1.0 | **Se mueve a `legacy/`** (2026-11-10). |
| 4 | Respaldo diario | **Almacenamiento en la nube con plan gratuito** (2026-11-10). |
| 5 | Proveedor del VPS | Se elige al contratar, con el precio vigente y el tope de $20.000 COP al mes. |

## 11. Orden de construcción

La spec 006 depende de la 002 (una sesión parte de una rutina), y la 002 todavía no tiene plan. Para no bloquearse, se construye en dos hitos:

- **Hito A — sesión libre:** todo el flujo de una sesión sin rutina (RF-006-20), con y sin conexión. No necesita rutinas ni catálogo: los ejercicios se escriben a mano.
- **Hito B — sesión desde rutina:** después de aprobar y planear la 002. Agrega RF-006-01, la precarga desde la rutina (RF-006-05) y las sugerencias del catálogo.

El detalle está en [`tasks.md`](tasks.md).

## 12. Revisión del 2026-11-10: de VPS a Railway

**Decidido por David el 2026-11-10.** El VPS no cabía en el presupuesto: en DigitalOcean, la configuración más pequeña disponible en su cuenta costaba unos 17 dólares al mes (unos $70.000 COP), contra un tope de $20.000 COP (RNF-PLA-05). Railway, en su plan Hobby, cobra un mínimo de 5 dólares al mes que se gastan en uso.

| Pieza | Plan original (sección 2) | Ahora |
|---|---|---|
| Hosting | VPS Linux con Docker Compose | Railway: un servicio para la app y otro de PostgreSQL |
| HTTPS y dominio | Caddy + subdominio de DuckDNS | Los da Railway (`*.up.railway.app`) |
| Entregar la pantalla | Caddy | Django + WhiteNoise: un solo sitio, la cookie de acceso y la protección CSRF funcionan igual |
| Servidor de Python | — | gunicorn, 1 proceso con 4 hilos (menos memoria, que es lo que Railway cobra) |
| Migraciones | A mano | Al arrancar cada versión (`Dockerfile`) |
| Respaldo diario (T-006-35) | Volcado a la nube | Pendiente: revisar lo que ofrece Railway para PostgreSQL |
| Desarrollo en el equipo | Docker Compose | Igual (`deploy/docker-compose.yml`), o SQLite con `settings_local` |

**Lo que se pierde:** la práctica de administrar un servidor Linux expuesto a internet (T-006-06). Esa práctica queda para la rama de Linux del plan de estudio, en la máquina virtual.

**Riesgo nuevo:** el cobro es por uso. Si la app consume más de 5 dólares al mes, se cobra la diferencia. Mitigación: límite de gasto en Railway y un solo proceso de gunicorn.

**Archivos nuevos:** `Dockerfile` y `.dockerignore` en la raíz (imagen de producción en dos etapas), `railway.json` (construcción y revisión de salud en `/salud/`), `backend/config/produccion.py` (HTTPS obligatorio con `GP_HTTPS=1` y cabecera Content-Security-Policy, RNF-SEG-02 y 05). La revisión automática "Imagen de producción" construye y arranca esa imagen en cada PR.

### Variables de entorno en Railway

| Variable | Valor |
|---|---|
| `GP_SECRET_KEY` | Una clave larga al azar, generada solo para producción |
| `GP_HTTPS` | `1` |
| `GP_ALLOWED_HOSTS` | `<tu-dominio>.up.railway.app,healthcheck.railway.app` |
| `GP_CSRF_TRUSTED_ORIGINS` | `https://<tu-dominio>.up.railway.app` |
| `GP_DB_NAME`, `GP_DB_USER`, `GP_DB_PASSWORD`, `GP_DB_HOST`, `GP_DB_PORT` | Referencias a las variables del servicio PostgreSQL: `${{Postgres.PGDATABASE}}`, `${{Postgres.PGUSER}}`, `${{Postgres.PGPASSWORD}}`, `${{Postgres.PGHOST}}`, `${{Postgres.PGPORT}}` |
