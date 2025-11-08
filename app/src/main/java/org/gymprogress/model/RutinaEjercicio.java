package org.gymprogress.model;

// Representa la tabla 'rutina_ejercicio'
public class RutinaEjercicio {
    private int codigoRutinaEjercicio;
    private int codigoRutina;
    private int codigoEjercicio;
    private int series;
    private int repeticiones;
    private double peso;

    // Getters y Setters
    public int getCodigoRutinaEjercicio() {
        return codigoRutinaEjercicio;
    }
    public void setCodigoRutinaEjercicio(int codigoRutinaEjercicio) {
        this.codigoRutinaEjercicio = codigoRutinaEjercicio;
    }
    public int getCodigoRutina() {
        return codigoRutina;
    }
    public void setCodigoRutina(int codigoRutina) {
        this.codigoRutina = codigoRutina;
    }
    public int getCodigoEjercicio() {
        return codigoEjercicio;
    }
    public void setCodigoEjercicio(int codigoEjercicio) {
        this.codigoEjercicio = codigoEjercicio;
    }
    public int getSeries() {
        return series;
    }
    public void setSeries(int series) {
        this.series = series;
    }
    public int getRepeticiones() {
        return repeticiones;
    }
    public void setRepeticiones(int repeticiones) {
        this.repeticiones = repeticiones;
    }
    public double getPeso() {
        return peso;
    }
    public void setPeso(double peso) {
        this.peso = peso;
    }
}