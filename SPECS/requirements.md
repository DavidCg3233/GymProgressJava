# Requisitos textuales

> Paso 1 del proceso SDD de la clase: lo que pidió el usuario, **con sus palabras**, sin corregir. Dictados por David (usuario) el 9 de noviembre de 2026.
>
> **Tipo:** `RF` si es regla del negocio (entrenar y medir el progreso); `RNF` todo lo demás. Los RF se convierten en historias de usuario dentro de una spec; los RNF van a [`rnf.md`](rnf.md) y los resuelve el framework o la IA.

## Lo que dijo el usuario

| # | Requisito textual (tal cual) | Tipo | Épica | Dónde se desarrolla |
|---|---|---|---|---|
| R-01 | "necesito hacer un seguimiento de las sesiones hechas" | RF | Sesiones | [006](006-sesiones/spec.md) |
| R-02 | "si hoy tengo dia de pecho, y en el ejercicio de press inclinado tengo 3 series, quiero ver como se registran esas 3 series, con cuanto peso y cuantas reps hice" | RF | Sesiones | [006](006-sesiones/spec.md) |
| R-03 | "las rutinas las puedo crear, y segun como vea mi progreso, eliminar, modificar y dejar para un dia de la semana en especifico" | RF | Rutinas | [002](002-rutinas/spec.md) |
| R-04 | "si estoy en una sesion, debe ser lo mas sencillo posible registrar los pesos que hice en esa sesion de ese ejercicio, de ese grupo muscular de esa rutina" | RNF | Sesiones | [rnf.md](rnf.md) · condiciona 006 |
| R-05 | *(¿ver lo que hice la última vez en ese ejercicio ya puesto, para solo ajustar?)* "si" | RF | Sesiones | [006](006-sesiones/spec.md) |
| R-06 | "el tiempo de sesion activo debera ser de unas 2 horas (lo que dura una sesion)" | RF | Sesiones | [006](006-sesiones/spec.md) |
| R-07 | "en el inicio de sesion, necesito que me permita entrar desde una pagina web […] donde yo pueda entrar desde el celular" · "necesito que sea web porque tengo iphone" | RNF | Plataforma | [rnf.md](rnf.md) |
| R-08 | "sin necesidad de estar iniciando cada vez, es decir necesito que sea rapido, a la hora de ingresar" | RNF | Acceso | [rnf.md](rnf.md) |
| R-09 | "sin pedir contraseñas, 7 dias, exacto" | RNF | Acceso | [rnf.md](rnf.md) |
| R-10 | "solo para mi, pero me gustaria compartirsela a algun ser querido o algo asi, (pocas personas)" | RNF | Acceso | [rnf.md](rnf.md) |
| R-11 | "la aplicacion es solo para mi, asi que a produccion no se va a ir como tal" | RNF | Plataforma | [rnf.md](rnf.md) |
| R-12 | "necesito que exista seguridad en esta aplicacion, que hayan pocas vulnerabilidades, o nulas" | RNF | Seguridad | [rnf.md](rnf.md) |
| R-13 | *(las contraseñas no deben poder leerse en los datos guardados)* "Exacto, no deben aparecer" | RNF | Seguridad | [rnf.md](rnf.md) |
| R-14 | *(las validaciones deben aplicarse aunque la interfaz no las haga)* "si" | RNF | Seguridad | [rnf.md](rnf.md) |
| R-15 | *(nadie puede modificar o eliminar la rutina de otro usuario)* "si" | RNF | Seguridad | [rnf.md](rnf.md) |
| R-16 | *(debe existir cerrar sesión)* "si" | RNF | Acceso | [rnf.md](rnf.md) |
| R-17 | *(los mensajes de error deben estar en lenguaje del usuario)* "si" | RNF | Usabilidad | [rnf.md](rnf.md) |
| R-18 | *(el título de cada número debe describir lo que se calcula)* "si" | RNF | Usabilidad | [rnf.md](rnf.md) · condiciona 004 |
| R-19 | *(las acciones irreversibles deben pedir confirmación)* "si" | RNF | Usabilidad | [rnf.md](rnf.md) |
| R-20 | "necesito reescribir el proyecto a un stack que se acople y sea facil de mantener y de escalar" | RNF | Mantenibilidad | [rnf.md](rnf.md) |
| R-21 | *(¿quién escribe el código?)* "Se genera, es un proyecto personal" | Restricción | — | [constitución](../docs/constitucion.md) |
| R-22 | *(¿qué datos personales guarda la app?)* "Nombre, correo, pero que tambien se pueda ingresar con un nombre de usuario" | RNF | Acceso | [rnf.md](rnf.md) |
| R-23 | *(¿peso corporal, IMC y peso objetivo entran en la versión nueva?)* "Sí, desde el inicio" | RF | Cuerpo | [003](003-progreso-corporal/spec.md) |
| R-24 | *(¿qué necesitas ver para decidir sobre tus rutinas?)* "Evolución por ejercicio, Récords por ejercicio, Sesiones por semana, Por grupo muscular" | RF | Progreso | [004](004-panel-y-estadisticas/spec.md) |
| R-25 | *(sesión libre, notas por sesión y por ejercicio, corregir y eliminar)* respuestas del 2026-11-09 | RF | Sesiones | [006](006-sesiones/spec.md), sección 9 |

