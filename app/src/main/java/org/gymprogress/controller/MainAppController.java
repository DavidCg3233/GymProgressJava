// Archivo: MainAppController.java
// (Versión 4 - Sincronizada y Corregida)

package org.gymprogress.controller;

// package org.gymprogress.controller;
import javafx.scene.control.Alert; // <-- ¡AÑADE ESTA LÍNEA!
import javafx.scene.control.Alert.AlertType; // <-- ¡AÑADE ESTA LÍNEA!
import javafx.fxml.FXML;
// ... (todos tus otros imports)
import javafx.stage.Stage;
import javafx.fxml.Initializable;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import netscape.javascript.JSObject;

import org.gymprogress.dao.RutinaDAO; // ¡NUEVO!
import org.gymprogress.dao.UsuarioDAO;
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Rutina; // ¡NUEVO!
import org.gymprogress.model.Usuario;

import java.net.URL;
import java.sql.Date;
import java.time.LocalDate;
import java.util.List; // ¡NUEVO!
import java.util.Random; // ¡NUEVO!
import java.util.ResourceBundle;
import javafx.application.Platform;
import javafx.scene.control.TextInputDialog;
import java.util.Optional;


/**
 * Esta clase actúa como el Controlador FXML
 * Y TAMBIÉN como el "Puente" de JavaScript (javaBridge)
 */
public class MainAppController implements Initializable {

    @FXML
    private WebView webView;
    private WebEngine webEngine;

    // DAOs
    private UsuarioDAO usuarioDAO;
    private RutinaDAO rutinaDAO; // ¡NUEVO!

    // Estado de la Sesión
    private Usuario usuarioLogueado;
    
    // --- ¡¡NUEVO!! ---
    // Variable para guardar la ventana principal
    private Stage mainStage; 
    
    /**
     * ¡¡NUEVO!! - Llamado por Main.java para inyectar el Stage
     */
    public void setStage(Stage stage) {
        this.mainStage = stage;
        System.out.println("MainAppController: ¡Stage principal inyectado exitosamente!");
    }
    // --- FIN ---


    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("MainAppController: Inicializando...");
        
        try {
            this.usuarioDAO = new UsuarioDAO();
            this.rutinaDAO = new RutinaDAO(); // ¡NUEVO!
            System.out.println("MainAppController: DAOs (Usuario y Rutina) inicializados.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al inicializar DAOs en MainAppController!!");
            e.printStackTrace();
        }

        webEngine = webView.getEngine();
        
        // (Quitamos el PromptHandler intencionalmente para evitar crashes)
        
        webEngine.setConfirmHandler(message -> {
            System.out.println("JS pide confirmación: " + message);
            return true; // Simple confirmación
        });

        // Carga de la página (con parámetro anti-caché)
        try {
            Random random = new Random();
            URL indexUrl = getClass().getResource("/webapp/index.html");
            if (indexUrl == null) {
                System.err.println("¡¡ERROR FATAL!! No se encontró /webapp/index.html");
                return;
            }
            String urlConAntiCache = indexUrl.toExternalForm() + "?v=" + random.nextLong();
            System.out.println("MainAppController: Cargando URL: " + urlConAntiCache);
            webEngine.load(urlConAntiCache);
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Configuración del "Puente" (JavaBridge)
        webEngine.getLoadWorker().stateProperty().addListener(
            (ov, oldState, newState) -> {
                if (newState == javafx.concurrent.Worker.State.SUCCEEDED) {
                    System.out.println("MainAppController: ¡Página cargada! Inyectando puente...");
                    JSObject window = (JSObject) webEngine.executeScript("window");
                    window.setMember("javaBridge", this);
                    
                    try {
                        webEngine.executeScript("if (typeof javaBridgeReady === 'function') { javaBridgeReady(); }");
                        System.out.println("CONTROLADOR: MainAppController inyectado en JavaScript como 'javaBridge'.");
                    } catch (Exception e) {
                        System.err.println("Advertencia: no se pudo llamar a javaBridgeReady(). " + e.getMessage());
                    }
                }
            }
        );
    }
    
