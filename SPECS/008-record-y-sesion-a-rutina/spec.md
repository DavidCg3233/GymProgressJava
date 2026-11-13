# Spec 008 — El récord manda y la sesión se vuelve rutina

| | |
|---|---|
| **Estado** | **Aprobada** por David el 2026-11-13 |
| **Autor** | David Calambás |
| **Creada** | 2026-11-13 |
| **Requisitos de origen** | R-27, R-28, R-29 |
| **Depende de** | 006 (sesiones), 002 (rutinas), 004 (récord, RN-004-03) |
| **Cambia** | RF-006-04, RF-006-05, RN-006-11 y sus criterios CA-006-04a, 05a (sección 9) |

> En este archivo no se nombra ninguna tecnología. Aquí va el **qué** y el **cómo se comprueba**.

## 1. Propósito

**Lo que manda son los ejercicios; las rutinas solo los agrupan.** Hoy cada rutina guarda sus propios pesos y no se entera de lo que haces en otra. Así hay que ir a buscar en qué rango de peso estás. Esta spec hace que el récord de cada ejercicio sea la referencia en todas partes. También permite convertir una buena sesión en rutina sin rehacerla, y corrige dos molestias de la sesión: la numeración de series y el buscador que se traba en el iPhone.

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista.

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-008-01 | **Yo como** deportista **quiero que** al poner un ejercicio en una rutina aparezca mi récord **para** no tener que buscar en qué rango de peso estoy, **en el contexto** de armar o editar una rutina, **debe tener el formato** de "Récord: 80 kg × 5" junto al ejercicio. | R-27 | Must |
| HU-008-02 | **Yo como** deportista **quiero que** mis rutinas se actualicen solas cuando supero mi récord **para** que el jueves no me proponga lo que ya superé el martes, **en el contexto** de tener el mismo ejercicio en varias rutinas, **debe tener el formato** del peso y las reps nuevos en la rutina y en la sesión. | R-27 | Must |
| HU-008-03 | **Yo como** deportista **quiero que** una sesión que me gustó se pueda guardar como rutina **para** no volver a armarla desde cero, **en el contexto** de terminar una sesión libre o revisar el historial, **debe tener el formato** de "Guardar como rutina" con nombre y días, o "Actualizar una rutina". | R-28 | Must |
| HU-008-04 | **Yo como** deportista **quiero que** las series se numeren seguidas y que quitar una por error tenga arreglo **para** no confundirme ni perder lo registrado, **en el contexto** de tocar rápido entre series, **debe tener el formato** de 1, 2, 3… siempre seguidos y un "Deshacer". | R-29 | Must |
| HU-008-05 | **Yo como** deportista **quiero que** escribir el nombre de un ejercicio sea fluido en el iPhone **para** agregarlo rápido, **en el contexto** de una sesión en curso, **debe tener el formato** de sugerencias que aparecen mientras escribo, sin tirones. | R-29 | Must |

## 3. Flujos — *Cómo*

**A. Armar una rutina con el récord a la vista**
1. En el editor agrego "Press inclinado".
2. Junto al ejercicio veo "Récord: 80 kg × 5", y peso y reps vienen propuestos con esos valores.
3. Los cambio si quiero y guardo.

**B. El récord sube y las rutinas se enteran**
1. El martes, en "Brazos", confirmo curl de bíceps 10 kg × 20. Mi récord era 10 kg × 18.
2. El récord pasa a 10 kg × 20 al instante, aunque no haya señal.
3. La rutina del jueves, que tenía previsto 10 kg × 18, ahora muestra 10 kg × 20.
4. Al empezar la sesión del jueves, las series vienen con 10 kg × 20 y, debajo, "última vez: 10 × 18".

**C. Guardar una sesión como rutina**
1. Termino una sesión libre: en el resumen toco "Guardar como rutina".
2. Elijo **Rutina nueva**, escribo nombre y días, y veo la lista de ejercicios que va a tener.
3. Guardo: la rutina queda con los ejercicios en el orden de la sesión, las series que confirmé y mi mejor serie de cada uno.
4. Alterno 2a: elijo **Actualizar una rutina** y la escojo. Veo la lista de cambios: ejercicios que se agregan y valores que mejoran. Confirmo.
5. Alterno 1a: lo mismo desde el detalle de una sesión en el historial.
6. Alterno 3a: sin señal, la app lo dice y conserva lo escrito.

