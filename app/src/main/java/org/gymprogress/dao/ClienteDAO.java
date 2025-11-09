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
    
}