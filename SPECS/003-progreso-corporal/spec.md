# Spec 003 — Progreso corporal

| | |
|---|---|
| **Estado** | En revisión (decisiones tomadas; falta la lectura final de David) |
| **Autor** | David Calambás |
| **Creada** | 2026-11-09 (ingeniería inversa de v1.0) · reescrita el 2026-11-09 con las decisiones del usuario |
| **Requisitos de origen** | R-23 |
| **Depende de** | — |
| **Resuelve** | H-14, H-26 |

## 1. Propósito

Llevar el peso corporal en el tiempo, ver hacia dónde va y cuánto falta para el peso objetivo. El IMC se muestra como dato orientativo.

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista.

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-003-01 | **Yo como** deportista **quiero que** la app guarde mi peso de un día **para** llevar mi historial, **en el contexto** de pesarme en la mañana o en el gimnasio, **debe tener el formato** de un solo número en kilogramos con la fecha de hoy ya puesta. | R-23 | Must |
| HU-003-02 | **Yo como** deportista **quiero que** la app me muestre mi peso actual, mi IMC y cuánto cambió desde el registro anterior **para** saber hacia dónde voy, **en el contexto** de abrir la pantalla de progreso, **debe tener el formato** de tres datos visibles sin desplazarme. | R-23 | Must |
| HU-003-03 | **Yo como** deportista **quiero que** la app me muestre una gráfica de mi peso en el tiempo **para** ver la tendencia y no solo el último dato, **en el contexto** de revisar mi mes, **debe tener el formato** de una línea de peso contra fecha con el peso objetivo marcado. | R-23 | Should |
| HU-003-04 | **Yo como** deportista **quiero que** pueda fijar un peso objetivo **para** saber cuánto me falta, **en el contexto** de definir una meta de subir o bajar, **debe tener el formato** de un número en kilogramos y un texto que diga cuánto falta y en qué dirección. | R-23 | Must |
| HU-003-05 | **Yo como** deportista **quiero que** pueda corregir o borrar un registro mal digitado **para** que mi historial sea confiable, **en el contexto** de notar un error después de guardar, **debe tener el formato** de editar o eliminar desde el historial, con confirmación al eliminar. | R-23 | Must |

## 3. Flujos — *Cómo*

**Registrar peso**
1. Abro "Progreso" y elijo registrar. La fecha viene con el día de hoy.
2. Escribo el peso y guardo.
3. Se actualizan el peso actual, el cambio, el IMC, la gráfica y el historial.

**Alternos**
- 1a. Nunca he escrito mi altura → la app me la pide una vez (se guarda en mi perfil). Sin altura, todo funciona pero el IMC no se muestra.
- 2a. Ya hay un registro en esa fecha → la app avisa y, si confirmo, el nuevo reemplaza al anterior.
- 2b. Peso fuera de rango o fecha futura → se rechaza con el motivo.
- 3a. Corrijo un registro desde el historial → todo se recalcula.
- 3b. Elimino un registro → la app pide confirmación; todo se recalcula.
- Sin ningún registro → la pantalla invita a registrar el primero; no muestra ceros ni guiones.

