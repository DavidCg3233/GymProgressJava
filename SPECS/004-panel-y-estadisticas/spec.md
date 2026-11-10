# Spec 004 — Panel y estadísticas

| | |
|---|---|
| **Estado** | Borrador (desbloqueada el 2026-11-09: sí se registran sesiones) |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 (ingeniería inversa de v1.0) |
| **Requisitos de origen** | R-24, R-01, R-03, R-18 |
| **Depende de** | 006, 002 |
| **Hallazgos relacionados** | H-07, H-08, H-11, H-12, H-16, H-23 |

> Esta spec no produce datos: solo muestra los de las sesiones (006) y las rutinas (002). Por eso es la última. En la v1.0 tres de sus números tenían un título que no correspondía a lo que calculaban; ahora que existen las sesiones, se calculan sobre lo que de verdad se hizo.
>
> El 2026-11-09 el usuario pidió cuatro vistas (R-24): evolución por ejercicio, récords por ejercicio, sesiones por semana y series por grupo muscular.

## 1. Propósito

`[DAVID]` Cuando abres la app, ¿cuál es la **única** cosa que quieres ver en 5 segundos? ¿Y qué número te diría que estás progresando?

## 2. Actores e historias de usuario — *Quién*

| ID | Historia | Prioridad |
|---|---|---|
| HU-004-01 | Como usuario, quiero un resumen al entrar (peso, IMC, cuántas rutinas tengo), para ubicarme rápido. | `[DAVID]` |
| HU-004-02 | Como usuario, quiero ver qué rutina me toca hoy y cuáles siguen. | `[DAVID]` |
| HU-004-03 | Como usuario, quiero ver mis récords por ejercicio. | `[DAVID]` |
| HU-004-04 | Como usuario, quiero ver qué grupos musculares trabajo más. | `[DAVID]` |
| HU-004-05 | Como usuario, quiero ver cuánto entrené cada mes. | `[DAVID]` |
| HU-004-06 | `[DAVID]` | |

## 3. Flujos — *Cómo*

**Panel Principal `[AS-IS]`**
1. Tras iniciar sesión, el usuario ve: peso actual, IMC con su categoría, número de rutinas.
2. "Actividad Reciente": lista de sus registros de peso.
3. "Tus Próximas Rutinas": hasta 5 rutinas ordenadas desde el día de hoy hacia adelante; la de hoy lleva la etiqueta "Hoy"; las que no tienen día van al final. Tocar una lleva al gestor de rutinas.

**Estadísticas `[AS-IS]`**
1. "Récords Personales": los 5 ejercicios con mayor peso.
2. "Distribución de Ejercicios": gráfica por grupo muscular.
3. "Entrenamientos por Mes": gráfica de los últimos 6 meses.

## 4. Requerimientos funcionales — *Resultado*

**Lo que el título promete vs. lo que se calcula hoy**

