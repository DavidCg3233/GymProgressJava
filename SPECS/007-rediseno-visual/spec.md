# Spec 007 — Rediseño visual

| | |
|---|---|
| **Estado** | **Aprobada** por David el 2026-11-11 |
| **Autor** | David Calambás |
| **Creada** | 2026-11-11 |
| **Requisitos de origen** | R-26 |
| **Depende de** | 006, 002, 004 y 003 (cambia cómo se ven y cómo se navega, no lo que hacen) |

> En este archivo no se nombra ninguna tecnología. Aquí va el **qué** y el **cómo se comprueba**. Los colores, tamaños y componentes exactos están en [`DESIGN.md`](../../DESIGN.md).

## 1. Propósito

La app funciona, pero se ve genérica y todo pesa lo mismo. En el gimnasio, entre series, con una mano y poco tiempo, lo que importa es encontrar el número y acertarle con el pulgar. Esta spec cambia la apariencia y la navegación para que la app sea **calmada en lo visual y densa en los datos**: poco color, sin cajas dentro de cajas, y el peso y las reps como protagonistas.

## 2. Actores e historias de usuario — *Quién*

**Actor:** el deportista.

| ID | Historia | Requisito | Prioridad |
|---|---|---|---|
| HU-007-01 | **Yo como** deportista **quiero que** la app tenga sus secciones siempre al alcance del pulgar **para** moverme sin volver al inicio, **en el contexto** de usarla con una mano, **debe tener el formato** de una barra fija abajo, como las apps del iPhone. | R-26 | Must |
| HU-007-02 | **Yo como** deportista **quiero que** las series se lean como una tabla **para** ver de un vistazo qué hice y qué falta, **en el contexto** de estar entre series, **debe tener el formato** de filas alineadas con el peso y las reps en números grandes. | R-26, R-04 | Must |
| HU-007-03 | **Yo como** deportista **quiero que** la app se vea clara u oscura según mi iPhone **para** que no me deslumbre en un gimnasio oscuro, **en el contexto** de cualquier hora, **debe tener el formato** de los dos temas, cambiando solos. | R-26 | Must |
| HU-007-04 | **Yo como** deportista **quiero que** una sesión en curso siga a la vista aunque mire otra sección **para** volver a ella en un toque, **en el contexto** de consultar mi progreso a mitad de entrenamiento, **debe tener el formato** de una franja sobre la barra con el nombre y el tiempo. | R-26, R-01 | Should |

## 3. Flujos — *Cómo*

**Principal: moverse por la app**
1. Abro la app: veo el Inicio con la barra abajo y su destino marcado.
2. Toco Rutinas, Progreso o Historial: la pantalla cambia y la barra marca el nuevo destino.
3. Empiezo una sesión: la sesión ocupa la pantalla entera, sin la barra, para que nada se toque por error.
4. Toco "Minimizar": vuelvo a la sección donde estaba y la sesión queda en una franja sobre la barra.
5. Toco la franja: vuelvo a la sesión.

**Alternos**
- 1a. Sin señal: todo se ve igual; lo que necesita conexión lo dice, como hoy.
- 3a. Termino la sesión: la franja desaparece y vuelvo al Inicio con el resumen, como hoy.
- 4a. Mi contraseña es temporal: no hay barra hasta que la cambie (RNF-ACC-09).

## 4. Requerimientos funcionales — *Resultado*

| ID | Requerimiento | Origen | Historia |
|---|---|---|---|
| RF-007-01 | Mientras haya acceso vigente, el sistema debe mostrar una barra fija abajo con cuatro destinos (Inicio, Rutinas, Progreso, Historial) y marcar el actual. | NUEVO | HU-007-01 |
| RF-007-02 | Mientras se muestra la sesión en curso, el sistema debe ocultar la barra y ofrecer "Minimizar" para volver a la sección anterior. | NUEVO | HU-007-01 |
| RF-007-03 | Mientras exista una sesión en curso y se muestre otra pantalla, el sistema debe mostrar sobre la barra una franja con el nombre de la sesión y el tiempo desde que empezó, que la abre en un toque. | NUEVO | HU-007-04 |
| RF-007-04 | El sistema debe mostrar el tema claro u oscuro según la configuración del teléfono, y cambiarlo sin recargar cuando el teléfono cambie. | CAMBIA | HU-007-03 |
| RF-007-05 | El sistema debe mostrar las series de un ejercicio como filas alineadas en columnas: número, peso, reps y confirmar. | CAMBIA | HU-007-02 |
| RF-007-06 | El sistema debe distinguir una serie confirmada de una pendiente por su forma y su texto, no solo por el color. | CAMBIA | HU-007-02 |
| RF-007-07 | El sistema debe ofrecer "Cambiar contraseña" y "Salir" desde un botón de cuenta en el encabezado del Inicio. | CAMBIA | HU-007-01 |
| RF-007-08 | El sistema debe ofrecer el catálogo de ejercicios desde la sección Rutinas. | AS-IS | HU-007-01 |

## 5. Reglas de negocio y datos — *Complementos*

| ID | Regla |
|---|---|
| RN-007-01 | La barra tiene siempre los mismos cuatro destinos, en este orden: Inicio, Rutinas, Progreso, Historial. Cada uno con ícono y nombre escrito. |
| RN-007-02 | El tiempo de la franja se muestra en minutos ("35 min") y, desde la primera hora, en horas y minutos ("1 h 05 min"). Se actualiza al menos cada minuto. |
| RN-007-03 | Los números de peso y reps usan cifras de ancho fijo, para que las columnas no se muevan al cambiar un valor. |
| RN-007-04 | Lo que se toca va en tinta (blanco y negro). Un solo color de realce, el dorado, y solo en lo hecho o logrado (serie confirmada, meta cumplida, récords). Los errores y avisos tienen sus propios colores. |

