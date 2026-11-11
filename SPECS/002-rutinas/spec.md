# Spec 002 — Rutinas y catálogo de ejercicios

| | |
|---|---|
| **Estado** | **Aprobada** por David el 2026-11-10 |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 (ingeniería inversa de v1.0) · reescrita el 2026-11-10 con las decisiones del usuario |
| **Requisitos de origen** | R-03, y el catálogo implícito en R-02 y R-04 |
| **Depende de** | — |
| **Resuelve** | H-09, H-10, H-11, H-20 |

## 1. Propósito

La rutina es **el plan**: una lista de ejercicios con series, repeticiones y peso previstos, asignada a uno o varios días de la semana. Lo que se hizo de verdad vive en las sesiones ([spec 006](../006-sesiones/spec.md)). El usuario crea, ajusta y elimina sus rutinas según el progreso que ve (R-03).

Cada usuario tiene su propio catálogo de ejercicios y grupos musculares. Arranca con una lista predefinida que puede cambiar o borrar a su gusto.

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista.

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-002-01 | **Yo como** deportista **quiero que** la app me deje crear una rutina con sus ejercicios, series, reps y peso previstos **para** saber qué me toca hacer, **en el contexto** de planear mi semana con calma, fuera del gimnasio, **debe tener el formato** de un nombre y una lista ordenada de ejercicios. | R-03 | Must |
| HU-002-02 | **Yo como** deportista **quiero que** pueda asignar la rutina a uno o varios días de la semana **para** que la app me muestre qué toca hoy, **en el contexto** de repetir una rutina dos veces por semana, **debe tener el formato** de siete días que marco o desmarco. | R-03 | Must |
| HU-002-03 | **Yo como** deportista **quiero que** pueda modificar una rutina **para** ajustarla según mi progreso, **en el contexto** de revisar mis sesiones y ver que un ejercicio se quedó corto, **debe tener el formato** del mismo formulario de creación con los datos ya puestos. | R-03 | Must |
| HU-002-04 | **Yo como** deportista **quiero que** pueda eliminar una rutina que ya no uso **para** mantener mi lista limpia, **en el contexto** de cambiar de plan de entrenamiento, **debe tener el formato** de una acción con confirmación que no borra mi historial. | R-03 | Must |
| HU-002-05 | **Yo como** deportista **quiero que** al armar una rutina pueda elegir ejercicios de mi catálogo o crear uno nuevo ahí mismo **para** no escribir lo mismo cada vez, **en el contexto** de agregar un ejercicio, **debe tener el formato** de un buscador que sugiere mientras escribo. | R-02, R-04 | Must |
| HU-002-06 | **Yo como** deportista **quiero que** mi catálogo venga con ejercicios comunes ya cargados y que pueda cambiarlos o borrarlos **para** empezar rápido sin quedar amarrado a una lista ajena, **en el contexto** de usar la app por primera vez, **debe tener el formato** de una lista por grupo muscular que puedo editar. | Decisión 2026-11-10 | Should |

## 3. Flujos — *Cómo*

**Crear una rutina**
1. Elijo crear. Escribo el nombre y marco los días (o ninguno).
2. Agrego un ejercicio: escribo y la app sugiere de mi catálogo. Si no existe, lo creo ahí mismo eligiendo su grupo muscular.
3. Indico series, reps y peso previstos. Repito con los demás y los ordeno.
4. Guardo. La rutina aparece en mi lista.

**Alternos**
- 4a. Sin nombre o sin ejercicios → se rechaza indicando qué falta.
- 4b. Un valor fuera de rango → se rechaza indicando el rango.
- Modificar con una sesión de esa rutina en curso → la sesión en curso no cambia; el cambio aplica desde la siguiente.
- Eliminar → la app pide confirmación; mis sesiones ya registradas se conservan.

**Catálogo**
1. Abro mi catálogo: ejercicios agrupados por grupo muscular.
2. Puedo crear, renombrar y cambiar de grupo un ejercicio, y crear o renombrar grupos.
3. Puedo eliminar un ejercicio o un grupo, con confirmación.

