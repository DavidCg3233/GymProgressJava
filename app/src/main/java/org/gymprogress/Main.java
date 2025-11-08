package org.gymprogress; // <-- ¡Paquete Corregido!

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;
import org.gymprogress.dao.ConexionDB; // <-- ¡Paquete Corregido!

import java.io.IOException;
import java.net.URL;

public class Main extends Application {

    @Override
    public void start(Stage primaryStage) {
        try {
            URL fxmlUrl = getClass().getResource("/fxml/main.fxml");
            if (fxmlUrl == null) {
                System.err.println("Error: No se pudo encontrar /fxml/main.fxml.");
                return;
            }
            Parent root = FXMLLoader.load(fxmlUrl);
            Scene scene = new Scene(root, 1280, 720); 
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