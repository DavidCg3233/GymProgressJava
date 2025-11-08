package org.gymprogress.bridge;

import org.gymprogress.dao.UsuarioDAO;
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Usuario;

import java.sql.Date;
import java.time.LocalDate;

public class JavaBridge {

    private UsuarioDAO usuarioDAO;

    public JavaBridge() {
        System.out.println("BRIDGE: Creando una nueva instancia de JavaBridge...");
        try {
            this.usuarioDAO = new UsuarioDAO();
            System.out.println("BRIDGE: UsuarioDAO inicializado.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al crear JavaBridge!!");
            e.printStackTrace();
        }
    }

    public String login(String email, String contrasena) {
        System.out.println("BRIDGE: Solicitud de login para: " + email);
        try {
            Usuario usuario = usuarioDAO.validarUsuario(email, contrasena);
            if (usuario != null) {
                System.out.println("BRIDGE (Login): ¡Éxito! Usuario encontrado: " + usuario.getNombreUsuario());
                return usuario.getNombreUsuario();
            } else {
                System.err.println("BRIDGE (Login): Fallo. El DAO devolvió null.");
                return "";
            }
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL EN BRIDGE (LOGIN)!!");
            e.printStackTrace(); 
            return "";
        }
    }

    public boolean registrarUsuario(
            String nombreUsuario, String email, String contrasena,
            String primerNombre, String segundoNombre,
            String primerApellido, String segundoApellido,
            int codigoSexo, String fechaNacimientoStr,
            double pesoInicial, double alturaInicial) {

        

        System.out.println("BRIDGE: Solicitud de registro para: " + email);
        try {
            
            // =========================================================
            // ¡¡AQUÍ ESTÁ LA CORRECCIÓN DE "DOBLE SEGURO"!!
            // (La línea 79 de tu log fallaba por esto)
            // =========================================================
            if (fechaNacimientoStr == null || fechaNacimientoStr.isEmpty()) {
                System.err.println("BRIDGE (Registro): ¡Validación fallida! La fecha de nacimiento llegó vacía.");
                return false; // Devuelve 'false' y evita el crash
            }
            // =========================================================

            Usuario usuario = new Usuario();
            usuario.setNombreUsuario(nombreUsuario);
            usuario.setEmail(email);
            usuario.setContrasena(contrasena);
            usuario.setFechaCreacion(Date.valueOf(LocalDate.now()));

            Cliente cliente = new Cliente();
            cliente.setPrimerNombre(primerNombre);
            cliente.setSegundoNombre(segundoNombre);
            cliente.setPrimerApellido(primerApellido);
            cliente.setSegundoApellido(segundoApellido);
            cliente.setCodigoSexo(codigoSexo);
            
            // Esta línea (la antigua línea 79) ahora es segura
            cliente.setFechaNacimiento(Date.valueOf(fechaNacimientoStr)); 

            Progreso progreso = new Progreso();
            progreso.setFecha(Date.valueOf(LocalDate.now()));
            progreso.setPesoCorporal(pesoInicial);
            progreso.setAltura(alturaInicial);

            System.out.println("BRIDGE (Registro): Datos preparados. Llamando al DAO...");
            boolean daoExito = usuarioDAO.registrarUsuarioCompleto(usuario, cliente, progreso);
            
            System.out.println("BRIDGE (Registro): El DAO respondió: " + daoExito);
            return daoExito;

        } catch (IllegalArgumentException e) {
             // Capturamos el error específico de 'Date.valueOf'
             System.err.println("¡¡ERROR DE FORMATO DE FECHA EN BRIDGE (REGISTRO)!!");
             System.err.println("El JS envió una fecha que 'Date.valueOf' no pudo parsear: " + fechaNacimientoStr);
             e.printStackTrace();
             return false;
        } catch (Exception e) {
            // (Si falla por cualquier otra razón, aún lo veremos aquí)
            System.err.println("¡¡ERROR FATAL EN BRIDGE (REGISTRO)!!");
            e.printStackTrace();
            return false;
        }
    }
    
    public void saludarDesdeJS(String mensaje) {
        System.out.println("JS dice: " + mensaje);
    }
}