**Alternos del catálogo**
- Elimino un ejercicio que está en alguna rutina → la app avisa en cuáles está; si confirmo, sale de esas rutinas. Las sesiones pasadas lo conservan.
- Elimino un grupo que tiene ejercicios → la app no lo permite hasta que mueva o elimine sus ejercicios.
- Creo un ejercicio con un nombre que ya tengo → se rechaza.

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-002-01 | Cuando el usuario guarda una rutina con nombre y al menos un ejercicio, el sistema debe mostrarla en su lista de rutinas. | AS-IS | HU-002-01 |
| ~~RF-002-02~~ | ~~Cada usuario ve únicamente sus rutinas.~~ Es RNF: RNF-ACC-06. | — | — |
| RF-002-03 | Si la rutina no tiene nombre o no tiene ningún ejercicio, entonces el sistema debe rechazar el guardado e indicar qué falta. | AS-IS | HU-002-01 |
| RF-002-04 | El sistema debe permitir asignar a la rutina uno, varios o ningún día de la semana. | CAMBIA | HU-002-02 |
| RF-002-05 | Cuando el usuario guarda cambios en una rutina, el sistema debe conservar el resultado completo o no cambiar nada. | AS-IS | HU-002-03 |
| RF-002-06 | Cuando el usuario confirma eliminar una rutina, el sistema debe eliminarla junto con sus ejercicios previstos, sin tocar las sesiones ya registradas (RF-006-11). | CAMBIA | HU-002-04 |
| ~~RF-002-07~~ | ~~Rechazar cambios a rutinas ajenas.~~ Es RNF: RNF-ACC-06 y RNF-SEG-06. | — | — |
| RF-002-08 | Mientras el usuario escribe el nombre de un ejercicio, el sistema debe sugerir los de su catálogo que coincidan. | AS-IS | HU-002-05 |
| RF-002-09 | Cuando el usuario usa un ejercicio que no está en su catálogo, el sistema debe pedirle el grupo muscular y crearlo en su catálogo. | CAMBIA | HU-002-05 |
| RF-002-10 | El sistema debe mantener un catálogo de ejercicios y grupos musculares propio de cada usuario; los cambios de un usuario no deben afectar a otro. | CAMBIA (H-10) | HU-002-06 |
| ~~RF-002-11~~ | ~~Conservar el valor anterior al editar cargas.~~ Resuelto: el historial son las sesiones (spec 006). | — | — |
| ~~RF-002-12~~ | ~~Registrar la sesión real.~~ Pasó a la spec 006. | — | — |
| RF-002-13 | Mientras exista una sesión en curso de una rutina, los cambios a esa rutina no deben alterar la sesión en curso. | NUEVO | HU-002-03 |
| RF-002-14 | Cuando se crea una cuenta, el sistema debe cargar en su catálogo los ejercicios y grupos predefinidos de la sección 5. | NUEVO | HU-002-06 |
| RF-002-15 | El usuario debe poder crear, renombrar y cambiar de grupo cualquier ejercicio de su catálogo, incluidos los predefinidos. | NUEVO | HU-002-06 |
| RF-002-16 | Cuando el usuario confirma eliminar un ejercicio de su catálogo, el sistema debe quitarlo del catálogo y de sus rutinas, y conservarlo en las sesiones ya registradas. | NUEVO | HU-002-06 |
| RF-002-17 | Antes de eliminar un ejercicio que está en alguna rutina, el sistema debe mostrar en cuáles está. | NUEVO | HU-002-06 |
| RF-002-18 | Si eliminar un ejercicio dejaría una rutina sin ejercicios, entonces el sistema debe advertirlo y, si el usuario confirma, eliminar también esa rutina. | NUEVO | HU-002-06 |
| RF-002-19 | El usuario debe poder crear y renombrar grupos musculares. Si un grupo tiene ejercicios, entonces el sistema no debe permitir eliminarlo. | NUEVO | HU-002-06 |
| RF-002-20 | El usuario debe poder cambiar el orden de los ejercicios dentro de una rutina; la sesión los presenta en ese orden. | NUEVO | HU-002-01 |
| RF-002-21 | El usuario debe poder duplicar una rutina; la copia se llama igual con " (copia)" y no tiene días asignados. | NUEVO | HU-002-01 |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla | Valor |
|---|---|---|
| RN-002-01 | Nombre de rutina | Obligatorio, de 1 a 50 caracteres; único entre las rutinas del usuario |
| RN-002-02 | Días | Cualquier combinación de lunes a domingo, o ninguno. Varias rutinas pueden compartir día |
| RN-002-03 | Ejercicios por rutina | De 1 a 20; un mismo ejercicio aparece una sola vez por rutina |
| RN-002-04 | Series previstas | Entero de 1 a 10 (igual que RN-006-05) |
| RN-002-05 | Repeticiones previstas | Entero de 1 a 100 (igual que RN-006-04) |
| RN-002-06 | Peso previsto | De 0 a 500 kg en múltiplos de 0,5; 0 = peso corporal (igual que RN-006-02 y 03) |
| RN-002-07 | Nombre de ejercicio | De 1 a 50 caracteres; único en el catálogo del usuario sin distinguir mayúsculas ni tildes ("Press Banca" y "press banca" son el mismo) |
| RN-002-08 | Grupo muscular | Obligatorio para cada ejercicio; nombre de 1 a 30 caracteres, único en el catálogo del usuario |
| RN-002-09 | Series previstas iguales | Todas las series previstas de un ejercicio comparten reps y peso. Las diferencias reales entre series se registran en la sesión |
| ~~RN-002-xx~~ | ~~Descripción de rutina (v1.0)~~ | Eliminada: nunca tuvo dónde escribirse |

