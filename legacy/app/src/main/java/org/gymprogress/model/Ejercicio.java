package org.gymprogress.model;

// Representa la tabla 'ejercicio'
public class Ejercicio {
    private int codigoEjercicio;
    private String nombre;
    private String grupoMuscular;
    private String descripcion;

    // Getters y Setters
    public int getCodigoEjercicio() {
        return codigoEjercicio;
    }
    public void setCodigoEjercicio(int codigoEjercicio) {
        this.codigoEjercicio = codigoEjercicio;
    }
    public String getNombre() {
        return nombre;
    }
    public void setNombre(String nombre) {
        this.nombre = nombre;
    }
    public String getGrupoMuscular() {
        return grupoMuscular;
    }
    public void setGrupoMuscular(String grupoMuscular) {
        this.grupoMuscular = grupoMuscular;
    }
    public String getDescripcion() {
        return descripcion;
    }
    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }
}