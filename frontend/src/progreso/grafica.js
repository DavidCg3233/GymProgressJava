// Escalas de la gráfica de evolución (T-004-14 · plan 004, sección 6).
// Convierte valores en coordenadas de un SVG. En SVG la "y" crece hacia abajo,
// así que el valor mayor queda con la "y" menor.

/**
 * @param {number[]} valores un valor por sesión, en orden de fecha
 * @param {{ ancho: number, alto: number, margen: number }} area
 */
export function puntosDeLaGrafica(valores, { ancho, alto, margen }) {
  if (valores.length === 0) {
    return { puntos: [], minimo: 0, maximo: 0 }
  }
  const minimo = Math.min(...valores)
  const maximo = Math.max(...valores)
  const anchoUtil = ancho - 2 * margen
  const altoUtil = alto - 2 * margen

  const x = (indice) => (valores.length === 1 ? ancho / 2 : margen + (anchoUtil * indice) / (valores.length - 1))
  // Si todos valen lo mismo no hay rango: la línea va por el medio.
  const y = (valor) => (maximo === minimo ? alto / 2 : margen + (altoUtil * (maximo - valor)) / (maximo - minimo))

  return { puntos: valores.map((valor, indice) => ({ x: x(indice), y: y(valor) })), minimo, maximo }
}
