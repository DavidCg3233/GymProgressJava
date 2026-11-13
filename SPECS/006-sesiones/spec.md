# Spec 006 — Sesiones de entrenamiento

| | |
|---|---|
| **Estado** | **Aprobada** por David el 2026-11-10 |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 |
| **Requisitos de origen** | R-01, R-02, R-04, R-05, R-06 |
| **Depende de** | 002 (una sesión parte de una rutina) |
| **Resuelve** | H-07, H-08, H-09, H-12 |

> Funcionalidad **nueva**: la v1.0 no tiene nada de esto. Es el núcleo del producto y la primera spec que se trabaja.

## 1. Propósito

Hoy la app solo guarda el plan (la rutina). No sabe qué se hizo en el gimnasio, así que no puede mostrar progreso real. Esta spec agrega el registro de cada sesión: qué ejercicios se hicieron y, serie por serie, con cuánto peso y cuántas repeticiones.

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista (David, y las pocas personas a las que les comparta la app).

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-006-01 | **Yo como** deportista **quiero que** la app me deje empezar la sesión de mi rutina de hoy **para** registrar lo que voy haciendo, **en el contexto** de estar en el gimnasio con el celular en la mano, **debe tener el formato** de una lista con los ejercicios de la rutina y sus series previstas. | R-01 | Must |
| HU-006-02 | **Yo como** deportista **quiero que** cada serie quede registrada con el peso y las repeticiones que hice **para** saber exactamente qué logré, **en el contexto** de los segundos de descanso entre series, **debe tener el formato** de una fila por serie con peso y reps, que confirmo con un toque. | R-02, R-04 | Must |
| HU-006-03 | **Yo como** deportista **quiero que** cada serie venga ya llena con lo que hice la última vez en ese ejercicio **para** solo ajustar lo que cambió, **en el contexto** de repetir la misma rutina cada semana, **debe tener el formato** de valores editables ya puestos. | R-05 | Must |
| HU-006-04 | **Yo como** deportista **quiero que** la app me muestre las sesiones que he hecho **para** hacerles seguimiento, **en el contexto** de revisar mi semana o mi mes, **debe tener el formato** de una lista por fecha que al abrirla muestra ejercicios y series. | R-01 | Must |
| HU-006-05 | **Yo como** deportista **quiero que** una sesión que dejé abierta se cierre sola **para** no dañar mi historial si olvido terminarla, **en el contexto** de salir del gimnasio sin abrir la app, **debe tener el formato** de una sesión terminada con lo que alcancé a registrar. | R-06 | Should |
| HU-006-06 | **Yo como** deportista **quiero que** la app me deje empezar una sesión sin rutina **para** registrar un entrenamiento improvisado, **en el contexto** de un día en que no sigo mi plan, **debe tener el formato** de una sesión vacía a la que voy agregando ejercicios y a la que le pongo nombre al terminar. | Decisión 2026-11-09 | Should |
| HU-006-07 | **Yo como** deportista **quiero que** pueda dejar una nota en la sesión **para** recordar cómo me sentí o qué pasó ese día, **en el contexto** de terminar el entrenamiento, **debe tener el formato** de un texto corto opcional. | Decisión 2026-11-09 | Could |
| HU-006-08 | **Yo como** deportista **quiero que** pueda dejar una nota en un ejercicio de la sesión **para** saber qué ajustar la próxima vez, **en el contexto** de acabar ese ejercicio, **debe tener el formato** de un texto corto opcional que veo la siguiente vez que haga ese ejercicio. | Decisión 2026-11-09 | Could |

## 3. Flujos — *Cómo*

**Principal: sesión del día de pecho**
1. Abro la app en el celular. Ya tengo acceso, no me pide contraseña.
2. Veo la rutina que toca hoy ("Pecho") y elijo empezar la sesión.
3. Veo los ejercicios de la rutina. Abro "Press inclinado": tiene 3 series.
4. Cada serie ya trae el peso y las reps de la última vez (por ejemplo 30 kg × 10).
5. Hago la serie 1. Si hice lo mismo, la confirmo con un toque. Si no, cambio el peso o las reps y confirmo. Queda guardada en ese momento.
6. Repito con las series 2 y 3, y con los demás ejercicios.
7. Termino la sesión. Veo un resumen de lo que hice.

