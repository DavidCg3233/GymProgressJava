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
| F-01 | Empezar una sesión desde una rutina o libre | 006 · RF-006-01, 02, 20, 21 | Aprobada |
| F-02 | Registrar, corregir, agregar y quitar series, precargadas con la última vez | 006 · RF-006-03 a 06, 12 a 14, 24 | Aprobada |
| F-03 | Terminar la sesión (a mano o sola a las 2 horas) y notas | 006 · RF-006-07, 08, 19, 22, 23 | Aprobada |
| F-04 | Historial de sesiones y eliminar | 006 · RF-006-09 a 11, 15 | Aprobada |
| F-11 | Registro sin conexión y sincronización | 006 · RF-006-16 a 18 | Aprobada |
| F-12 | Peso corporal, IMC y peso objetivo | 003 | Aprobada |
| F-05 | Crear, modificar, duplicar y eliminar rutinas con días de la semana | 002 | En revisión |
| F-06 | Catálogo propio de ejercicios y grupos, con lista predefinida | 002 · RF-002-08 a 10, 14 a 19 | En revisión |
| F-07 | Progreso: evolución por ejercicio, récords, sesiones por semana con meta, series por grupo | 004 | En revisión |
| F-08 | Inicio con la rutina de hoy | 004 · RF-004-01 a 03, 07, 10 | En revisión |
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
