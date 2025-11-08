package org.gymprogress.controller;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import netscape.javascript.JSObject; 
import org.gymprogress.dao.UsuarioDAO; // Importamos el DAO
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Usuario;

import java.net.URL;
import java.sql.Date;
import java.time.LocalDate;
import java.util.ResourceBundle;

/**
 * Esta clase ahora actúa como el Controlador FXML Y como el Puente de Java.
 */
public class MainAppController implements Initializable {

    @FXML
    private WebView webView; 
    private WebEngine webEngine;
    
    // 1. Traemos el DAO aquí
    private UsuarioDAO usuarioDAO;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        
        System.out.println("MainAppController: Inicializando...");
        try {
            // 2. Inicializamos el DAO aquí
            this.usuarioDAO = new UsuarioDAO();
            System.out.println("MainAppController: UsuarioDAO inicializado.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al crear UsuarioDAO en MainAppController!!");
            e.printStackTrace();
            return; // No continuar si el DAO falla
        }

        webEngine = webView.getEngine();
        webEngine.setJavaScriptEnabled(true);

        URL htmlUrl = getClass().getResource("/webapp/index.html");
        if (htmlUrl == null) {
            System.err.println("¡¡ERROR FATAL!! No se pudo encontrar /webapp/index.html");
            webEngine.loadContent("<h1>Error: /webapp/index.html no encontrado.</h1>");
            return;
        }
        
        String urlConCacheBuster = htmlUrl.toExternalForm() + "?v=" + System.currentTimeMillis();
        System.out.println("MainAppController: Cargando URL: " + urlConCacheBuster);
        
        webEngine.load(urlConCacheBuster); 

        // 3. ¡EL NUEVO PUENTE!
        webEngine.getLoadWorker().stateProperty().addListener(
            (obs, oldState, newState) -> {
                if (newState == javafx.concurrent.Worker.State.SUCCEEDED) {
                    
                    System.out.println("MainAppController: ¡Página cargada! Inyectando puente...");
                    JSObject jsWindow = (JSObject) webEngine.executeScript("window");
                    
                    // 4. Inyectamos "ESTA CLASE" (this) como el "javaBridge"
                    jsWindow.setMember("javaBridge", this);
                    
                    System.out.println("CONTROLADOR: MainAppController inyectado en JavaScript como 'javaBridge'.");
                    
                    webEngine.setOnAlert(event -> System.out.println("Alerta JS: " + event.getData()));
                }
            }
        );
    }

    // =================================================================
    // MÉTODOS DEL PUENTE (Copiados de la antigua clase JavaBridge)
    // ¡JavaScript llamará a estos métodos!
    // =================================================================

    public String login(String email, String contrasena) {
        System.out.println("MainAppController(Bridge): Solicitud de login para: " + email);
        try {
            Usuario usuario = usuarioDAO.validarUsuario(email, contrasena);
            if (usuario != null) {
                System.out.println("MainAppController(Bridge): ¡Éxito! Usuario encontrado: " + usuario.getNombreUsuario());
                return usuario.getNombreUsuario();
            } else {
                System.err.println("MainAppController(Bridge): Fallo. El DAO devolvió null.");
                return "";
            }
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL EN MainAppController(Bridge) (LOGIN)!!");
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

        System.out.println("MainAppController(Bridge): Solicitud de registro para: " + email);
        try {
            
            if (fechaNacimientoStr == null || fechaNacimientoStr.isEmpty()) {
                System.err.println("MainAppController(Bridge): ¡Validación fallida! La fecha de nacimiento llegó vacía.");
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

            System.out.println("MainAppController(Bridge): Datos preparados. Llamando al DAO...");
            boolean daoExito = usuarioDAO.registrarUsuarioCompleto(usuario, cliente, progreso);
            
            System.out.println("MainAppController(Bridge): El DAO respondió: " + daoExito);
            return daoExito;

        } catch (IllegalArgumentException e) {
             System.err.println("¡¡ERROR DE FORMATO DE FECHA EN MainAppController(Bridge) (REGISTRO)!!");
             System.err.println("El JS envió una fecha que 'Date.valueOf' no pudo parsear: " + fechaNacimientoStr);
             e.printStackTrace();
             return false;
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL EN MainAppController(Bridge) (REGISTRO)!!");
            e.printStackTrace();
            return false;
        }
    }
    
    public void saludarDesdeJS(String mensaje) {
        System.out.println("JS dice: " + mensaje);
    }
}