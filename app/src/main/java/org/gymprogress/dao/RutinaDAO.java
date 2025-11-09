package org.gymprogress.dao;

import org.gymprogress.model.Rutina;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement; // <-- ¡NUEVO IMPORT!
import java.util.ArrayList;
import java.util.List;

public class RutinaDAO {

    private Connection conn;

    public RutinaDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en RutinaDAO!! La conexión a la BD (conn) es NULL.");
        }
    }

    /**
     * RF03: Obtiene todas las rutinas de un usuario específico.
     * (Sin cambios)
     */
    public List<Rutina> getRutinasPorUsuario(int codigoUsuario) throws SQLException {
        List<Rutina> rutinas = new ArrayList<>();
        String sql = "SELECT * FROM rutina WHERE codigo_usuario = ?";
        
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        System.out.println("DAO (Rutina): Ejecutando consulta: " + sql);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Rutina rutina = new Rutina();
                    rutina.setCodigoRutina(rs.getInt("codigo_rutina"));
                    rutina.setCodigoUsuario(rs.getInt("codigo_usuario"));
                    rutina.setNombreRutina(rs.getString("nombre_rutina"));
                    
                    // ¡¡NUEVO!! Añadir el día de la semana
                    rutina.setDiaSemana(rs.getString("dia_semana")); 
                    
                    rutina.setDescripcion(rs.getString("descripcion"));
                    rutina.setFechaCreacion(rs.getDate("fecha_creacion"));
                    rutinas.add(rutina);
                }
            }
        }
        System.out.println("DAO (Rutina): Encontradas " + rutinas.size() + " rutinas para el usuario " + codigoUsuario);
        return rutinas;
    }

    /**
     * ¡¡MÉTODO MODIFICADO!!
     * RF03 (Crear): Crea una nueva rutina y DEVUELVE el ID generado.
     */
    public int crearRutina(Rutina nuevaRutina) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        String sql = "INSERT INTO rutina (codigo_usuario, nombre_rutina, descripcion, fecha_creacion, dia_semana) " +
                     "VALUES (?, ?, ?, ?, ?)";
        
        System.out.println("DAO (Rutina-Crear): Solicitud para crear rutina: " + nuevaRutina.getNombreRutina());

        // Usamos RETURN_GENERATED_KEYS
        try (PreparedStatement stmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            stmt.setInt(1, nuevaRutina.getCodigoUsuario());
            stmt.setString(2, nuevaRutina.getNombreRutina());
            stmt.setString(3, nuevaRutina.getDescripcion());
            stmt.setDate(4, nuevaRutina.getFechaCreacion());
            stmt.setString(5, nuevaRutina.getDiaSemana()); // <-- ¡NUEVO!
            
            int filasAfectadas = stmt.executeUpdate();
            
            if (filasAfectadas == 0) {
                throw new SQLException("Falló la creación de la rutina, no se insertaron filas.");
            }

            // Obtener y devolver el nuevo ID generado
            try (ResultSet generatedKeys = stmt.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    int nuevoId = generatedKeys.getInt(1);
                    System.out.println("DAO (Rutina-Crear): ¡Rutina creada exitosamente! Nuevo ID: " + nuevoId);
                    return nuevoId;
                } else {
                    throw new SQLException("Falló la creación de la rutina, no se pudo obtener el ID.");
                }
            }
        }
    }
    
    /**
     * ¡¡NUEVO MÉTODO!!
     * RF03 (Actualizar): Actualiza el nombre y día de una rutina existente.
     */
    public boolean actualizarRutina(int codigoRutina, String nombreRutina, String diaSemana) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        String sql = "UPDATE rutina SET nombre_rutina = ?, dia_semana = ? WHERE codigo_rutina = ?";
        System.out.println("DAO (Rutina-Actualizar): Actualizando rutina ID: " + codigoRutina);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, nombreRutina);
            stmt.setString(2, diaSemana);
            stmt.setInt(3, codigoRutina);
            
            int filasAfectadas = stmt.executeUpdate();
            return filasAfectadas > 0;
        }
    }
     public List<Rutina> getRutinasRecientes(int codigoUsuario, int limit) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        List<Rutina> rutinas = new ArrayList<>();
        String sql = "SELECT * FROM rutina WHERE codigo_usuario = ? ORDER BY fecha_creacion DESC LIMIT ?";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            stmt.setInt(2, limit);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Rutina r = new Rutina();
                    r.setNombreRutina(rs.getString("nombre_rutina"));
                    r.setDiaSemana(rs.getString("dia_semana"));
                    rutinas.add(r);
                }
            }
        }
        return rutinas;
    }
    /**
     * ¡¡NUEVO MÉTODO!!
     * RF03 (Eliminar): Elimina una rutina de la base de datos.
     * Gracias a 'ON DELETE CASCADE' en el SQL, esto también borrará
     * todas las entradas en 'rutina_ejercicio' asociadas.
     */
    public boolean eliminarRutina(int codigoRutina) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        String sql = "DELETE FROM rutina WHERE codigo_rutina = ?";
        System.out.println("DAO (Rutina-Eliminar): Eliminando rutina ID: " + codigoRutina);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoRutina);
            int filasAfectadas = stmt.executeUpdate();
            return filasAfectadas > 0;
        }
    }
}