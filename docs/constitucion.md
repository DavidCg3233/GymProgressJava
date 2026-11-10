# Constitución de GymProgress

> Las reglas que valen para **todas** las specs y todo el código. Como el código lo va a generar una IA (R-21), este archivo es lo primero que se le entrega: es la parte de **restricción** y **condición de calidad** del prompt de 5 partes, escrita una sola vez.
>
> **Estado:** Borrador · **Versión:** 0.2 · `[DAVID]` Léela completa y cambia lo que no compartas. Tú respondes por lo que diga.

## Principios

### P1. La spec va primero
- **Regla:** ningún comportamiento se programa sin un requerimiento con ID en una spec `Aprobada`.
- **Por qué:** la v1.0 se hizo con vibe coding y nadie podía decir qué debía hacer cada pantalla.
- **Se verifica:** cada commit de funcionalidad nombra el ID (`RF-006-03`) en su mensaje.

### P2. Nada que nadie pidió
- **Regla:** la IA no agrega funcionalidades, pantallas ni campos que no estén en una spec. Si cree que falta algo, lo pregunta.
- **Por qué:** la v1.0 tenía tablas, clases y un método completo que nunca se usaron.
- **Se verifica:** cada archivo de código se puede rastrear a un RF o un RNF.

### P3. Los RNF de seguridad no se negocian
- **Regla:** todo lo que se construya cumple la sección Seguridad y Acceso de [`SPECS/rnf.md`](../SPECS/rnf.md), aunque la spec de la funcionalidad no lo repita.
- **Por qué:** R-12. La v1.0 guardaba contraseñas legibles y dejaba borrar rutinas ajenas.
- **Se verifica:** las pruebas de RNF-ACC-06 y RNF-SEG-04 corren en cada cambio.

### P4. Cada requerimiento tiene su prueba
- **Regla:** un RF no está hecho sin una prueba automatizada por cada criterio de aceptación, con el ID del criterio en el nombre.
- **Por qué:** es la única forma de saber si lo que generó la IA cumple la spec sin leer todo el código. Es el TDD que vive dentro del SDD.
- **Se verifica:** el reporte de pruebas lista los `CA-xxx` y todos pasan.

### P5. Las reglas de negocio viven solas
- **Regla:** los cálculos y validaciones del negocio no dependen de la pantalla ni del almacenamiento.
- **Por qué:** en la v1.0 todo estaba en una clase de 761 líneas; lo único que se podía probar era el cálculo del IMC, porque estaba aparte.
- **Se verifica:** las pruebas de reglas corren sin base de datos ni navegador.

### P6. David entiende lo que se entrega
- **Regla:** nada se da por terminado hasta que David pueda explicar qué hace y por qué. La IA entrega cada tarea con una explicación corta de lo que cambió.
- **Por qué:** el proyecto va al portafolio y lo van a preguntar en una entrevista. Código que no puedes explicar te resta.
- **Se verifica:** David escribe en la bitácora de `tasks.md` una línea con lo que entendió de cada tarea.

### P7. `[DAVID]` *(uno tuyo)*

## Restricciones

| Tema | Decisión |
|---|---|
| ¿Quién escribe el código? | La IA, a partir de specs aprobadas (R-21). David especifica, revisa, prueba y aprueba. |
| Idioma de la interfaz | Español |
| Idioma del código | `[DECIDIR]` inglés (recomendado: es el estándar y practicas) · español |
| Unidades | Kilogramos |
| Stack | Se decide en el `plan.md` de la spec 006, con los criterios de RNF-MAN y RNF-PLA. |
| Commits | `[DECIDIR]` [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) · libre |

## Definition of Done

Una tarea está terminada cuando:

- [ ] Cumple los criterios de aceptación de su requerimiento y sus pruebas pasan.
- [ ] No rompe ningún principio de este archivo ni ningún RNF.
- [ ] David la probó en su iPhone.
- [ ] David puede explicar lo que hace.

## Historial de cambios

| Versión | Fecha | Cambio | Motivo |
|---|---|---|---|
| 0.1 | 2026-11-09 | Borrador con propuestas | Ingeniería inversa de v1.0 |
| 0.2 | 2026-11-09 | Reescrita: el código lo genera la IA, el producto pasa a web | Requisitos del usuario (R-07, R-12, R-20, R-21) |
