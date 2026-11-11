# Requisitos no funcionales

> Según el proceso de la clase, los RNF no pasan por historias de usuario: se le entregan al framework o a la IA como condiciones que **todo** el sistema debe cumplir. Para que eso funcione, cada uno tiene que poder comprobarse. Por eso "rápido", "sencillo" y "seguro" están traducidos a algo que se mide.
>
> **Origen:** el requisito textual de [`requirements.md`](requirements.md). **Estado:** todos aprobados por el usuario el 2026-11-09.

## Plataforma

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-PLA-01 | La aplicación debe usarse desde el navegador de un iPhone, sin instalar nada desde una tienda. | Se abre y se completa una sesión en Safari de iOS. | R-07 |
| RNF-PLA-02 | Todas las pantallas deben poder usarse en vertical, en un ancho de 375 px, sin desplazamiento horizontal. | Revisión en ese ancho. | R-07 |
| RNF-PLA-03 | Debe poder agregarse a la pantalla de inicio del iPhone y abrirse como una app, también sin conexión. *(Necesario para el uso sin señal decidido en la spec 006.)* | Se agrega, se pone modo avión y abre. | R-08 |
| RNF-PLA-06 | El registro de sesiones debe funcionar sin conexión y sincronizar al volver la señal (detalle en RNF-006-05 a 07). | CA-006-16a y CA-006-17a. | R-04 |
| RNF-PLA-04 | La aplicación es de uso privado: no aparece en buscadores ni tiene registro público. | No existe pantalla de registro abierta. | R-10, R-11 |
| RNF-PLA-05 | La aplicación debe ser accesible desde cualquier lugar por internet (se usa en el gimnasio). Eso implica estar publicada, aunque sea de uso privado. Presupuesto máximo de hosting: **$20.000 COP al mes**. Decidido 2026-11-09. Publicada en Railway (plan 006, sección 12), por presupuesto. | Se abre con datos móviles fuera de casa. | R-07, R-11 |

## Acceso

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-ACC-01 | El usuario se identifica con su **correo o su nombre de usuario**, más su contraseña. | Entra con cualquiera de los dos. | R-07, R-22 |
| RNF-ACC-02 | Tras identificarse, el dispositivo recuerda el acceso 7 días sin volver a pedir contraseña. Si el acceso vence sin conexión en mitad de una sesión de entrenamiento, los registros no se pierden: se sincronizan cuando el usuario vuelva a identificarse. | Día 6: entra directo. Día 8: pide contraseña. | R-09 |
| RNF-ACC-03 | Los 7 días se cuentan desde el último uso: cada vez que el usuario abre la app se renuevan. Decidido 2026-11-09. | Uso el día 6 y el día 12: no pide contraseña. Sin uso 7 días: la pide. | R-09 |
| RNF-ACC-04 | El usuario puede cerrar el acceso cuando quiera; después de hacerlo no se ve ningún dato sin contraseña. | Cerrar y volver atrás en el navegador no muestra datos. | R-16 |
| RNF-ACC-05 | Solo el dueño puede crear cuentas para otras personas. Máximo **5 cuentas** en total. Decidido 2026-11-09. | Sin invitación no se puede crear cuenta; la sexta se rechaza. | R-10 |
| RNF-ACC-06 | Cada persona ve y modifica únicamente sus rutinas, sesiones y datos. | Con la cuenta B se intenta abrir, editar y borrar un dato de la cuenta A: todo se rechaza. | R-15 |
| RNF-ACC-07 | Tras 5 contraseñas incorrectas seguidas, el acceso a esa cuenta se bloquea 15 minutos. | Sexto intento rechazado aunque sea correcto. | R-12 |
| RNF-ACC-08 | El usuario puede cambiar su contraseña escribiendo la actual. | — | R-12 |
| RNF-ACC-09 | Si un usuario olvida su contraseña, el dueño le genera una temporal que debe cambiar al entrar. La del dueño se restablece desde el servidor. No hay correo de recuperación. Decidido 2026-11-09. | Se restablece una cuenta de prueba. | R-12 |
| RNF-ACC-10 | De cada cuenta se guardan solo: nombre para mostrar, nombre de usuario (único), correo (único) y contraseña. Decidido 2026-11-09. | No existen más campos personales. | R-22 |

## Seguridad

