package org.gymprogress.utils;

/**
 * Clase de utilidad para cálculos relacionados con el IMC.
 * (RF04, RF05)
 */
public class CalculoIMC {

    /**
     * Constructor privado para evitar que esta clase de utilidad sea instanciada.
     */
    private CalculoIMC() {}

    /**
     * Calcula el Índice de Masa Corporal (IMC).
     *
     * @param pesoKg El peso del usuario en kilogramos (ej. 75.5)
     * @param alturaM La altura del usuario en metros (ej. 1.75)
     * @return El valor del IMC calculado.
     */
    public static double calcularIMC(double pesoKg, double alturaM) {
        // Evitar división por cero si la altura es 0 o no está registrada
        if (alturaM <= 0) {
            return 0;
        }
        
        // Fórmula del IMC: peso / (altura * altura)
        double imc = pesoKg / (alturaM * alturaM);
        
        // Redondear a un decimal para consistencia
        return Math.round(imc * 10.0) / 10.0;
    }

    /**
     * Devuelve la categoría de IMC basada en el valor.
     * (Basado en la lógica de 'getBMICategory' del código de React)
     *
     * @param imc El valor del IMC (ej. 24.5)
     * @return Un String con la categoría (ej. "Normal", "Sobrepeso")
     */
    public static String getCategoriaIMC(double imc) {
        if (imc <= 0) {
            return "N/A";
        }
        if (imc < 18.5) {
            return "Bajo Peso";
        }
        if (imc < 25) {
            return "Normal";
        }
        if (imc < 30) {
            return "Sobrepeso";
        }
        return "Obesidad";
    }
}