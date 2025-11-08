package org.gymprogress.dao; // <-- ¡Paquete Corregido!

import org.gymprogress.model.Cliente; // <-- ¡Paquete Corregido!
import org.gymprogress.model.Progreso; // <-- ¡Paquete Corregido!
import org.gymprogress.model.Usuario; // <-- ¡Paquete Corregido!

import java.sql.*;

public class UsuarioDAO {

    private Connection conn;

    public UsuarioDAO() {
        System.out.println("DAO: Creando una nueva instancia de UsuarioDAO...");
        this.conn = ConexionDB.getConnection();
        
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en UsuarioDAO!! La conexión a la BD (conn) es NULL.");
        } else {
            System.out.println("DAO: Conexión obtenida exitosamente.");
        }
    }

    public Usuario validarUsuario(String email, String contrasena) throws SQLException {
        if (conn == null) {
            System.err.println("DAO (Login): No se puede ejecutar la consulta, la conexión es NULL.");
            throw new SQLException("La conexión a la base de datos es nula.");
        }

        String sql = "SELECT * FROM usuario WHERE email = ? AND contrasena = ?";
        System.out.println("DAO (Login): Ejecutando consulta: " + sql);
        
        try (PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, email);
            stmt.setString(2, contrasena);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) { 
                    Usuario user = new Usuario();
                    user.setCodigoUsuario(rs.getInt("codigo_usuario"));
                    user.setNombreUsuario(rs.getString("nombre_usuario"));
                    user.setEmail(rs.getString("email"));
                    user.setFechaCreacion(rs.getDate("fecha_creacion"));
                    System.out.println("DAO (Login): Usuario validado -> " + user.getEmail());
                    return user;
                } else {
                    System.out.println("DAO (Login): Consulta exitosa, pero no se encontró el usuario.");
                    return null;
                }
            }
        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Login)!!");
            e.printStackTrace(); 
            throw e; 
        }
    }

    public boolean registrarUsuarioCompleto(Usuario usuario, Cliente cliente, Progreso progreso) {
        
        if (conn == null) {
            System.err.println("DAO (Registro): No se puede ejecutar la transacción, la conexión es NULL.");
            return false;
        }

        String sqlUsuario = "INSERT INTO usuario (nombre_usuario, email, fecha_creacion, contrasena) VALUES (?, ?, ?, ?)";
        String sqlCliente = "INSERT INTO cliente (codigo_usuario, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, codigo_sexo, fecha_nacimiento) VALUES (?, ?, ?, ?, ?, ?, ?)";
        String sqlProgreso = "INSERT INTO progreso (codigo_usuario, fecha, peso_corporal, altura, notas) VALUES (?, ?, ?, ?, ?)";
        
        ResultSet generatedKeys = null;
        try {
            System.out.println("DAO (Registro): Iniciando transacción...");
            conn.setAutoCommit(false); 

            // 1. Insertar en 'usuario'
            System.out.println("DAO (Registro): Paso 1/3 - Insertando usuario...");
            int codigoUsuarioGenerado = 0;
            try (PreparedStatement stmtUsuario = conn.prepareStatement(sqlUsuario, Statement.RETURN_GENERATED_KEYS)) {
                stmtUsuario.setString(1, usuario.getNombreUsuario());
                stmtUsuario.setString(2, usuario.getEmail());
                stmtUsuario.setDate(3, usuario.getFechaCreacion());
                stmtUsuario.setString(4, usuario.getContrasena());
                stmtUsuario.executeUpdate();

                generatedKeys = stmtUsuario.getGeneratedKeys();
                if (generatedKeys.next()) {
                    codigoUsuarioGenerado = generatedKeys.getInt(1);
                    System.out.println("DAO (Registro): Usuario insertado. ID generado: " + codigoUsuarioGenerado);
                } else {
                    throw new SQLException("No se pudo obtener el ID del usuario creado.");
                }
            }
            
            // 2. Insertar en 'cliente'
            System.out.println("DAO (Registro): Paso 2/3 - Insertando cliente...");
            try (PreparedStatement stmtCliente = conn.prepareStatement(sqlCliente)) {
                stmtCliente.setInt(1, codigoUsuarioGenerado);
                stmtCliente.setString(2, cliente.getPrimerNombre());
                stmtCliente.setString(3, cliente.getSegundoNombre());
                stmtCliente.setString(4, cliente.getPrimerApellido());
                stmtCliente.setString(5, cliente.getSegundoApellido());
                stmtCliente.setInt(6, cliente.getCodigoSexo());
                stmtCliente.setDate(7, cliente.getFechaNacimiento());
                stmtCliente.executeUpdate();
            }

            // 3. Insertar en 'progreso'
            System.out.println("DAO (Registro): Paso 3/3 - Insertando progreso inicial...");
            try (PreparedStatement stmtProgreso = conn.prepareStatement(sqlProgreso)) {
                stmtProgreso.setInt(1, codigoUsuarioGenerado);
                stmtProgreso.setDate(2, progreso.getFecha());
                stmtProgreso.setDouble(3, progreso.getPesoCorporal());
                stmtProgreso.setDouble(4, progreso.getAltura());
                stmtProgreso.setString(5, "Registro inicial.");
                stmtProgreso.executeUpdate();
            }

            conn.commit(); 
            System.out.println("DAO (Registro): ¡Transacción exitosa! Commit realizado.");
            return true;

        } catch (SQLException e) {
            System.err.println("¡¡ERROR SQL en DAO (Registro)!! Haciendo rollback...");
            e.printStackTrace(); 
            try {
                conn.rollback();
            } catch (SQLException ex) {
                System.err.println("¡¡ERROR FATAL al hacer rollback!!");
                ex.printStackTrace();
            }
            return false;
        } finally {
            try {
                conn.setAutoCommit(true); 
                if (generatedKeys != null) generatedKeys.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}