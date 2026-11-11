# DESIGN.md — GymProgress

| | |
|---|---|
| **Estado** | **Borrador**, va con la [spec 007](SPECS/007-rediseno-visual/spec.md) |
| **Modo** | *Operate*: la persona completa una tarea, con una mano, entre series |
| **Muestra** | [`docs/diseno/muestra.html`](docs/diseno/muestra.html): la paleta y las piezas clave, en claro y en oscuro |

## 1. La idea

**Calmado en lo visual, denso en los datos.** La pantalla casi no tiene color, ni sombras, ni cajas dentro de cajas. Lo que manda es el tamaño: el peso y las reps son lo más grande, el resto se aparta. Un solo color de acento marca lo que se toca y lo que ya está hecho, así que en una pantalla quieta lo importante salta solo.

Referencias: la densidad de **Hevy** y **Strong** (series como filas de una tabla) con la calma y los patrones del **iPhone** (letra del sistema, barra de pestañas, listas agrupadas).

**Anti-referencias:**
- Tarjetas con borde dentro de tarjetas con borde: la app de hoy.
- Degradados, sombras marcadas y vidrio esmerilado decorativo.
- Emojis como íconos.
- Más de un color "de marca".
- Violeta.

## 2. Color

Un solo acento: **verde pino**. Es tranquilo en claro y bien visible en oscuro. En la cabeza se asocia a "hecho" sin gritar como un verde lima, y es distinto del salvia de hoy.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--fondo` | `#F6F6F3` | `#0B0C0D` | Fondo de la pantalla (en oscuro, casi negro: ahorra batería en la pantalla OLED) |
| `--superficie` | `#FFFFFF` | `#161819` | Grupos de filas, barra, hojas |
| `--superficie-2` | `#EFEFEB` | `#202224` | Controles en reposo (los +/−), filas presionadas |
| `--linea` | `#E3E3DE` | `#2A2D30` | Separadores de 1 px entre filas. Nunca como borde de tarjeta |
| `--tinta` | `#16181A` | `#F1F2F0` | Texto y números |
| `--tinta-suave` | `#5E6368` | `#9A9FA4` | Etiquetas, fechas, unidades ("kg", "reps") |
| `--acento` | `#0B7A62` | `#3CCFA8` | Lo que se toca, el destino actual, lo hecho |
| `--sobre-acento` | `#FFFFFF` | `#06231B` | Texto sobre el acento |
| `--acento-tinte` | `#E2F2EC` | `#12302A` | Fondo de una serie confirmada, botón secundario |
| `--error` | `#B42318` | `#FF8B7B` | Errores y eliminar |
| `--aviso` | `#8A5300` | `#F3C350` | "Sin conexión", pendientes |

**Contraste medido** (WCAG): todo texto ≥ 4,5:1 en los dos temas. Los más justos son el acento sobre su tinte en claro (4,6:1) y la tinta suave sobre el fondo en claro (5,6:1).

El tema sigue al teléfono (`prefers-color-scheme`); la barra de estado del iPhone y `theme-color` cambian con él.

## 3. Letra

La del iPhone: `-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif`. Nada se descarga.

| Rol | Tamaño / alto de línea | Peso | Nota |
|---|---|---|---|
| Título grande | 30 / 36 | 700 | Uno por pantalla, arriba a la izquierda, como en iOS |
| Título de grupo | 20 / 26 | 600 | Nombre del ejercicio, "Esta semana" |
| Número protagonista | 24 / 28 | 600 | Peso y reps de una serie, "3 de 4" |
| Cuerpo | 17 / 24 | 400 | El tamaño de texto de iOS |
| Etiqueta | 13 / 18 | 500 | "kg", "reps", fechas, encabezados de columna en mayúsculas pequeñas con 0,04 em de espaciado |
| Barra | 11 / 13 | 500 | Nombre de cada destino |

Todos los números llevan **`font-variant-numeric: tabular-nums`** (RN-007-03), para que las columnas no "bailen". Los campos nunca bajan de 16 px: con menos, Safari hace zoom.

## 4. Espacio, forma y profundidad

- **Rejilla de 4 pt:** 4, 8, 12, 16, 20, 24, 32. El margen lateral es de 16 (12 en la sesión en curso, ver Fila de serie); entre grupos van 24.
- **Radios:** 10 para controles y 14 para grupos. Nada es una píldora, salvo la franja de sesión.
- **Profundidad sin sombras:** la superficie se separa del fondo solo por el color. La barra y la franja llevan un velo de fondo al 85 % con desenfoque, como en iOS, y una línea de 1 px arriba.
- **Objetivos táctiles:** mínimo 44 × 44, con 8 de separación (RNF-007-02).

## 5. Componentes

