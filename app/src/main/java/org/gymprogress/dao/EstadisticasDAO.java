package org.gymprogress.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * DAO especializado en consultas de agregación (GROUP BY, MAX, COUNT)
 * para la página de Estadísticas (RF-STATS).
 */
public class EstadisticasDAO {

    private Connection conn;

    public EstadisticasDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en EstadisticasDAO!! La conexión a la BD es NULL.");
        }
    }

    /**
     * Obtiene los Récords Personales (PRs) de un usuario.
     * Busca el peso máximo levantado para cada ejercicio.
     * (Basado en 'statistics-view.tsx')
     */
    public List<Map<String, String>> getRecordsPersonales(int codigoUsuario) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        
        List<Map<String, String>> records = new ArrayList<>();
        
        // Consulta compleja para obtener el MAX(peso) por nombre de ejercicio para un usuario
        String sql = "SELECT e.nombre, MAX(re.peso) as max_peso " +
                     "FROM rutina_ejercicio re " +
                     "JOIN ejercicio e ON re.codigo_ejercicio = e.codigo_ejercicio " +
                     "JOIN rutina r ON re.codigo_rutina = r.codigo_rutina " +
                     "WHERE r.codigo_usuario = ? AND re.peso > 0 " +
                     "GROUP BY e.nombre " +
                     "ORDER BY max_peso DESC " +
                     "LIMIT 5"; // Limitar a los 5 mejores

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Map<String, String> record = new HashMap<>();
                    record.put("ejercicio", rs.getString("nombre"));
                    record.put("peso", String.format("%.1f kg", rs.getDouble("max_peso")));
                    records.add(record);
                }
            }
        }
        return records;
    }

    /**
     * Obtiene el conteo de entrenamientos por mes (últimos 6 meses).
     * (Basado en 'statistics-view.tsx')
     */
    public List<Map<String, Object>> getEntrenamientosPorMes(int codigoUsuario) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");

        List<Map<String, Object>> data = new ArrayList<>();
        
        // Consulta para agrupar rutinas por mes
        String sql = "SELECT DATE_FORMAT(fecha_creacion, '%Y-%m') as mes, COUNT(codigo_rutina) as total " +
                     "FROM rutina " +
                     "WHERE codigo_usuario = ? AND fecha_creacion >= CURDATE() - INTERVAL 6 MONTH " +
                     "GROUP BY mes " +
                     "ORDER BY mes ASC";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Map<String, Object> item = new HashMap<>();
                    item.put("mes", rs.getString("mes"));
                    item.put("total", rs.getInt("total"));
                    data.add(item);
                }
            }
        }
        return data;
    }

    /**
     * Obtiene la distribución de ejercicios por grupo muscular.
     * (Basado en 'statistics-view.tsx')
     * NOTA: Esto requiere que tu tabla 'ejercicio' tenga la columna 'grupo_muscular'.
     * Si no la tiene, esta consulta fallará.
     */
    public List<Map<String, Object>> getDistribucionEjercicios(int codigoUsuario) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");

        List<Map<String, Object>> data = new ArrayList<>();
        
        // Contar ejercicios por grupo muscular
        String sql = "SELECT e.grupo_muscular, COUNT(re.codigo_ejercicio) as total " +
                     "FROM rutina r " +
                     "JOIN rutina_ejercicio re ON r.codigo_rutina = re.codigo_rutina " +
                     "JOIN ejercicio e ON re.codigo_ejercicio = e.codigo_ejercicio " +
                     "WHERE r.codigo_usuario = ? AND e.grupo_muscular IS NOT NULL AND e.grupo_muscular != '' " +
                     "GROUP BY e.grupo_muscular";

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Map<String, Object> item = new HashMap<>();
                    item.put("grupo", rs.getString("grupo_muscular"));
                    item.put("total", rs.getInt("total"));
                    data.add(item);
                }
            }
        }
        return data;
    }
}