| Lo que dice la pantalla | Lo que calcula `[AS-IS]` | Hallazgo |
|---|---|---|
| Récords Personales | El peso **planeado** más alto que aparece en alguna rutina tuya. Si editas la rutina y lo bajas, el "récord" baja. | H-08 |
| Entrenamientos por Mes | Cuántas rutinas **creaste** cada mes. Si creaste 4 en enero y entrenaste todo el año, febrero a diciembre salen en 0. | H-07 |
| Distribución de Ejercicios | Cuántas veces aparece cada grupo muscular en tus rutinas (no cuánto lo entrenaste). | H-11 |
| Actividad Reciente | Solo registros de peso corporal. | H-12 |

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-004-01 | `[DECIDIR]` Al entrar, el sistema debe mostrar primero la rutina de hoy con la opción de empezar la sesión (RNF-006-03). ¿Qué más, si algo? *(La v1.0 mostraba peso corporal, IMC y número de rutinas; el peso corporal ya entra, por la spec 003.)* | CAMBIA | HU-004-01 |
| RF-004-02 | El sistema debe listar hasta 5 rutinas empezando por la del día actual y siguiendo el orden de la semana. | AS-IS | HU-004-02 |
| RF-004-03 | El sistema debe marcar como "Hoy" las rutinas asignadas al día actual. | AS-IS | HU-004-02 |
| RF-004-04 | El sistema debe mostrar, por ejercicio, el mayor peso registrado en una serie confirmada de cualquier sesión del usuario, con la fecha en que se logró. `[DECIDIR]` ¿el récord es solo por peso, o por peso × reps? | CAMBIA | HU-004-03 |
| RF-004-05 | El sistema debe mostrar cuántas sesiones terminó el usuario en cada semana (de lunes a domingo). `[DECIDIR]` ¿se compara contra una meta semanal que tú fijas (por ejemplo 4)? sí · no | CAMBIA (R-24) | HU-004-05 |
| RF-004-06 | El sistema debe mostrar cuántas series confirmadas hizo el usuario de cada grupo muscular en un periodo. `[DECIDIR]` periodo: semana · últimas 4 semanas · elegible | CAMBIA (R-24) | HU-004-04 |
| RF-004-09 | Cuando el usuario elige un ejercicio, el sistema debe mostrar cómo cambiaron el peso y las repeticiones de sus series, sesión a sesión. `[DECIDIR]` ¿qué se grafica por sesión? la serie más pesada · el promedio · todas las series | NUEVO (R-24) | HU-004-03 |
| RF-004-07 | "Actividad reciente" muestra las últimas sesiones terminadas. | CAMBIA | HU-004-01 |
| RF-004-08 | `[DAVID]` | | |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla | Hoy `[AS-IS]` | Regla nueva |
|---|---|---|---|
| RN-004-01 | Récords mostrados | 5, de mayor a menor; se ignoran los de peso 0 | `[DAVID]` |
| RN-004-02 | Periodo de la gráfica mensual | Últimos 6 meses; los meses sin datos no aparecen | `[DECIDIR]` ¿se muestran en 0? |
| RN-004-03 | Primer día de la semana | Lunes | Igual |
| RN-004-04 | Usuario sin datos | Panel: "--" y "No tienes rutinas creadas." | `[DAVID]` ¿qué debería invitarlo a hacer? |

## 6. Requerimientos no funcionales — *Complementos*

| ID | Requerimiento |
|---|---|
| RNF-004-01 | `[PROPUESTA]` El título de cada número debe describir exactamente lo que se calcula. |
| RNF-004-02 | `[DAVID]` Tiempo máximo para que el panel muestre datos tras iniciar sesión. |

## 7. Fuera de alcance — *Complementos*

- `[DECIDIR]` Comparar periodos (este mes contra el anterior).
- `[DECIDIR]` Exportar estadísticas.
- `[DECIDIR]` Reportes guardados. *(La v1.0 tiene estructura para "reportes" que nunca se usó — H-23.)*
- `[DAVID]`

## 8. Criterios de aceptación — *Pruebas*

**CA-004-02a** (RF-004-02, RF-004-03) — `[AS-IS]`
- **Given** hoy es miércoles y tengo rutinas para Lunes, Miércoles, Viernes y una sin día
- **When** abro el panel
- **Then** veo en este orden: Miércoles (con "Hoy"), Viernes, Lunes, sin día.

**CA-004-04a** (RF-004-04) — `[AS-IS]`, documenta el comportamiento actual
- **Given** una rutina con "Sentadilla" a 100 kg
- **When** edito la rutina y dejo "Sentadilla" en 60 kg
- **Then** el récord de Sentadilla pasa de 100.0 kg a 60.0 kg.
- `[DAVID]` ¿Este es el comportamiento que quieres? Reescribe el *Then* con el correcto.

**CA-004-xx** — `[DAVID]` Faltan: usuario nuevo sin datos, más de 5 rutinas, mes sin actividad.

## 9. Preguntas abiertas

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿Se registran sesiones de entrenamiento? | — | **Sí** (2026-11-09, R-01). |
| 2 | Si la respuesta es no, ¿vale la pena la pantalla de Estadísticas? | Se queda renombrada · Se elimina y el panel absorbe lo útil | `[DECIDIR]` |
| 3 | ¿Panel y Estadísticas son dos pantallas o una? | Dos · Una | `[DECIDIR]` |

## 10. Checklist antes de aprobar

- [ ] La spec 006 está aprobada.
- [ ] No queda ningún `[DAVID]` ni `[DECIDIR]`.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada número de la pantalla tiene una definición exacta de cómo se calcula.
- [ ] Cada RF tiene al menos un CA, y cada CA tiene datos concretos.
