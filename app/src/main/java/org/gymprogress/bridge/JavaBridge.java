package org.gymprogress.bridge;

import org.gymprogress.dao.RutinaDAO;
import org.gymprogress.dao.UsuarioDAO;
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Rutina;
import org.gymprogress.model.Usuario;

import java.sql.Date;
import java.time.LocalDate;

public class JavaBridge {

    private UsuarioDAO usuarioDAO;
    private RutinaDAO rutinaDAO;
    private Usuario usuarioLogueado;

    public JavaBridge() {
        System.out.println("BRIDGE: Creando una nueva instancia de JavaBridge...");
        try {
            this.usuarioDAO = new UsuarioDAO();
            this.rutinaDAO = new RutinaDAO();
            System.out.println("BRIDGE: UsuarioDAO y RutinaDAO inicializados.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al crear JavaBridge!!");
            e.printStackTrace();
        }
    }

    public String login(String email, String contrasena) {
        System.out.println("BRIDGE: Solicitud de login para: " + email);
        try {
            this.usuarioLogueado = usuarioDAO.validarUsuario(email, contrasena);
            if (this.usuarioLogueado != null) {
                System.out.println("BRIDGE (Login): ¡Éxito! Usuario encontrado: " + this.usuarioLogueado.getNombreUsuario());
                return this.usuarioLogueado.getNombreUsuario();
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
            if (fechaNacimientoStr == null || fechaNacimientoStr.isEmpty()) {
                System.err.println("BRIDGE (Registro): ¡Validación fallida! La fecha de nacimiento llegó vacía.");
                return false;
            }

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
            cliente.setFechaNacimiento(Date.valueOf(fechaNacimientoStr));

            Progreso progreso = new Progreso();
            progreso.setFecha(Date.valueOf(LocalDate.now()));
            progreso.setPesoCorporal(pesoInicial);
            progreso.setAltura(alturaInicial);

            System.out.println("BRIDGE (Registro): Datos preparados. Llamando al DAO...");
            boolean daoExito = usuarioDAO.registrarNuevoUsuarioCompleto(usuario, cliente, progreso);
            
            System.out.println("BRIDGE (Registro): El DAO respondió: " + daoExito);
            return daoExito;

        } catch (IllegalArgumentException e) {
            System.err.println("¡¡ERROR DE FORMATO DE FECHA EN BRIDGE (REGISTRO)!!");
            System.err.println("El JS envió una fecha que 'Date.valueOf' no pudo parsear: " + fechaNacimientoStr);
            e.printStackTrace();
            return false;
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL EN BRIDGE (REGISTRO)!!");
            e.printStackTrace();
            return false;
        }
    }
    
    public void saludarDesdeJS(String mensaje) {
        System.out.println("JS dice: " + mensaje);
    }

    public void logDesdeJS(String mensaje) {
        if (mensaje.toLowerCase().contains("error")) {
            System.err.println("JS Error: " + mensaje);
        } else {
            System.out.println("JS Log: " + mensaje);
        }
    }

    public String getNombreUsuarioLogueado() {
        if (this.usuarioLogueado != null) {
            return this.usuarioLogueado.getNombreUsuario();
        }
        System.err.println("JavaBridge: getNombreUsuarioLogueado() - ¡No hay usuario logueado!");
        return "Usuario";
    }

    public boolean crearNuevaRutina(String nombreRutina, String descripcion) {
        System.out.println("BRIDGE (CrearRutina): Iniciando creación de rutina...");
        
        try {
            // 1. Validar usuario logueado
            if (this.usuarioLogueado == null) {
                System.err.println("BRIDGE (CrearRutina): ¡ERROR! No hay usuario logueado.");
                return false;
            }
            System.out.println("BRIDGE (CrearRutina): Usuario validado: " + this.usuarioLogueado.getNombreUsuario());

            // 2. Validar parámetros
            if (nombreRutina == null || nombreRutina.trim().isEmpty()) {
                System.err.println("BRIDGE (CrearRutina): ¡ERROR! El nombre de la rutina está vacío.");
                return false;
            }
            System.out.println("BRIDGE (CrearRutina): Nombre rutina válido: " + nombreRutina);

            // 3. Validar conexión y DAO
            if (rutinaDAO == null) {
                System.err.println("BRIDGE (CrearRutina): ¡ERROR! RutinaDAO es null");
                return false;
            }
            
            // 4. Crear objeto Rutina
            Rutina nuevaRutina = new Rutina();
            nuevaRutina.setCodigoUsuario(this.usuarioLogueado.getCodigoUsuario());
            nuevaRutina.setNombreRutina(nombreRutina.trim());
            nuevaRutina.setDescripcion(descripcion != null ? descripcion.trim() : "");
            nuevaRutina.setFechaCreacion(Date.valueOf(LocalDate.now()));
            
            System.out.println("BRIDGE (CrearRutina): Objeto Rutina creado, intentando guardar en BD...");
            
            // 5. Intentar crear en la base de datos
            boolean resultado = rutinaDAO.crearRutina(nuevaRutina);
            
            if (resultado) {
                System.out.println("BRIDGE (CrearRutina): ¡Rutina creada exitosamente!");
            } else {
                System.err.println("BRIDGE (CrearRutina): La creación falló en el DAO");
            }
            
            return resultado;

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en BRIDGE (crearNuevaRutina)!!");
            System.err.println("Detalles del error: " + e.getMessage());
            System.err.println("Causa: " + (e.getCause() != null ? e.getCause().getMessage() : "Desconocida"));
            e.printStackTrace();
            return false;
        }
    }

    public String getRutinasDelUsuarioJSON() {
        if (this.usuarioLogueado == null) {
            System.err.println("BRIDGE (getRutinasDelUsuarioJSON): ¡ERROR! No hay usuario logueado.");
            return "[]";
        }
        
        try {
            System.out.println("BRIDGE: Obteniendo rutinas para usuario: " + this.usuarioLogueado.getNombreUsuario());
            java.util.List<Rutina> rutinas = rutinaDAO.getRutinasPorUsuario(this.usuarioLogueado.getCodigoUsuario());
            
            if (rutinas == null || rutinas.isEmpty()) {
                System.out.println("BRIDGE: No se encontraron rutinas para el usuario.");
                return "[]";
            }

            StringBuilder jsonBuilder = new StringBuilder("[");
            boolean first = true;
            
            for (Rutina rutina : rutinas) {
                if (!first) jsonBuilder.append(",");
                jsonBuilder.append("{")
                          .append("\"codigoRutina\":").append(rutina.getCodigoRutina()).append(",")
                          .append("\"nombreRutina\":\"").append(escapeJSON(rutina.getNombreRutina())).append("\",")
                          .append("\"descripcion\":\"").append(escapeJSON(rutina.getDescripcion())).append("\",")
                          .append("\"fechaCreacion\":\"").append(rutina.getFechaCreacion()).append("\"")
                          .append("}");
                first = false;
            }
            
            jsonBuilder.append("]");
            return jsonBuilder.toString();

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en BRIDGE (getRutinasDelUsuarioJSON)!!");
            e.printStackTrace();
            return "[]";
        }
    }

    private String escapeJSON(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\")
                   .replace("\"", "\\\"")
                   .replace("\b", "\\b")
                   .replace("\f", "\\f")
                   .replace("\n", "\\n")
                   .replace("\r", "\\r")
                   .replace("\t", "\\t");
    }
}