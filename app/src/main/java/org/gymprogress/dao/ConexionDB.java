package org.gymprogress.dao; // <-- ¡Paquete Corregido!

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class ConexionDB {

    // --- ¡¡REVISA ESTAS 3 LÍNEAS!! ---
    private static final String URL = "jdbc:mysql://localhost:3306/gymprogress";
    private static final String USER = "root";    // Tu usuario
    private static final String PASSWORD = "12345678"; // Tu contraseña
    // ------------------------------------

    private static Connection connection = null;

    public static Connection getConnection() {
        if (connection != null) {
            return connection;
        }
        try {
            System.out.println("ConexionDB: Intentando conectar a la base de datos...");
            System.out.println("ConexionDB: URL=" + URL);
            System.out.println("ConexionDB: User=" + USER);

            Class.forName("com.mysql.cj.jdbc.Driver");
            connection = DriverManager.getConnection(URL, USER, PASSWORD);
            
            System.out.println("¡¡CONEXIÓN EXITOSA a 'gymprogress'!!");
            return connection;

        } catch (ClassNotFoundException e) {
            System.err.println("¡¡ERROR FATAL en ConexionDB: Driver no encontrado!!");
            e.printStackTrace();
            return null;
        } catch (SQLException e) {
            System.err.println("¡¡ERROR FATAL en ConexionDB: No se pudo conectar!!");
            e.printStackTrace();
            return null;
        }
    }

    public static void closeConnection() {
        if (connection != null) {
            try {
                connection.close();
                connection = null;
                System.out.println("ConexionDB: Conexión cerrada.");
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}