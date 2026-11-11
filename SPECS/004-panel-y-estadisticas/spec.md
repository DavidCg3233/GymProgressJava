# Spec 004 — Inicio y progreso

| | |
|---|---|
| **Estado** | **Aprobada** por David el 2026-11-10 |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 (ingeniería inversa de v1.0) · reescrita el 2026-11-10 con las decisiones del usuario |
| **Requisitos de origen** | R-24, R-01, R-03, R-08, R-18 |
| **Depende de** | 006, 002, 003 |
| **Resuelve** | H-07, H-08, H-11, H-12 |

> Esta spec no produce datos: muestra los de las sesiones (006), las rutinas (002) y el peso corporal (003). En la v1.0 tres de sus números tenían un título que no correspondía a lo que calculaban; aquí cada indicador tiene su definición exacta (RNF-USA-03).

## 1. Propósito

Dos cosas: que al abrir la app el usuario llegue en segundos a la sesión de hoy, y que pueda ver su progreso real para decidir cómo ajustar sus rutinas (R-03: "según como vea mi progreso").

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista.

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-004-01 | **Yo como** deportista **quiero que** al abrir la app vea la rutina que toca hoy y pueda empezarla **para** no perder tiempo navegando, **en el contexto** de llegar al gimnasio, **debe tener el formato** de una pantalla de inicio con la rutina de hoy arriba y un botón para empezar. | R-08 | Must |
| HU-004-02 | **Yo como** deportista **quiero que** la app me muestre cómo han cambiado mis cargas en un ejercicio **para** decidir si subo peso o cambio la rutina, **en el contexto** de revisar mi progreso con calma, **debe tener el formato** de una gráfica por sesión que alterna entre la serie más pesada y el volumen total. | R-24 | Must |
| HU-004-03 | **Yo como** deportista **quiero que** la app me muestre mi récord en cada ejercicio **para** saber cuál es mi marca a superar, **en el contexto** de prepararme para una serie pesada, **debe tener el formato** de "peso × reps" con la fecha. | R-24 | Must |
| HU-004-04 | **Yo como** deportista **quiero que** la app me muestre cuántas sesiones hice cada semana frente a mi meta **para** saber si estoy siendo constante, **en el contexto** de mi revisión semanal, **debe tener el formato** de "3 de 4 esta semana" y las semanas anteriores. | R-24 | Must |
| HU-004-05 | **Yo como** deportista **quiero que** la app me muestre cuántas series hice de cada grupo muscular esta semana **para** ver si estoy descuidando alguno, **en el contexto** de planear lo que queda de la semana, **debe tener el formato** de una lista de grupos con su número de series. | R-24 | Should |

## 3. Flujos — *Cómo*

**Inicio**
1. Abro la app. Arriba veo la rutina de hoy con el botón para empezar la sesión.
2. Debajo: cuántas sesiones llevo esta semana frente a mi meta, y mis últimas sesiones.

**Alternos del inicio**
- 1a. Tengo una sesión en curso → en lugar de la rutina de hoy veo "Continuar sesión" (RF-006-02).
- 1b. Hoy tocan varias rutinas → las veo todas, cada una con su botón.
- 1c. Hoy no toca ninguna → veo "Hoy no tienes rutina" con las opciones de elegir una rutina o empezar una sesión libre.
- 1d. No tengo rutinas → una invitación a crear la primera.
- 1e. Ya terminé hoy la rutina de hoy → aparece marcada como hecha; puedo empezarla otra vez si quiero.

**Progreso**
1. Abro "Progreso". Veo sesiones por semana y series por grupo muscular de esta semana.
2. Abro la lista de ejercicios que he hecho; cada uno muestra su récord.
3. Toco un ejercicio: veo su gráfica de evolución y alterno entre "serie más pesada" y "volumen".

## 4. Requerimientos funcionales — *Resultado*

### Inicio

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-004-01 | Al entrar, el sistema debe mostrar primero las rutinas asignadas al día actual, cada una con la opción de empezar su sesión. | CAMBIA | HU-004-01 |
| RF-004-02 | Mientras haya una sesión en curso, el sistema debe mostrar en primer lugar la opción de continuarla. | NUEVO | HU-004-01 |
| RF-004-03 | Si ninguna rutina está asignada al día actual, entonces el sistema debe ofrecer elegir cualquier rutina o empezar una sesión libre. | CAMBIA | HU-004-01 |
| RF-004-07 | El sistema debe mostrar en el inicio las 3 sesiones terminadas más recientes, con fecha y nombre. | CAMBIA | HU-004-01 |
| RF-004-10 | El sistema debe marcar como hecha una rutina de hoy que ya tiene una sesión terminada hoy. | NUEVO | HU-004-01 |

