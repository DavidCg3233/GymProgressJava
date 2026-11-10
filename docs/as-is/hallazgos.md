# Hallazgos de la ingeniería inversa

> Encontrados leyendo el código del commit `761716d`, sin ejecutar la app. Cada uno apunta al archivo donde está la evidencia. La columna **Spec** dice dónde debes decidir qué hacer con él.
>
> Severidad: **A** = rompe seguridad o datos · **M** = el comportamiento no es el que el usuario espera · **B** = mantenibilidad.

## Seguridad y datos

| ID | Sev. | Hallazgo | Evidencia | Spec |
|---|---|---|---|---|
| H-01 | A | Las contraseñas se guardan y comparan en **texto plano**. | `UsuarioDAO.validarUsuario` (`WHERE email = ? AND contrasena = ?`) | 001 |
| H-02 | A | Usuario `root` y contraseña de MySQL escritos en el código **y publicados en GitHub** (están en el historial de commits). | `ConexionDB.java` | constitución |
| H-03 | A | `eliminarRutina` y `guardarRutinaCompleta` (al editar) no comprueban que la rutina sea del usuario en sesión: se filtra solo por `codigo_rutina`. | `RutinaDAO.eliminarRutina`, `RutinaDAO.actualizarRutina` | 002 |
| H-04 | A | No existe cerrar sesión. El usuario queda en memoria hasta cerrar la ventana. | Ningún HTML tiene la opción; el controlador no tiene el método | 001 |
| H-05 | A | La transacción de guardar rutina no es confiable: usa la misma conexión compartida que el resto de la app, así que cualquier otra consulta entra en esa transacción. | `MainAppController.guardarRutinaCompleta`, `ConexionDB` | plan |
| H-06 | M | El servidor no valida nada del registro: correo, largo de contraseña, peso, altura y fecha solo se revisan en el navegador (y poco). | `MainAppController.registrarUsuario`, `Validaciones.java` vacío | 001 |

## Comportamiento que no es lo que dice la pantalla

| ID | Sev. | Hallazgo | Evidencia | Spec |
|---|---|---|---|---|
| H-07 | M | **"Entrenamientos por Mes" cuenta rutinas creadas**, no entrenamientos hechos. La app no registra sesiones de entrenamiento en ningún lado. | `EstadisticasDAO.getEntrenamientosPorMes` | 004 |
| H-08 | M | **"Récords Personales" es el peso más alto planeado** en una rutina, no el más alto levantado. Si editas la rutina y bajas el peso, el récord baja. | `EstadisticasDAO.getRecordsPersonales` | 004 |
| H-09 | M | Editar una rutina borra todos sus ejercicios y los vuelve a insertar: no queda historial de cómo progresaron las cargas. | `guardarRutinaCompleta` → `deleteEjerciciosPorRutina` | 002 |
| H-10 | M | El catálogo de ejercicios y grupos musculares es **global**. Si un usuario cambia el grupo de "Press de Banca", les cambia a todos. | `EjercicioDAO.findOrCreateEjercicio(nombre, grupo)` | 002 |
| H-11 | M | La distribución por grupo muscular lee la columna vieja de texto, no la tabla `grupo_muscular`; las dos pueden no coincidir. | `EstadisticasDAO.getDistribucionEjercicios` | 004 |
| H-12 | M | "Actividad Reciente" del panel solo lista registros de peso; no aparece nada relacionado con entrenar. | `dashboard.html` (`renderActividad` recibe `history` de progreso) | 004 |
| H-13 | M | El perfil no deja cambiar correo, contraseña, sexo ni nombre de usuario, y no se puede eliminar la cuenta. | `perfil.html`, `ClienteDAO.actualizarCliente` | 005 |
| H-14 | M | Un registro de peso no se puede editar ni borrar, y se aceptan varios en la misma fecha y fechas futuras. | `ProgresoDAO` (solo `INSERT` y `SELECT`) | 003 |
| H-15 | M | Todos los errores le llegan al usuario como un `false` genérico; algunos mensajes hablan de Java ("Java devolvió 'false'"). | `rutinas.html:485`, `progreso.html:491` | todas |
| H-16 | M | Sin internet no hay gráficas ni íconos (dependen de CDN) y Chart.js no tiene versión fija. | `progreso.html:17`, `estadisticas.html:17` | plan |

## Mantenibilidad

| ID | Sev. | Hallazgo | Evidencia |
|---|---|---|---|
| H-17 | B | **God class:** `MainAppController` (761 líneas) mezcla puente, sesión, reglas de negocio, transacciones y armado de JSON. |  `MainAppController.java` |
| H-18 | B | JSON construido a mano con `StringBuilder`; el panel incluso recorta JSON con `substring`. | `getDashboardOverviewJSON` |
| H-19 | B | El esquema cambia solo en tiempo de ejecución (`CREATE TABLE`, `ALTER TABLE` dentro de constructores de DAO). El script `.sql` ya no describe la base real. | `EjercicioDAO.ensureNormalizedSchema`, `ClienteDAO.ensurePesoObjetivoColumn` |
| H-20 | B | Dato duplicado: `ejercicio.grupo_muscular` (texto) y `ejercicio.codigo_grupo_muscular` (FK) guardan lo mismo. | `EjercicioDAO` |
| H-21 | B | Excepciones tragadas (`catch` vacío) y diagnóstico con `System.out.println`, que además imprime datos del usuario. | Todos los DAO |
| H-22 | B | Cero tests automatizados. | No existe `src/test` |
| H-23 | B | Código muerto: `getDashboardOverviewJSON`, `PruebaConexion`, `Validaciones`, `RutinaEjercicio`, `Ejercicio`, tablas `reporte` y `tipo_reporte`. | — |
| H-24 | B | 29 archivos compilados (`app/bin/`) están versionados en Git; `.gitignore` solo excluye `.gradle` y `build`. | `git ls-files app/bin` |
| H-25 | B | `ResultSet` que salen del DAO hacia el controlador y se cierran allá. | `EjercicioDAO.listAllEjerciciosRaw`, `listAllGrupos` |
| H-26 | B | El IMC asume altura en metros, pero nada impide escribir 175. Con 175 el IMC da 0,0. | `CalculoIMC`, `index.html:385` |

## Lo que está bien hecho (y hay que conservar)

- **Todas las consultas usan `PreparedStatement` con parámetros.** No hay concatenación de SQL, así que no hay SQL injection. Es la decisión de seguridad más importante del proyecto y está bien tomada.
- **El registro es atómico:** usuario, cliente y primer progreso se insertan en una transacción con rollback.
- **`CalculoIMC` es una función pura** (sin base de datos ni UI): es el único código que hoy se podría testear sin cambiar nada. Es el modelo a seguir para el resto.
- **La UI escapa el HTML** (`escapeHTML`) antes de pintar texto del usuario.
- **El modelo de datos base está normalizado** y con llaves foráneas y `ON DELETE CASCADE` coherentes.
