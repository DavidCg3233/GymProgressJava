# Visión de producto

> Para quién es GymProgress, qué problema resuelve y qué **no** va a hacer. Es el filtro para decidir si un requerimiento entra.
>
> **Estado:** Borrador · llenado el 2026-11-09 con lo que dijo el usuario en [`SPECS/requirements.md`](../SPECS/requirements.md). Lo marcado `[DAVID]` falta.

## 1. El problema

Voy al gimnasio 4 días por semana con rutinas por día. La v1.0 solo guardaba el plan, así que no sabía qué había hecho de verdad ni si estaba progresando. Además era una app de escritorio y yo entreno con un iPhone en la mano.

`[DAVID]` ¿Cómo lo resuelves hoy (notas, memoria, tu registro de pesos) y qué te falla de eso?

## 2. Usuario

| | |
|---|---|
| ¿Quién la usa? | David. Más adelante, pocas personas cercanas por invitación (R-10). |
| ¿Cuándo? | Durante el entrenamiento, entre series. |
| ¿En qué dispositivo? | iPhone, en el navegador (R-07). |
| ¿Cuánto tiempo tiene? | Segundos: el descanso entre series. Por eso registrar una serie es 1 toque (R-04). |

## 3. Propuesta de valor

> Para **quien entrena con rutinas** y **quiere saber si está progresando**, GymProgress es **una app web para el celular** que **registra cada serie con su peso y sus reps en un toque**. A diferencia de `[DAVID: lo que usas hoy]`, GymProgress **trae puesto lo que hiciste la última vez y guarda el historial real de cada sesión**.

## 4. Objetivos y cómo se miden

| # | Objetivo | Métrica | Meta |
|---|---|---|---|
| 1 | Registrar sin interrumpir el entrenamiento | Toques para confirmar una serie | 1 sin cambios, máximo 3 con cambios |
| 2 | Entrar sin fricción | Tiempo desde abrir la app hasta ver la rutina de hoy | Máximo 2 segundos, sin contraseña durante 7 días |
| 3 | Usarla de verdad | Sesiones registradas por semana | `[DAVID]` *(tu meta de gimnasio es 4 por semana)* |

## 5. Alcance

| Capacidad | ¿Entra? | Spec |
|---|---|---|
| Registrar sesiones: series con peso y reps | **Sí, núcleo** | 006 |
| Crear, modificar y eliminar rutinas por día de la semana | Sí | 002 |
| Catálogo de ejercicios y grupos musculares | Sí | 002 |
| Ver progreso por ejercicio y récords reales | Sí | 004 |
| Acceso con correo y contraseña, recordado 7 días | Sí (RNF) | rnf.md |
| Peso corporal, IMC y peso objetivo | `[DECIDIR]` | 003 (en espera) |
| Datos personales más allá de un nombre | `[DECIDIR]` | — |

## 6. Fuera de alcance

- Registro público, redes sociales, compartir rutinas o compararse con otros.
- App nativa en tiendas de aplicaciones.
- Planes de entrenamiento prediseñados, recomendaciones o inteligencia artificial dentro de la app.
- Nutrición, calorías, sueño.
- `[DAVID]` agrega lo que se te ocurra y **no** quieras.

## 7. Supuestos y riesgos

| Supuesto o riesgo | Qué pasa si es falso |
|---|---|
| En el gimnasio hay señal o wifi. | Sin señal no se puede registrar nada: habría que soportar uso sin conexión, que es la decisión más cara del proyecto (RNF-006-05). |
| "No va a producción" (R-11). | Si la uso desde el gimnasio, la app tiene que estar publicada en internet. Aunque sea solo para mí, eso es producción: necesita hosting, cifrado y respaldos. |
| El código lo genera la IA a partir de las specs (R-21). | Si una spec es ambigua, la IA inventa. La calidad del resultado es la calidad de la spec. |
| Mantener esto no le quita tiempo a Linux y Redes. | Hay prueba el 14 de noviembre y la meta de empleo es el 31 de enero de 2027. Si choca, GymProgress espera. |
