package org.gymprogress.dao;

import org.gymprogress.model.Progreso;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

/**
 * DAO para manejar todas las operaciones CRUD de la tabla 'progreso'.
 * (RF04, RF05)
 */
public class ProgresoDAO {

    private Connection conn;

    public ProgresoDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en ProgresoDAO!! La conexión a la BD (conn) es NULL.");
        }
    }

    /**
     * Inserta un nuevo registro de progreso en la base de datos.
     *
     * @param progreso El objeto Progreso (con codigo_usuario, fecha, peso y altura)
     * @return true si la inserción fue exitosa, false en caso contrario.
     */
    public boolean registrarProgreso(Progreso progreso) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");

        String sql = "INSERT INTO progreso (codigo_usuario, fecha, peso_corporal, altura, notas) VALUES (?, ?, ?, ?, ?)";
        
        System.out.println("DAO (Progreso-Crear): Registrando nuevo progreso para usuario: " + progreso.getCodigoUsuario());

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, progreso.getCodigoUsuario());
            stmt.setDate(2, progreso.getFecha());
            stmt.setDouble(3, progreso.getPesoCorporal());
            stmt.setDouble(4, progreso.getAltura());
            stmt.setString(5, progreso.getNotas());
            
            int filasAfectadas = stmt.executeUpdate();
            return filasAfectadas > 0;
        }
    }

    /**
     * Obtiene TODO el historial de progreso de un usuario, ordenado por fecha.
     * Esencial para las gráficas.
     *
     * @param codigoUsuario El ID del usuario logueado.
     * @return Una lista de objetos Progreso.
     */
    public List<Progreso> getProgresoPorUsuario(int codigoUsuario) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        List<Progreso> historial = new ArrayList<>();
        // ¡ORDER BY fecha ASC es crucial para las gráficas!
        String sql = "SELECT * FROM progreso WHERE codigo_usuario = ? ORDER BY fecha ASC";

        System.out.println("DAO (Progreso-Leer): Obteniendo historial de progreso para usuario: " + codigoUsuario);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Progreso p = new Progreso();
                    p.setCodigoProgreso(rs.getInt("codigo_progreso"));
                    p.setCodigoUsuario(rs.getInt("codigo_usuario"));
                    p.setFecha(rs.getDate("fecha"));
                    p.setPesoCorporal(rs.getDouble("peso_corporal"));
                    p.setAltura(rs.getDouble("altura"));
                    p.setNotas(rs.getString("notas"));
                    historial.add(p);
                }
            }
        }
        System.out.println("DAO (Progreso-Leer): Encontrados " + historial.size() + " registros.");
        return historial;
    }

    /**
     * Obtiene la altura MÁS RECIENTE registrada por el usuario.
     * Esto es vital para calcular el IMC cuando el usuario solo registra su peso.
     *
     * @param codigoUsuario El ID del usuario logueado.
     * @return La altura más reciente en metros (ej. 1.75) o 0 si no se encuentra.
     */
    public double getAlturaReciente(int codigoUsuario) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        // Busca la última entrada donde la altura se haya registrado (altura > 0)
        String sql = "SELECT altura FROM progreso WHERE codigo_usuario = ? AND altura > 0 ORDER BY fecha DESC LIMIT 1";
        
        System.out.println("DAO (Progreso-Altura): Buscando altura más reciente para usuario: " + codigoUsuario);

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);
            
            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    double altura = rs.getDouble("altura");
                    System.out.println("DAO (Progreso-Altura): Altura encontrada: " + altura);
                    return altura;
                } else {
                    // No debería pasar si el registro (RF01) funciona, 
                    // pero es una salvaguarda.
                    System.err.println("DAO (Progreso-Altura): ¡ADVERTENCIA! No se encontró altura para el usuario " + codigoUsuario);
                    return 0; 
                }
            }
        }
    }
}