**D. Quitar una serie**
1. Tengo las series 1, 2 y 3; quito la 2.
2. Quedan 1 y 2 (la que era 3 pasa a ser 2), y aparece "Serie quitada · Deshacer" durante unos segundos.
3. Si agrego otra, sale como la 3.

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-008-01 | Cuando el usuario agrega a una rutina un ejercicio que tiene récord, el sistema debe mostrar ese récord junto al ejercicio y proponer su peso y sus reps como previstos. | NUEVO | HU-008-01 |
| RF-008-02 | El sistema debe mostrar en cada ejercicio de una rutina su **referencia** (RN-008-03): el récord del ejercicio si supera lo previsto, o lo previsto si no. | NUEVO | HU-008-02 |
| RF-008-03 | Cuando el usuario empieza una sesión desde una rutina, el sistema debe precargar cada serie con la referencia del ejercicio y mostrar, si existe, la última vez de esa serie como pista. | CAMBIA (RF-006-04, 05) | HU-008-02 |
| RF-008-04 | Cuando el usuario agrega un ejercicio en vivo, el sistema debe precargar su primera serie con el récord del ejercicio, si lo tiene. | CAMBIA (RN-006-11) | HU-008-02 |
| RF-008-05 | Cuando el usuario confirma una serie que supera el récord de ese ejercicio, el sistema debe actualizar el récord en el momento, también sin conexión, y todas las rutinas que lo tienen deben mostrarlo. | NUEVO | HU-008-02 |
| RF-008-06 | Desde el resumen al terminar una sesión y desde el detalle de una sesión del historial, el usuario debe poder guardarla como **rutina nueva**, con nombre y días. | NUEVO | HU-008-03 |
| RF-008-07 | Desde los mismos lugares, el usuario debe poder **actualizar una rutina existente** con la sesión: se agregan los ejercicios que no tenía y mejoran los que la sesión superó, sin quitar nada. Antes de guardar, el sistema muestra la lista de cambios. | NUEVO | HU-008-03 |
| RF-008-08 | Cuando el usuario quita una serie, el sistema debe volver a numerar las restantes de forma seguida, y la siguiente que se agregue debe llevar el número que sigue. | CAMBIA (RF-006-12) | HU-008-04 |
| RF-008-09 | Cuando el usuario quita una serie, el sistema debe ofrecer deshacerlo durante 5 segundos. | NUEVO | HU-008-04 |
| RF-008-10 | Mientras el usuario escribe el nombre de un ejercicio, el sistema debe sugerir los del catálogo que coinciden, y tocar uno lo elige con su grupo. | CAMBIA (RF-002-08) | HU-008-05 |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla |
|---|---|
| RN-008-01 | **Récord** de un ejercicio: el de RN-004-03 (mayor peso; con el mismo peso, más reps; si siguen empatados, el más antiguo). En peso corporal, el de más reps. Es uno solo por ejercicio, sin importar la rutina. |
| RN-008-02 | **"Supera"**: con la misma regla. Más peso supera, sin importar las reps. Con el mismo peso, más reps supera. Ejemplos: 2 kg × 18 supera a 1 kg × 20; 10 kg × 20 supera a 10 kg × 18; 10 kg × 18 **no** supera a 10 kg × 20. |
| RN-008-03 | **Referencia** de un ejercicio en una rutina: lo previsto en la rutina, reemplazado por el récord **solo si el récord lo supera** (RN-008-02). Las series previstas no cambian. |
| RN-008-04 | **Nada guardado se sobreescribe solo.** La rutina conserva lo que escribiste; la referencia se calcula al mostrar. Solo cambia lo guardado cuando guardas una rutina (editor, "Guardar como rutina" o "Actualizar"). |
| RN-008-05 | **Sesión → rutina nueva:** cada ejercicio con al menos una serie confirmada entra en el orden de la sesión. Series previstas: las confirmadas de ese ejercicio (de 1 a 10). Peso y reps: su mejor serie de esa sesión (RN-008-01). Si el mismo ejercicio aparece dos veces, queda una vez, con sus series sumadas (máximo 10) y la mejor serie de las dos. |
| RN-008-06 | **Sesión → rutina nueva** cumple las reglas de una rutina (RN-002-01 a 04): nombre único de 1 a 50 caracteres y máximo 20 ejercicios. El nombre se propone igual al de la sesión, salvo "Sesión libre". Con más de 20 ejercicios se rechaza y se dice cuántos sobran. |
| RN-008-07 | **Actualizar una rutina:** los ejercicios nuevos se agregan al final, en el orden de la sesión, con los valores de RN-008-05. Los que ya estaban toman peso y reps de la sesión solo si su mejor serie supera lo previsto (RN-008-02). Ningún ejercicio se quita y las series previstas no cambian. Si al sumar pasa de 20 ejercicios, se rechaza y se dice cuántos sobran. |
| RN-008-08 | **Numeración:** al quitar una serie, las restantes conservan su orden y sus valores, y se numeran 1, 2, 3… sin huecos. |
| RN-008-09 | **Deshacer** devuelve la serie quitada a su lugar, con su número y sus valores, también si estaba confirmada. |
| RN-008-10 | **Sugerencias:** coinciden sin importar mayúsculas ni tildes. Primero los que empiezan por lo escrito y luego los que lo contienen, máximo 6. Desde la primera letra. |

