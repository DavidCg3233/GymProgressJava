# Plan 007 — Rediseño visual

| | |
|---|---|
| **Estado** | **Aprobado** por David el 2026-11-11 |
| **Spec** | [spec.md](spec.md) (Aprobada el 2026-11-11) · [DESIGN.md](../../DESIGN.md) (Aprobado el 2026-11-11) |
| **Stack** | El de siempre: Vue 3 con su CSS, sin librerías nuevas |
| **Creado** | 2026-11-11 |

## 1. Resumen técnico

Solo cambia la pantalla: el servidor, la base, las reglas, la cola sin conexión y el estado del celular **no se tocan**. Tres piezas:

1. **Fichas de diseño** (los colores, tamaños y radios de `DESIGN.md`) como variables de CSS en un solo archivo, con su versión oscura. Todas las pantallas las usan; ninguna escribe un color a mano.
2. **Navegación nueva:** una barra inferior y una franja de sesión, decididas por dos funciones puras con pruebas: a qué destino pertenece cada vista y cómo se escribe el tiempo de la sesión.
3. **Cada pantalla, rehecha** con los componentes de `DESIGN.md`. Se conserva cada texto y cada nombre accesible que usan las pruebas.

## 2. Chequeo contra la constitución

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1. La spec va primero | Sí | Cada tarea nombra sus `RF-007-xx`. |
| P2. Nada que nadie pidió | Sí | Nada nuevo fuera de la spec y `DESIGN.md`. |
| P3. RNF de seguridad | Sí | No cambia nada del servidor; la política de contenido sigue igual (los íconos van dentro del código, nada externo). |
| P4. Cada requerimiento tiene su prueba | Sí, con una parte a mano | Sección 6. Lo que es puro juicio visual va en el recorrido a mano. |
| P5. Reglas de negocio solas | Sí | Las dos reglas nuevas (destino de cada vista, formato del tiempo) son funciones puras con pruebas. |
| P6. David entiende lo que se entrega | Depende de ti | Bitácora de `tasks.md`. |

## 3. Qué hay hoy y qué cambia

| Pieza | Hoy | Después |
|---|---|---|
| Colores | `--color-*` en `estilos/base.css`, verde salvia | Las fichas de `DESIGN.md` (`--fondo`, `--tinta`, `--acento`…), verde pino, en claro y oscuro |
| Navegación | Botones en el Inicio y "Volver" en cada pantalla | Barra inferior con 4 destinos; "Volver" solo dentro de una sección (editor, catálogo, evolución) |
| Sesión en curso | Pantalla con "Inicio" para salir | Pantalla completa sin barra, con "Minimizar"; fuera de ella, la franja |
| Cuenta | "Cambiar contraseña" y "Salir" al pie del Inicio | Botón de cuenta en el encabezado del Inicio |
| Serie | Tarjeta con `− 0 kg +` y un ✓ aparte | Fila de tres columnas; el número de la serie dentro del círculo de confirmar |
| Tarjetas | Borde en todo, tarjetas dentro de tarjetas | Grupos de filas sin borde, separados por líneas |
| `theme-color` | Uno fijo | Uno para claro y otro para oscuro (`media`) |

## 4. Diseño

### 4.1 Fichas

`estilos/fichas.css` define en `:root` las fichas de `DESIGN.md` y su versión oscura en `@media (prefers-color-scheme: dark)`. Cambiar el tema del teléfono cambia las variables y todo se repinta sin recargar (CA-007-04a). Las clases comunes (`.grupo`, `.fila`, `.boton--principal`…) pasan a `estilos/base.css`, reescrito sobre las fichas.

Una prueba lee los dos bloques de fichas y **mide el contraste** de cada par de texto (RNF-007-01). Si alguien cambia un color y baja de 4,5:1, falla la revisión automática.

### 4.2 Navegación

- `navegacion/destinos.js`:
  - `DESTINOS`, los cuatro de RN-007-01, en orden;
  - `destinoDe(vista)`: a qué destino pertenece cada vista. El editor y el catálogo son de Rutinas; la evolución, de Progreso; cambiar la contraseña, de Inicio. Sirve para marcar el destino actual.
- `navegacion/tiempo.js`: `tiempoDeSesion(inicio, ahora)` → "35 min", "1 h 05 min" (RN-007-02).
- `App.vue` guarda `vistaAnterior`: "Minimizar" vuelve ahí (RF-007-02).
- `BarraInferior.vue` se muestra con acceso vigente y fuera de la sesión (RF-007-01, 02).
- `FranjaDeSesion.vue` se muestra con sesión en curso y fuera de ella; recalcula el tiempo cada 30 segundos (RF-007-03).

