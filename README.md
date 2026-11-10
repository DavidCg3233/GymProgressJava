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

## Cómo ejecutar

**v2 (en construcción).** Hoy existe el servidor con sus pruebas:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  ·  source .venv/bin/activate en Linux / macOS
pip install -r requirements-dev.txt
pytest
```

**v1.0 (legado).** Instrucciones en [`legacy/README.md`](legacy/README.md).

## Estructura

```
GymProgressJava/
├── backend/               # v2: servidor en Python + Django
│   ├── config/            # configuración del proyecto (lee variables de entorno)
│   ├── reglas/            # reglas de negocio puras, sin base de datos ni pantalla
│   └── tests/             # pruebas; cada una nombra el criterio de la spec que verifica
├── SPECS/                 # requisitos, RNF, issues y una carpeta por funcionalidad
├── docs/                  # guía SDD, constitución, visión e ingeniería inversa de la v1.0
└── legacy/                # v1.0 en Java (referencia, no se mantiene)
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
