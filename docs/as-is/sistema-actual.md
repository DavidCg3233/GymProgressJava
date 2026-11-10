# Sistema actual (as-is)

> Ingeniería inversa del commit `761716d` (v1.0), hecha el 9 de noviembre de 2026 leyendo el código, sin ejecutar la app. Todo lo de este archivo es `[AS-IS]`: describe lo que el código **hace**, no lo que debería hacer. No lo edites para "arreglarlo"; si algo cambia, cambia la spec y luego el código.

## 1. Qué es

Aplicación de escritorio de un solo usuario por sesión para llevar rutinas de gimnasio y el peso corporal. 2.293 líneas de Java y 2.654 de HTML/CSS/JS.

## 2. Stack

| Capa | Tecnología | Versión |
|---|---|---|
| Lenguaje | Java | JDK 17+ |
| Ventana | JavaFX (`controls`, `fxml`, `web`) | 21 |
| Interfaz | HTML + CSS + JavaScript dentro de un `WebView` | — |
| Gráficas | Chart.js por CDN (`cdn.jsdelivr.net`) | sin versión fija |
| Íconos | Phosphor Icons por CDN (`unpkg.com`) | 2.0.3 |
| Base de datos | MySQL con `mysql-connector-java` | 8.0.33 |
| Build | Gradle (wrapper) | 8.14 |
| Tests | Ninguno | — |

## 3. Arquitectura

```
┌──────────────────────── Ventana JavaFX (Main.java) ────────────────────────┐
│  main.fxml → WebView                                                        │
│  ┌───────────────────────────────┐        ┌──────────────────────────────┐ │
│  │ webapp/*.html (UI + JS)       │ ─────► │ MainAppController            │ │
│  │ index, dashboard, rutinas,    │ window │ (761 líneas: puente, sesión, │ │
│  │ progreso, estadisticas, perfil│ .java  │ reglas, armado de JSON)      │ │
│  └───────────────────────────────┘ Bridge └──────────────┬───────────────┘ │
│                                                           │                 │
│                                            ┌──────────────▼───────────────┐ │
│                                            │ dao/* (JDBC, SQL a mano)     │ │
│                                            └──────────────┬───────────────┘ │
└───────────────────────────────────────────────────────────┼─────────────────┘
                                                             ▼
                                              MySQL localhost:3306/gymprogress
```

- **El puente (`javaBridge`):** al cargar cada página, el controlador se inyecta en `window.javaBridge`. El JavaScript llama métodos Java de forma **síncrona** y recibe `String` (JSON armado a mano con `StringBuilder`), `boolean` o `null`.
- **Navegación:** cada pantalla es un HTML distinto; `javaBridge.navegar("rutinas.html")` recarga el `WebView`.
- **Sesión:** un campo `usuarioLogueado` en el controlador. No hay forma de cerrarla.
- **Conexión:** una sola `Connection` estática compartida por todos los DAO, abierta al iniciar y cerrada al salir.

### Paquetes

| Paquete | Archivos | Responsabilidad real |
|---|---|---|
| `org.gymprogress` | `Main`, `PruebaConexion` (vacío) | Arranque de la ventana |
| `controller` | `MainAppController` | Todo: puente, sesión, transacciones, cálculo, JSON |
| `dao` | `ConexionDB`, `UsuarioDAO`, `ClienteDAO`, `RutinaDAO`, `EjercicioDAO`, `RutinaEjercicioDAO`, `ProgresoDAO`, `EstadisticasDAO` | SQL. Dos DAO además **modifican el esquema** al arrancar |
| `model` | `Usuario`, `Cliente`, `Rutina`, `Ejercicio`, `RutinaEjercicio`, `RutinaEjercicioDTO`, `Progreso` | POJOs |
| `utils` | `CalculoIMC`, `Validaciones` (vacío) | Fórmula y categorías de IMC |

## 4. Contrato del puente (lo que la UI le pide a Java)

