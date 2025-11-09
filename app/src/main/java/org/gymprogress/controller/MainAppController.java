// Archivo: MainAppController.java
// (Versión 6 - FINAL CON RF03 y RF04/RF05)

package org.gymprogress.controller;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import netscape.javascript.JSObject;

// DAOs
import org.gymprogress.dao.RutinaDAO; 
import org.gymprogress.dao.UsuarioDAO;
import org.gymprogress.dao.EjercicioDAO;
import org.gymprogress.dao.RutinaEjercicioDAO;
import org.gymprogress.dao.ProgresoDAO; // <-- ¡NUEVO!
import org.gymprogress.dao.ConexionDB;

// Models
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Rutina; 
import org.gymprogress.model.Usuario;
import org.gymprogress.model.RutinaEjercicioDTO;

// Utils
import org.gymprogress.utils.CalculoIMC; // <-- ¡NUEVO!

import java.net.URL;
import java.sql.Connection;
import java.sql.Date;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter; // <-- ¡NUEVO!
import java.util.List; 
import java.util.Random; 
import java.util.ResourceBundle;
import java.util.Map; // <-- ¡NUEVO!
import java.util.HashMap; // <-- ¡NUEVO!

// JavaFX
import javafx.application.Platform;
import javafx.scene.control.TextInputDialog;
import javafx.scene.control.Alert;
import javafx.scene.control.Alert.AlertType;
import javafx.stage.Stage;
import java.util.Optional;

public class MainAppController implements Initializable {

    @FXML
    private WebView webView;
    private WebEngine webEngine;

    // DAOs
    private UsuarioDAO usuarioDAO;
    private RutinaDAO rutinaDAO; 
    private EjercicioDAO ejercicioDAO;
    private RutinaEjercicioDAO rutinaEjercicioDAO;
    private ProgresoDAO progresoDAO; // <-- ¡NUEVO!

    // Estado
    private Usuario usuarioLogueado;
    private Stage mainStage; 
    
    public void setStage(Stage stage) {
        this.mainStage = stage;
        System.out.println("MainAppController: ¡Stage principal inyectado exitosamente!");
    }
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        System.out.println("MainAppController: Inicializando...");
        
        try {
            this.usuarioDAO = new UsuarioDAO();
            this.rutinaDAO = new RutinaDAO();
            this.ejercicioDAO = new EjercicioDAO();
            this.rutinaEjercicioDAO = new RutinaEjercicioDAO();
            this.progresoDAO = new ProgresoDAO(); // <-- ¡NUEVO!
            System.out.println("MainAppController: Todos los DAOs inicializados.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al inicializar DAOs!!");
            e.printStackTrace();
        }

        webEngine = webView.getEngine();
        
        // Manejador de confirm() de JS
        webEngine.setConfirmHandler(message -> {
            Alert alert = new Alert(AlertType.CONFIRMATION);
            alert.setTitle("Confirmación Requerida");
            alert.setHeaderText("Confirmar Acción");
            alert.setContentText(message);
            if (this.mainStage != null) alert.initOwner(this.mainStage);
            
            Optional<javafx.scene.control.ButtonType> result = alert.showAndWait();
            return result.isPresent() && result.get() == javafx.scene.control.ButtonType.OK;
        });

        // Carga de página y listener
        try {
            Random random = new Random();
            URL indexUrl = getClass().getResource("/webapp/index.html");
            if (indexUrl == null) { System.err.println("¡¡ERROR FATAL!! No se encontró /webapp/index.html"); return; }
            String urlConAntiCache = indexUrl.toExternalForm() + "?v=" + random.nextLong();
            System.out.println("MainAppController: Cargando URL: " + urlConAntiCache);
            webEngine.load(urlConAntiCache);
        } catch (Exception e) { e.printStackTrace(); }