"Pocas vulnerabilidades o nulas" (R-12) se comprueba contra el [OWASP Top 10](https://owasp.org/www-project-top-ten/), la lista estándar de los fallos más comunes en aplicaciones web. Cada fila es una condición verificable.

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-SEG-01 | Ninguna contraseña se guarda de forma que pueda leerse o recuperarse. | Se revisan los datos guardados: no aparece ninguna contraseña. | R-13 |
| RNF-SEG-02 | Toda la comunicación entre el celular y la aplicación viaja cifrada. | No responde por conexión sin cifrar. | R-12 |
| RNF-SEG-03 | Ningún secreto (claves, contraseñas de servicios) está en el repositorio ni en su historial. | Búsqueda automática de secretos en cada cambio. | R-12 · H-02 |
| RNF-SEG-04 | Toda regla de validación se aplica del lado del servidor, aunque la pantalla también la aplique. | Se envía un dato inválido saltándose la pantalla: se rechaza. | R-14 |
| RNF-SEG-05 | Ningún dato escrito por el usuario puede alterar una consulta ni ejecutarse como código en la pantalla. | Pruebas con texto malicioso en cada campo de texto. | R-12 |
| RNF-SEG-06 | Toda operación comprueba en el servidor quién la pide y si el dato es suyo. | Igual que RNF-ACC-06. | R-15 · H-03 |
| RNF-SEG-07 | Las dependencias tienen versión fija y sin vulnerabilidades conocidas de severidad alta. | Auditoría automática de dependencias. | R-12 · H-16 |
| RNF-SEG-08 | Los registros de diagnóstico no contienen contraseñas ni datos personales. | Revisión de los registros tras usar la app. | R-12 · H-21 |
| RNF-SEG-09 | Los mensajes de error no revelan detalles internos del sistema. | Se provoca un error: el mensaje no nombra tecnología ni rutas. | R-12, R-17 |
| RNF-SEG-10 | Contraseña de mínimo 10 caracteres. | 9 se rechaza, 10 se acepta. | R-12 |

## Rendimiento

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-REN-01 | Con acceso recordado, desde abrir la app hasta ver la rutina de hoy: máximo 2 segundos con datos móviles. | Cronómetro, 5 intentos. | R-08 |
| RNF-REN-02 | Confirmar una serie responde en menos de 1 segundo. | Cronómetro. | R-04 |

## Usabilidad

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-USA-01 | Registrar una serie: 1 toque sin cambios, máximo 3 con cambios. | Ver RNF-006-01 y 02 en la spec 006. | R-04 |
| RNF-USA-02 | Cada mensaje de error dice qué pasó y qué hacer, sin términos técnicos. | Lista de mensajes revisada. | R-17 · H-15 |
| RNF-USA-03 | El título de cada número describe exactamente lo que se calcula. | Cada indicador tiene su fórmula en la spec 004. | R-18 · H-07, H-08 |
| RNF-USA-04 | Toda acción que no se puede deshacer pide confirmación antes. | Eliminar rutina, sesión o cuenta. | R-19 |
| RNF-USA-05 | Interfaz en español. | — | — |

## Mantenibilidad

"Fácil de mantener y de escalar" (R-20) se vuelve criterio para elegir el stack en el `plan.md` y regla para el código generado.

| ID | Requisito | Cómo se comprueba | Origen |
|---|---|---|---|
| RNF-MAN-01 | Cada requerimiento funcional tiene al menos una prueba automatizada que lleva su ID. | Reporte de pruebas. | R-20 · H-22 |
| RNF-MAN-02 | La estructura de los datos cambia solo mediante scripts versionados en el repositorio. | No hay cambios de estructura al arrancar la app. | R-20 · H-19 |
| RNF-MAN-03 | Las reglas de negocio están separadas de la pantalla y del almacenamiento, y pueden probarse solas. | Las pruebas de reglas corren sin base de datos ni navegador. | R-20 · H-17 |
| RNF-MAN-04 | El proyecto se instala y arranca con máximo 3 comandos documentados en el README. | Se sigue el README en un equipo limpio. | R-20 |
| RNF-MAN-05 | El código debe estar en **Python** (servidor) y **JavaScript** (pantalla), los dos lenguajes que David puede leer y explicar. Decidido 2026-11-09. | No hay código en otro lenguaje. | R-20 |
| RNF-MAN-06 | Copia de respaldo automática de los datos, al menos una vez al día. | Se restaura una copia en limpio. | R-01 |
