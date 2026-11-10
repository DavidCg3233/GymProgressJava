package org.gymprogress.model;

import java.sql.Date;

// Representa la tabla 'rutina'
public class Rutina {
    private int codigoRutina;
    private int codigoUsuario;
    private String nombreRutina;
    private String descripcion;
    private Date fechaCreacion;
    
    // --- ¡¡NUEVO CAMPO!! ---
    private String diaSemana; // Corresponde a la columna 'dia_semana'

    // Getters y Setters
    public int getCodigoRutina() {
        return codigoRutina;
    }
    public void setCodigoRutina(int codigoRutina) {
        this.codigoRutina = codigoRutina;
    }
    public int getCodigoUsuario() {
        return codigoUsuario;
    }
    public void setCodigoUsuario(int codigoUsuario) {
        this.codigoUsuario = codigoUsuario;
    }
    public String getNombreRutina() {
        return nombreRutina;
    }
    public void setNombreRutina(String nombreRutina) {
        this.nombreRutina = nombreRutina;
    }
    public String getDescripcion() {
        return descripcion;
    }
    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }
    public Date getFechaCreacion() {
        return fechaCreacion;
    }
    public void setFechaCreacion(Date fechaCreacion) {
        this.fechaCreacion = fechaCreacion;
    }

    // --- ¡¡NUEVOS MÉTODOS!! ---
    public String getDiaSemana() {
        return diaSemana;
    }
    public void setDiaSemana(String diaSemana) {
        this.diaSemana = diaSemana;
    }
}