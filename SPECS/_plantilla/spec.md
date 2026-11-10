# Spec NNN — Nombre de la funcionalidad

| | |
|---|---|
| **Estado** | Borrador |
| **Autor** | David Calambás |
| **Creada** | AAAA-MM-DD |
| **Depende de** | (otras specs) |

> En este archivo no se nombra ninguna tecnología. Aquí va el **qué** y el **cómo se comprueba**; el cómo técnico va en `plan.md`.

## 1. Propósito

*Dos o tres frases: qué problema del usuario resuelve esta funcionalidad y por qué importa. Si no puedes conectarla con un objetivo de `docs/vision.md`, no debería existir.*

## 2. Actores e historias de usuario — *Quién*

*Formato de la clase: "Yo como <rol> quiero que <acción> para <beneficio>, en el contexto <cuándo y dónde>, debe tener el formato <cómo se ve o se entrega>". Columna "Requisito": el R-xx de `requirements.md` del que sale. Prioridad con MoSCoW: Must, Should, Could, Won't.*

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-NNN-01 | Yo como … quiero que … para …, en el contexto …, debe tener el formato … | R-01 | Must |

## 3. Flujos — *Cómo*

*Pasos numerados desde lo que ve el usuario. Un flujo principal (todo sale bien) y los alternos (qué pasa cuando algo falla o el usuario se desvía).*

**Principal**
1. …

**Alternos**
- 2a. Si …, entonces …

## 4. Requerimientos funcionales — *Resultado*

*Uno por fila, en forma EARS, verificable. Columna "Origen": `AS-IS` si la v1.0 ya lo hace, `NUEVO` si no, `CAMBIA` si lo hace distinto.*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-NNN-01 | Cuando …, el sistema debe … | | HU-NNN-01 |

## 5. Reglas de negocio y datos — *Complementos*

*Validaciones, rangos, formatos, cálculos. Con números.*

| ID | Regla |
|---|---|
| RN-NNN-01 | |

## 6. Requerimientos no funcionales — *Complementos*

*Solo los que apliquen a esta funcionalidad: seguridad, tiempos, uso sin conexión, mensajes de error. Medibles.*

| ID | Requerimiento |
|---|---|
| RNF-NNN-01 | |

## 7. Fuera de alcance — *Complementos*

*Lo que esta spec no cubre a propósito. Evita que crezca sola.*

- …

## 8. Criterios de aceptación — *Pruebas*

*Mínimo uno por requerimiento, con datos concretos. Incluye los casos de error y los bordes (vacío, cero, máximo, duplicado).*

**CA-NNN-01a** (verifica RF-NNN-01)
- **Given** …
- **When** …
- **Then** …

## 9. Preguntas abiertas

*Mientras quede una, la spec no se aprueba.*

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | | | |

## 10. Checklist antes de aprobar

- [ ] No queda ningún `[DAVID]` ni `[DECIDIR]`.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA, y cada CA tiene datos concretos.
- [ ] Hay al menos un CA de error por cada dato que el usuario escribe.
- [ ] Puedo explicarle cada requerimiento a alguien que no conoce la app.