### Catálogo predefinido (RF-002-14)

8 grupos y 40 ejercicios, aprobados por David el 2026-11-10. Cada usuario puede cambiarlos o borrarlos en su catálogo (RF-002-15, 16).

| Grupo | Ejercicios |
|---|---|
| Pecho | Press de banca · Press inclinado · Press declinado · Press con mancuernas · Aperturas con mancuernas · Cruce de poleas · Fondos |
| Espalda | Dominadas · Jalón al pecho · Remo con barra · Remo con mancuerna · Remo en polea baja · Peso muerto |
| Hombro | Press militar · Press Arnold · Elevaciones laterales · Elevaciones frontales · Pájaros · Face pull |
| Bíceps | Curl con barra · Curl con mancuernas · Curl martillo · Curl predicador |
| Tríceps | Extensión en polea · Press francés · Fondos en banco · Patada de tríceps |
| Pierna | Sentadilla · Prensa · Zancadas · Extensión de cuádriceps · Curl femoral · Peso muerto rumano · Hip thrust |
| Pantorrilla | Elevación de talones de pie · Elevación de talones sentado |
| Abdomen | Crunch · Plancha · Elevación de piernas · Rueda abdominal |

> La plancha se mide en tiempo, no en repeticiones. La spec 006 solo registra peso y reps: o la registras como reps (segundos) con peso 0, o la quitas de la lista.

## 6. Requerimientos no funcionales — *Complementos*

Los generales están en [`rnf.md`](../rnf.md). Propio de esta spec:

| ID | Requerimiento |
|---|---|
| RNF-002-01 | Crear y modificar rutinas y catálogo requiere conexión. Solo el registro de sesiones funciona sin ella (RNF-PLA-06). Si no hay conexión, el sistema lo indica sin perder lo escrito. |

## 7. Fuera de alcance — *Complementos*

- Compartir rutinas entre usuarios.
- Rutinas prediseñadas (solo se predefinen ejercicios).
- Tiempos de descanso, superseries y ejercicios por tiempo.
- Programar rutinas por fecha o por ciclos (solo por día de la semana).

## 8. Criterios de aceptación — *Pruebas*

**CA-002-01a** (RF-002-01, RF-002-04)
- **Given** no tengo rutinas
- **When** creo "Pecho" para lunes y jueves con "Press inclinado", 3 series de 10 reps con 30 kg
- **Then** veo "Pecho" en mi lista con los días lunes y jueves y ese ejercicio.

**CA-002-03a** (RF-002-03)
- **Given** el formulario con nombre "Pecho" y sin ejercicios
- **When** guardo
- **Then** se rechaza indicando que falta al menos un ejercicio **y** no se crea la rutina.

**CA-002-06a** (RF-002-06)
- **Given** la rutina "Pecho" con 2 sesiones terminadas
- **When** la elimino y confirmo
- **Then** "Pecho" ya no está en mis rutinas **y** las 2 sesiones siguen en mi historial.

