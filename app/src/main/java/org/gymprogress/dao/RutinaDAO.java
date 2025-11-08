package org.gymprogress.dao;

import org.gymprogress.model.Rutina;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
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
     */
    public List<Rutina> getRutinasPorUsuario(int codigoUsuario) throws SQLException {
        List<Rutina> rutinas = new ArrayList<>();
        String sql = "SELECT * FROM rutina WHERE codigo_usuario = ?";
        
        if (conn == null) {
            System.err.println("DAO (Rutina): No se puede ejecutar la consulta, la conexión es NULL.");
            throw new SQLException("La conexión a la base de datos es nula.");
        }
        
        System.out.println("DAO (Rutina): Ejecutando consulta: " + sql);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Rutina rutina = new Rutina();
                    rutina.setCodigoRutina(rs.getInt("codigo_rutina"));
                    rutina.setCodigoUsuario(rs.getInt("codigo_usuario"));
                    rutina.setNombreRutina(rs.getString("nombre_rutina"));
                    rutina.setDescripcion(rs.getString("descripcion"));
                    rutina.setFechaCreacion(rs.getDate("fecha_creacion"));
                    rutinas.add(rutina);
                }
            }
        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Rutina)!! Buscando rutinas.");
            e.printStackTrace();
            throw e; // Lanza la excepción para que el Bridge la atrape
        }
        
        System.out.println("DAO (Rutina): Encontradas " + rutinas.size() + " rutinas para el usuario " + codigoUsuario);
        return rutinas;
    }

    /**
     * RF03 (Crear): Inserta una nueva rutina en la base de datos.
     * Devuelve 'true' si fue exitoso.
     */
    public boolean crearRutina(Rutina nuevaRutina) throws SQLException {
        // 1. Validar conexión
        if (conn == null) {
            String error = "DAO (Rutina-Crear): No se puede insertar, la conexión es NULL.";
            System.err.println(error);
            throw new SQLException(error);
        }

        // 2. Validar datos de la rutina
        if (nuevaRutina == null) {
            String error = "DAO (Rutina-Crear): La rutina es NULL";
            System.err.println(error);
            throw new SQLException(error);
        }

        if (nuevaRutina.getCodigoUsuario() <= 0) {
            String error = "DAO (Rutina-Crear): Código de usuario inválido: " + nuevaRutina.getCodigoUsuario();
            System.err.println(error);
            throw new SQLException(error);
        }

        // 3. Preparar y ejecutar la consulta
        String sql = "INSERT INTO rutina (codigo_usuario, nombre_rutina, descripcion, fecha_creacion) VALUES (?, ?, ?, ?)";
        System.out.println("DAO (Rutina-Crear): Preparando consulta: " + sql);
        System.out.println("DAO (Rutina-Crear): Datos a insertar:");
        System.out.println("  - Código Usuario: " + nuevaRutina.getCodigoUsuario());
        System.out.println("  - Nombre Rutina: " + nuevaRutina.getNombreRutina());
        System.out.println("  - Descripción: " + nuevaRutina.getDescripcion());
        System.out.println("  - Fecha: " + nuevaRutina.getFechaCreacion());

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, nuevaRutina.getCodigoUsuario());
            stmt.setString(2, nuevaRutina.getNombreRutina());
            stmt.setString(3, nuevaRutina.getDescripcion());
            stmt.setDate(4, nuevaRutina.getFechaCreacion());
            
            System.out.println("DAO (Rutina-Crear): Ejecutando la consulta...");
            int filasAfectadas = stmt.executeUpdate();
            
            boolean exito = filasAfectadas > 0;
            if (exito) {
                System.out.println("DAO (Rutina-Crear): ¡Rutina creada exitosamente!");
            } else {
                String error = "DAO (Rutina-Crear): Error, 0 filas afectadas.";
                System.err.println(error);
                throw new SQLException(error);
            }
            return exito;

        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Rutina-Crear)!!");
            System.err.println("Mensaje: " + e.getMessage());
            System.err.println("Código de Error: " + e.getErrorCode());
            System.err.println("Estado SQL: " + e.getSQLState());
            e.printStackTrace();
            throw e;
        }
    }
}