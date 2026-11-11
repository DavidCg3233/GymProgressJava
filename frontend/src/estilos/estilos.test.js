// Las fichas de diseño mandan (T-007-01, T-007-02 · RN-007-04 · RNF-007-01 · DESIGN.md, sección 2).
//
// Lee los archivos como texto: así la regla vale para cualquier pantalla nueva.

import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { describe, expect, it } from 'vitest'

const SRC = fileURLToPath(new URL('..', import.meta.url))
const FICHAS = join(SRC, 'estilos', 'fichas.css')

function archivos(carpeta) {
  return readdirSync(carpeta).flatMap((nombre) => {
    const ruta = join(carpeta, nombre)
    return statSync(ruta).isDirectory() ? archivos(ruta) : [ruta]
  })
}

const conEstilos = archivos(SRC).filter((ruta) => /\.(vue|css)$/.test(ruta) && ruta !== FICHAS)

// --- T-007-01: un solo lugar para los colores --------------------------------

describe('los colores salen de las fichas', () => {
  it('ninguna pantalla usa las variables viejas --color-*', () => {
    const conViejas = conEstilos.filter((ruta) => /--color-/.test(readFileSync(ruta, 'utf8')))

    expect(conViejas).toEqual([])
  })

  it('ninguna pantalla escribe un color a mano', () => {
    const conColores = conEstilos.filter((ruta) => /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/.test(readFileSync(ruta, 'utf8')))

    expect(conColores).toEqual([])
  })
})

// --- T-007-02: contraste medido en los dos temas -----------------------------

function fichasDe(bloque) {
  return Object.fromEntries([...bloque.matchAll(/--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;/g)].map(([, nombre, hex]) => [nombre, hex]))
}

function temas() {
  const css = readFileSync(FICHAS, 'utf8')
  const claro = css.match(/:root\s*\{([^}]*)\}/)
  const oscuro = css.match(/prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}/)
  return { claro: fichasDe(claro[1]), oscuro: fichasDe(oscuro[1]) }
}

function luminancia(hex) {
  const [r, g, b] = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
  const lineal = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  return 0.2126 * lineal(r) + 0.7152 * lineal(g) + 0.0722 * lineal(b)
}

export function contraste(a, b) {
  const [claro, oscuro] = [luminancia(a), luminancia(b)].sort((x, y) => y - x)
  return (claro + 0.05) / (oscuro + 0.05)
}

// Cada texto sobre cada fondo donde puede aparecer (DESIGN.md, sección 5).
const PARES_DE_TEXTO = [
  ['tinta', 'fondo'],
  ['tinta', 'superficie'],
  ['tinta', 'superficie-2'],
  ['tinta', 'acento-tinte'],
  ['tinta-suave', 'fondo'],
  ['tinta-suave', 'superficie'],
  ['tinta-suave', 'superficie-2'],
  ['tinta-suave', 'acento-tinte'],
  ['acento', 'fondo'],
  ['acento', 'superficie'],
  ['acento', 'acento-tinte'],
  ['sobre-acento', 'acento'],
  ['error', 'fondo'],
  ['error', 'superficie'],
  ['aviso', 'fondo'],
  ['aviso', 'superficie'],
]

describe('contraste (RNF-007-01)', () => {
  it('la fórmula de WCAG da 21:1 entre blanco y negro', () => {
    expect(contraste('#FFFFFF', '#000000')).toBeCloseTo(21, 5)
  })

  it('los dos temas tienen las mismas fichas', () => {
    const { claro, oscuro } = temas()

    expect(Object.keys(oscuro).sort()).toEqual(Object.keys(claro).sort())
  })

  for (const tema of ['claro', 'oscuro']) {
    it.each(PARES_DE_TEXTO)(`${tema}: --%s sobre --%s llega a 4,5:1`, (texto, fondo) => {
      const fichas = temas()[tema]

      expect(contraste(fichas[texto], fichas[fondo])).toBeGreaterThanOrEqual(4.5)
    })
  }
})
