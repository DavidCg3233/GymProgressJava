package org.gymprogress.model;
import java.sql.Date;

public class Progreso {
    private int codigoProgreso;
    private int codigoUsuario;
    private Date fecha;
    private double pesoCorporal;
    private double altura;
    private String notas;

    // Getters y Setters
    public int getCodigoProgreso() { return codigoProgreso; }
    public void setCodigoProgreso(int c) { this.codigoProgreso = c; }
    public int getCodigoUsuario() { return codigoUsuario; }
    public void setCodigoUsuario(int codigoUsuario) { this.codigoUsuario = codigoUsuario; }
    public Date getFecha() { return fecha; }
    public void setFecha(Date fecha) { this.fecha = fecha; }
    public double getPesoCorporal() { return pesoCorporal; }
    public void setPesoCorporal(double pesoCorporal) { this.pesoCorporal = pesoCorporal; }
    public double getAltura() { return altura; }
    public void setAltura(double altura) { this.altura = altura; }
    public String getNotas() { return notas; }
    public void setNotas(String notas) { this.notas = notas; }
}