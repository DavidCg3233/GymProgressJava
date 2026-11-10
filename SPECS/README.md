# SPECS

Proceso de la clase: requisitos → RF / RNF → épicas → historias → especificación → issues → tasks. Cómo se llena cada archivo: [docs/guia-sdd.md](../docs/guia-sdd.md).

## Estado

| Archivo | Qué es | Estado |
|---|---|---|
| [requirements.md](requirements.md) | Requisitos textuales del usuario, clasificados | 25 requisitos · completo |
| [rnf.md](rnf.md) | Requisitos no funcionales, medibles | **Aprobado** (2026-11-09) |
| [issues.md](issues.md) | Features, bugs y errores | Borrador |

| # | Spec (RF) | Épica | spec.md | plan.md | tasks.md |
|---|---|---|---|---|---|
| 006 | [Sesiones de entrenamiento](006-sesiones/spec.md) | Sesiones | **En revisión** · falta la lectura final | — | — |
| 002 | [Rutinas](002-rutinas/spec.md) | Rutinas | Borrador | — | — |
| 004 | [Panel y estadísticas](004-panel-y-estadisticas/spec.md) | Progreso | Borrador | — | — |
| 003 | [Progreso corporal](003-progreso-corporal/spec.md) | Cuerpo | **En revisión** · falta la lectura final | — | — |
| ~~001~~ | ~~Cuentas y acceso~~ | — | Retirada: es RNF → `rnf.md` | | |
| ~~005~~ | ~~Perfil~~ | — | Retirada: es RNF → `rnf.md` | | |

Estados de un documento: `Borrador` → `En revisión` → `Aprobada` → `Implementada`.

## Reglas

1. **Una spec nueva** = copiar `_plantilla/` a `NNN-nombre-corto/` con el siguiente número (el próximo es 007).
2. `plan.md` no se crea hasta que `spec.md` esté `Aprobada`. `tasks.md` no se crea hasta que `plan.md` esté `Aprobado`.
3. Los IDs nunca se reutilizan. Lo que se elimina se tacha y se deja con el motivo.
4. Solo los RF tienen spec. Un RNF va a `rnf.md`.
5. Todo RF debe rastrearse a un requisito `R-xx` de `requirements.md`.

## Orden de trabajo

1. ~~`requirements.md`~~: completo.
2. **006 Sesiones**: 13 decisiones tomadas el 2026-11-09. Falta leerla completa y pasarla a `Aprobada`.
3. ~~`rnf.md`~~: aprobado. Funciona sin conexión, Python + JavaScript, hosting de máximo $20.000 COP al mes.
3b. **003 Progreso corporal**: decisiones tomadas; falta leerla y aprobarla.
4. **002 Rutinas** y luego **004 Panel**.
5. Con la 006 aprobada: `plan.md` de la 006 (ahí se elige el stack) y sus tasks.
