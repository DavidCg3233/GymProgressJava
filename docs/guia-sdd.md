# Guía SDD de GymProgress

**SDD (Spec-Driven Development):** *the spec is the source of truth; code is its implementation.* Primero se escribe **qué** debe hacer el sistema y **cómo se comprueba**, después se decide el **cómo técnico**, y solo al final se programa. Si el código y la spec no coinciden, uno de los dos tiene un bug.

Referencia oficial (léela, 10 min): [GitHub Spec Kit — Spec-Driven Development](https://github.com/github/spec-kit/blob/main/spec-driven.md).

## El flujo, en orden

| # | Fase | Archivo | Pregunta que responde | Quién escribe |
|---|---|---|---|---|
| 0 | As-is | `docs/as-is/*` | ¿Qué hace el sistema hoy de verdad? | Ya hecho (ingeniería inversa) |
| 1 | Constitution | `docs/constitucion.md` | ¿Qué reglas no se negocian en este proyecto? | David |
| 2 | Vision | `docs/vision.md` | ¿Para quién es, qué problema resuelve, qué queda fuera? | David |
| 3a | Requirements | `SPECS/requirements.md` | ¿Qué pide el usuario, con sus palabras? ¿Es RF o RNF? | David (como usuario) |
| 3b | Specify | `SPECS/NNN-nombre/spec.md` | ¿Qué debe hacer esta funcionalidad y cómo sé que está bien? | David (como analista) |
| 4 | Plan | `SPECS/NNN-nombre/plan.md` | ¿Cómo lo construyo técnicamente? | David (como dev) |
| 5 | Tasks | `SPECS/NNN-nombre/tasks.md` | ¿Cuáles son los pasos pequeños, en orden? | David |
| 6 | Implement | código + tests | — | La IA, con las specs aprobadas; David revisa y prueba. Un task = un commit |

**Regla de oro:** no se pasa a la fase siguiente con la anterior en `Borrador`. Una spec pasa a `Aprobada` cuando no le queda ningún `[DECIDIR]`.

## Cómo encaja con el proceso de la clase

| Paso de la clase (Análisis de Algoritmos) | Dónde vive en este repo |
|---|---|
| 1. Requisitos textuales | `SPECS/requirements.md` |
| 2. Clasificar RF / RNF | Columna "Tipo" de `requirements.md`. Los RF van a una spec; los RNF van a `SPECS/rnf.md` |
| 3. Épicas → historias de usuario | Tabla de épicas en `requirements.md`; sección 2 de cada `spec.md` |
| 4. Especificación (Quién → Cómo → Resultado → Complementos → Pruebas) | `spec.md` |
| 5. Issues: feature, bug, error | `SPECS/issues.md` como borrador; pasan a GitHub Issues cuando su spec está aprobada. |
| 6. Tasks | `tasks.md` |

`constitucion.md`, `vision.md` y `plan.md` no están en el proceso de la clase: vienen de Spec Kit. Se quedan porque el código lo va a generar una IA y necesita esas tres cosas escritas: las reglas, el para qué y el stack.

**Formato de historia de usuario de la clase:**

> Yo como `___` quiero que `___` para `___`, en el contexto `___`, debe tener el formato `___`.

Las historias de las specs 002, 003 y 004 están en la forma corta ("Como…, quiero…, para…") porque salieron del código. Al llenarlas, pásalas a este formato: el **contexto** y el **formato** son justo lo que el código no puede decir y tú sí.

## Mapa de archivos

```
docs/
├── guia-sdd.md            ← este archivo
├── constitucion.md        ← reglas para todo el proyecto (y para la IA)
├── vision.md              ← usuario, problema y alcance
└── as-is/
    ├── sistema-actual.md  ← cómo era la v1.0
    └── hallazgos.md       ← lo que la versión nueva no puede repetir
SPECS/
├── README.md              ← índice, estado y orden de trabajo
├── requirements.md        ← paso 1 y 2: requisitos textuales, RF / RNF, épicas
├── rnf.md                 ← los RNF, medibles (se le entregan a la IA tal cual)
├── issues.md              ← paso 5: features, bugs y errores
├── _plantilla/            ← copiar para cada funcionalidad nueva
│   ├── spec.md            ← paso 3 y 4: historias y especificación
│   ├── plan.md            ← el cómo técnico (stack, datos, contratos)
│   └── tasks.md           ← paso 6: tareas
├── 006-sesiones/spec.md           ← núcleo, empieza aquí
├── 002-rutinas/spec.md
├── 004-panel-y-estadisticas/spec.md
└── 003-progreso-corporal/spec.md  ← en espera
```

## Marcadores que vas a encontrar

| Marcador | Significado | Qué haces |
|---|---|---|
| `[AS-IS]` | Hecho comprobado leyendo el código actual. | Nada. No lo edites: es evidencia. |
| `[DAVID]` | Hueco que solo tú puedes llenar (eres el usuario). | Escribes tu respuesta y borras el marcador. |
| `[DECIDIR]` | Pregunta abierta con opciones. | Eliges una, escribes por qué en una línea, borras el marcador. |
| `[PROPUESTA]` | Sugerencia mía. | La aceptas, la cambias o la borras. |

Para ver cuánto te falta:

```bash
grep -rn "\[DAVID\]\|\[DECIDIR\]" docs specs | wc -l
```

## Cómo escribir un buen requerimiento

Un requerimiento sirve si alguien que no eres tú puede **probarlo** y decir "pasa" o "no pasa".

1. **Habla del comportamiento, no de la tecnología.** En `spec.md` están prohibidas las palabras JavaFX, MySQL, DAO, tabla, clase. Eso va en `plan.md`.
2. **Una cosa por requerimiento**, con ID estable (`RF-002-03` = spec 002, requerimiento 3). Los IDs no se reciclan.
3. **Usa la forma EARS** (*Easy Approach to Requirements Syntax*):
   - Siempre: `El sistema debe <respuesta>.`
   - Evento: `Cuando <evento>, el sistema debe <respuesta>.`
   - Error: `Si <condición no deseada>, entonces el sistema debe <respuesta>.`
4. **Cada requerimiento lleva al menos un criterio de aceptación** en formato *Given / When / Then* con datos concretos.
5. **Nada de palabras blandas:** "rápido", "fácil", "seguro", "amigable". Cámbialas por un número o un caso.

| Malo | Bueno |
|---|---|
| "El login debe ser seguro." | "RF-001-04: Si la contraseña es incorrecta, entonces el sistema debe rechazar el acceso y mostrar 'Usuario o contraseña incorrectos' sin indicar cuál de los dos falló." |
| "Guardar rutinas en la tabla rutina." | "RF-002-01: Cuando el usuario guarda una rutina con nombre y al menos un ejercicio, el sistema debe mostrarla en su lista de rutinas." |

## Tu mini-spec y esta plantilla son lo mismo

La plantilla de `spec.md` sigue tu orden de mini-spec (Quién → Cómo → Resultado → Complementos → Pruebas):

| Tu mini-spec | Sección de `spec.md` |
|---|---|
| Quién | 2. Actores e historias de usuario |
| Cómo | 3. Flujo principal y alternos |
| Resultado | 4. Requerimientos funcionales (EARS) |
| Complementos | 5. Reglas de negocio · 6. No funcionales · 7. Fuera de alcance |
| Pruebas | 8. Criterios de aceptación (Given/When/Then) |

## Glosario

| Término | EN | ES |
|---|---|---|
| Spec | A document that states what the software must do and how to verify it. | Documento que dice qué debe hacer el software y cómo verificarlo. |
| As-is / To-be | The current state vs. the desired future state. | Estado actual vs. estado deseado. |
| Reverse engineering | Deriving the design/requirements from existing code. | Deducir diseño y requerimientos a partir del código existente. |
| Acceptance criteria | Conditions a feature must meet to be accepted. | Condiciones que una funcionalidad debe cumplir para darse por buena. |
| EARS | A constrained sentence pattern for unambiguous requirements. | Patrón de frases para requerimientos sin ambigüedad. |
| Technical debt | Cost of rework caused by shortcuts taken earlier. | Costo de rehacer lo que se hizo con atajos. |
| ADR | Architecture Decision Record: a short note on one technical decision and why. | Registro corto de una decisión técnica y su porqué. |
| Traceability | Being able to follow a requirement to its code and its test. | Poder seguir un requerimiento hasta su código y su prueba. |

## Cómo se le pasa a la IA

Cuando una spec y su plan estén aprobados, cada tarea se entrega con el prompt de 5 partes de la clase. Casi todo ya está escrito en el repo:

| Parte | De dónde sale |
|---|---|
| **Rol** | Una línea: qué tipo de desarrollador debe ser. |
| **Contexto** | `docs/vision.md` + el `plan.md` de la spec. |
| **Requerimiento** | La tarea de `tasks.md` con sus `RF-xxx` y `CA-xxx`. |
| **Restricción** | `docs/constitucion.md` + `SPECS/rnf.md`. |
| **Condición de calidad** | Los criterios de aceptación de la spec, convertidos en pruebas que pasan. |
