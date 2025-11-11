package org.gymprogress.dao;

import org.gymprogress.model.Cliente;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;


/**
 * Esta clase se usa para operaciones de perfil
 * como "Obtener Perfil" o "Actualizar Perfil".
 */
public class ClienteDAO {

    private Connection conn;

    public ClienteDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en ClienteDAO!! La conexión a la BD (conn) es NULL.");
        }
        // Intentar garantizar columna 'peso_objetivo'
        ensurePesoObjetivoColumn();
    }

    private void ensurePesoObjetivoColumn() {
        if (conn == null) return;
        try (PreparedStatement ps = conn.prepareStatement("SELECT peso_objetivo FROM cliente LIMIT 1")) {
            ps.executeQuery();
        } catch (SQLException e) {
            String msg = e.getMessage() != null ? e.getMessage().toLowerCase() : "";
            if (msg.contains("unknown column") || msg.contains("columna desconocida") || msg.contains("column not found")) {
                System.out.println("DAO(Cliente): Columna 'peso_objetivo' no existe. Intentando crearla...");
                try (PreparedStatement alter = conn.prepareStatement(
                        "ALTER TABLE cliente ADD COLUMN peso_objetivo DECIMAL(5,2) NULL AFTER fecha_nacimiento")) {
                    alter.executeUpdate();
                    System.out.println("DAO(Cliente): Columna 'peso_objetivo' creada exitosamente.");
                } catch (SQLException ex) {
                    System.err.println("DAO(Cliente): No se pudo crear la columna 'peso_objetivo'. Debes ejecutar el script SQL manualmente.");
                }
            }
        }
    }

    /**
     * Obtiene los datos de un cliente basado en su ID de usuario.
     */
    public Cliente obtenerClientePorId(int codigoUsuario) {
        if (conn == null) {
            System.err.println("DAO (Cliente): No se puede ejecutar la consulta, la conexión es NULL.");
            return null;
        }
        
        String sql = "SELECT * FROM cliente WHERE codigo_usuario = ?";
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, codigoUsuario);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    Cliente cliente = new Cliente();
                    cliente.setCodigoUsuario(rs.getInt("codigo_usuario"));
                    cliente.setPrimerNombre(rs.getString("primer_nombre"));
                    cliente.setSegundoNombre(rs.getString("segundo_nombre"));
                    cliente.setPrimerApellido(rs.getString("primer_apellido"));
                    cliente.setSegundoApellido(rs.getString("segundo_apellido"));
                    cliente.setCodigoSexo(rs.getInt("codigo_sexo"));
                    cliente.setFechaNacimiento(rs.getDate("fecha_nacimiento"));
                    // Leer peso_objetivo si existe
                    try { Object pesoObj = rs.getObject("peso_objetivo"); if (pesoObj != null) { if (pesoObj instanceof java.math.BigDecimal) { cliente.setPesoObjetivo(((java.math.BigDecimal) pesoObj).doubleValue()); } else if (pesoObj instanceof Double) { cliente.setPesoObjetivo((Double) pesoObj); } else if (pesoObj instanceof Number) { cliente.setPesoObjetivo(((Number) pesoObj).doubleValue()); } } } catch (SQLException ignore) {}
                    return cliente;
                }
            }
        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Cliente - obtenerClientePorId)!!");
            e.printStackTrace();
        }
        return null; // No se encontró
    }
    
    /**
     * ¡¡NUEVO MÉTODO!!
     * Actualiza los datos de un cliente en la base de datos.
     * @param cliente El objeto Cliente con los nuevos datos y el codigo_usuario.
     * @return true si la actualización fue exitosa, false en caso contrario.
     */
    public boolean actualizarCliente(Cliente cliente) throws SQLException {
        if (conn == null) throw new SQLException("La conexión a la base de datos es nula.");
        
        String sql = "UPDATE cliente SET " +
                     "primer_nombre = ?, " +
                     "segundo_nombre = ?, " +
                     "primer_apellido = ?, " +
                     "segundo_apellido = ?, " +
                     "fecha_nacimiento = ? " +
                     "WHERE codigo_usuario = ?";
        
        System.out.println("DAO (Cliente): Actualizando perfil para usuario ID: " + cliente.getCodigoUsuario());

        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, cliente.getPrimerNombre());
            stmt.setString(2, cliente.getSegundoNombre());
            stmt.setString(3, cliente.getPrimerApellido());
            stmt.setString(4, cliente.getSegundoApellido());
            stmt.setDate(5, cliente.getFechaNacimiento());
            stmt.setInt(6, cliente.getCodigoUsuario()); // ID para el WHERE

            int filasAfectadas = stmt.executeUpdate();
            return filasAfectadas > 0;
        }
    }

    // --- NUEVO: Get/Set Peso Objetivo ---
    public Double obtenerPesoObjetivo(int codigoUsuario) {
        if (conn == null) return null;
        String sql = "SELECT peso_objetivo FROM cliente WHERE codigo_usuario = ?";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, codigoUsuario);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    // MySQL normalmente devuelve BigDecimal para DECIMAL. Evitamos ClassCastException.
                    Object raw = rs.getObject(1);
                    if (raw == null) {
                        System.out.println("DAO(Cliente): peso_objetivo=NULL para usuario=" + codigoUsuario);
                        return null;
                    }
                    if (raw instanceof Number) {
                        double val = ((Number) raw).doubleValue();
                        System.out.println("DAO(Cliente): peso_objetivo leído=" + val + " para usuario=" + codigoUsuario);
                        return val;
                    }
                    try {
                        double parsed = Double.parseDouble(raw.toString());
                        System.out.println("DAO(Cliente): peso_objetivo parseado=" + parsed + " para usuario=" + codigoUsuario);
                        return parsed;
                    } catch (NumberFormatException nfe) {
                        System.err.println("DAO(Cliente): No se pudo parsear peso_objetivo ('" + raw + "') para usuario=" + codigoUsuario);
                        return null;
                    }
                }
            }
        } catch (SQLException e) {
            System.err.println("DAO(Cliente): Error obteniendo peso_objetivo: " + e.getMessage());
        }
        return null;
    }

    public boolean actualizarPesoObjetivo(int codigoUsuario, double pesoObjetivo) {
        if (conn == null) return false;
        String sql = "UPDATE cliente SET peso_objetivo = ? WHERE codigo_usuario = ?";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setDouble(1, pesoObjetivo);
            ps.setInt(2, codigoUsuario);
            int rows = ps.executeUpdate();
            System.out.println("DAO(Cliente): actualizarPesoObjetivo filas afectadas=" + rows);
            return rows > 0;
        } catch (SQLException e) {
            System.err.println("DAO(Cliente): Error actualizando peso_objetivo: " + e.getMessage());
            return false;
        }
    }
    
}
