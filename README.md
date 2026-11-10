# GymProgress

Aplicación web para planear rutinas de gimnasio y seguir el peso corporal, el IMC y los pesos de entrenamientos pasados

> **Estado:** en reescritura con **Spec-Driven Development**. La v1.0 (el código de este repo) es una app de escritorio en Java que solo guarda el plan de las rutinas. La v2 será una **app web para el celular** que registra las sesiones reales, serie por serie. Hoy el proyecto está en la fase de especificación; el avance está en [`SPECS/README.md`](SPECS/README.md).

<!-- [DAVID] 2 o 3 capturas reales en docs/img/ y enlázalas aquí:
![Panel principal](docs/img/panel.png)
-->

## Qué hace la v1.0

| Módulo | Funcionalidad |
|---|---|
| Cuentas | Registro e inicio de sesión con correo y contraseña |
| Rutinas | Crear, editar y eliminar rutinas con ejercicios, series, repeticiones y peso; asignarlas a un día de la semana |
| Ejercicios | Catálogo de ejercicios y grupos musculares que crece a medida que se usa |
| Progreso | Registro de peso corporal, cálculo y categoría de IMC, peso objetivo, gráficas e historial |
| Panel | Resumen de peso, IMC, número de rutinas y la rutina que toca hoy |
| Estadísticas | Cargas máximas por ejercicio, distribución por grupo muscular y actividad mensual |
| Perfil | Edición de datos personales |

Limitaciones conocidas de la v1.0, con su evidencia en el código: [`docs/as-is/hallazgos.md`](docs/as-is/hallazgos.md).

## Stack de la v1.0

| Capa | Tecnología |
|---|---|
| Lenguaje | Java 17+ |
| Ventana | JavaFX 21 (`WebView`) |
| Interfaz | HTML, CSS y JavaScript, con Chart.js |
| Base de datos | MySQL 8 por JDBC |
| Build | Gradle (wrapper incluido) |

La interfaz HTML corre dentro de un `WebView` y habla con Java a través de un puente (`window.javaBridge`). El detalle de la arquitectura, el modelo de datos y el contrato del puente está en [`docs/as-is/sistema-actual.md`](docs/as-is/sistema-actual.md).

## Cómo ejecutar la v1.0

**Requisitos:** JDK 17 o superior (`java -version`), MySQL Server 8 en ejecución, Git y conexión a internet (las gráficas y los íconos se cargan por CDN).

1. Clona el repositorio:
   ```bash
   git clone https://github.com/DavidCg3233/GymProgressJava.git
   cd GymProgressJava
   ```
2. Crea la base de datos:
   ```bash
   mysql -u root -p < gymprogress.sql
   ```
3. Escribe tu usuario y contraseña de MySQL en `app/src/main/java/org/gymprogress/dao/ConexionDB.java`. **No subas ese cambio a Git.**
4. Ejecuta:
   ```bash
   ./gradlew run        # Linux / macOS
   gradlew.bat run      # Windows
   ```

La primera vez que arranca, la aplicación crea por su cuenta la tabla `grupo_muscular` y dos columnas que no están en el script.

## Estructura

```
GymProgressJava/
├── app/src/main/
│   ├── java/org/gymprogress/
│   │   ├── Main.java          # arranque de la ventana
│   │   ├── controller/        # puente entre la interfaz y Java
│   │   ├── dao/               # acceso a MySQL
│   │   ├── model/             # entidades
│   │   └── utils/             # cálculo de IMC
│   └── resources/
│       ├── fxml/              # ventana con el WebView
│       └── webapp/            # pantallas HTML, CSS y JS
├── docs/
│   ├── guia-sdd.md            # cómo se trabaja en este repo
│   ├── constitucion.md        # principios del proyecto
│   ├── vision.md              # usuario, problema y alcance
│   └── as-is/                 # ingeniería inversa de la v1.0
├── SPECS/                     # requisitos, RNF, issues y una carpeta por funcionalidad
└── gymprogress.sql            # esquema de la base de datos
```

## Cómo se desarrolla: Spec-Driven Development

Ningún cambio de comportamiento se programa sin un requerimiento escrito y verificable.

```
requisitos  →  RF / RNF  →  épicas  →  historias  →  especificación  →  issues  →  tasks  →  IA
```

| Documento | Responde |
|---|---|
| [`docs/guia-sdd.md`](docs/guia-sdd.md) | Cómo se llena cada archivo y en qué orden |
| [`docs/constitucion.md`](docs/constitucion.md) | Qué reglas valen para todo el proyecto |
| [`docs/vision.md`](docs/vision.md) | Para quién es y qué queda fuera |
| [`SPECS/requirements.md`](SPECS/requirements.md) | Qué pidió el usuario, con sus palabras, clasificado en RF y RNF |
| [`SPECS/rnf.md`](SPECS/rnf.md) | Plataforma, acceso, seguridad y rendimiento, en forma medible |
| [`SPECS/`](SPECS/README.md) | Qué debe hacer cada funcionalidad y cómo se comprueba |

## Hoja de ruta

- [x] v1.0 funcional
- [x] Ingeniería inversa: sistema actual y hallazgos
- [x] Requisitos textuales del usuario, clasificados en RF y RNF
- [ ] Spec 006 (sesiones) y RNF aprobados
- [ ] Plan técnico: elección del stack web
- [ ] Specs 002 y 004 aprobadas
- [ ] Tasks e implementación con pruebas automatizadas
- [ ] v2 en uso desde el celular

## Autor

David Fernando Calambás Gómez · [GitHub](https://github.com/DavidCg3233)

<!-- [DAVID] Confirma: ¿proyecto individual o en equipo? Si fue en equipo, di cuál fue tu parte. -->