**Peso objetivo**
1. Escribo mi peso objetivo y guardo.
2. Veo "Te faltan X kg por bajar" o "por subir", o "Objetivo alcanzado".

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-003-01 | Cuando el usuario registra un peso válido con una fecha, el sistema debe agregarlo a su historial. | AS-IS | HU-003-01 |
| RF-003-02 | Si ya existe un registro en esa fecha, entonces el sistema debe pedir confirmación y, si se confirma, reemplazar el anterior. | NUEVO | HU-003-01 |
| RF-003-03 | El sistema debe mostrar como peso actual el del registro con la fecha más reciente. | AS-IS | HU-003-02 |
| RF-003-04 | El sistema debe mostrar la diferencia entre los dos registros más recientes e indicar si subió, bajó o no cambió. | AS-IS | HU-003-02 |
| RF-003-05 | Mientras el usuario tenga una altura registrada, el sistema debe mostrar el IMC del peso actual y su categoría, con la aclaración de que es un dato orientativo. | CAMBIA | HU-003-02 |
| RF-003-06 | El sistema debe mostrar el historial completo, del más reciente al más antiguo, con fecha y peso. | AS-IS | HU-003-03 |
| RF-003-07 | El sistema debe graficar el peso contra la fecha y marcar el peso objetivo si existe. | CAMBIA | HU-003-03 |
| RF-003-08 | Cuando el usuario guarda un peso objetivo válido, el sistema debe mostrar cuántos kilogramos faltan y si es por subir o por bajar. | CAMBIA | HU-003-04 |
| RF-003-09 | Cuando el peso actual iguala o cruza el peso objetivo, el sistema debe indicar que el objetivo se alcanzó. | NUEVO | HU-003-04 |
| RF-003-10 | El usuario debe poder corregir el peso de un registro de su historial. | NUEVO (H-14) | HU-003-05 |
| RF-003-11 | Cuando el usuario confirma eliminar un registro, el sistema debe eliminarlo. | NUEVO (H-14) | HU-003-05 |
| RF-003-12 | El sistema debe guardar la altura del usuario una sola vez, como dato de su perfil, y permitirle cambiarla. | CAMBIA | HU-003-02 |
| RF-003-13 | Si el peso, la altura o la fecha están fuera de rango, entonces el sistema debe rechazarlos, conservar lo escrito e indicar el rango permitido. | NUEVO | HU-003-01 |
| ~~RF-003-xx~~ | ~~Altura en cada registro de peso (v1.0).~~ Eliminado: la altura es del perfil. | — | — |
| ~~RF-003-xx~~ | ~~Gráfica de IMC contra fecha (v1.0).~~ Eliminado: con altura fija es la misma curva del peso. | — | — |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla | Valor |
|---|---|---|
| RN-003-01 | Fórmula del IMC | peso (kg) ÷ altura (m)², redondeado a 1 decimal |
| RN-003-02 | Categorías ([OMS](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)) | menor que 18,5 Bajo peso · de 18,5 a menos de 25 Normal · de 25 a menos de 30 Sobrepeso · 30 o más Obesidad. **La categoría se decide con el IMC sin redondear.** |
| RN-003-03 | Peso corporal | `[PROPUESTA]` de 20,0 a 300,0 kg, con un decimal |
| RN-003-04 | Altura | `[PROPUESTA]` en centímetros, entero de 100 a 250. *(La v1.0 la pedía en metros y aceptaba 175, lo que daba IMC 0.)* |
| RN-003-05 | Fecha | Obligatoria; no puede ser futura |
| RN-003-06 | Registros por día | Uno; uno nuevo en la misma fecha reemplaza al anterior, con confirmación |
| RN-003-07 | Peso objetivo | Uno por usuario, opcional, mismo rango que el peso corporal |
| RN-003-08 | "Objetivo alcanzado" | Si el objetivo es menor que el primer registro: cuando el peso actual es menor o igual al objetivo. Si es mayor: cuando es mayor o igual. |
| RN-003-09 | Texto del IMC | `[PROPUESTA]` "El IMC es orientativo: no distingue músculo de grasa." |

> RN-003-02 corrige un detalle de la v1.0: redondeaba primero y clasificaba después, así que 24,975 se mostraba como 25,0 y caía en "Sobrepeso".

## 6. Requerimientos no funcionales — *Complementos*

Los generales están en [`rnf.md`](../rnf.md). Propio de esta spec:

| ID | Requerimiento |
|---|---|
| RNF-003-01 | Registrar el peso de hoy debe tomar máximo 3 toques además de escribir el número. |
| RNF-003-02 | `[DECIDIR]` ¿Registrar el peso corporal debe funcionar sin conexión, como las sesiones? sí · no hace falta |

## 7. Fuera de alcance — *Complementos*

- Medidas corporales (cintura, pecho, brazo) y porcentaje de grasa.
- Fotos de progreso.
- Fecha límite para el peso objetivo.
- Notas en el registro de peso.

