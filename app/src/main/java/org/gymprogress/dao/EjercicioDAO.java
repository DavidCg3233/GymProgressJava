package org.gymprogress.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class EjercicioDAO {

    private Connection conn;

    public EjercicioDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en EjercicioDAO!! La conexión a la BD es NULL.");
        }
    }

    /**
     * Busca un ejercicio por su nombre. Si no existe, lo crea y devuelve el nuevo ID.
     * Esto es CRUCIAL para guardar las rutinas.
     *
     * @param nombre El nombre del ejercicio (ej. "Press de Banca")
     * @return El codigo_ejercicio (existente o nuevo)
     * @throws SQLException
     */
    public int findOrCreateEjercicio(String nombre) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        
        // 1. Intentar buscar el ejercicio
        String sqlSelect = "SELECT codigo_ejercicio FROM ejercicio WHERE nombre = ?";
        try (PreparedStatement stmtSelect = conn.prepareStatement(sqlSelect)) {
            stmtSelect.setString(1, nombre);
            try (ResultSet rs = stmtSelect.executeQuery()) {
                if (rs.next()) {
                    // ¡Encontrado! Devolver el ID existente.
                    return rs.getInt("codigo_ejercicio");
                }
            }
        }
        
        // 2. Si no se encontró, crearlo.
        System.out.println("DAO (Ejercicio): No se encontró '" + nombre + "', creando nuevo ejercicio...");
        String sqlInsert = "INSERT INTO ejercicio (nombre, grupo_muscular, descripcion) VALUES (?, ?, ?)";
        
        try (PreparedStatement stmtInsert = conn.prepareStatement(sqlInsert, Statement.RETURN_GENERATED_KEYS)) {
            
            stmtInsert.setString(1, nombre);
            stmtInsert.setString(2, "General"); // Valor por defecto
            stmtInsert.setString(3, "Ejercicio añadido automáticamente"); // Valor por defecto

            int filasAfectadas = stmtInsert.executeUpdate();

            if (filasAfectadas == 0) {
                throw new SQLException("Falló la creación del ejercicio, no se insertaron filas.");
            }

            // 3. Obtener y devolver el nuevo ID generado
            try (ResultSet generatedKeys = stmtInsert.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    int nuevoId = generatedKeys.getInt(1);
                    System.out.println("DAO (Ejercicio): Creado nuevo ejercicio '" + nombre + "' con ID: " + nuevoId);
                    return nuevoId;
                } else {
                    throw new SQLException("Falló la creación del ejercicio, no se pudo obtener el ID.");
                }
            }
        }
    }
}