// Archivo: MainAppController.java
// (Versión 8 - Lógica de Panel Principal y Estadísticas IMPLEMENTADA)

package org.gymprogress.controller;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import netscape.javascript.JSObject;

// DAOs
import org.gymprogress.dao.*; // Importar todos los DAOs

// Models
import org.gymprogress.model.*; // Importar todos los Modelos

// Utils
import org.gymprogress.utils.CalculoIMC;

import java.net.URL;
import java.sql.Connection;
import java.sql.Date;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

import java.util.List; 
import java.util.Random; 
import java.util.ResourceBundle;
import java.util.Map; 


// JavaFX
import javafx.application.Platform;

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
    private ProgresoDAO progresoDAO;
    private ClienteDAO clienteDAO;
    private EstadisticasDAO estadisticasDAO; // <-- ¡NUEVO!

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
            this.progresoDAO = new ProgresoDAO();
            this.clienteDAO = new ClienteDAO();
            this.estadisticasDAO = new EstadisticasDAO(); // <-- ¡NUEVO!
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
            // Siempre cargamos 'index.html' (Login) al iniciar
            URL indexUrl = getClass().getResource("/webapp/index.html"); 
            if (indexUrl == null) { System.err.println("¡¡ERROR FATAL!! No se encontró /webapp/index.html"); return; }
            String urlConAntiCache = indexUrl.toExternalForm() + "?v=" + new Random().nextLong();
            System.out.println("MainAppController: Cargando URL inicial: " + urlConAntiCache);
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
    // FUNCIÓN DE NAVEGACIÓN
    // ==================================================================
    
    /**
     * Permite a JavaScript navegar a una nueva página HTML dentro de la WebView.
     * @param pagina El nombre del archivo HTML (ej. "rutinas.html")
     */
    public void navegar(String pagina) {
        System.out.println("MainAppController(Navegar): Solicitud para navegar a: " + pagina);
        try {
            URL pageUrl = getClass().getResource("/webapp/" + pagina);
            if (pageUrl == null) {
                System.err.println("¡¡ERROR DE NAVEGACIÓN!! No se encontró /webapp/" + pagina);
                return;
            }
            String urlConAntiCache = pageUrl.toExternalForm() + "?v=" + new Random().nextLong();
            
            // Usamos Platform.runLater para asegurar que la carga se hace en el hilo de UI
            Platform.runLater(() -> {
                System.out.println("MainAppController(Navegar): Cargando URL: " + urlConAntiCache);
                webEngine.load(urlConAntiCache);
            });
            
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (navegar)!!");
            e.printStackTrace();
        }
    }

    
    // ==================================================================
    // MÉTODOS DEL PUENTE (LOGIN / REGISTRO / PERFIL BÁSICO)
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
                
                // Añadir ejercicios anidados
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
            conn.setAutoCommit(false); // Iniciar Transacción
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
            
            // Añadir/Re-añadir todos los ejercicios
            int numEjercicios = ((Number) jsEjercicios.getMember("length")).intValue();
            System.out.println("DAO (Transacción): Añadiendo " + numEjercicios + " ejercicios...");
            for (int i = 0; i < numEjercicios; i++) {
                JSObject jsEx = (JSObject) jsEjercicios.getSlot(i);
                String exNombre = (String) jsEx.getMember("nombre");
                int exSeries = ((Number) jsEx.getMember("series")).intValue();
                int exRepeticiones = ((Number) jsEx.getMember("repeticiones")).intValue();
                double exPeso = ((Number) jsEx.getMember("peso")).doubleValue();
                
                // Buscar o crear el ejercicio para obtener su ID
                int codigoEjercicio = ejercicioDAO.findOrCreateEjercicio(exNombre);
                
                // Añadir a la tabla 'rutina_ejercicio'
                rutinaEjercicioDAO.addEjercicioARutina(codigoRutina, codigoEjercicio, exSeries, exRepeticiones, exPeso);
            }
            
            conn.commit(); // Finalizar Transacción
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
            for (Progreso p : historial) {
                double peso = p.getPesoCorporal();
                double altura = p.getAltura();
                double imc = CalculoIMC.calcularIMC(peso, altura);
                String cat = CalculoIMC.getCategoriaIMC(imc);
                String fechaStr = p.getFecha().toLocalDate().format(chartFormatter);
                String fechaFull = p.getFecha().toString();
                
                if (!firstChart) chartData.append(",");
                chartData.append("{")
                         .append("\"date\":\"").append(escapeJSON(fechaStr)).append("\",")
                         .append("\"weight\":").append(peso).append(",")
                         .append("\"bmi\":").append(imc)
                         .append("}");
                firstChart = false;
                
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
            
            String statsJSON = String.format(
                "{\"currentWeight\": %.1f, \"currentBMI\": %.1f, \"bmiCategory\": \"%s\", \"weightChange\": %.1f}",
                currentWeight, currentBMI, escapeJSON(bmiCategory), weightChange
            );
            
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

    public boolean registrarNuevoProgreso(double peso, String fechaStr, double alturaNueva) {
        if (this.usuarioLogueado == null) return false;
        System.out.println("MainAppController(Bridge-Progreso): Registrando nuevo peso: " + peso + " en fecha: " + fechaStr + " (Altura opcional: " + alturaNueva + ")");
        try {
            int codigoUsuario = this.usuarioLogueado.getCodigoUsuario();
            double alturaParaGuardar = 0;
            
            if (alturaNueva > 0) {
                System.out.println("MainAppController(Bridge-Progreso): Se proporcionó nueva altura: " + alturaNueva);
                alturaParaGuardar = alturaNueva;
            } else {
                System.out.println("MainAppController(Bridge-Progreso): No se proporcionó altura, buscando la más reciente...");
                alturaParaGuardar = progresoDAO.getAlturaReciente(codigoUsuario);
            }
            
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

    
    // ==================================================================
    // ¡¡LÓGICA ACTUALIZADA!! - Para las nuevas páginas
    // ==================================================================
    
    /**
     * RF-DASH: Obtiene los datos para el "Panel Principal"
     * ¡¡AHORA IMPLEMENTADO!!
     */
    public String getDashboardOverviewJSON() {
        if (this.usuarioLogueado == null) return "{}";
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario();
        System.out.println("MainAppController(Bridge-DASH): Obteniendo datos para el Panel Principal...");

        try {
            // 1. Obtener Estadísticas Rápidas (reutilizando la lógica de Progreso)
            String progresoJsonStr = getDatosDeProgresoJSON();
            String statsJson = "null";
            if (progresoJsonStr.contains("\"stats\": {")) {
                statsJson = progresoJsonStr.substring(progresoJsonStr.indexOf("\"stats\": {") + 8);
                statsJson = statsJson.substring(0, statsJson.indexOf("}") + 1);
            }

            // 2. Obtener Rutinas Activas/Recientes (limitemos a 3)
            List<Rutina> rutinas = rutinaDAO.getRutinasRecientes(codigoUsuario, 3);
            StringBuilder rutinasJson = new StringBuilder("[");
            boolean first = true;
            for (Rutina r : rutinas) {
                if (!first) rutinasJson.append(",");
                rutinasJson.append("{")
                           .append("\"nombre\":\"").append(escapeJSON(r.getNombreRutina())).append("\",")
                           .append("\"dia\":\"").append(escapeJSON(r.getDiaSemana())).append("\"")
                           .append("}");
                first = false;
            }
            rutinasJson.append("]");

            // 3. Obtener Actividad Reciente (limitemos a 5)
            List<Progreso> actividad = progresoDAO.getProgresoReciente(codigoUsuario, 5);
            StringBuilder actividadJson = new StringBuilder("[");
            first = true;
            for (Progreso p : actividad) {
                if (!first) actividadJson.append(",");
                actividadJson.append("{")
                           .append("\"accion\":\"Peso Registrado\",")
                           .append("\"detalle\":\"").append(p.getPesoCorporal()).append(" kg\",")
                           .append("\"fecha\":\"").append(p.getFecha().toString()).append("\"")
                           .append("}");
                first = false;
            }
            actividadJson.append("]");

            // 4. Construir el JSON final
            return String.format(
                "{\"stats\": %s, \"rutinasActivas\": %s, \"actividadReciente\": %s}",
                statsJson,
                rutinasJson.toString(),
                actividadJson.toString()
            );

        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (getDashboardOverviewJSON)!!");
            e.printStackTrace();
            return "{\"stats\": null, \"rutinasActivas\": [], \"actividadReciente\": []}";
        }
    }
    
    /**
     * RF-STATS: Obtiene los datos para la página de "Estadísticas"
     * ¡¡AHORA IMPLEMENTADO!!
     */
    public String getStatisticsDataJSON() {
        if (this.usuarioLogueado == null) return "{}";
        int codigoUsuario = this.usuarioLogueado.getCodigoUsuario();
        System.out.println("MainAppController(Bridge-STATS): Obteniendo datos para Estadísticas...");

        try {
            // 1. Obtener Récords Personales
            List<Map<String, String>> records = estadisticasDAO.getRecordsPersonales(codigoUsuario);
            String recordsJson = mapListToJson(records);

            // 2. Obtener Entrenamientos por Mes
            List<Map<String, Object>> workouts = estadisticasDAO.getEntrenamientosPorMes(codigoUsuario);
            String workoutsJson = mapListToJson(workouts);

            // 3. Obtener Distribución de Ejercicios
            List<Map<String, Object>> dist = estadisticasDAO.getDistribucionEjercicios(codigoUsuario);
            String distJson = mapListToJson(dist);
            
            // 4. Construir JSON final
            return String.format(
                "{\"recordsPersonales\": %s, \"entrenamientosPorMes\": %s, \"distribucionEjercicios\": %s}",
                recordsJson,
                workoutsJson,
                distJson
            );
            
        } catch (Exception e) {
            System.err.println("¡¡ERROR FATAL en (getStatisticsDataJSON)!!");
            e.printStackTrace();
            return "{\"recordsPersonales\": [], \"entrenamientosPorMes\": [], \"distribucionEjercicios\": []}";
        }
    }

    /**
     * RF-PERFIL: Obtiene los datos del perfil del cliente
     * (Esta lógica ya estaba en tu Versión 7)
     */
    public String getClienteDataJSON() {
        if (this.usuarioLogueado == null) return "{}";
        System.out.println("MainAppController(Bridge-PERFIL): Obteniendo datos del cliente...");
        try {
            Cliente c = clienteDAO.obtenerClientePorId(this.usuarioLogueado.getCodigoUsuario());
            if (c == null) return "{}";
            
            // Construir JSON manualmente
            return String.format(
                "{\"primerNombre\": \"%s\", \"segundoNombre\": \"%s\", \"primerApellido\": \"%s\", \"segundoApellido\": \"%s\", \"fechaNacimiento\": \"%s\", \"codigoSexo\": %d}",
                escapeJSON(c.getPrimerNombre()),
                escapeJSON(c.getSegundoNombre()),
                escapeJSON(c.getPrimerApellido()),
                escapeJSON(c.getSegundoApellido()),
                c.getFechaNacimiento().toString(),
                c.getCodigoSexo()
            );
        } catch (Exception e) {
            e.printStackTrace();
            return "{}";
        }
    }
    
    /**
     * RF-PERFIL (Actualizar): Actualiza los datos del perfil del cliente
  

    // --- Helpers de construcción de JSON ---

    /**
     * Convierte una Lista de Mapas a un String JSON.
     * (Helper genérico para evitar repetir código)
     */
    private String mapListToJson(List<? extends Map<String, ?>> list) {
        StringBuilder json = new StringBuilder("[");
        boolean firstItem = true;
        for (Map<String, ?> item : list) {
            if (!firstItem) json.append(",");
            json.append(mapToJson(item));
            firstItem = false;
        }
        json.append("]");
        return json.toString();
    }
    public boolean actualizarClienteData(String pNombre, String sNombre, String pApellido, String sApellido, String fechaNac) {
    if (this.usuarioLogueado == null) return false;
    System.out.println("MainAppController(Bridge-PERFIL): Actualizando datos del cliente...");
    
        try {
// 1. Crear un objeto Cliente con los nuevos datos
            Cliente clienteActualizado = new Cliente();
            clienteActualizado.setCodigoUsuario(this.usuarioLogueado.getCodigoUsuario()); // ID de usuario
            clienteActualizado.setPrimerNombre(pNombre);
            clienteActualizado.setSegundoNombre(sNombre);
            clienteActualizado.setPrimerApellido(pApellido);
            clienteActualizado.setSegundoApellido(sApellido);
            clienteActualizado.setFechaNacimiento(Date.valueOf(fechaNac)); // Convertir String a java.sql.Date

// 2. Llamar al DAO para actualizar
    boolean exito = clienteDAO.actualizarCliente(clienteActualizado);

    if (exito) {
        System.out.println("MainAppController(Bridge-PERFIL): ¡Perfil actualizado exitosamente!");
    } else {
        System.err.println("MainAppController(Bridge-PERFIL): DAO no reportó filas afectadas.");
        }
        return exito;

    } catch (Exception e) {
        System.err.println("¡¡ERROR FATAL en (actualizarClienteData)!!");
        e.printStackTrace();
            return false;
    }
    }
    /**
     * Convierte un Map<String, Object> a un String JSON.
     * (Maneja Numbers, Booleans y Strings)
     */
    private String mapToJson(Map<String, ?> map) {
        StringBuilder json = new StringBuilder("{");
        boolean firstKey = true;
        for (Map.Entry<String, ?> entry : map.entrySet()) {
            if (!firstKey) json.append(",");
            json.append("\"").append(escapeJSON(entry.getKey())).append("\":");
            
            Object value = entry.getValue();
            if (value instanceof String) {
                json.append("\"").append(escapeJSON((String) value)).append("\"");
            } else if (value instanceof Number || value instanceof Boolean) {
                json.append(value.toString());
            } else {
                json.append("\"").append(escapeJSON(String.valueOf(value))).append("\"");
            }
            firstKey = false;
        }
        json.append("}");
        return json.toString();
    }

    // Helper para escapar JSON
    private String escapeJSON(String input) {
        if (input == null) return "";
        return input.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n").replace("\r", "\\r");
    }
}