## 6. Requerimientos no funcionales — *Complementos*

| ID | Requerimiento |
|---|---|
| RNF-007-01 | Contraste mínimo de 4,5:1 para todo texto y de 3:1 para íconos y bordes que comunican estado, en los dos temas. |
| RNF-007-02 | Todo lo que se toca mide al menos 44 × 44 puntos, con al menos 8 puntos de separación entre dos objetivos. |
| RNF-007-03 | El rediseño no agrega toques: siguen valiendo RNF-006-01 (1 toque para confirmar sin cambios), RNF-006-02 (máximo 3 con cambios) y RNF-006-03 (máximo 2 hasta la primera serie de hoy). |
| RNF-007-04 | Si el teléfono tiene activado "Reducir movimiento", ninguna transición se anima. |
| RNF-007-05 | El rediseño no agrega descargas externas (letras, íconos ni imágenes de otros sitios): la app sigue abriendo sin señal. |
| RNF-007-06 | En 375 px de ancho no hay desplazamiento horizontal, y la barra respeta la zona inferior del iPhone. |

## 7. Fuera de alcance — *Complementos*

- Cambiar lo que hace la app: reglas, cálculos, textos de error o datos.
- Elegir el tema a mano dentro de la app (sigue al teléfono).
- Cambiar los +/− por un teclado numérico (decidido: se quedan los +/−).
- Animaciones decorativas, sonidos o vibración.
- El ícono de la app en la pantalla de inicio del iPhone.

## 8. Criterios de aceptación — *Pruebas*

**CA-007-01a** (RF-007-01, RN-007-01)
- **Given** tengo acceso vigente y estoy en el Inicio
- **When** toco "Progreso" en la barra
- **Then** veo Progreso **y** la barra marca "Progreso" **y** sigue mostrando los cuatro destinos con su nombre.

**CA-007-02a** (RF-007-02, RF-007-03, RN-007-02)
- **Given** empecé "Pecho" hace 35 minutos
- **When** toco "Minimizar" en la sesión
- **Then** vuelvo a la sección anterior **y** sobre la barra veo "Pecho · 35 min" **y**, al tocarla, vuelvo a la sesión con mis series.

**CA-007-02b** (RF-007-02)
- **Given** estoy en la sesión en curso
- **Then** no veo la barra inferior.

**CA-007-04a** (RF-007-04)
- **Given** la app abierta con el teléfono en tema claro
- **When** cambio el teléfono a tema oscuro
- **Then** la app se ve oscura sin recargar **y** no pierdo lo que estaba escribiendo.

**CA-007-05a** (RF-007-05, RN-007-03)
- **Given** un ejercicio con series de 30 × 10, 32,5 × 8 y 100 × 5
- **Then** los pesos quedan alineados en una columna y las reps en otra, **y** al cambiar 30 por 32,5 la columna no se mueve.

**CA-007-06a** (RF-007-06)
- **Given** una serie confirmada y una pendiente
- **When** veo la pantalla en escala de grises
- **Then** distingo cuál está confirmada por su marca y su texto.

**CA-007-07a** (RF-007-07)
- **Given** estoy en el Inicio
- **When** toco el botón de cuenta
- **Then** veo "Cambiar contraseña" y "Salir", **y** "Salir" sigue avisando si hay cambios sin enviar (RNF-USA-04).

**CA-007-RNF** (RNF-007-01 a 06)
- **Then:**
  - en los dos temas, ningún texto baja de 4,5:1 (medido en cada pantalla);
  - ningún objetivo táctil mide menos de 44 × 44;
  - confirmar una serie sin cambios sigue tomando 1 toque;
  - con "Reducir movimiento" nada se anima;
  - la prueba automática de modo avión (T-006-34) sigue pasando;
  - en 375 px no hay desplazamiento horizontal.

## 9. Preguntas abiertas

*Mientras quede una, la spec no se aprueba.*

| # | Pregunta | Opciones | Decisión |
|---|---|---|---|
| 1 | ¿Estilo? | — | **Minimal y calmado** (2026-11-11). |
| 2 | ¿Tema? | — | **Seguir al iPhone** (2026-11-11). |
| 3 | ¿Navegación? | — | **Barra inferior fija** (2026-11-11). |
| 4 | ¿Letra? | — | **La del iPhone** (2026-11-11). |
| 5 | ¿Cambiar peso y reps? | — | **Botones +/−, como hoy** (2026-11-11). |
| 6 | ¿Referencia? | — | **Hevy o Strong** (2026-11-11). |
| 7 | ¿Color de acento? | Verde pino (aprobado y luego cambiado) | **Blanco y negro con toques dorados** (2026-11-11): el verde pino se veía chillón. Detalle en `DESIGN.md`, sección 2. |

Reglas que definí yo y que puedes cambiar: la sesión oculta la barra y se minimiza a una franja (RF-007-02, 03, como en Hevy); la cuenta pasa a un botón del Inicio (RF-007-07); el formato del tiempo de la franja (RN-007-02). Y una que salió de medir la muestra: el número de la serie va dentro del círculo de confirmar, porque con +/− de 44 px no cabe una columna aparte en 375 px (ver `DESIGN.md`, Fila de serie).

## 10. Checklist antes de aprobar

- [ ] Vi la muestra de la paleta en claro y en oscuro.
- [ ] Estoy de acuerdo con las "reglas que definí yo" o las cambié.
- [ ] No se menciona ninguna tecnología.
- [ ] Cada RF tiene al menos un CA con datos concretos.