## 8. Criterios de aceptación — *Pruebas*

Datos base: altura 175 cm.

**CA-003-01a** (RF-003-01, 03, 04, 05)
- **Given** mi único registro es 80,0 kg de ayer
- **When** registro 79,0 kg con fecha de hoy
- **Then** el peso actual es 79,0 kg, el cambio es 1,0 kg hacia abajo y el IMC es 25,8 (Sobrepeso) con el texto orientativo.

**CA-003-02a** (RF-003-02)
- **Given** ya registré 79,0 kg hoy
- **When** registro 78,5 kg hoy y confirmo el reemplazo
- **Then** el historial tiene un solo registro de hoy, con 78,5 kg.

**CA-003-05a** (RF-003-05, alterno 1a)
- **Given** no he registrado mi altura
- **When** registro un peso
- **Then** veo el peso y el cambio, y en lugar del IMC una invitación a registrar la altura.

**CA-003-05b** (RN-003-02) — bordes de categoría, con altura 200 cm

| Peso | IMC exacto | Se muestra | Categoría |
|---|---|---|---|
| 73,9 | 18,475 | 18,5 | Bajo peso |
| 74,0 | 18,5 | 18,5 | Normal |
| 99,9 | 24,975 | 25,0 | Normal |
| 100,0 | 25,0 | 25,0 | Sobrepeso |
| 119,9 | 29,975 | 30,0 | Sobrepeso |
| 120,0 | 30,0 | 30,0 | Obesidad |

**CA-003-08a** (RF-003-08)
- **Given** mi peso actual es 79,0 kg
- **When** guardo 75 como peso objetivo
- **Then** veo "Te faltan 4,0 kg por bajar".

**CA-003-09a** (RF-003-09, RN-003-08)
- **Given** primer registro 80,0 kg y objetivo 75,0 kg
- **When** registro 74,8 kg
- **Then** veo "Objetivo alcanzado".

**CA-003-10a** (RF-003-10)
- **Given** un registro de ayer con 97,0 kg que debía ser 79,0
- **When** lo corrijo a 79,0
- **Then** el historial, la gráfica y el cambio usan 79,0.

**CA-003-11a** (RF-003-11)
- **Given** 3 registros
- **When** elimino el más reciente y confirmo
- **Then** quedan 2 **y** el peso actual es el del que ahora es más reciente.

**CA-003-13a** (RF-003-13) — bordes

| Dato | Valor | Resultado |
|---|---|---|
| Peso | 19,9 | Se rechaza |
| Peso | 20,0 | Se acepta |
| Peso | 300,0 | Se acepta |
| Peso | 300,1 | Se rechaza |
| Altura | 99 | Se rechaza |
| Altura | 100 | Se acepta |
| Altura | 250 | Se acepta |
| Altura | 251 | Se rechaza |
| Altura | 1,75 | Se rechaza: va en centímetros |
| Fecha | mañana | Se rechaza |
| Fecha | hoy | Se acepta |

## 9. Preguntas abiertas

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿Entra en la primera versión? | — | **Sí, desde el inicio.** Decidido 2026-11-09. |
| 2 | ¿Altura en cada registro o en el perfil? | — | **Una vez, en el perfil.** Decidido 2026-11-09. |
| 3 | ¿El IMC se queda? | — | **Sí, como dato informativo.** Decidido 2026-11-09. |
| 4 | ¿Registros por día y edición? | — | **Uno por día, editable y eliminable; sin fechas futuras.** Decidido 2026-11-09. |
| 5 | Rangos de peso y altura, y unidad de la altura | RN-003-03, RN-003-04 | `[PROPUESTA]` pendiente de tu sí |
| 6 | ¿Sin conexión? | RNF-003-02 | `[DECIDIR]` |

## 10. Checklist antes de aprobar

- [ ] No queda ningún `[DECIDIR]` ni `[PROPUESTA]`.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
- [ ] Verifiqué a mano dos filas de la tabla de bordes del IMC.
- [ ] Puedo explicarle cada requerimiento a alguien que no conoce la app.
