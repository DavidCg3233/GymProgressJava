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
| 006 | [Sesiones de entrenamiento](006-sesiones/spec.md) | Sesiones | **Aprobada** (2026-11-10) | [**Aprobado**](006-sesiones/plan.md) (2026-11-10) | [Escritas](006-sesiones/tasks.md) · 0 de 38 |
| 002 | [Rutinas y catálogo](002-rutinas/spec.md) | Rutinas | **Aprobada** (2026-11-10) | [**Aprobado**](002-rutinas/plan.md) (2026-11-10) | [Escritas](002-rutinas/tasks.md) · 0 de 20 |
| 004 | [Inicio y progreso](004-panel-y-estadisticas/spec.md) | Progreso | **Aprobada** (2026-11-10) | [**Aprobado**](004-panel-y-estadisticas/plan.md) (2026-11-10) | [Escritas](004-panel-y-estadisticas/tasks.md) · 16 de 18 con código |
| 003 | [Progreso corporal](003-progreso-corporal/spec.md) | Cuerpo | **Aprobada** (2026-11-10) | [**Aprobado**](003-progreso-corporal/plan.md) (2026-11-11) | [Escritas](003-progreso-corporal/tasks.md) · 14 de 16 con código |
| 007 | [Rediseño visual](007-rediseno-visual/spec.md) | Diseño | **Aprobada** (2026-11-11) · con [DESIGN.md](../DESIGN.md) y su [muestra](../docs/diseno/muestra.html) | [**Aprobado**](007-rediseno-visual/plan.md) (2026-11-11) | [Escritas](007-rediseno-visual/tasks.md) · 9 de 18 con código |
| 008 | [El récord manda y la sesión se vuelve rutina](008-record-y-sesion-a-rutina/spec.md) | Rutinas | **Aprobada** (2026-11-13) | [**Aprobado**](008-record-y-sesion-a-rutina/plan.md) (2026-11-13) | [Escritas](008-record-y-sesion-a-rutina/tasks.md) · 16 de 17 con código |
| ~~001~~ | ~~Cuentas y acceso~~ | — | Retirada: es RNF → `rnf.md` | | |
| ~~005~~ | ~~Perfil~~ | — | Retirada: es RNF → `rnf.md` | | |

Estados de un documento: `Borrador` → `En revisión` → `Aprobada` → `Implementada`.

## Reglas

1. **Una spec nueva** = copiar `_plantilla/` a `NNN-nombre-corto/` con el siguiente número (el próximo es 009).
2. `plan.md` no se crea hasta que `spec.md` esté `Aprobada`. `tasks.md` no se crea hasta que `plan.md` esté `Aprobado`.
3. Los IDs nunca se reutilizan. Lo que se elimina se tacha y se deja con el motivo.
4. Solo los RF tienen spec. Un RNF va a `rnf.md`.
5. Todo RF debe rastrearse a un requisito `R-xx` de `requirements.md`.

## Orden de trabajo

1. ~~`requirements.md` y `rnf.md`~~: completos y aprobados.
2. ~~006 Sesiones y 003 Progreso corporal~~: aprobadas.
3. ~~002 Rutinas y 004 Inicio y progreso~~: aprobadas el 2026-11-10. Siguen sus `plan.md` y `tasks.md`.
4. ~~`plan.md` de la 006~~: aprobado. Stack: Django + DRF, PostgreSQL, Vue 3 como app instalable, Caddy y Docker Compose en un VPS.
5. **[Tasks de la 006](006-sesiones/tasks.md)**: 38 tareas en dos hitos. El hito A (sesión libre) se puede empezar ya; el hito B espera a la spec 002.