**CA-002-09a** (RF-002-09)
- **Given** mi catálogo no tiene "Press en máquina"
- **When** lo escribo al armar una rutina, elijo el grupo Pecho y guardo la rutina
- **Then** "Press en máquina" queda en mi catálogo dentro de Pecho.

**CA-002-10a** (RF-002-10, RF-002-14)
- **Given** dos cuentas nuevas, A y B, ambas con "Press de banca" en Pecho
- **When** A lo renombra a "Bench press" y elimina "Fondos"
- **Then** el catálogo de B sigue teniendo "Press de banca" y "Fondos".

**CA-002-13a** (RF-002-13)
- **Given** una sesión de "Pecho" en curso con "Press inclinado" de 3 series
- **When** modifico la rutina a 4 series y vuelvo a la sesión
- **Then** la sesión en curso sigue con 3 series **y** la siguiente sesión de "Pecho" empieza con 4.

**CA-002-16a** (RF-002-16, RF-002-17)
- **Given** "Fondos" está en la rutina "Pecho" (que tiene más ejercicios) y en 3 sesiones terminadas
- **When** lo elimino del catálogo
- **Then** la app me avisa que está en "Pecho"; al confirmar, sale del catálogo y de "Pecho" **y** las 3 sesiones lo siguen mostrando.

**CA-002-18a** (RF-002-18)
- **Given** la rutina "Solo fondos" tiene únicamente "Fondos"
- **When** elimino "Fondos" del catálogo
- **Then** la app advierte que "Solo fondos" quedaría vacía y se eliminará; si cancelo, no cambia nada.

**CA-002-19a** (RF-002-19)
- **When** intento eliminar el grupo Pecho, que tiene ejercicios
- **Then** se rechaza indicando que primero debo mover o eliminar sus ejercicios.

**CA-002-21a** (RF-002-21)
- **When** duplico "Pecho" (lunes y jueves)
- **Then** aparece "Pecho (copia)" con los mismos ejercicios y sin días.

**CA-002-RN** — bordes

| Dato | Valor | Resultado |
|---|---|---|
| Nombre de rutina | 50 caracteres | Se acepta |
| Nombre de rutina | 51 caracteres | Se rechaza |
| Nombre de rutina | igual a otra mía | Se rechaza |
| Ejercicios | 20 | Se acepta |
| Ejercicios | 21 | Se rechaza |
| Mismo ejercicio dos veces | — | Se rechaza |
| Series | 0 / 1 / 10 / 11 | Rechaza / acepta / acepta / rechaza |
| Reps | 0 / 1 / 100 / 101 | Rechaza / acepta / acepta / rechaza |
| Peso | −0,5 / 0 / 500 / 500,5 / 30,3 | Rechaza / acepta / acepta / rechaza / rechaza |
| Ejercicio nuevo | "press de banca" existiendo "Press de banca" | Se rechaza: ya existe |

## 9. Decisiones

| # | Pregunta | Decisión |
|---|---|---|
| 1 | ¿Solo plan o plan + sesiones? | **Plan + sesiones** (2026-11-09, R-01). |
| 2 | ¿De quién es el catálogo? | **De cada usuario, con una lista predefinida que puede cambiar o eliminar** (2026-11-10). |
| 3 | ¿Varios días por rutina? | **Sí** (2026-11-10). |
| 4 | ¿Modificar con sesión en curso? | **Aplica desde la siguiente** (2026-11-10). |
| 5 | ¿Quién define la lista predefinida? | **La de la sección 5**, aprobada el 2026-11-10. |

Reglas que definí yo para que la spec fuera comprobable y que puedes cambiar: nombres únicos, máximo 20 ejercicios por rutina, un ejercicio una sola vez por rutina, grupo muscular obligatorio, duplicar rutina, y qué pasa al eliminar un ejercicio o un grupo en uso.

## 10. Checklist antes de aprobar

- [ ] Revisé y ajusté la lista predefinida de la sección 5.
- [ ] Leí las "reglas que definí yo" y estoy de acuerdo o las cambié.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
- [ ] Puedo explicarle cada requerimiento a alguien que no conoce la app.