*Entre paréntesis y en cursiva: la pregunta o propuesta del analista a la que el usuario respondió.*

## Lo que la v1.0 hacía y el usuario no había pedido

Revisado con el usuario el 2026-11-09:

| Capacidad de la v1.0 | Decisión | Requisito |
|---|---|---|
| Peso corporal, IMC, peso objetivo y gráficas | **Entra desde el inicio.** Altura una sola vez en el perfil; IMC como dato informativo; un registro por día, editable. | R-23 |
| Panel y estadísticas | **Entra**, con cuatro vistas calculadas sobre sesiones reales. | R-24 |
| Catálogo de ejercicios y grupos musculares | Entra (implícito en R-02 y R-04). | — |
| Dos nombres, dos apellidos, sexo, fecha de nacimiento | **Se eliminan.** Solo nombre para mostrar, nombre de usuario y correo. | R-22 |

## Épicas

| Épica | Tipo | Qué agrupa | Requisitos | Spec |
|---|---|---|---|---|
| **Sesiones** | RF | Lo que hice: sesión de entrenamiento, series, peso y reps | R-01, R-02, R-05, R-06 | 006 |
| **Rutinas** | RF | Lo que planeo: rutinas, ejercicios, día de la semana | R-03 | 002 |
| **Progreso** | RF | Lo que veo para decidir: evolución, récords, sesiones por semana, grupos musculares | R-24 (y R-01, R-03) | 004 |
| **Cuerpo** | RF | Peso corporal, IMC y peso objetivo | R-23 | 003 |
| Acceso, Plataforma, Seguridad, Usabilidad, Mantenibilidad | RNF | Sin historias de usuario | R-04, R-07 a R-20, R-22 | rnf.md |

## Glosario del usuario

La palabra "sesión" aparece con dos sentidos en los requisitos. En todas las specs se usan así:

| Término | Significado |
|---|---|
| **Sesión** (de entrenamiento) | Una visita al gimnasio en la que se ejecuta una rutina. Dura unas 2 horas (R-06). |
| **Acceso** | Estar identificado en la app. Se recuerda 7 días en el dispositivo (R-09). |
| **Rutina** | El plan: ejercicios con series, reps y peso previstos para un día. |
| **Serie** | Un bloque de repeticiones seguidas de un ejercicio, con un peso. |

## Supuesto confirmado

El **acceso** se recuerda 7 días sin pedir contraseña, contados desde el último uso, y una **sesión de entrenamiento** abierta se da por terminada sola a las 2 horas. Confirmado por el usuario el 2026-11-09.