**Alternos**
- 2a. Hoy no hay rutina asignada → puedo elegir cualquiera de mis rutinas.
- 2c. Quiero improvisar → empiezo una **sesión libre**, sin ejercicios, y los voy agregando. Al terminar le pongo nombre; si no, queda "Sesión libre".
- 2b. Ya hay una sesión en curso → la app me lleva a ella en vez de crear otra.
- 4a. Es la primera vez que hago ese ejercicio → la serie trae los valores previstos en la rutina.
- 5a. Cierro la app a mitad de sesión → al volver, la sesión sigue en curso con las series ya confirmadas.
- 5c. No hay señal → sigo registrando igual; cada serie queda guardada en el celular y marcada como "pendiente de sincronizar". Cuando vuelve la señal se envía sola.
- 5d. Me equivoqué en una serie ya confirmada → la corrijo mientras la sesión siga en curso.
- 5e. Hice una serie de más o no voy a hacer una → agrego o quito la serie; solo cambia esta sesión, no la rutina.
- 5f. La máquina está ocupada y hago otro ejercicio → lo agrego a esta sesión; la rutina no cambia.
- 5b. No hice una serie → la dejo sin confirmar y no cuenta.
- 5g. Escribo un peso o unas reps fuera de rango → la serie no se confirma y veo el rango permitido.
- 6a. Quiero anotar algo de un ejercicio ("subir peso la próxima") → escribo la nota en ese ejercicio. La próxima vez que lo haga, la veo.
- 7c. Al terminar puedo escribir una nota de la sesión ("dormí mal").
- 7a. Olvido terminar → a las 2 horas de haber empezado, la sesión se termina sola con lo registrado.
- 7b. Termino (o se cierra sola) sin ninguna serie confirmada → la sesión se descarta y no aparece en el historial.

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Historia |
|---|---|---|
| RF-006-01 | Cuando el usuario empieza una sesión a partir de una rutina, el sistema debe crear una sesión con la fecha y hora actuales y con los ejercicios y series previstos en esa rutina. | HU-006-01 |
| RF-006-02 | Mientras el usuario tenga una sesión en curso, el sistema no debe permitir empezar otra y debe llevarlo a la que está en curso. | HU-006-01 |
| RF-006-03 | Cuando el usuario confirma una serie, el sistema debe guardar de inmediato el peso y las repeticiones de esa serie. | HU-006-02 |
| RF-006-04 | El sistema debe presentar cada serie con el peso y las repeticiones que el usuario registró en esa misma serie de ese ejercicio en su sesión más reciente. **Cambiado por la [spec 008](../008-record-y-sesion-a-rutina/spec.md): cada serie viene con la referencia del ejercicio y la última vez queda como pista (RF-008-03).** | HU-006-03 |
| RF-006-05 | Si el usuario nunca ha registrado ese ejercicio, entonces el sistema debe presentar la serie con el peso y las repeticiones previstos en la rutina. **Cambiado por la [spec 008](../008-record-y-sesion-a-rutina/spec.md): viene con la referencia, que sin récord es lo previsto (RF-008-03).** | HU-006-03 |
| RF-006-06 | El sistema debe distinguir a la vista las series confirmadas de las pendientes. | HU-006-02 |
| RF-006-07 | Cuando el usuario termina la sesión, el sistema debe marcarla como terminada, guardar la hora y mostrar un resumen de ejercicios y series hechas. | HU-006-01 |
| RF-006-08 | Cuando pasan 2 horas desde el inicio de una sesión en curso, el sistema debe terminarla conservando las series confirmadas. | HU-006-05 |
| RF-006-09 | El sistema debe mostrar al usuario la lista de sus sesiones terminadas, de la más reciente a la más antigua, con fecha y nombre de la rutina. | HU-006-04 |
| RF-006-10 | Cuando el usuario abre una sesión terminada, el sistema debe mostrar cada ejercicio con sus series, y el peso y las repeticiones de cada una. | HU-006-04 |
| RF-006-11 | El sistema debe conservar las sesiones terminadas tal como se registraron, aunque después la rutina se modifique o se elimine. | HU-006-04 |
| RF-006-12 | Mientras la sesión esté en curso, el usuario debe poder agregar o quitar series de un ejercicio, sin que cambie la rutina. **Cambiado por la [spec 008](../008-record-y-sesion-a-rutina/spec.md): al quitar, las series se numeran seguidas y hay Deshacer (RF-008-08, 09).** | HU-006-02 |
| RF-006-13 | Mientras la sesión esté en curso, el usuario debe poder agregar un ejercicio que no estaba en la rutina; queda en esa sesión y la rutina no cambia. | HU-006-01 |
| RF-006-14 | Mientras la sesión esté en curso, el usuario debe poder corregir el peso y las repeticiones de una serie ya confirmada. Si la sesión está terminada, entonces el sistema no debe permitir cambiar sus series. | HU-006-02 |
| RF-006-15 | Cuando el usuario confirma eliminar una sesión terminada, el sistema debe eliminarla con todas sus series. | HU-006-04 |
| RF-006-16 | Si no hay conexión al confirmar, corregir, agregar o quitar una serie, entonces el sistema debe guardar el cambio en el dispositivo y enviarlo sin intervención del usuario cuando la conexión vuelva. | HU-006-02 |
| RF-006-17 | El sistema debe permitir empezar y terminar una sesión sin conexión, con las rutinas y los valores de la última vez que el dispositivo tenía cuando hubo conexión por última vez. | HU-006-01 |
| RF-006-18 | El sistema debe indicar a la vista si hay registros pendientes de sincronizar. | HU-006-02 |
| RF-006-19 | Si una sesión termina sin ninguna serie confirmada, entonces el sistema debe descartarla. | HU-006-05 |
| RF-006-20 | Cuando el usuario empieza una sesión libre, el sistema debe crear una sesión sin rutina y sin ejercicios, a la que se agregan ejercicios como en RF-006-13. | HU-006-06 |
| RF-006-21 | Cuando el usuario termina una sesión libre, el sistema debe permitirle ponerle un nombre; si lo deja vacío, el sistema debe nombrarla "Sesión libre". | HU-006-06 |
| RF-006-22 | El sistema debe permitir agregar una nota opcional a la sesión, mientras esté en curso o al terminarla, y mostrarla en el historial. | HU-006-07 |
| RF-006-23 | El sistema debe permitir agregar una nota opcional a cada ejercicio de una sesión en curso, y mostrarla en el historial y la siguiente vez que el usuario haga ese ejercicio. | HU-006-08 |
| RF-006-24 | Si el peso o las repeticiones de una serie están fuera del rango o del formato permitido, entonces el sistema debe rechazar la confirmación, conservar lo escrito e indicar el rango permitido. | HU-006-02 |

