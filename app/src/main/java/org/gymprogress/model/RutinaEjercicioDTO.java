package org.gymprogress.model;

/**
 * DTO (Data Transfer Object) para el Frontend.
 * Esto es lo que el JavaScript de dashboard.html espera recibir.
 * Combina datos de 'rutina_ejercicio' (series, reps, peso)
 * y de 'ejercicio' (nombre).
 */
public class RutinaEjercicioDTO {
    
    // De la tabla 'ejercicio'
    private String nombre; 
    
    // De la tabla 'rutina_ejercicio'
    private int series;
    private int repeticiones;
    private double peso;

    // Getters y Setters
    
    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
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