## 6. Requerimientos no funcionales — *Complementos*

| ID | Requerimiento |
|---|---|
| RNF-008-01 | En el iPhone, cada letra aparece en el campo al escribirla, sin tirones, también con el catálogo completo de 40 ejercicios o más. Se comprueba en el iPhone de David. |
| RNF-008-02 | El récord, la referencia y la precarga funcionan sin conexión, con lo que el celular trajo la última vez (como RF-006-17). |
| RNF-008-03 | Guardar o actualizar una rutina desde una sesión requiere conexión (como RNF-002-01). Sin ella, el sistema lo dice y conserva lo escrito. |
| RNF-008-04 | Esta spec no borra ni modifica ningún dato ya guardado: ni sesiones, ni series, ni rutinas, salvo lo que el usuario guarda a propósito (RN-008-04). |
| RNF-008-05 | "Quitar" no está en la misma fila que "Confirmar": queda en otra zona de la serie, a 16 px o más. |

## 7. Fuera de alcance — *Complementos*

- Cambiar la definición de récord de la spec 004.
- Quitar ejercicios de una rutina al actualizarla (decidido: se suma y se mejora, no se borra).
- Una referencia distinta por serie (todas las series previstas de un ejercicio usan la misma referencia).
- Temporizador de descanso.

## 8. Criterios de aceptación — *Pruebas*

**CA-008-01a** (RF-008-01)
- **Given** mi récord de "Press inclinado" es 80 kg × 5
- **When** agrego "Press inclinado" a la rutina "Miércoles"
- **Then** veo "Récord: 80 kg × 5" **y** peso y reps vienen en 80 y 5.

**CA-008-02a** (RF-008-02, RF-008-05, RN-008-02, 03) — el caso de R-27
- **Given** "Curl con barra" está en "Brazos" (martes) y en "Jueves" con 10 kg × 18 previstos, y mi récord es 10 kg × 18
- **When** el martes confirmo 10 kg × 20
- **Then** el récord pasa a 10 kg × 20 **y** "Jueves" muestra 10 kg × 20, aunque lo guardado en ella siga siendo 10 × 18.

**CA-008-02b** (RN-008-02) — el peso manda
- **Given** previstos 1 kg × 20
- **When** mi récord pasa a 2 kg × 18
- **Then** la referencia es 2 kg × 18.

**CA-008-02c** (RN-008-03)
- **Given** previstos 12 kg × 10 y récord 10 kg × 20
- **Then** la referencia sigue en 12 kg × 10 (el récord no la supera).

**CA-008-03a** (RF-008-03) — reemplaza CA-006-04a
- **Given** la referencia de "Press inclinado" en "Pecho" es 32,5 kg × 8, y la última vez hice 30 × 10, 32,5 × 8 y 32,5 × 6
- **When** empiezo "Pecho"
- **Then** las tres series vienen con 32,5 × 8 **y** debajo de cada una veo su última vez: 30 × 10, 32,5 × 8 y 32,5 × 6.

**CA-008-03b** (RF-008-03) — reemplaza CA-006-05a
- **Given** nunca he registrado "Press inclinado" y la rutina lo prevé en 30 × 10
- **When** empiezo "Pecho"
- **Then** las tres series vienen con 30 × 10, sin pista de última vez.

**CA-008-04a** (RF-008-04)
- **Given** mi récord de "Dominadas" es peso corporal × 12
- **When** agrego "Dominadas" en una sesión libre
- **Then** su primera serie viene con 0 kg × 12.

**CA-008-05a** (RF-008-05, RNF-008-02) — sin señal
- **Given** el celular en modo avión y mi récord de "Sentadilla" en 60 × 6
- **When** confirmo 62,5 × 6 y luego abro "Mis rutinas"
- **Then** las rutinas con "Sentadilla" muestran 62,5 × 6.

**CA-008-06a** (RF-008-06, RN-008-05, 06)
- **Given** una sesión libre con Sentadilla (60 × 8, 70 × 6, 70 × 5) y Prensa (120 × 10, 120 × 10)
- **When** la guardo como rutina nueva "Pierna B" para el sábado
- **Then** "Pierna B" tiene Sentadilla con 3 series de 70 × 6 y Prensa con 2 series de 120 × 10, en ese orden, asignada al sábado.

**CA-008-06b** (RN-008-06)
- **Given** ya existe una rutina "Pierna B"
- **When** intento guardar otra sesión con ese nombre
- **Then** se rechaza indicando que el nombre ya existe, y lo escrito se conserva.