    // ==================================================================
    // MÉTODOS DEL PUENTE (Llamados desde JavaScript)
    // ==================================================================

    /**
     * Utilidad para recibir logs desde JS.
     */
    public void logDesdeJS(String mensaje) {
        System.out.println("Consola JS: " + mensaje);
    }

    /**
     * RF01/RF02 (Login): Llamado desde index.html
     */
    public String login(String email, String contrasena) {
        System.out.println("MainAppController(Bridge): Solicitud de login para: " + email);
        try {
            this.usuarioLogueado = usuarioDAO.validarUsuario(email, contrasena);
            if (this.usuarioLogueado != null) {
                System.out.println("MainAppController(Bridge): ¡Éxito! Usuario encontrado: " + this.usuarioLogueado.getNombreUsuario());
                return this.usuarioLogueado.getNombreUsuario(); 
            } else {
                System.err.println("MainAppController(Bridge): ¡Fallo! Usuario o contraseña incorrectos.");
                return null;
            }
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en MainAppController (Login)!!");
            e.printStackTrace();
            return null;
        }
    }
    
    // --- ¡¡FUNCIÓN AÑADIDA!! (Para solucionar Error 1 del dashboard) ---
    /**
     * Llamado por dashboard.html para obtener el nombre del usuario
     * que se guardó durante el login.
     */
    public String getNombreUsuarioLogueado() {
        if (this.usuarioLogueado != null) {
            return this.usuarioLogueado.getNombreUsuario();
        }
        System.err.println("MainAppController(Bridge-GetNombre): Se pidió el nombre, pero 'usuarioLogueado' es NULL.");
        return null;
    }
    
    /**
     * RF01 (Registro): Llamado desde index.html
     */
    public boolean registrarUsuario(String nombreUsuario, String email, String contrasena, 
                                   String pNombre, String sNombre, String pApellido, String sApellido, 
                                   int sexo, String fechaNac, 
                                   double peso, double altura) {
        
        System.out.println("MainAppController(Bridge): Solicitud de registro para: " + email);
        try {
            Usuario u = new Usuario();
            u.setNombreUsuario(nombreUsuario);
            u.setEmail(email);
            u.setContrasena(contrasena); 
            u.setFechaCreacion(Date.valueOf(LocalDate.now()));

            Cliente c = new Cliente();
            c.setPrimerNombre(pNombre);
            c.setSegundoNombre(sNombre);
            c.setPrimerApellido(pApellido);
            c.setSegundoApellido(sApellido);
            c.setCodigoSexo(sexo);
            c.setFechaNacimiento(Date.valueOf(fechaNac)); 

            Progreso p = new Progreso();
            p.setFecha(Date.valueOf(LocalDate.now()));
            p.setPesoCorporal(peso);
            p.setAltura(altura);

            return usuarioDAO.registrarNuevoUsuarioCompleto(u, c, p);
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en MainAppController (Registro)!!");
            e.printStackTrace();
            return false;
        }
    }

    // --- ¡¡NOMBRE CORREGIDO!! (Para solucionar Error 2 del dashboard) ---
    /**
     * RF03: Llamado desde dashboard.html para cargar la lista de rutinas.
     */
    public String getRutinasDelUsuarioJSON() {
        if (this.usuarioLogueado == null) {
            System.err.println("MainAppController(Bridge-GetRutinas): ¡ERROR! No hay usuario logueado.");
            return "[]"; // Devuelve un JSON array vacío
        }
        
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario(); 
        System.out.println("MainAppController(Bridge): Buscando rutinas para el usuario: " + codigoUsuario);
        
        try {
            List<Rutina> rutinas = rutinaDAO.getRutinasPorUsuario(codigoUsuario);
            System.out.println("DAO (Rutina): Encontradas " + rutinas.size() + " rutinas para el usuario " + codigoUsuario);
            
            if (rutinas.isEmpty()) return "[]";
            
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
            System.err.println("¡¡ERROR FATAL en MainAppController (getRutinasDelUsuarioJSON)!!");
            e.printStackTrace();
            return "[]";
        }
    }