### Barra inferior (RF-007-01)
- Cuatro destinos iguales: Inicio, Rutinas, Progreso, Historial.
- Ícono de 24 px con trazo de 1,75 y su nombre debajo.
- 49 pt de alto, más la zona inferior del iPhone (`env(safe-area-inset-bottom)`).
- El destino actual va en acento; los demás, en tinta suave.

### Franja de sesión (RF-007-03)
- Va sobre la barra, con 8 de margen.
- Una píldora en `--acento-tinte` con un punto de acento, "Pecho · 35 min" y un chevrón.
- Se toca entera.

### Encabezado
- Título grande a la izquierda y, como mucho, una acción a la derecha (cuenta en el Inicio, "Minimizar" en la sesión).
- Sin línea debajo.

### Grupo de filas
- Superficie con radio de 14 y filas separadas por `--linea`, con 16 de sangría a la izquierda.
- Reemplaza a todas las "tarjetas" de hoy. Un grupo nunca contiene otro grupo.

### Fila de serie (RF-007-05, 06)
Rejilla de tres columnas: `peso 1,2fr | reps 1fr | ✓ 44 px`, con 8 entre columnas y 8 a los lados del grupo. La columna de peso es más ancha porque "32,5" ocupa más que "10". En esta pantalla el margen lateral baja a 12: es la única forma de que los +/− de 44 quepan en 375 px con 8 de separación (RNF-007-02), medido en la muestra. Cada valor es `− número +`, con los +/− de 44 × 44.

- **El número de la serie va dentro del círculo de confirmar:** no hay columna aparte. Con 44 px por botón no caben cinco columnas en 375 px, y así el círculo dice a la vez qué serie es y si está hecha.
- **Encabezado de columnas** en etiqueta: KG · REPS.
- **Pendiente:** los +/− en `--superficie-2` y el círculo con contorno y el número de la serie adentro ("3").
- **Confirmada:**
  - la fila con fondo `--acento-tinte`;
  - el círculo relleno en acento con la palomita en lugar del número;
  - el texto "Hecha" para lectores de pantalla;
  - los +/− se ocultan y solo queda el número. Así se distingue en escala de grises (CA-007-06a).
- **Origen del valor** ("última vez", "de la rutina"): etiqueta debajo del número, en tinta suave.

### Botones
| Tipo | Aspecto | Uso |
|---|---|---|
| Principal | Relleno de acento, texto `--sobre-acento`, 50 de alto, ancho completo | Una sola acción por pantalla: "Empezar Pecho", "Guardar", "Terminar" |
| Secundario | Fondo `--acento-tinte`, texto en acento | "+ Serie", "+ Ejercicio" |
| Texto | Sin fondo, texto en acento | "Editar", "Cancelar" |
| Peligro | Texto en `--error`; relleno solo en la confirmación final | "Eliminar" |

Al presionar, el botón se oscurece un 8 % y baja al 98 % de escala en 100 ms. Sin rebotes.

### Campos
- Fondo `--superficie-2` sin borde, radio de 10 y 44 de alto.
- Etiqueta encima, en el estilo etiqueta.
- El error va debajo del campo, en `--error`.

### Mensajes
- **Sin conexión y pendientes:** una línea con un punto de color `--aviso`, no una caja de color.
- **Errores:** texto en `--error` junto a lo que falló.

### Gráficas
- Línea de 2 px en acento y puntos de 4 px; el elegido, de 6 px y relleno.
- Rejilla con 3 líneas de `--linea`, sin ejes dibujados.
- El objetivo va en línea discontinua en tinta suave.
- Las barras de semanas: en `--superficie-2` y, si cumplen la meta, en acento.

### Estado vacío
Una frase y una acción principal, sin ilustraciones.

## 6. Íconos

Son propios, en SVG dentro de la app (RNF-007-05): trazo de 1,75, extremos redondeados, 24 px. Solo los que hacen falta:
- los cuatro de la barra (casa, lista, gráfica de línea, reloj);
- más, menos, palomita, chevrón, cuenta y minimizar.

## 7. Movimiento

- Todo dura entre 150 y 200 ms, con salida suave (`cubic-bezier(.2,.8,.2,1)`).
- Cambiar de pantalla es un fundido de 150 ms. Confirmar una serie llena el ✓ en 150 ms.
- Nada se anima al hacer desplazamiento, y nada se mueve solo.
- Con "Reducir movimiento", todo es instantáneo (RNF-007-04).

## 8. Cómo se comprueba

- Contraste medido en cada pantalla, en los dos temas.
- Recorrido a 375 px en claro y en oscuro.
- La prueba automática de modo avión (T-006-34) sigue pasando.
- Toques contados para confirmar una serie (RNF-007-03).