### 4.3 Componentes

| Componente | Qué es | Reemplaza |
|---|---|---|
| `Icono.vue` | Los íconos de `DESIGN.md` en SVG, por nombre | Los caracteres "✓", "✕", "›" |
| `Encabezado.vue` | Título grande, subtítulo y una acción | Los `<header class="fila">` de cada pantalla |
| `BarraInferior.vue`, `FranjaDeSesion.vue` | Sección 4.2 | Los botones del Inicio |
| `MenuDeCuenta.vue` | Hoja con "Cambiar contraseña" y "Salir" (con su aviso de pendientes) | El pie del Inicio |
| `FilaDeSerie.vue` (rehecho) | Rejilla de tres columnas y el círculo con el número | El actual |
| `PasoNumerico.vue` (rehecho) | `− número +` con botones de 44 y cifras de ancho fijo | El actual |

### 4.4 Lo que no cambia

- Los **nombres accesibles** que usan las pruebas: "Confirmar serie N", "Serie N confirmada", "+ Serie", "+ Ejercicio", "Terminar sesión", "Empezar sesión libre", los campos "kg" y "reps", y el saludo "Hola…".
- La franja se anuncia como "Continuar sesión: Pecho, 35 min", así que la prueba de modo avión la sigue encontrando.
- Los textos de error y de aviso: los rehace el rediseño visual, no su redacción.

## 5. Decisiones técnicas

| Decisión | Alternativas | Por qué esta |
|---|---|---|
| Variables de CSS con `prefers-color-scheme` | Clase de tema puesta por código | El tema sigue al teléfono sin código y cambia en vivo |
| Íconos propios en SVG dentro del código | Una librería de íconos | 10 íconos no justifican una dependencia; nada externo (RNF-007-05) |
| Renombrar las variables viejas en vez de convivir con ellas | Dejar los `--color-*` como alias | Dos nombres para lo mismo se mezclan para siempre; una prueba impide que vuelvan |
| Navegación con la `vista` de hoy, más la barra | Un enrutador de páginas | La app no tiene direcciones que compartir; el estado de hoy funciona y está probado |
| Medir toques y tamaños en la prueba de Playwright | Medirlos a mano | Así ningún cambio futuro baja un botón de 44 sin que se note |

## 6. Estrategia de pruebas

| Criterios | Tipo | Dónde |
|---|---|---|
| RN-007-01 (destinos), RN-007-02 (tiempo) | Unitaria | `frontend/src/navegacion` |
| RNF-007-01 (contraste en los dos temas) | Unitaria, leyendo las fichas | `frontend/src/estilos` |
| Ninguna variable `--color-*` vieja ni colores escritos a mano en las pantallas | Unitaria, leyendo los archivos | `frontend/src/estilos` |
| RNF-007-02 (44 px y 8 de separación), RNF-007-03 (1 toque para confirmar), CA-007-02a y 02b | Flujo completo en WebKit | `frontend/e2e` |
| RNF-007-04 y 05, CA-007-04a (tema en vivo), 05a, 06a, 07a | Recorrido a mano a 375 px, en claro y en oscuro | Bitácora |
| Que nada se rompa | Toda la suite de siempre más la prueba de modo avión (T-006-34) | Revisión automática |

## 7. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| El iPhone instalado pinta la barra de estado con el color equivocado en un tema | Media | Dos `theme-color` con `media`. Si iOS no los respeta en modo instalado, se deja la barra de estado transparente y la app pinta su propio fondo. Se revisa en tu iPhone (T-007-17). |
| El rediseño rompe un nombre accesible y una prueba deja de encontrar un botón | Media | Las pruebas fallan en la revisión antes de fusionar; la sección 4.4 lista los nombres que no se tocan. |
| 375 px queda justo para la fila de serie | Baja | Medido en la muestra; una prueba en WebKit lo vuelve a medir. |
| Rediseñar 11 pantallas lleva días | Alta | Se fusiona por partes: base y navegación primero, luego las pantallas por grupos. La app nunca queda a medias en `main`. |

## 8. Orden de construcción

1. **Base:** fichas, prueba de contraste, íconos, encabezado.
2. **Navegación:** destinos, tiempo, barra, franja, minimizar, menú de cuenta.
3. **Pantallas,** en orden de uso: sesión en curso, inicio, progreso y peso, rutinas y catálogo, historial, acceso.
4. **Cierre:** medidas en WebKit, recorrido en claro y oscuro, tu iPhone.

El detalle está en [`tasks.md`](tasks.md).