### Progreso

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-004-04 | El sistema debe mostrar, por cada ejercicio con series confirmadas, su récord: el peso y las repeticiones de la mejor serie, y la fecha en que se logró. | CAMBIA (H-08) | HU-004-03 |
| RF-004-05 | El sistema debe mostrar cuántas sesiones terminó el usuario en la semana actual y en cada una de las 11 anteriores. | CAMBIA (H-07) | HU-004-04 |
| RF-004-06 | El sistema debe mostrar cuántas series confirmadas hizo el usuario de cada grupo muscular en la semana actual. | CAMBIA (H-11) | HU-004-05 |
| RF-004-09 | Cuando el usuario elige un ejercicio, el sistema debe graficar un punto por sesión en la que lo hizo, y permitir alternar entre la serie más pesada y el volumen total. | NUEVO | HU-004-02 |
| RF-004-11 | El usuario debe poder fijar, cambiar o quitar su meta de sesiones por semana. Mientras exista, el sistema debe mostrar el avance de la semana actual frente a ella e indicar qué semanas la cumplieron. | NUEVO | HU-004-04 |
| RF-004-12 | Si el usuario no tiene sesiones terminadas, entonces el sistema debe mostrar en Progreso una invitación a registrar la primera, sin gráficas vacías ni ceros. | NUEVO | HU-004-02 |
| ~~RF-004-08~~ | ~~Hueco de la versión borrador.~~ No usado. | — | — |

## 5. Reglas de negocio y datos — *Complementos*

Definición exacta de cada indicador (RNF-USA-03):

| ID | Indicador o regla | Definición |
|---|---|---|
| RN-004-01 | Qué cuenta | Solo series **confirmadas** de sesiones **terminadas**. Las sesiones eliminadas dejan de contar. |
| RN-004-02 | Semana | De lunes a domingo. Una sesión pertenece al día en que empezó. |
| RN-004-03 | **Récord** de un ejercicio | La serie de mayor peso. Si varias empatan en peso, la de más repeticiones. Si siguen empatadas, la más antigua (el récord es de quien lo logró primero). |
| RN-004-04 | Récord en ejercicios de peso corporal | Si todas las series del ejercicio tienen peso 0, el récord es la serie de más repeticiones y se muestra como "peso corporal × reps". |
| RN-004-05 | **Serie más pesada** de una sesión (gráfica) | El mayor peso entre las series confirmadas de ese ejercicio en esa sesión; al tocar el punto se ven sus reps. |
| RN-004-06 | **Volumen** de una sesión (gráfica) | Suma de peso × repeticiones de las series confirmadas de ese ejercicio en esa sesión. En ejercicios de peso corporal, suma de repeticiones. |
| RN-004-07 | **Sesiones por semana** | Número de sesiones terminadas cuya fecha de inicio cae en esa semana. Incluye las sesiones libres. |
| RN-004-08 | Meta semanal | Opcional, entero de 1 a 14, propia de cada usuario. Una semana "cumple" si sus sesiones son mayores o iguales a la meta vigente hoy. |
| RN-004-09 | **Series por grupo muscular** | Número de series confirmadas en la semana actual, agrupadas por el grupo que tiene hoy cada ejercicio en el catálogo. Se listan de mayor a menor; los grupos con 0 series también aparecen. |
| RN-004-10 | Ejercicio eliminado del catálogo | Sus series siguen contando en récords y gráficas con el nombre que tenía; en grupos musculares cuentan en el grupo que tenía al eliminarse. |
| RN-004-11 | Rutina "de hoy" | Toda rutina que tenga marcado el día actual de la semana. |

## 6. Requerimientos no funcionales — *Complementos*

Los generales están en [`rnf.md`](../rnf.md) (RNF-REN-01: 2 segundos hasta ver la rutina de hoy). Propios de esta spec:

| ID | Requerimiento |
|---|---|
| RNF-004-01 | El inicio debe funcionar sin conexión, con los datos que el dispositivo ya tenía (necesario para RF-006-17). |
| RNF-004-02 | Las vistas de Progreso requieren conexión. Sin ella, el sistema lo indica. |
| RNF-004-03 | Cada indicador debe mostrar, al tocarlo, una frase que explique cómo se calcula. |

## 7. Fuera de alcance — *Complementos*

