package org.gymprogress.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class EjercicioDAO {

    private Connection conn;

    public EjercicioDAO() {
        this.conn = ConexionDB.getConnection();
        if (this.conn == null) {
            System.err.println("¡¡ERROR FATAL en EjercicioDAO!! La conexión a la BD es NULL.");
        }
        try {
            ensureNormalizedSchema();
        } catch (Exception e) {
            System.err.println("EjercicioDAO: No se pudo asegurar el esquema normalizado de grupos. Continuando con compatibilidad...");
            e.printStackTrace();
        }
    }

    /**
     * Busca un ejercicio por su nombre. Si no existe, lo crea y devuelve el nuevo ID.
     * Esto es CRUCIAL para guardar las rutinas.
     *
     * @param nombre El nombre del ejercicio (ej. "Press de Banca")
     * @return El codigo_ejercicio (existente o nuevo)
     * @throws SQLException
     */
    public int findOrCreateEjercicio(String nombre) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        
        // 1. Intentar buscar el ejercicio
        String sqlSelect = "SELECT codigo_ejercicio FROM ejercicio WHERE nombre = ?";
        try (PreparedStatement stmtSelect = conn.prepareStatement(sqlSelect)) {
            stmtSelect.setString(1, nombre);
            try (ResultSet rs = stmtSelect.executeQuery()) {
                if (rs.next()) {
                    // ¡Encontrado! Devolver el ID existente.
                    return rs.getInt("codigo_ejercicio");
                }
            }
        }
        
        // 2. Si no se encontró, crearlo.
        System.out.println("DAO (Ejercicio): No se encontró '" + nombre + "', creando nuevo ejercicio...");
        String sqlInsert = "INSERT INTO ejercicio (nombre, grupo_muscular, descripcion) VALUES (?, ?, ?)";
        
        try (PreparedStatement stmtInsert = conn.prepareStatement(sqlInsert, Statement.RETURN_GENERATED_KEYS)) {
            
            stmtInsert.setString(1, nombre);
            stmtInsert.setString(2, "General"); // Valor por defecto
            stmtInsert.setString(3, "Ejercicio añadido automáticamente"); // Valor por defecto

            int filasAfectadas = stmtInsert.executeUpdate();

            if (filasAfectadas == 0) {
                throw new SQLException("Falló la creación del ejercicio, no se insertaron filas.");
            }

            // 3. Obtener y devolver el nuevo ID generado
            try (ResultSet generatedKeys = stmtInsert.getGeneratedKeys()) {
                if (generatedKeys.next()) {
                    int nuevoId = generatedKeys.getInt(1);
                    System.out.println("DAO (Ejercicio): Creado nuevo ejercicio '" + nombre + "' con ID: " + nuevoId);
                    return nuevoId;
                } else {
                    throw new SQLException("Falló la creación del ejercicio, no se pudo obtener el ID.");
                }
            }
        }
    }

    /**
     * Variante con grupo muscular: si no existe, lo crea usando el grupo indicado
     * y una descripción por defecto. Si 'grupo' es nulo o vacío, usa 'General'.
     */
    public int findOrCreateEjercicio(String nombre, String grupo) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");

        // 1. Buscar por nombre (y capturar grupo actual para posible actualización)
        String sqlSelect = "SELECT e.codigo_ejercicio, e.codigo_grupo_muscular, COALESCE(g.nombre_grupo_muscular, e.grupo_muscular) AS grupo_actual " +
                           "FROM ejercicio e LEFT JOIN grupo_muscular g ON e.codigo_grupo_muscular = g.codigo_grupo_muscular " +
                           "WHERE e.nombre = ?";
        try (PreparedStatement stmtSelect = conn.prepareStatement(sqlSelect)) {
            stmtSelect.setString(1, nombre);
            try (ResultSet rs = stmtSelect.executeQuery()) {
                if (rs.next()) {
                    int codigo = rs.getInt("codigo_ejercicio");
                    String grupoActual = rs.getString("grupo_actual");
                    String grupoFinal = (grupo == null || grupo.trim().isEmpty()) ? "General" : grupo.trim();
                    // Si viene un grupo y es distinto del actual, actualizar clasificación del ejercicio
                    if (grupoFinal != null && !grupoFinal.isEmpty() && (grupoActual == null || !grupoFinal.equalsIgnoreCase(grupoActual))) {
                        try {
                            Integer gid = findOrCreateGrupo(grupoFinal);
                            try (PreparedStatement upd = conn.prepareStatement("UPDATE ejercicio SET codigo_grupo_muscular = ?, grupo_muscular = ? WHERE codigo_ejercicio = ?")) {
                                upd.setInt(1, gid);
                                upd.setString(2, grupoFinal);
                                upd.setInt(3, codigo);
                                upd.executeUpdate();
                            }
                        } catch (SQLException upEx) {
                            // Si falla la normalización, al menos actualizamos la columna de texto
                            try (PreparedStatement updTxt = conn.prepareStatement("UPDATE ejercicio SET grupo_muscular = ? WHERE codigo_ejercicio = ?")) {
                                updTxt.setString(1, grupoFinal);
                                updTxt.setInt(2, codigo);
                                updTxt.executeUpdate();
                            }
                        }
                    }
                    return codigo;
                }
            }
        }

        // 2. Insertar con grupo (normalizado, y manteniendo columna de texto para compatibilidad)
        String grupoFinal = (grupo == null || grupo.trim().isEmpty()) ? "General" : grupo.trim();
        System.out.println("DAO (Ejercicio): Creando nuevo ejercicio '" + nombre + "' con grupo '" + grupoFinal + "'...");
        Integer grupoId = null;
        try {
            grupoId = findOrCreateGrupo(grupoFinal);
        } catch (SQLException ex) {
            System.err.println("Advertencia: No se pudo usar tabla grupo_muscular. Se usará solo texto. Causa: " + ex.getMessage());
        }

        String sqlInsert;
        if (grupoId != null) {
            sqlInsert = "INSERT INTO ejercicio (nombre, codigo_grupo_muscular, grupo_muscular, descripcion) VALUES (?, ?, ?, ?)";
            try (PreparedStatement stmtInsert = conn.prepareStatement(sqlInsert, Statement.RETURN_GENERATED_KEYS)) {
                stmtInsert.setString(1, nombre);
                stmtInsert.setInt(2, grupoId);
                stmtInsert.setString(3, grupoFinal); // compatibilidad
                stmtInsert.setString(4, "Ejercicio añadido automáticamente");
                int filas = stmtInsert.executeUpdate();
                if (filas == 0) throw new SQLException("No se insertó el ejercicio");
                try (ResultSet keys = stmtInsert.getGeneratedKeys()) {
                    if (keys.next()) return keys.getInt(1);
                }
            }
        } else {
            sqlInsert = "INSERT INTO ejercicio (nombre, grupo_muscular, descripcion) VALUES (?, ?, ?)";
            try (PreparedStatement stmtInsert = conn.prepareStatement(sqlInsert, Statement.RETURN_GENERATED_KEYS)) {
                stmtInsert.setString(1, nombre);
                stmtInsert.setString(2, grupoFinal);
                stmtInsert.setString(3, "Ejercicio añadido automáticamente");
                int filas = stmtInsert.executeUpdate();
                if (filas == 0) throw new SQLException("No se insertó el ejercicio");
                try (ResultSet keys = stmtInsert.getGeneratedKeys()) {
                    if (keys.next()) return keys.getInt(1);
                }
            }
        }
        throw new SQLException("No se pudo obtener ID de ejercicio creado");
    }

    /**
     * Lista todos los ejercicios: nombre y grupo_muscular.
     */
    public ResultSet listAllEjerciciosRaw() throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        // Intentar usar la tabla normalizada; si falla, hacer fallback a la columna texto
        try {
            String sql = "SELECT e.codigo_ejercicio, e.nombre, COALESCE(g.nombre_grupo_muscular, e.grupo_muscular, 'General') AS grupo_muscular " +
                         "FROM ejercicio e LEFT JOIN grupo_muscular g ON e.codigo_grupo_muscular = g.codigo_grupo_muscular " +
                         "ORDER BY e.nombre ASC";
            PreparedStatement ps = conn.prepareStatement(sql);
            return ps.executeQuery();
        } catch (SQLException joinEx) {
            System.err.println("EjercicioDAO: listAllEjerciciosRaw fallback por error en JOIN: " + joinEx.getMessage());
            PreparedStatement ps = conn.prepareStatement("SELECT codigo_ejercicio, nombre, grupo_muscular FROM ejercicio ORDER BY nombre ASC");
            return ps.executeQuery();
        }
    }

    // ===================== Grupos Musculares (Normalización) =====================
    private void ensureNormalizedSchema() throws SQLException {
        // Crear tabla de grupos si no existe
        try (Statement st = conn.createStatement()) {
            st.executeUpdate("CREATE TABLE IF NOT EXISTS grupo_muscular (" +
                             "codigo_grupo_muscular INT AUTO_INCREMENT PRIMARY KEY, " +
                             "nombre_grupo_muscular VARCHAR(100) NOT NULL UNIQUE) ENGINE=InnoDB");
        }
        // Agregar columna FK a ejercicio si no existe
        boolean hasColumn = false;
        String checkCol = "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'ejercicio' AND column_name = 'codigo_grupo_muscular'";
        try (PreparedStatement ps = conn.prepareStatement(checkCol); ResultSet rs = ps.executeQuery()) {
            if (rs.next()) hasColumn = rs.getInt(1) > 0;
        }
        if (!hasColumn) {
            try (Statement st = conn.createStatement()) {
                st.executeUpdate("ALTER TABLE ejercicio ADD COLUMN codigo_grupo_muscular INT NULL");
            }
            try (Statement st = conn.createStatement()) {
                st.executeUpdate("ALTER TABLE ejercicio ADD CONSTRAINT fk_ejercicio_grupo FOREIGN KEY (codigo_grupo_muscular) REFERENCES grupo_muscular(codigo_grupo_muscular)");
            } catch (SQLException fkEx) {
                System.err.println("Advertencia: No se pudo agregar FK (posible motor/caso ya existente): " + fkEx.getMessage());
            }
        }
        // Insertar grupo 'General' si no existe
        try (PreparedStatement ps = conn.prepareStatement("INSERT IGNORE INTO grupo_muscular (nombre_grupo_muscular) VALUES (?)")) {
            ps.setString(1, "General");
            ps.executeUpdate();
        }
        // Backfill: asignar codigo_grupo_muscular cuando sea nulo basándose en la columna texto
        String selectDistinct = "SELECT DISTINCT grupo_muscular FROM ejercicio WHERE grupo_muscular IS NOT NULL AND (codigo_grupo_muscular IS NULL OR codigo_grupo_muscular = 0)";
        try (PreparedStatement ps = conn.prepareStatement(selectDistinct); ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                String nombreGrupo = rs.getString(1);
                if (nombreGrupo == null || nombreGrupo.trim().isEmpty()) nombreGrupo = "General";
                int gid = findOrCreateGrupo(nombreGrupo.trim());
                try (PreparedStatement upd = conn.prepareStatement("UPDATE ejercicio SET codigo_grupo_muscular = ? WHERE (codigo_grupo_muscular IS NULL OR codigo_grupo_muscular = 0) AND (grupo_muscular = ? OR (grupo_muscular IS NULL AND ? = 'General'))")) {
                    upd.setInt(1, gid);
                    upd.setString(2, nombreGrupo);
                    upd.setString(3, nombreGrupo);
                    upd.executeUpdate();
                }
            }
        }
    }

    public int findOrCreateGrupo(String nombreGrupo) throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        String limpio = (nombreGrupo == null || nombreGrupo.trim().isEmpty()) ? "General" : nombreGrupo.trim();
        // Buscar
        try (PreparedStatement ps = conn.prepareStatement("SELECT codigo_grupo_muscular FROM grupo_muscular WHERE nombre_grupo_muscular = ?")) {
            ps.setString(1, limpio);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return rs.getInt(1);
            }
        }
        // Crear
        try (PreparedStatement ins = conn.prepareStatement("INSERT INTO grupo_muscular (nombre_grupo_muscular) VALUES (?)", Statement.RETURN_GENERATED_KEYS)) {
            ins.setString(1, limpio);
            ins.executeUpdate();
            try (ResultSet keys = ins.getGeneratedKeys()) {
                if (keys.next()) return keys.getInt(1);
            }
        } catch (SQLException dup) {
            // Si es duplicado por condición de carrera, volver a consultar
            try (PreparedStatement ps = conn.prepareStatement("SELECT codigo_grupo_muscular FROM grupo_muscular WHERE nombre_grupo_muscular = ?")) {
                ps.setString(1, limpio);
                try (ResultSet rs = ps.executeQuery()) { if (rs.next()) return rs.getInt(1); }
            }
            throw dup;
        }
        throw new SQLException("No se pudo crear/recuperar grupo muscular");
    }

    public ResultSet listAllGrupos() throws SQLException {
        if (conn == null) throw new SQLException("Conexión a BD es NULL");
        PreparedStatement ps = conn.prepareStatement("SELECT codigo_grupo_muscular, nombre_grupo_muscular FROM grupo_muscular ORDER BY nombre_grupo_muscular ASC");
        return ps.executeQuery();
    }
}