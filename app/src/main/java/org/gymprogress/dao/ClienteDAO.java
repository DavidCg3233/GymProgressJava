package org.gymprogress.dao;

import org.gymprogress.model.Cliente;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Esta clase se usará para futuras operaciones
 * como "Obtener Perfil" o "Actualizar Perfil".
 * NO se usa para el registro inicial.
 */
public class ClienteDAO {

    private Connection conn;

    public ClienteDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en ClienteDAO!! La conexión a la BD (conn) es NULL.");
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
                    return cliente;
                }
            }
        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Cliente - obtenerClientePorId)!!");
            e.printStackTrace();
        }
        return null; // No se encontró
    }
    
    // Aquí irían métodos como actualizarCliente(Cliente cliente), etc.
}