- Comparar periodos o usuarios.
- Estimación de repetición máxima (1RM).
- Exportar estadísticas o generar reportes.
- Elegir el periodo de los grupos musculares (queda fijo en la semana actual).
- Mostrar el peso corporal en el inicio (se ve en su propia pantalla, spec 003).

## 8. Criterios de aceptación — *Pruebas*

**CA-004-01a** (RF-004-01, RN-004-11)
- **Given** hoy es lunes; "Pecho" está en lunes y jueves, "Pierna" en martes
- **When** abro la app
- **Then** veo "Pecho" arriba con la opción de empezar **y** no veo "Pierna" como rutina de hoy.

**CA-004-02a** (RF-004-02)
- **Given** una sesión de "Pecho" en curso
- **When** abro la app
- **Then** lo primero que veo es "Continuar sesión: Pecho".

**CA-004-03a** (RF-004-03)
- **Given** hoy es domingo y ninguna rutina tiene domingo
- **When** abro la app
- **Then** veo que hoy no hay rutina, con las opciones de elegir una y de sesión libre.

**CA-004-04a** (RF-004-04, RN-004-03) — récord

Series confirmadas de "Press inclinado":

| Fecha | Peso | Reps |
|---|---|---|
| 2 nov | 32,5 | 8 |
| 9 nov | 35 | 5 |
| 16 nov | 35 | 6 |
| 23 nov | 35 | 6 |
| 23 nov | 30 | 15 |

- **Then** el récord es **35 kg × 6, del 16 nov** (mayor peso; entre los de 35, más reps; entre los empatados, el más antiguo).

**CA-004-04b** (RN-004-04)
- **Given** "Dominadas" con series de 0 kg × 8 y 0 kg × 10
- **Then** el récord es "peso corporal × 10".

**CA-004-04c** (H-08: lo que la v1.0 hacía mal)
- **Given** el récord de "Press inclinado" es 35 kg × 6
- **When** modifico la rutina y bajo el peso previsto a 20 kg
- **Then** el récord sigue siendo 35 kg × 6.

**CA-004-05a** (RF-004-05, RF-004-11, RN-004-07)
- **Given** mi meta es 4 y esta semana terminé 3 sesiones (una de ellas libre)
- **Then** veo "3 de 4 esta semana" **y** la semana no aparece como cumplida.

**CA-004-05b** (RN-004-02)
- **Given** empecé una sesión el domingo a las 11:30 p. m. y la terminé el lunes a las 12:40 a. m.
- **Then** cuenta para la semana del domingo.

**CA-004-06a** (RF-004-06, RN-004-09)
- **Given** esta semana confirmé 9 series de ejercicios de Pecho y 4 de Bíceps, y ninguna de Pierna
- **Then** veo Pecho 9, Bíceps 4 y Pierna 0, en ese orden.

**CA-004-09a** (RF-004-09, RN-004-05, RN-004-06)
- **Given** una sesión con "Press inclinado": 30 × 10, 32,5 × 8, 32,5 × 6
- **Then** su punto en "serie más pesada" vale 32,5 **y** en "volumen" vale 755 (300 + 260 + 195).

**CA-004-12a** (RF-004-12)
- **Given** una cuenta nueva sin sesiones
- **When** abro Progreso
- **Then** veo una invitación a registrar mi primera sesión, sin gráficas.

## 9. Decisiones

| # | Pregunta | Decisión |
|---|---|---|
| 1 | ¿Se registran sesiones? | **Sí** (2026-11-09, R-01). |
| 2 | ¿Qué vistas de progreso? | **Evolución por ejercicio, récords, sesiones por semana y series por grupo muscular** (2026-11-09, R-24). |
| 3 | ¿Qué es el récord? | **Mayor peso, con sus reps** (2026-11-10). |
| 4 | ¿Periodo de los grupos musculares? | **Semana actual** (2026-11-10). |
| 5 | ¿Qué se grafica por sesión? | **Serie más pesada y volumen, con selector** (2026-11-10). |
| 6 | ¿Meta semanal? | **Sí, la fija cada usuario** (2026-11-10). |

Reglas que definí yo y que puedes cambiar: desempate del récord (más reps, luego el más antiguo), tratamiento del peso corporal en récord y volumen, 12 semanas de historia, 3 sesiones recientes en el inicio, meta de 1 a 14, y que Progreso necesite conexión.

## 10. Checklist antes de aprobar

- [ ] Verifiqué a mano el récord de CA-004-04a y el volumen de CA-004-09a.
- [ ] Leí las "reglas que definí yo" y estoy de acuerdo o las cambié.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
- [ ] Puedo explicar con mis palabras cómo se calcula cada indicador.