| Método | Entrada | Devuelve | Usado en |
|---|---|---|---|
| `login` | email, contraseña | nombre de usuario o `null` | index |
| `registrarUsuario` | 11 campos (cuenta, datos personales, peso, altura) | `boolean` | index |
| `getNombreUsuarioLogueado` | — | nombre o `null` | todas |
| `navegar` | nombre del HTML | — | todas |
| `getRutinasDelUsuarioJSON` | — | lista de rutinas con sus ejercicios | rutinas, dashboard |
| `guardarRutinaCompleta` | objeto JS (`codigoRutina` 0 = crear) | `boolean` | rutinas |
| `eliminarRutina` | código de rutina | `boolean` | rutinas |
| `getEjerciciosDisponiblesJSON` | — | catálogo de ejercicios | rutinas |
| `getGruposMuscularesJSON` | — | catálogo de grupos | rutinas |
| `crearNuevoGrupoMuscular` | nombre | `boolean` | rutinas |
| `getDatosDeProgresoJSON` | — | `stats`, `chartData`, `history` | progreso, dashboard |
| `registrarNuevoProgreso` | peso, fecha, altura (0 = usar la última) | `boolean` | progreso |
| `getPesoObjetivo` / `actualizarPesoObjetivo` | — / peso | texto / `boolean` | progreso |
| `getStatisticsDataJSON` | — | récords, entrenamientos por mes, distribución | estadisticas |
| `getClienteDataJSON` / `actualizarClienteData` | — / 5 campos | JSON / `boolean` | perfil |
| `getDashboardOverviewJSON` | — | resumen | **nadie lo llama** (código muerto) |
| `logDesdeJS` | mensaje | — | todas (47 llamadas) |

## 5. Modelo de datos

Lo que realmente existe en la base después de arrancar la app una vez (script `gymprogress.sql` **más** lo que el código crea solo):

```
sexo ──1:N── cliente ──1:1── usuario ──1:N── rutina ──1:N── rutina_ejercicio ──N:1── ejercicio ──N:1── grupo_muscular
                                │
                                ├──1:N── progreso
                                └──1:N── reporte ──N:1── tipo_reporte
```

| Tabla | Columnas clave | Origen | Uso |
|---|---|---|---|
| `usuario` | `nombre_usuario`, `email` (UNIQUE), `contrasena`, `fecha_creacion` | script | login, registro |
| `cliente` | nombres, apellidos, `codigo_sexo`, `fecha_nacimiento`, `peso_objetivo` | script + `ALTER` en runtime (`ClienteDAO`) | perfil, peso objetivo |
| `sexo` | 1 Masculino, 2 Femenino | script | registro |
| `rutina` | `nombre_rutina`, `descripcion`, `fecha_creacion`, `dia_semana` | script | rutinas |
| `ejercicio` | `nombre`, `grupo_muscular` (texto), `codigo_grupo_muscular` (FK), `descripcion` | script + `ALTER` en runtime (`EjercicioDAO`) | catálogo **global**, compartido entre usuarios |
| `grupo_muscular` | `nombre_grupo_muscular` (UNIQUE) | **solo runtime** (`EjercicioDAO`), no está en el script | catálogo global |
| `rutina_ejercicio` | `series`, `repeticiones`, `peso` | script | ejercicios planeados de una rutina |
| `progreso` | `fecha`, `peso_corporal`, `altura`, `notas` | script | peso e IMC |
| `reporte`, `tipo_reporte` | — | script | **ninguno**: no hay código que las toque |

## 6. Pantallas

| Archivo | Pantalla | Qué muestra |
|---|---|---|
| `index.html` | Login / Registro | Dos formularios |
| `dashboard.html` | Panel Principal | Peso actual, IMC, n.º de rutinas, actividad reciente, próximas rutinas |
| `rutinas.html` | Gestor de Entrenamientos | Tarjetas de rutinas y modal de crear/editar |
| `progreso.html` | Seguimiento de Progreso | Tarjetas de peso/IMC/objetivo, 2 gráficas, historial, 2 modales |
| `estadisticas.html` | Estadísticas | Récords, distribución por grupo, entrenamientos por mes |
| `perfil.html` | Mi Perfil | Formulario de datos personales |

## 7. Cómo se ejecuta hoy

1. MySQL 8 corriendo en `localhost:3306`, base `gymprogress` creada con `gymprogress.sql`.
2. Editar a mano usuario y contraseña en `ConexionDB.java`.
3. `gradlew.bat run`.
4. Internet activo (si no, no cargan las gráficas ni los íconos).
