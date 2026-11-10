# Spec 002 — Rutinas

| | |
|---|---|
| **Estado** | Borrador |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 (ingeniería inversa de v1.0) |
| **Requisitos de origen** | R-03 (y el catálogo implícito en R-02 y R-04) |
| **Depende de** | — |
| **Hallazgos relacionados** | H-05, H-09, H-10 |

## 1. Propósito

La rutina es **el plan**: una lista de ejercicios con series, repeticiones y peso previstos para un día de la semana. Lo que se hizo de verdad vive en las sesiones ([spec 006](../006-sesiones/spec.md)). El usuario ajusta sus rutinas según el progreso que ve en sus sesiones (R-03).

> Las historias de abajo están en forma corta porque salieron del código. `[DAVID]` Pásalas al formato de la clase agregando **contexto** y **formato**, como en la spec 006.

## 2. Actores e historias de usuario — *Quién*

| ID | Historia | Prioridad |
|---|---|---|
| HU-002-01 | Como usuario, quiero crear una rutina con sus ejercicios, para saber qué me toca hacer. | `[DAVID]` |
| HU-002-02 | Como usuario, quiero asignarle un día de la semana, para ver qué me toca hoy. | `[DAVID]` |
| HU-002-03 | Como usuario, quiero editar una rutina, para ajustar ejercicios y cargas. | `[DAVID]` |
| HU-002-04 | Como usuario, quiero eliminar una rutina que ya no uso. | `[DAVID]` |
| HU-002-05 | Como usuario, quiero elegir ejercicios de una lista y poder agregar uno que no esté, para no escribir lo mismo cada vez. | `[DAVID]` |
| ~~HU-002-06~~ | ~~Registrar lo que hice en cada sesión.~~ Decidido el 2026-11-09 (R-01, R-02): se desarrolla en la spec 006. | — |

## 3. Flujos — *Cómo*

**Crear `[AS-IS]`**
1. En "Gestor de Entrenamientos" el usuario elige crear.
2. Escribe el nombre, elige un día (opcional) y agrega uno o más ejercicios. Por cada ejercicio: nombre (escrito o elegido de la lista), grupo muscular, series, repeticiones y peso en kg.
3. Guarda. La rutina aparece como tarjeta con sus primeros 3 ejercicios y un "+N más".

**Editar `[AS-IS]`**
1. El usuario abre una rutina; el formulario se llena con sus datos.
2. Cambia lo que quiera y guarda. El sistema reemplaza la lista completa de ejercicios por la nueva.

**Eliminar `[AS-IS]`**
1. El usuario elige eliminar; el sistema pregunta "¿Estás seguro de que quieres eliminar la rutina «X»?".
2. Si confirma, la rutina y sus ejercicios desaparecen.

**Grupo muscular nuevo `[AS-IS]`**
1. En la lista de grupos, el usuario elige crear uno y escribe su nombre.
2. El grupo queda disponible para todos los ejercicios (y para todos los usuarios).