    /**
     * RF03 (Crear): Llamado internamente por 'solicitarCreacionRutina'.
     */
    public boolean crearNuevaRutina(String nombreRutina, String descripcion) {
        if (this.usuarioLogueado == null) {
            System.err.println("MainAppController(Bridge-CrearRutina): ¡ERROR! No hay usuario logueado.");
            return false;
        }
        if (nombreRutina == null || nombreRutina.trim().isEmpty()) {
            System.err.println("MainAppController(Bridge-CrearRutina): ¡ERROR! El nombre de la rutina está vacío.");
            return false;
        }
        
        System.out.println("MainAppController(Bridge-CrearRutina): Solicitud para crear rutina: " + nombreRutina);
        
        try {
            Rutina nuevaRutina = new Rutina();
            nuevaRutina.setCodigoUsuario(this.usuarioLogueado.getCodigoUsuario()); 
            nuevaRutina.setNombreRutina(nombreRutina.trim());
            nuevaRutina.setDescripcion(descripcion != null ? descripcion : "");
            nuevaRutina.setFechaCreacion(Date.valueOf(LocalDate.now())); 

            return rutinaDAO.crearRutina(nuevaRutina);
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en MainAppController (crearNuevaRutina)!!");
            e.printStackTrace();
            return false;
        }
    }
    
    // ==================================================================
    // MÉTODO ASÍNCRONO PARA "CREAR RUTINA"
    // (Este código ya lo tenías, me aseguro de que esté bien)
    // ==================================================================
    public void solicitarCreacionRutina() {
        System.out.println("MainAppController(Bridge): JS solicita crear una rutina. Mostrando diálogo...");
        
        Platform.runLater(() -> {
            TextInputDialog dialogNombre = new TextInputDialog();
            dialogNombre.setTitle("Crear Nueva Rutina");
            dialogNombre.setHeaderText("Ingresa el nombre para tu nueva rutina:");
            dialogNombre.setContentText("Nombre:");
            if (this.mainStage != null) dialogNombre.initOwner(this.mainStage);
            
            Optional<String> resultNombre = dialogNombre.showAndWait();
            
            if (resultNombre.isPresent() && !resultNombre.get().trim().isEmpty()) {
                String nombreRutina = resultNombre.get().trim();
                System.out.println("MainAppController(Dialog): Nombre obtenido: " + nombreRutina);
                
                TextInputDialog dialogDesc = new TextInputDialog();
                dialogDesc.setTitle("Crear Nueva Rutina");
                dialogDesc.setHeaderText("Ingresa una descripción (opcional):");
                dialogDesc.setContentText("Descripción:");
                if (this.mainStage != null) dialogDesc.initOwner(this.mainStage);
                
                Optional<String> resultDesc = dialogDesc.showAndWait();
                String descripcion = resultDesc.orElse(""); 

                boolean exito = this.crearNuevaRutina(nombreRutina, descripcion);
                
                if (exito) {
                    System.out.println("MainAppController(Dialog): Rutina creada. Refrescando JS...");
                    webEngine.executeScript("cargarMisRutinas();");
                    
                    Alert alert = new Alert(AlertType.INFORMATION);
                    alert.setTitle("Éxito");
                    alert.setHeaderText("Rutina creada exitosamente.");
                    if (this.mainStage != null) alert.initOwner(this.mainStage);
                    alert.showAndWait();
                } else {
                    System.err.println("MainAppController(Dialog): Falló la creación (DAO devolvió false).");
                    Alert alert = new Alert(AlertType.ERROR);
                    alert.setTitle("Error");
                    alert.setHeaderText("No se pudo crear la rutina.");
                    if (this.mainStage != null) alert.initOwner(this.mainStage);
                    alert.showAndWait();
                }
            } else {
                System.out.println("MainAppController(Dialog): El usuario canceló o dejó el nombre vacío.");
            }
        });
    }

    /**
     * Utilidad para escapar JSON manualmente.
     */
    private String escapeJSON(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\")
                   .replace("\"", "\\\"")
                   .replace("\n", "\\n")
                   .replace("\r", "\\r")
                   .replace("\t", "\\t");
    }
}