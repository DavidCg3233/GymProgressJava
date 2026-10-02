# GymProgress

Aplicación de escritorio para registrar y hacer seguimiento de rutinas de entrenamiento, métricas y progreso físico.

- **Tipo de proyecto:** Proyecto académico.
- **Mi rol:** Desarrollador y analista de lógica. **[COMPLETAR: ¿fue en equipo o individual?]**

## Funcionalidades

**[COMPLETAR: lista corta de lo que hace la app, por ejemplo: registrar rutinas, guardar métricas de entrenamiento, ver el progreso, etc. Solo lo que realmente funciona.]**

## Capturas de pantalla

**[COMPLETAR: 2 o 3 imágenes de la app funcionando (carpeta `docs/` o `img/` del repo).]**

## Tecnologías

- Java con **JavaFX 21** (interfaz de escritorio; `javafx-web` para mostrar vistas HTML dentro de la ventana)
- **Gradle** (wrapper incluido, no hace falta instalarlo)
- **MySQL 8** con `mysql-connector-java` 8.0.33

## Requisitos previos

- **JDK 17 o superior** (recomendado JDK 21). JavaFX 21 no funciona con Java 8.
- **MySQL Server 8.x** en ejecución (y, opcionalmente, MySQL Workbench).
- Git.

Comprueba tu versión de Java con `java -version`.

## Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/DavidCg3233/GymProgressJava.git
   cd GymProgressJava
   ```
2. Crea la base de datos en MySQL: **[COMPLETAR: nombre de la base de datos y script `.sql` con las tablas; subir el script al repo]**.
3. Configura la conexión (host, puerto, usuario, contraseña y nombre de la base) en `app/src/main/java/org/gymprogress/dao/ConexionDB.java`. **[COMPLETAR: confirmar la ruta exacta]**
4. Ejecuta la aplicación:
   ```bash
   ./gradlew run          # Linux / macOS
   gradlew.bat run        # Windows
   ```
   La clase principal es `org.gymprogress.Main`.

## Estructura del proyecto

```
app/src/main/java/org/gymprogress/
├── Main.java        # Punto de entrada de la aplicación
├── controller/      # Controladores de la interfaz
└── dao/             # Acceso a datos (ConexionDB y consultas MySQL)
```

## Autor

David Fernando Calambás Gómez — [GitHub](https://github.com/DavidCg3233)