> RF-006-11 sale de cruzar R-01 con R-03: quieres modificar y eliminar rutinas "según como vea mi progreso", y eso no puede borrar el progreso que estabas mirando.

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla | Valor |
|---|---|---|
| RN-006-01 | Unidad de peso | Kilogramos |
| RN-006-02 | Peso de una serie | De 0 a 500 kg, en múltiplos de 0,5. Decidido 2026-11-09. |
| RN-006-03 | Peso 0 | Significa "peso corporal" (dominadas, fondos) |
| RN-006-04 | Repeticiones de una serie | Entero de 1 a 100 |
| RN-006-05 | Series por ejercicio | De 1 a 10 |
| RN-006-06 | Duración máxima de una sesión en curso | 2 horas desde el inicio (R-06) |
| RN-006-07 | Sesiones por día | Varias; solo una en curso a la vez. Decidido 2026-11-09. |
| RN-006-08 | "Última vez" (para RF-006-04) | La sesión terminada más reciente en la que ese ejercicio tiene esa serie confirmada, **sin importar de qué rutina era**. |
| RN-006-10 | Serie agregada sin antecedente (la 4.ª cuando siempre hice 3) | Viene con los valores de la serie anterior de esa misma sesión |
| RN-006-11 | Ejercicio agregado en vivo | Empieza con 1 serie; si ya lo he hecho antes, con los valores de la última vez. **Cambiado por la [spec 008](../008-record-y-sesion-a-rutina/spec.md): con el récord (RF-008-04).** |
| RN-006-12 | Cierre a las 2 horas sin conexión | Se aplica en el dispositivo; la hora de cierre es inicio + 2 horas |
| RN-006-13 | Dispositivos | Una sesión en curso se registra desde un solo dispositivo. No se resuelven ediciones simultáneas desde dos. Decidido 2026-11-09. |
| RN-006-17 | Hora de cada acción | Cada serie o ejercicio se registra con la hora en que el usuario lo hizo en su celular. Una acción se acepta si ocurrió antes del cierre de la sesión, **aunque llegue al servidor horas después**. Una acción posterior al cierre se rechaza. *(Agregada el 2026-11-10 al construir: sin ella, lo registrado sin señal durante más de 2 horas se perdía al sincronizar.)* |
| RN-006-18 | Sesión vencida y vacía | Una sesión que cumplió sus 2 horas sin series confirmadas deja de mostrarse de inmediato, pero se conserva 24 horas desde la última vez que el celular envió algo de ella, por si aún tiene series por sincronizar. Después se borra. *(Agregada el 2026-11-10.)* |
| RN-006-19 | Cierre del servidor y cierre del celular | Si el servidor cerró la sesión a las 2 horas y después llega el cierre hecho en el celular (con su hora, nombre y nota), vale el del celular. *(Agregada el 2026-11-10.)* |
| RN-006-14 | Notas (de sesión y de ejercicio) | Opcionales, texto de hasta 280 caracteres |
| RN-006-15 | Nombre de una sesión libre | Opcional, hasta 50 caracteres |
| RN-006-16 | "La siguiente vez" de una nota de ejercicio (RF-006-23) | Se muestra la nota de la sesión terminada más reciente que tenga ese ejercicio; si esa no tiene nota, no se muestra ninguna |
| RN-006-09 | Serie no confirmada | No se guarda y no cuenta para récords ni estadísticas |

