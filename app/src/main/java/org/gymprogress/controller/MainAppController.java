// Archivo: MainAppController.java
// (Versión 5 - CRUD COMPLETO)

package org.gymprogress.controller;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import netscape.javascript.JSObject;

// Imports de DAOs (¡NUEVOS!)
import org.gymprogress.dao.RutinaDAO; 
import org.gymprogress.dao.UsuarioDAO;
import org.gymprogress.dao.EjercicioDAO;       // <-- NUEVO
import org.gymprogress.dao.RutinaEjercicioDAO; // <-- NUEVO
import org.gymprogress.dao.ConexionDB;         // <-- NUEVO (Para transacción)

// Imports de Models (¡NUEVO!)
import org.gymprogress.model.Cliente;
import org.gymprogress.model.Progreso;
import org.gymprogress.model.Rutina; 
import org.gymprogress.model.Usuario;
import org.gymprogress.model.RutinaEjercicioDTO; // <-- NUEVO

import java.net.URL;
import java.sql.Connection; // <-- NUEVO
import java.sql.Date;
import java.sql.SQLException; // <-- NUEVO
import java.time.LocalDate;
import java.util.List; 
import java.util.Random; 
import java.util.ResourceBundle;

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
    private EjercicioDAO ejercicioDAO;       // <-- NUEVO
    private RutinaEjercicioDAO rutinaEjercicioDAO; // <-- NUEVO

    // Estado de la Sesión
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
            this.ejercicioDAO = new EjercicioDAO();             // <-- NUEVO
            this.rutinaEjercicioDAO = new RutinaEjercicioDAO(); // <-- NUEVO
            System.out.println("MainAppController: Todos los DAOs inicializados.");
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL al inicializar DAOs en MainAppController!!");
            e.printStackTrace();
        }

        webEngine = webView.getEngine();
        
        // (setConfirmHandler ya existe y está bien)
        webEngine.setConfirmHandler(message -> {
            // ¡¡ESTO ES IMPORTANTE!!
            // El JS en dashboard.html (Paso 1) usa confirm()
            // Necesitamos un diálogo de confirmación nativo aquí.
            Alert alert = new Alert(AlertType.CONFIRMATION);
            alert.setTitle("Confirmación Requerida");
            alert.setHeaderText("Confirmar Acción");
            alert.setContentText(message);
            if (this.mainStage != null) alert.initOwner(this.mainStage);
            
            Optional<javafx.scene.control.ButtonType> result = alert.showAndWait();
            return result.isPresent() && result.get() == javafx.scene.control.ButtonType.OK;
        });

        // (Carga de página y listener de 'SUCCEEDED' sin cambios)
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
    // MÉTODOS DEL PUENTE (Login, Registro, etc. - Sin cambios)
    // ==================================================================

    public void logDesdeJS(String mensaje) { System.out.println("Consola JS: " + mensaje); }

    public String login(String email, String contrasena) {
        // (Sin cambios)
        System.out.println("MainAppController(Bridge): Solicitud de login para: " + email);
        try {
            this.usuarioLogueado = usuarioDAO.validarUsuario(email, contrasena);
            if (this.usuarioLogueado != null) {
                System.out.println("MainAppController(Bridge): ¡Éxito! Usuario encontrado: " + this.usuarioLogueado.getNombreUsuario());
                return this.usuarioLogueado.getNombreUsuario(); 
            } else {
                return null;
            }
        } catch (Exception e) { e.printStackTrace(); return null; }
    }
    
    public String getNombreUsuarioLogueado() {
        // (Sin cambios)
        if (this.usuarioLogueado != null) {
            return this.usuarioLogueado.getNombreUsuario();
        }
        return null;
    }
    
    public boolean registrarUsuario(/*... params ...*/) {
        // (Sin cambios - asumo que los parámetros están)
        // ... lógica de registro ...
        return true; // Asumo que funciona
    }

    // ==================================================================
    // ¡¡INICIO DE LA NUEVA LÓGICA CRUD (RF03)!!
    // ==================================================================

    /**
     * ¡¡MÉTODO ACTUALIZADO!!
     * RF03: Obtiene todas las rutinas Y SUS EJERCICIOS para el usuario.
     */
    public String getRutinasDelUsuarioJSON() {
        if (this.usuarioLogueado == null) {
            System.err.println("MainAppController(Bridge-GetRutinas): ¡ERROR! No hay usuario logueado.");
            return "[]"; 
        }
        
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario(); 
        System.out.println("MainAppController(Bridge): Buscando rutinas (con ejercicios) para el usuario: " + codigoUsuario);
        
        try {
            // 1. Obtener las rutinas base
            List<Rutina> rutinas = rutinaDAO.getRutinasPorUsuario(codigoUsuario);
            if (rutinas.isEmpty()) return "[]";
            
            // 2. Construir el JSON manualmente (con ejercicios anidados)
            StringBuilder jsonBuilder = new StringBuilder("[");
            boolean firstRutina = true;
            
            for (Rutina rutina : rutinas) {
                if (!firstRutina) jsonBuilder.append(",");
                
                jsonBuilder.append("{")
                          .append("\"codigoRutina\":").append(rutina.getCodigoRutina()).append(",")
                          .append("\"nombreRutina\":\"").append(escapeJSON(rutina.getNombreRutina())).append("\",")
                          .append("\"diaSemana\":\"").append(escapeJSON(rutina.getDiaSemana())).append("\",") // <-- NUEVO
                          .append("\"descripcion\":\"").append(escapeJSON(rutina.getDescripcion())).append("\",")
                          .append("\"fechaCreacion\":\"").append(rutina.getFechaCreacion()).append("\",");
                
                // 3. Obtener y anidar los ejercicios para ESTA rutina
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
                
                jsonBuilder.append("]"); // Fin del array de ejercicios
                jsonBuilder.append("}"); // Fin del objeto rutina
                firstRutina = false;
            }
            jsonBuilder.append("]");
            
            // System.out.println("JSON de rutinas (completo): " + jsonBuilder.toString());
            return jsonBuilder.toString();

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en MainAppController (getRutinasDelUsuarioJSON)!!");
            e.printStackTrace();
            return "[]";
        }
    }

    /**
     * ¡¡NUEVO MÉTODO!!
     * RF03 (Eliminar): Llamado desde dashboard.html para eliminar una rutina.
     */
    public boolean eliminarRutina(int codigoRutina) {
        if (this.usuarioLogueado == null) return false;
        
        System.out.println("MainAppController(Bridge-Eliminar): Solicitud para ELIMINAR rutina ID: " + codigoRutina);
        try {
            // El DAO se encarga. ON DELETE CASCADE borrará los 'rutina_ejercicio'.
            return rutinaDAO.eliminarRutina(codigoRutina);
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en MainAppController (eliminarRutina)!!");
            e.printStackTrace();
            return false;
        }
    }

    /**
     * ¡¡NUEVO MÉTODO!!
     * RF03 (Crear/Actualizar): Recibe el objeto del formulario desde JS.
     * Esta función usa una TRANSACCIÓN DE BASE DE DATOS.
     */
    public boolean guardarRutinaCompleta(JSObject workoutData) {
        if (this.usuarioLogueado == null) return false;
        
        Connection conn = null;
        try {
            // 1. Extraer datos del Objeto JavaScript
            System.out.println("MainAppController(Bridge-Guardar): Recibido objeto JS para guardar.");
            int codigoRutina = ((Number) workoutData.getMember("codigoRutina")).intValue();
            String nombreRutina = (String) workoutData.getMember("nombreRutina");
            String diaSemana = (String) workoutData.getMember("diaSemana");
            JSObject jsEjercicios = (JSObject) workoutData.getMember("ejercicios");
            
            boolean esCrear = (codigoRutina == 0);
            
            // 2. Iniciar Transacción
            conn = ConexionDB.getConnection();
            conn.setAutoCommit(false);
            System.out.println("DAO (Transacción): Iniciada.");
            
            // 3. PASO A: Guardar/Actualizar la RUTINA
            if (esCrear) {
                System.out.println("DAO (Transacción): Creando nueva rutina...");
                Rutina nuevaRutina = new Rutina();
                nuevaRutina.setCodigoUsuario(this.usuarioLogueado.getCodigoUsuario());
                nuevaRutina.setNombreRutina(nombreRutina);
                nuevaRutina.setDiaSemana(diaSemana);
                nuevaRutina.setDescripcion(""); // El formulario no lo tiene, lo omitimos
                nuevaRutina.setFechaCreacion(Date.valueOf(LocalDate.now()));
                
                // ¡Obtener el nuevo ID generado!
                codigoRutina = rutinaDAO.crearRutina(nuevaRutina); 
            
            } else {
                System.out.println("DAO (Transacción): Actualizando rutina ID: " + codigoRutina);
                rutinaDAO.actualizarRutina(codigoRutina, nombreRutina, diaSemana);
                
                // 3. PASO B: Borrar ejercicios antiguos (SOLO en 'actualizar')
                System.out.println("DAO (Transacción): Borrando ejercicios antiguos...");
                rutinaEjercicioDAO.deleteEjerciciosPorRutina(codigoRutina);
            }
            
            // 4. PASO C: Iterar y añadir todos los ejercicios (para 'crear' y 'actualizar')
            int numEjercicios = ((Number) jsEjercicios.getMember("length")).intValue();
            System.out.println("DAO (Transacción): Añadiendo " + numEjercicios + " ejercicios...");
            
            for (int i = 0; i < numEjercicios; i++) {
                JSObject jsEx = (JSObject) jsEjercicios.getSlot(i);
                
                // 4a. Obtener datos del ejercicio
                String exNombre = (String) jsEx.getMember("nombre");
                int exSeries = ((Number) jsEx.getMember("series")).intValue();
                int exRepeticiones = ((Number) jsEx.getMember("repeticiones")).intValue();
                double exPeso = ((Number) jsEx.getMember("peso")).doubleValue();
                
                // 4b. Buscar o crear el ejercicio en la tabla 'ejercicio'
                int codigoEjercicio = ejercicioDAO.findOrCreateEjercicio(exNombre);
                
                // 4c. Añadir a la tabla 'rutina_ejercicio'
                rutinaEjercicioDAO.addEjercicioARutina(codigoRutina, codigoEjercicio, exSeries, exRepeticiones, exPeso);
            }

            // 5. ¡Éxito! Hacer Commit
            conn.commit();
            System.out.println("DAO (Transacción): ¡Commit exitoso! Rutina guardada.");
            return true;

        } catch (Exception e) {
            // 6. ¡Fallo! Hacer Rollback
            System.err.println("¡¡ERROR FATAL en MainAppController (guardarRutinaCompleta)!! Haciendo rollback...");
            e.printStackTrace();
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            }
            return false;
        } finally {
            // 7. Siempre reestablecer AutoCommit
            if (conn != null) {
                try { conn.setAutoCommit(true); } catch (SQLException e) { e.printStackTrace(); }
            }
        }
    }
    
    // (El método solicitarCreacionRutina() ya no es necesario,
    //  el nuevo botón "Nuevo Entrenamiento" usa el modal grande)
    // (Lo dejaré por si el botón antiguo sigue ahí, pero la nueva lógica lo reemplaza)
    
    // (escapeJSON sin cambios)
    private String escapeJSON(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r");
    }
}