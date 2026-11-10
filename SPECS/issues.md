# Issues

> Paso 5 del proceso de la clase: los issues son la **materialización de las especificaciones**. Tres tipos:
>
> | Tipo | Cuándo | Qué se hace |
> |---|---|---|
> | **Feature** | Funcionalidad que sale de una spec | Se desarrolla |
> | **Bug** | Se probó y salió mal | Se devuelve para corregir |
> | **Error** | Está mal de raíz | Se borra y se rehace |
>
> Este archivo es el borrador. Un feature se pasa a GitHub Issues solo cuando su spec esté `Aprobada`; ahí se divide en tasks.

## Features

| ID | Feature | Spec | Estado de la spec |
|---|---|---|---|
| F-01 | Empezar una sesión desde una rutina | 006 · RF-006-01, 02 | Borrador |
| F-02 | Registrar cada serie con peso y reps, precargada con la última vez | 006 · RF-006-03 a 06 | Borrador |
| F-03 | Terminar la sesión (a mano o sola a las 2 horas) | 006 · RF-006-07, 08 | Borrador |
| F-04 | Historial de sesiones | 006 · RF-006-09 a 11 | Borrador |
| F-05 | Crear, modificar y eliminar rutinas con día de la semana | 002 | Borrador |
| F-06 | Catálogo de ejercicios y grupos musculares | 002 · RF-002-08 a 10 | Borrador |
| F-07 | Ver el progreso por ejercicio y los récords | 004 | Borrador |
| F-08 | Pantalla de entrada con la rutina de hoy | 004 · RF-004-01 a 03 | Borrador |
| F-09 | Acceso recordado 7 días, cierre de acceso, cuentas por invitación | rnf.md · RNF-ACC | — (RNF: se automatiza) |
| F-10 | Base del proyecto: stack nuevo, pruebas, migraciones, despliegue | rnf.md · RNF-MAN, RNF-PLA | — (RNF: se automatiza) |

## Errores (v1.0: se borra y se rehace)

Como el stack cambia (de escritorio a web), todo el código de la v1.0 entra aquí. No se corrige: se reemplaza. Los hallazgos quedan como lista de lo que la versión nueva **no puede repetir**, y cada uno ya tiene un RNF o un RF que lo impide.

| Hallazgos | Qué estaba mal de raíz | Lo impide |
|---|---|---|
| H-01, H-02 | Contraseñas legibles y secretos en el repositorio | RNF-SEG-01, RNF-SEG-03 |
| H-03 | Sin control de quién es dueño de cada dato | RNF-ACC-06, RNF-SEG-06 |
| H-04 | Sin cierre de acceso | RNF-ACC-04 |
| H-06 | Sin validación en el servidor | RNF-SEG-04 |
| H-07, H-08, H-09, H-12 | Estadísticas calculadas sobre el plan, porque no existían sesiones | Spec 006 y RF-004-04, 05 |
| H-10, H-11, H-20 | Catálogo de ejercicios compartido y dato de grupo muscular duplicado | RF-002-10 |
| H-15 | Mensajes de error técnicos | RNF-USA-02 |
| H-16 | Dependencias sin versión fija | RNF-SEG-07 |
| H-17, H-18, H-25 | Todo mezclado en una sola clase | RNF-MAN-03 |
| H-19 | El esquema cambiaba solo al arrancar | RNF-MAN-02 |
| H-21 | Errores silenciados y datos personales en la consola | RNF-SEG-08 |
| H-22 | Sin pruebas | RNF-MAN-01 |
| H-05, H-23, H-24 | Transacción poco confiable, código muerto, binarios en Git | Desaparecen con la reescritura |
| H-13, H-14, H-26 | Perfil y peso corporal incompletos | Spec 003, en espera |

## Bugs

Ninguno todavía: un bug aparece cuando se prueba algo construido contra una spec y no cumple un criterio de aceptación. Se anotan aquí con el ID del criterio que falló (por ejemplo, `CA-006-04a`).

| ID | Criterio que falló | Qué pasó | Estado |
|---|---|---|---|
| | | | |

## Acción pendiente fuera del código

- **Cambiar la contraseña de `root` de MySQL** si la usas en algún otro lugar: está en el historial público de GitHub (H-02) y borrar el archivo no la quita del historial.