**Alternos `[AS-IS]`**
- Guardar sin ejercicios → "Por favor, añade al menos un ejercicio."
- Quitar el único ejercicio → "Una rutina debe tener al menos un ejercicio."
- Ejercicio sin nombre → "El nombre de un ejercicio no puede estar vacío."
- Ejercicio escrito que no existe en la lista → se crea solo, con el grupo elegido o "General".
- Ejercicio que ya existe pero con otro grupo elegido → **se le cambia el grupo al ejercicio para todos** (H-10).

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-002-01 | Cuando el usuario guarda una rutina con nombre y al menos un ejercicio, el sistema debe mostrarla en su lista de rutinas. | AS-IS | HU-002-01 |
| ~~RF-002-02~~ | ~~Cada usuario ve únicamente sus rutinas.~~ Es RNF: pasa a RNF-ACC-06 en `rnf.md`. | — | — |
| RF-002-03 | Si la rutina no tiene ningún ejercicio, entonces el sistema debe rechazar el guardado e indicar el motivo. | AS-IS | HU-002-01 |
| RF-002-04 | El sistema debe permitir asignar a la rutina un día de la semana o ninguno. | AS-IS | HU-002-02 |
| RF-002-05 | Cuando el usuario guarda cambios en una rutina, el sistema debe conservar el resultado completo o no cambiar nada. | AS-IS (ver H-05) | HU-002-03 |
| RF-002-06 | Cuando el usuario confirma eliminar una rutina, el sistema debe eliminarla junto con sus ejercicios previstos, **sin tocar las sesiones ya registradas** (RF-006-11). | CAMBIA | HU-002-04 |
| ~~RF-002-07~~ | ~~Rechazar cambios a rutinas ajenas.~~ Es RNF: pasa a RNF-ACC-06 y RNF-SEG-06 en `rnf.md`. | — | — |
| RF-002-08 | El sistema debe ofrecer la lista de ejercicios existentes al escribir el nombre de un ejercicio. | AS-IS | HU-002-05 |
| RF-002-09 | Cuando el usuario usa un ejercicio que no existe, el sistema debe crearlo. | AS-IS | HU-002-05 |
| RF-002-10 | `[DECIDIR]` ¿De quién son los ejercicios y grupos? Hoy son compartidos por todos (H-10). Opciones: catálogo base fijo + los propios de cada usuario · todo propio de cada usuario · todo compartido como hoy. | CAMBIA | HU-002-05 |
| ~~RF-002-11~~ | ~~Conservar el valor anterior al editar cargas.~~ Resuelto: el historial de cargas son las sesiones (spec 006); la rutina solo guarda el plan vigente. | — | — |
| RF-002-13 | `[DECIDIR]` Si modifico una rutina mientras tengo una sesión de esa rutina en curso, ¿el cambio aplica a la sesión en curso o desde la siguiente? | NUEVO | HU-002-03 |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Campo | Hoy `[AS-IS]` | Regla nueva |
|---|---|---|---|
| RN-002-01 | Nombre de rutina | Obligatorio, máx. 50 caracteres; se permiten repetidos | `[DAVID]` ¿repetidos? |
| RN-002-02 | Día | Vacío o Lunes…Domingo; varias rutinas pueden compartir día | `[DECIDIR]` ¿una rutina puede tener varios días? |
| RN-002-03 | Ejercicios por rutina | Mínimo 1, sin máximo; el mismo ejercicio puede repetirse | `[DAVID]` |
| RN-002-04 | Series | Entero ≥ 1 (solo en la interfaz) | `[DAVID]` máximo |
| RN-002-05 | Repeticiones | Entero ≥ 1 (solo en la interfaz) | `[DAVID]` máximo |
| RN-002-06 | Peso (kg) | ≥ 0 en pasos de 0,5; máx. 999,99 | `[DAVID]` ¿0 = peso corporal? |
| RN-002-07 | Nombre de ejercicio | Obligatorio, máx. 50; "Press Banca" y "press banca" `[DAVID]` *(pruébalo en la app: ¿quedan como uno o como dos?)* | `[DAVID]` |
| RN-002-08 | Descripción de rutina | Existe el dato pero no hay dónde escribirla | `[DECIDIR]` se muestra · se elimina |

## 6. Requerimientos no funcionales — *Complementos*

| ID | Requerimiento |
|---|---|
| — | Los generales están en [`rnf.md`](../rnf.md). Esta spec no agrega propios. |

## 7. Fuera de alcance — *Complementos*

- `[DECIDIR]` Compartir rutinas entre usuarios.
- `[DECIDIR]` Rutinas prediseñadas.
- `[DECIDIR]` Tiempos de descanso, superseries, notas por ejercicio.
- `[DAVID]`

## 8. Criterios de aceptación — *Pruebas*

**CA-002-01a** (RF-002-01) — `[AS-IS]`
- **Given** que inicié sesión y no tengo rutinas
- **When** creo "Tren superior" para Lunes con "Press de Banca", grupo Pecho, 4 series, 10 repeticiones, 40 kg
- **Then** veo una tarjeta "Tren superior" con día Lunes y ese ejercicio.

**CA-002-03a** (RF-002-03) — `[AS-IS]`
- **Given** el formulario de rutina con nombre y sin ejercicios
- **When** guardo
- **Then** veo "Por favor, añade al menos un ejercicio." **y** no se crea la rutina.

**CA-002-05a** (RF-002-05) — `[AS-IS]`
- **Given** la rutina "Tren superior" con 2 ejercicios
- **When** la edito, quito uno, cambio el peso del otro a 45 kg y guardo
- **Then** la tarjeta muestra 1 ejercicio con 45 kg.

**CA-002-06a** (RF-002-06) — NUEVO
- **Given** la rutina "Pecho" con 2 sesiones terminadas
- **When** elimino la rutina y confirmo
- **Then** "Pecho" ya no está en mis rutinas **y** las 2 sesiones siguen en mi historial.

**CA-002-xx** — `[DAVID]` Uno por cada regla de la sección 5 (límite que pasa y primero que no).

## 9. Preguntas abiertas

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿La rutina es solo un plan, o también se registra cada sesión hecha? | Solo plan · Plan + registro de sesiones | **Plan + sesiones** (2026-11-09, R-01). Las sesiones van en la spec 006. |
| 2 | ¿De quién es el catálogo de ejercicios? | Ver RF-002-10 | `[DECIDIR]` |
| 3 | ¿El grupo muscular es obligatorio? | Sí · No ("General" por defecto como hoy) | `[DECIDIR]` |
| 4 | ¿Se puede duplicar una rutina? | Sí · No | `[DECIDIR]` |

## 10. Checklist antes de aprobar

- [ ] No queda ningún `[DAVID]` ni `[DECIDIR]`.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA, y cada CA tiene datos concretos.
- [ ] Hay un CA de error por cada campo de la sección 5.
- [ ] Puedo explicarle cada requerimiento a alguien que no conoce la app.