## 6. Requerimientos no funcionales — *Complementos*

Los generales están en [`rnf.md`](../rnf.md). Aquí solo los propios de esta spec, que vuelven medible el "lo más sencillo posible" de R-04:

| ID | Requerimiento |
|---|---|
| RNF-006-01 | Confirmar una serie sin cambios debe tomar **1 toque**. |
| RNF-006-02 | Confirmar una serie cambiando peso o reps debe tomar **máximo 3 toques**, sin abrir otra pantalla. |
| RNF-006-03 | Desde abrir la app con acceso recordado hasta ver la primera serie de la rutina de hoy: **máximo 2 toques**. |
| RNF-006-04 | Todo el flujo debe poder hacerse con una mano en una pantalla de celular en vertical. |
| RNF-006-05 | Todo el flujo de una sesión (empezar, registrar, corregir, terminar) debe funcionar sin conexión. |
| RNF-006-06 | Ningún registro hecho sin conexión debe perderse al cerrar la app o apagar la pantalla antes de sincronizar. |
| RNF-006-07 | Al volver la conexión, los registros pendientes se sincronizan en menos de 10 segundos con la app abierta. |

## 7. Fuera de alcance — *Complementos*

- Temporizador de descanso entre series.
- Notas por serie y sensación de esfuerzo (RPE).
- Convertir una sesión libre en rutina.
- Compartir o comparar sesiones con otra persona.
- Récords y gráficas de evolución → spec 004.

## 8. Criterios de aceptación — *Pruebas*

Datos base: rutina "Pecho" asignada al lunes, con "Press inclinado" (grupo Pecho), 3 series previstas de 10 reps con 30 kg.

**CA-006-01a** (RF-006-01)
- **Given** hoy es lunes y no tengo sesión en curso
- **When** empiezo la sesión de "Pecho"
- **Then** veo "Press inclinado" con 3 series pendientes.

**CA-006-02a** (RF-006-02)
- **Given** una sesión de "Pecho" en curso
- **When** intento empezar una sesión de otra rutina
- **Then** la app me lleva a la sesión de "Pecho" **y** no se crea otra.