        webEngine.getLoadWorker().stateProperty().addListener(
            (ov, oldState, newState) -> {
                if (newState == javafx.concurrent.Worker.State.SUCCEEDED) {
                    System.out.println("MainAppController: ¡Página cargada! Inyectando puente...");
                    JSObject window = (JSObject) webEngine.executeScript("window");
                    window.setMember("javaBridge", this);
                    try {
                        webEngine.executeScript("if (typeof javaBridgeReady === 'function') { javaBridgeReady(); }");
                        System.out.println("CONTROLADOR: MainAppController inyectado en JavaScript como 'javaBridge'.");
                    } catch (Exception e) { System.err.println("Advertencia: no se pudo llamar a javaBridgeReady(). " + e.getMessage()); }
                }
            }
        );
    }
    
    // ==================================================================
    // MÉTODOS DEL PUENTE (LOGIN / REGISTRO)
    // ==================================================================

    public void logDesdeJS(String mensaje) { System.out.println("Consola JS: " + mensaje); }

    public String login(String email, String contrasena) {
        System.out.println("MainAppController(Bridge): Solicitud de login para: " + email);
        try {
            this.usuarioLogueado = usuarioDAO.validarUsuario(email, contrasena);
            if (this.usuarioLogueado != null) {
                System.out.println("MainAppController(Bridge): ¡Éxito! Usuario encontrado: " + this.usuarioLogueado.getNombreUsuario());
                return this.usuarioLogueado.getNombreUsuario(); 
            } else { return null; }
        } catch (Exception e) { e.printStackTrace(); return null; }
    }
    
    public String getNombreUsuarioLogueado() {
        if (this.usuarioLogueado != null) {
            return this.usuarioLogueado.getNombreUsuario();
        }
        return null;
    }
    
    public boolean registrarUsuario(String nombreUsuario, String email, String contrasena, 
                                   String pNombre, String sNombre, String pApellido, String sApellido, 
                                   int sexo, String fechaNac, 
                                   double peso, double altura) {
        System.out.println("MainAppController(Bridge): Solicitud de registro para: " + email);
        try {
            Usuario u = new Usuario(); u.setNombreUsuario(nombreUsuario); u.setEmail(email); u.setContrasena(contrasena); u.setFechaCreacion(Date.valueOf(LocalDate.now()));
            Cliente c = new Cliente(); c.setPrimerNombre(pNombre); c.setSegundoNombre(sNombre); c.setPrimerApellido(pApellido); c.setSegundoApellido(sApellido); c.setCodigoSexo(sexo); c.setFechaNacimiento(Date.valueOf(fechaNac));
            Progreso p = new Progreso(); p.setFecha(Date.valueOf(LocalDate.now())); p.setPesoCorporal(peso); p.setAltura(altura); p.setNotas("Registro inicial.");
            
            return usuarioDAO.registrarNuevoUsuarioCompleto(u, c, p);
        } catch (Exception e) { e.printStackTrace(); return false; }
    }

    // ==================================================================
    // MÉTODOS DEL PUENTE (RUTINAS - RF03)
    // ==================================================================

    public String getRutinasDelUsuarioJSON() {
        if (this.usuarioLogueado == null) return "[]"; 
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario(); 
        System.out.println("MainAppController(Bridge-RF03): Buscando rutinas (con ejercicios) para usuario: " + codigoUsuario);
        
        try {
            List<Rutina> rutinas = rutinaDAO.getRutinasPorUsuario(codigoUsuario);
            if (rutinas.isEmpty()) return "[]";
            
            StringBuilder jsonBuilder = new StringBuilder("[");
            boolean firstRutina = true;
            for (Rutina rutina : rutinas) {
                if (!firstRutina) jsonBuilder.append(",");
                jsonBuilder.append("{")
                          .append("\"codigoRutina\":").append(rutina.getCodigoRutina()).append(",")
                          .append("\"nombreRutina\":\"").append(escapeJSON(rutina.getNombreRutina())).append("\",")
                          .append("\"diaSemana\":\"").append(escapeJSON(rutina.getDiaSemana())).append("\",")
                          .append("\"descripcion\":\"").append(escapeJSON(rutina.getDescripcion())).append("\",")
                          .append("\"fechaCreacion\":\"").append(rutina.getFechaCreacion()).append("\",");
                
                List<RutinaEjercicioDTO> ejercicios = rutinaEjercicioDAO.getEjerciciosPorRutina(rutina.getCodigoRutina());
                jsonBuilder.append("\"ejercicios\": [");
                boolean firstEx = true;
                for (RutinaEjercicioDTO ex : ejercicios) {
                    if (!firstEx) jsonBuilder.append(",");
                    jsonBuilder.append("{")
                              .append("\"nombre\":\"").append(escapeJSON(ex.getNombre())).append("\",")
                              .append("\"series\":").append(ex.getSeries()).append(",")
                              .append("\"repeticiones\":").append(ex.getRepeticiones()).append(",")
                              .append("\"peso\":").append(ex.getPeso())
                              .append("}");
                    firstEx = false;
                }
                jsonBuilder.append("]}");
                firstRutina = false;
            }
            jsonBuilder.append("]");
            return jsonBuilder.toString();
        } catch (Exception e) { e.printStackTrace(); return "[]"; }
    }

    public boolean eliminarRutina(int codigoRutina) {
        if (this.usuarioLogueado == null) return false;
        System.out.println("MainAppController(Bridge-RF03): Solicitud para ELIMINAR rutina ID: " + codigoRutina);
        try {
            return rutinaDAO.eliminarRutina(codigoRutina);
        } catch (Exception e) { e.printStackTrace(); return false; }
    }

    public boolean guardarRutinaCompleta(JSObject workoutData) {
        if (this.usuarioLogueado == null) return false;
        
        Connection conn = null;
        try {
            System.out.println("MainAppController(Bridge-RF03): Recibido objeto JS para guardar.");
            int codigoRutina = ((Number) workoutData.getMember("codigoRutina")).intValue();
            String nombreRutina = (String) workoutData.getMember("nombreRutina");
            String diaSemana = (String) workoutData.getMember("diaSemana");
            JSObject jsEjercicios = (JSObject) workoutData.getMember("ejercicios");
            boolean esCrear = (codigoRutina == 0);
            
            conn = ConexionDB.getConnection();
            conn.setAutoCommit(false);
            System.out.println("DAO (Transacción): Iniciada.");
            
            if (esCrear) {
                System.out.println("DAO (Transacción): Creando nueva rutina...");
                Rutina nuevaRutina = new Rutina();
                nuevaRutina.setCodigoUsuario(this.usuarioLogueado.getCodigoUsuario());
                nuevaRutina.setNombreRutina(nombreRutina);
                nuevaRutina.setDiaSemana(diaSemana);
                nuevaRutina.setDescripcion("");
                nuevaRutina.setFechaCreacion(Date.valueOf(LocalDate.now()));
                codigoRutina = rutinaDAO.crearRutina(nuevaRutina); 
            } else {
                System.out.println("DAO (Transacción): Actualizando rutina ID: " + codigoRutina);
                rutinaDAO.actualizarRutina(codigoRutina, nombreRutina, diaSemana);
                System.out.println("DAO (Transacción): Borrando ejercicios antiguos...");
                rutinaEjercicioDAO.deleteEjerciciosPorRutina(codigoRutina);
            }
            
            int numEjercicios = ((Number) jsEjercicios.getMember("length")).intValue();
            System.out.println("DAO (Transacción): Añadiendo " + numEjercicios + " ejercicios...");
            for (int i = 0; i < numEjercicios; i++) {
                JSObject jsEx = (JSObject) jsEjercicios.getSlot(i);
                String exNombre = (String) jsEx.getMember("nombre");
                int exSeries = ((Number) jsEx.getMember("series")).intValue();
                int exRepeticiones = ((Number) jsEx.getMember("repeticiones")).intValue();
                double exPeso = ((Number) jsEx.getMember("peso")).doubleValue();
                int codigoEjercicio = ejercicioDAO.findOrCreateEjercicio(exNombre);
                rutinaEjercicioDAO.addEjercicioARutina(codigoRutina, codigoEjercicio, exSeries, exRepeticiones, exPeso);
            }

            conn.commit();
            System.out.println("DAO (Transacción): ¡Commit exitoso! Rutina guardada.");
            return true;

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (guardarRutinaCompleta)!! Haciendo rollback...");
            e.printStackTrace();
            if (conn != null) { try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); } }
            return false;
        } finally {
            if (conn != null) { try { conn.setAutoCommit(true); } catch (SQLException e) { e.printStackTrace(); } }
        }
    }
    
    // ==================================================================
    // MÉTODOS DEL PUENTE (PROGRESO - RF04/RF05)
    // ==================================================================

    /**
     * RF04/RF05 (Leer): Obtiene todos los datos para las gráficas y estadísticas.
     */
    public String getDatosDeProgresoJSON() {
        if (this.usuarioLogueado == null) return "{}";
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario();
        System.out.println("MainAppController(Bridge-RF04): Obteniendo datos de progreso para usuario: " + codigoUsuario);
        
        try {
            List<Progreso> historial = progresoDAO.getProgresoPorUsuario(codigoUsuario);
            if (historial.isEmpty()) {
                System.out.println("MainAppController(Bridge-RF04): No se encontró historial.");
                return "{\"stats\": null, \"chartData\": [], \"history\": []}";
            }

            // Formateador para las etiquetas de la gráfica (ej. "8 Ene")
            DateTimeFormatter chartFormatter = DateTimeFormatter.ofPattern("d MMM");
            
            StringBuilder chartData = new StringBuilder("[");
            StringBuilder historyData = new StringBuilder("[");
            
            Progreso ultimo = historial.get(historial.size() - 1);
            Progreso penultimo = (historial.size() > 1) ? historial.get(historial.size() - 2) : ultimo;

            double currentWeight = ultimo.getPesoCorporal();
            double currentHeight = ultimo.getAltura();
            double currentBMI = CalculoIMC.calcularIMC(currentWeight, currentHeight);
            String bmiCategory = CalculoIMC.getCategoriaIMC(currentBMI);
            double weightChange = currentWeight - penultimo.getPesoCorporal();

            boolean firstChart = true;
            boolean firstHistory = true;

            // Procesamos la lista (asumiendo que está ordenada por fecha ASC desde el DAO)
            for (Progreso p : historial) {
                double peso = p.getPesoCorporal();
                double altura = p.getAltura();
                double imc = CalculoIMC.calcularIMC(peso, altura);
                String cat = CalculoIMC.getCategoriaIMC(imc);
                String fechaStr = p.getFecha().toLocalDate().format(chartFormatter); // "8 Ene"
                String fechaFull = p.getFecha().toString(); // "2025-01-08"

                // Añadir a datos de gráfica
                if (!firstChart) chartData.append(",");
                chartData.append("{")
                         .append("\"date\":\"").append(escapeJSON(fechaStr)).append("\",")
                         .append("\"weight\":").append(peso).append(",")
                         .append("\"bmi\":").append(imc)
                         .append("}");
                firstChart = false;

                // Añadir a datos de historial (el historial se revierte en JS)
                if (!firstHistory) historyData.append(",");
                historyData.append("{")
                           .append("\"date\":\"").append(escapeJSON(fechaFull)).append("\",")
                           .append("\"weight\":").append(peso).append(",")
                           .append("\"bmi\":").append(imc).append(",")
                           .append("\"bmiCategory\":\"").append(escapeJSON(cat)).append("\"")
                           .append("}");
                firstHistory = false;
            }
            chartData.append("]");
            historyData.append("]");
            
            // Construir el JSON de estadísticas
            String statsJSON = String.format(
                "{\"currentWeight\": %.1f, \"currentBMI\": %.1f, \"bmiCategory\": \"%s\", \"weightChange\": %.1f}",
                currentWeight, currentBMI, escapeJSON(bmiCategory), weightChange
            );

            // Construir el JSON final
            return String.format(
                "{\"stats\": %s, \"chartData\": %s, \"history\": %s}",
                statsJSON, chartData.toString(), historyData.toString()
            );

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (getDatosDeProgresoJSON)!!");
            e.printStackTrace();
            return "{}";
        }
    }

    /**
     * RF04 (Crear): Registra un nuevo peso desde el modal.
     * ¡¡MÉTODO ACTUALIZADO!! Ahora acepta una altura opcional.
     */
    public boolean registrarNuevoProgreso(double peso, String fechaStr, double alturaNueva) {
        if (this.usuarioLogueado == null) return false;

        System.out.println("MainAppController(Bridge-Progreso): Registrando nuevo peso: " + peso + " en fecha: " + fechaStr + " (Altura opcional: " + alturaNueva + ")");

        try {
            int codigoUsuario = this.usuarioLogueado.getCodigoUsuario();
            double alturaParaGuardar = 0;

            // --- ¡¡NUEVA LÓGICA DE ALTURA!! ---
            if (alturaNueva > 0) {
                System.out.println("MainAppController(Bridge-Progreso): Se proporcionó nueva altura: " + alturaNueva);
                alturaParaGuardar = alturaNueva;
            } else {
                System.out.println("MainAppController(Bridge-Progreso): No se proporcionó altura, buscando la más reciente...");
                alturaParaGuardar = progresoDAO.getAlturaReciente(codigoUsuario);
            }
            // --- FIN DE LA LÓGICA ---

            if (alturaParaGuardar <= 0) {
                System.err.println("MainAppController(Bridge-Progreso): ¡ERROR! No se pudo encontrar altura para el usuario. Registro fallido.");
                return false;
            }
            
            Progreso nuevoProgreso = new Progreso();
            nuevoProgreso.setCodigoUsuario(codigoUsuario);
            nuevoProgreso.setPesoCorporal(peso);
            nuevoProgreso.setAltura(alturaParaGuardar);
            nuevoProgreso.setFecha(Date.valueOf(fechaStr));
            nuevoProgreso.setNotas("Registro desde modal.");

            return progresoDAO.registrarProgreso(nuevoProgreso);

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (registrarNuevoProgreso)!!");
            e.printStackTrace();
            return false;
        }
    }

    // Helper para escapar JSON
    private String escapeJSON(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r");
    }
}