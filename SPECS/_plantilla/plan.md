# Plan NNN — Nombre de la funcionalidad

| | |
|---|---|
| **Estado** | Borrador |
| **Spec** | [spec.md](spec.md) (debe estar `Aprobada`) |
| **Creado** | AAAA-MM-DD |

> Aquí va el **cómo técnico**. Todo lo que escribas debe poder rastrearse a un requerimiento de la spec. Si una decisión no responde a ningún RF, RN o RNF, sobra.

## 1. Resumen técnico

*Tres o cuatro frases: qué se construye o cambia y con qué enfoque.*

## 2. Chequeo contra la constitución

*Una fila por principio de `docs/constitucion.md`. Si alguno no se cumple, justifícalo o cambia el plan.*

| Principio | ¿Cumple? | Cómo |
|---|---|---|
| P1 | | |

## 3. Qué hay hoy y qué cambia

*Parte de `docs/as-is/sistema-actual.md`. Lista archivos reales.*

| Archivo o componente | Hoy | Después | Hallazgo que resuelve |
|---|---|---|---|
| | | | H-xx |

## 4. Diseño

### 4.1 Componentes y responsabilidades
*Qué pieza hace qué. Un diagrama de cajas en texto basta.*

### 4.2 Datos
*Tablas y columnas nuevas o cambiadas, con tipo y restricciones. Script de migración que lo aplica.*

### 4.3 Contratos
*Qué recibe y qué devuelve cada operación que la interfaz le pide al backend. Incluye los errores.*

| Operación | Entrada | Salida | Errores |
|---|---|---|---|
| | | | |

## 5. Decisiones técnicas

*Una fila por decisión que tuvo alternativas. Si es grande, haz un ADR aparte.*

| Decisión | Alternativas consideradas | Por qué esta |
|---|---|---|
| | | |

## 6. Estrategia de pruebas

*Cómo se va a comprobar cada criterio de aceptación.*

| Criterio | Tipo de prueba (unitaria, integración, manual) | Dónde vive |
|---|---|---|
| CA-NNN-01a | | |

## 7. Riesgos

| Riesgo | Probabilidad | Mitigación |
|---|---|---|
| | | |