**CA-008-07a** (RF-008-07, RN-008-07)
- **Given** "Pierna" tiene Sentadilla (3 × 65 kg × 6) y Curl femoral (3 × 30 × 12), y la sesión tiene Sentadilla (mejor 70 × 6) y Prensa (2 series, mejor 120 × 10)
- **When** actualizo "Pierna" con esa sesión
- **Then** antes de guardar veo: "Prensa se agrega", "Sentadilla mejora a 70 × 6", "Curl femoral queda igual"; **y** al confirmar, "Pierna" tiene Sentadilla 3 × 70 × 6, Curl femoral 3 × 30 × 12 y Prensa 2 × 120 × 10.

**CA-008-08a** (RF-008-08, RN-008-08) — el caso de R-29
- **Given** un ejercicio con series 1, 2 y 3
- **When** quito la 2 y agrego una serie
- **Then** veo las series 1, 2 y 3, donde la 2 es la que antes era la 3 y la 3 es la nueva.

**CA-008-09a** (RF-008-09, RN-008-09)
- **Given** quité por error la serie 2, que estaba confirmada con 32,5 × 8
- **When** toco "Deshacer" antes de 5 segundos
- **Then** vuelve como serie 2, confirmada, con 32,5 × 8.

**CA-008-10a** (RF-008-10, RN-008-10)
- **When** escribo "pr" al agregar un ejercicio
- **Then** las sugerencias empiezan por "Press de banca", "Press inclinado"… (los que empiezan por "pr") **y**, al tocar "Press inclinado", queda elegido con su grupo "Pecho".

**CA-008-RNF** (RNF-008-01 a 05)
- **Then:**
  - en el iPhone, escribir "Press inclinado" no se traba;
  - CA-008-05a pasa en modo avión;
  - guardar una sesión como rutina sin señal avisa y no pierde lo escrito;
  - después de todo el recorrido, las sesiones y rutinas que ya existían siguen iguales;
  - "Quitar" no está en la fila de "Confirmar".

## 9. Lo que cambia en otras specs

| Spec | Antes | Ahora |
|---|---|---|
| 006 · RF-006-04 | Cada serie viene con lo que hice en esa serie la última vez | Viene con la referencia del ejercicio (RF-008-03); la última vez queda como pista debajo |
| 006 · RF-006-05 | Sin historial, viene con lo previsto | Viene con la referencia, que sin récord es lo previsto (igual en la práctica) |
| 006 · RN-006-11 | Ejercicio en vivo: con la última vez | Con el récord (RF-008-04) |
| 006 · CA-006-04a, 05a | — | Reemplazados por CA-008-03a y 03b |
| 006 · RF-006-12 | Agregar o quitar series | Igual, más la numeración seguida y "Deshacer" (RF-008-08, 09) |
| 002 · RF-002-08 | Sugerencias del catálogo | Con la lista propia de RF-008-10 |

## 10. Preguntas abiertas

*Mientras quede una, la spec no se aprueba.*

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿La sesión se precarga con el récord o con la última vez? | — | **Con el récord**, y la última vez como pista (2026-11-13). |
| 2 | ¿La rutina toma el récord siempre? | — | **Solo si supera lo previsto** (2026-11-13). |
| 3 | ¿Desde dónde se guarda una sesión como rutina? | — | **Al terminar y desde el historial** (2026-11-13). |
| 4 | ¿Actualizar una rutina reemplaza o suma? | — | **Suma y mejora, sin borrar** (2026-11-13). |
| 5 | **Serie pesada de prueba.** Con la regla del peso, una serie de 80 kg × 2 **supera** a 70 kg × 10 previsto, así que la rutina pasaría a 80 × 2. La respuesta 2 no lo evita (corrección de la IA del 2026-11-13). ¿Qué hacemos? | **a)** Aceptarlo y corregir a mano en el editor cuando pase · **b)** Para la referencia de una rutina, el récord solo cuenta series con al menos las reps previstas menos 3 (70 × 10 previsto: solo cuentan series de 7 reps o más) · **c)** Otra regla que propongas | **a) Aceptarlo:** si pasa, se corrige a mano en el editor (2026-11-13). |

Reglas que definí yo y que puedes cambiar: "Deshacer" dura 5 segundos (RN-008-09); máximo 6 sugerencias (RN-008-10); si un ejercicio sale dos veces en una sesión, sus series se suman (RN-008-05); al actualizar, los ejercicios nuevos van al final (RN-008-07).

## 11. Checklist antes de aprobar

- [x] Respondí la pregunta 5.
- [ ] Revisé a mano CA-008-06a: la mejor serie de Sentadilla es 70 × 6 (70 le gana a 60; entre los de 70, 6 reps le gana a 5).
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
