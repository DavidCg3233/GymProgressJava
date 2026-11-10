package org.gymprogress.dao;

import org.gymprogress.model.RutinaEjercicioDTO; // <-- ¡Usamos el nuevo DTO!
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class RutinaEjercicioDAO {

    private Connection conn;

    public RutinaEjercicioDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en RutinaEjercicioDAO!! La conexión a la BD es NULL.");
        }
    }

    /**
     * Obtiene la lista de ejercicios (con nombres) para una rutina específica.
     * Esta es la función clave para poblar el modal de "Editar".
     *
     * @param codigoRutina El ID de la rutina
     * @return Una lista de DTOs listos para el JSON
     * @throws SQLException
     */
    public List<RutinaEjercicioDTO> getEjerciciosPorRutina(int codigoRutina) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");

        List<RutinaEjercicioDTO> ejercicios = new ArrayList<>();
        
        // Hacemos un JOIN para obtener el NOMBRE del ejercicio
    String sql = "SELECT e.nombre, COALESCE(g.nombre_grupo_muscular, e.grupo_muscular, 'General') AS grupo_muscular, " +
             "re.series, re.repeticiones, re.peso " +
             "FROM rutina_ejercicio re " +
             "JOIN ejercicio e ON re.codigo_ejercicio = e.codigo_ejercicio " +
             "LEFT JOIN grupo_muscular g ON e.codigo_grupo_muscular = g.codigo_grupo_muscular " +
             "WHERE re.codigo_rutina = ?";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoRutina);

            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    RutinaEjercicioDTO dto = new RutinaEjercicioDTO();
                    dto.setNombre(rs.getString("nombre"));
                    dto.setSeries(rs.getInt("series"));
                    dto.setRepeticiones(rs.getInt("repeticiones"));
                    dto.setPeso(rs.getDouble("peso"));
                    try { dto.setGrupoMuscular(rs.getString("grupo_muscular")); } catch (Exception ignore) {}
                    ejercicios.add(dto);
                }
            }
        }
        return ejercicios;
    }

    /**
     * Borra TODOS los ejercicios asociados a una rutina.
     * Esto es vital para el proceso de "Actualizar".
     *
     * @param codigoRutina El ID de la rutina
     * @throws SQLException
     */
    public void deleteEjerciciosPorRutina(int codigoRutina) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        
        System.out.println("DAO (RutinaEjercicio): Borrando antiguos ejercicios para la rutina ID: " + codigoRutina);
        String sql = "DELETE FROM rutina_ejercicio WHERE codigo_rutina = ?";
        
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoRutina);
            stmt.executeUpdate();
        }
    }

    /**
     * Añade un nuevo ejercicio a una rutina.
     *
     * @param codigoRutina El ID de la rutina
     * @param codigoEjercicio El ID del ejercicio (obtenido de EjercicioDAO)
     * @param series
     * @param repeticiones
     * @param peso
     * @throws SQLException
     */
    public void addEjercicioARutina(int codigoRutina, int codigoEjercicio, int series, int repeticiones, double peso) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");

        String sql = "INSERT INTO rutina_ejercicio (codigo_rutina, codigo_ejercicio, series, repeticiones, peso) " +
                     "VALUES (?, ?, ?, ?, ?)";
        
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoRutina);
            stmt.setInt(2, codigoEjercicio);
            stmt.setInt(3, series);
            stmt.setInt(4, repeticiones);
            stmt.setDouble(5, peso);
            
            stmt.executeUpdate();
        }
    }
}