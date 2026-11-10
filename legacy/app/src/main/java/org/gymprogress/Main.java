package org.gymprogress; // <-- ¡Paquete Corregido!


import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import org.gymprogress.controller.MainAppController;
import org.gymprogress.dao.ConexionDB;

import java.io.IOException;
import java.net.URL;

public class Main extends Application {

    // Archivo: Main.java

@Override
public void start(Stage primaryStage) {
    try {
        URL fxmlUrl = getClass().getResource("/fxml/main.fxml");
        if (fxmlUrl == null) {
            System.err.println("Error: No se pudo encontrar /fxml/main.fxml.");
            return;
        }

      // 1. Crear un FXMLLoader en lugar de usar el método estático
            FXMLLoader loader = new FXMLLoader(fxmlUrl);
            
            // 2. Cargar el FXML
            Parent root = loader.load();
            
            // 3. Obtener la instancia del controlador que se creó
            MainAppController controller = loader.getController();
            
            // 4. ¡¡LA LÍNEA CLAVE!!
            // Inyectamos la ventana principal (Stage) en el controlador
            controller.setStage(primaryStage); 

        Scene scene = new Scene(root, 1280, 720);
        
        // Configurar el ícono de la aplicación
        Image icon = new Image(getClass().getResourceAsStream("/img/Gemini_Generated_Image_m66imgm66imgm66i-removebg-preview.png"));
        primaryStage.getIcons().add(icon);
        
        // Establecer tamaño mínimo para evitar problemas de visualización
        primaryStage.setMinWidth(1000);  // Ancho mínimo
        primaryStage.setMinHeight(700);   // Alto mínimo
        
        primaryStage.setTitle("GymProgress v1.0");
        primaryStage.setScene(scene);
        primaryStage.show();
        
    } catch (IOException e) {
        e.printStackTrace();
    }
}

    public static void main(String[] args) {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            ConexionDB.closeConnection();
            System.out.println("Aplicación cerrada, conexión a BD finalizada.");
        }));
        launch(args);
    }
}