**CA-006-03a** (RF-006-03, RNF-006-01)
- **Given** la serie 1 de "Press inclinado" muestra 30 kg × 10
- **When** la confirmo con un toque
- **Then** queda marcada como confirmada con 30 kg × 10.

**CA-006-03b** (RF-006-03, alterno 5a)
- **Given** confirmé las series 1 y 2
- **When** cierro la app y la abro otra vez 10 minutos después
- **Then** la sesión sigue en curso, las series 1 y 2 están confirmadas y la 3 pendiente.

**CA-006-04a** (RF-006-04) — el caso de R-02 y R-05 · **Reemplazado por CA-008-03a**
- **Given** el lunes pasado registré en "Press inclinado": 30 × 10, 32,5 × 8 y 32,5 × 6
- **When** empiezo hoy la sesión de "Pecho"
- **Then** las tres series vienen con 30 × 10, 32,5 × 8 y 32,5 × 6.

**CA-006-05a** (RF-006-05) · **Reemplazado por CA-008-03b**
- **Given** nunca he registrado "Press inclinado"
- **When** empiezo la sesión de "Pecho"
- **Then** las tres series vienen con 30 × 10.

**CA-006-08a** (RF-006-08)
- **Given** empecé una sesión a las 6:00 p. m. y confirmé 5 series
- **When** abro la app a las 8:01 p. m.
- **Then** la sesión aparece terminada con 5 series **y** puedo empezar una nueva.

**CA-006-10a** (RF-006-09, RF-006-10)
- **Given** terminé la sesión del CA-006-04a cambiando la serie 3 a 32,5 × 7
- **When** abro esa sesión en el historial
- **Then** veo "Press inclinado": 30 × 10, 32,5 × 8, 32,5 × 7.

**CA-006-11a** (RF-006-11)
- **Given** una sesión terminada de "Pecho" con "Press inclinado"
- **When** elimino la rutina "Pecho"
- **Then** la sesión sigue en el historial con su nombre y todas sus series.

**CA-006-12a** (RF-006-12, RN-006-10)
- **Given** "Press inclinado" con 3 series, la tercera confirmada con 32,5 × 6
- **When** agrego una serie
- **Then** aparece la serie 4 con 32,5 × 6 pendiente **y** la rutina "Pecho" sigue teniendo 3 series.

**CA-006-13a** (RF-006-13)
- **Given** una sesión de "Pecho" en curso
- **When** agrego "Aperturas con mancuerna" y confirmo 1 serie de 12 × 12
- **Then** al terminar, el historial muestra ese ejercicio en la sesión **y** la rutina "Pecho" no lo tiene.

**CA-006-14a** (RF-006-14)
- **Given** confirmé la serie 1 con 30 × 10 y la sesión sigue en curso
- **When** la corrijo a 32,5 × 10
- **Then** la serie 1 queda con 32,5 × 10.

**CA-006-14b** (RF-006-14)
- **Given** una sesión terminada
- **When** la abro en el historial
- **Then** no hay forma de cambiar el peso ni las reps de sus series.

**CA-006-15a** (RF-006-15)
- **Given** 3 sesiones en el historial
- **When** elimino una y confirmo
- **Then** quedan 2 **y** sus series ya no cuentan para "la última vez" ni para récords.

**CA-006-16a** (RF-006-16, RF-006-18, RNF-006-06) — sin señal
- **Given** una sesión en curso y el celular en modo avión
- **When** confirmo 3 series, cierro la app, la abro otra vez y quito el modo avión
- **Then** mientras no hay señal veo las 3 series confirmadas con el aviso de pendientes **y** al volver la señal el aviso desaparece **y** las 3 series están en el historial al terminar.

**CA-006-17a** (RF-006-17)
- **Given** abrí la app ayer con conexión y hoy el celular está en modo avión
- **When** empiezo la sesión de "Pecho"
- **Then** veo los ejercicios con los valores de la última vez **y** puedo terminarla sin conexión.

**CA-006-19a** (RF-006-19)
- **Given** empecé una sesión y no confirmé ninguna serie
- **When** la termino
- **Then** no aparece en el historial.

**CA-006-20a** (RF-006-20, RF-006-21)
- **Given** no tengo sesión en curso
- **When** empiezo una sesión libre, agrego "Dominadas", confirmo 1 serie de 0 kg × 8 y termino sin escribir nombre
- **Then** el historial muestra "Sesión libre" con Dominadas: peso corporal × 8.

**CA-006-21a** (RF-006-21)
- **When** termino una sesión libre y escribo "Hotel Bogotá"
- **Then** el historial la muestra como "Hotel Bogotá".

**CA-006-22a** (RF-006-22)
- **When** termino una sesión con la nota "dormí mal"
- **Then** al abrirla en el historial veo "dormí mal".

**CA-006-23a** (RF-006-23, RN-006-16)
- **Given** el lunes pasado dejé en "Press inclinado" la nota "subir a 35"
- **When** empiezo hoy una sesión que tiene "Press inclinado"
- **Then** veo "subir a 35" junto al ejercicio.

**CA-006-24a** (RF-006-24, RN-006-02, RN-006-04) — bordes

| Peso | Reps | Resultado |
|---|---|---|
| 0 | 8 | Se confirma (peso corporal) |
| −0,5 | 8 | Se rechaza: "El peso debe estar entre 0 y 500 kg" |
| 500 | 1 | Se confirma |
| 500,5 | 1 | Se rechaza |
| 30,3 | 10 | Se rechaza: el peso va de a 0,5 kg |
| 30 | 0 | Se rechaza: "Las repeticiones deben estar entre 1 y 100" |
| 30 | 100 | Se confirma |
| 30 | 101 | Se rechaza |
| 30 | 8,5 | Se rechaza: las repeticiones son enteras |
| (vacío) | 10 | Se rechaza |

En cada rechazo, lo escrito sigue en pantalla y la serie queda pendiente.

**CA-006-24b** (RN-006-14)
- **When** escribo una nota de 281 caracteres
- **Then** se rechaza indicando el máximo de 280.

## 9. Preguntas abiertas

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿Sin señal en el gimnasio? | RNF-006-05 | **Sí, debe funcionar sin conexión.** Decidido 2026-11-09. |
| 2 | ¿Agregar o quitar series en vivo? | RF-006-12 | **Sí, agregar y quitar.** Decidido 2026-11-09. |
| 3 | ¿Ejercicio fuera de la rutina? | RF-006-13 | **Sí, solo en esa sesión.** Decidido 2026-11-09. |
| 4 | ¿Corregir una serie ya confirmada? | RF-006-14 | **Solo durante la sesión.** Decidido 2026-11-09. |
| 5 | ¿Eliminar sesiones? | RF-006-15 | **Sí, con confirmación.** Decidido 2026-11-09. |
| 6 | ¿"Última vez" es por ejercicio o por ejercicio dentro de la misma rutina? | RN-006-08 | **Por ejercicio, en cualquier rutina.** Decidido 2026-11-09. |
| 7 | ¿Sesión sin series confirmadas? | Se descarta · Se guarda | **Se descarta.** Decidido 2026-11-09. |
| 8 | ¿Aceptas que una sesión se registre desde un solo dispositivo? | RN-006-13 | **Sí.** Decidido 2026-11-09. |
| 9 | Paso del peso | 0,5 · 1 · 2,5 · libre | **0,5 kg.** Decidido 2026-11-09. |
| 10 | Sesiones por día | Una · Varias | **Varias.** Decidido 2026-11-09. |
| 11 | ¿Sesión libre, sin rutina? | Sí · No | **Sí, y el usuario le pone nombre.** Decidido 2026-11-09. |
| 12 | Valor fuera de rango | Rechazar · Ajustar | **Rechazar con mensaje.** Decidido 2026-11-09. |
| 13 | Extras | Notas, temporizador | **Nota por sesión y nota por ejercicio.** Temporizador fuera de alcance. Decidido 2026-11-09. |

## 10. Checklist antes de aprobar

- [ ] No queda ningún `[DAVID]` ni `[DECIDIR]`.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
- [ ] Leí el flujo principal imaginándome en el gimnasio y no sobra ni falta ningún paso.
- [ ] Puedo explicarle cada requerimiento a alguien que no conoce la app.
