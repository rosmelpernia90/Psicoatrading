# REPORTE DE ESTADO — APP CLÍNICA PSICOATRADING
**Corte al:** 2026-06-22
**Generado desde:** código real del repo (commit `08c37b0`) + pruebas end-to-end verificadas en producción

> Metodología: cada afirmación está respaldada por código del repo, output de curl/SQL real, o se marca explícitamente como "NO VERIFICADO / requiere comando en servidor".

---

## SECCIÓN 1 — MÓDULOS Y ESTADO REAL

### 1. SISTEMA DE LOGIN Y AUTENTICACIÓN
**Estado:** ✅ COMPLETADO
**Hecho:** JWT con python-jose, bcrypt para passwords. `POST /api/auth/login` busca en `psychologists` y luego en `clients`. Token incluye sub/name/role, TTL 480 min. Verificado con curl (admin y cliente devuelven token + role correcto).
**Falta:** Nada crítico. Opcional: refresh tokens, recuperación de contraseña.

### 2. SISTEMA DE ROLES (admin / psychologist / cliente)
**Estado:** ✅ COMPLETADO
**Hecho:** 3 roles funcionando. `admin`/`psychologist` en tabla `psychologists` (ENUM), `cliente` en tabla `clients` (VARCHAR). Frontend enruta por rol: admin/psychologist → panel clínico; cliente → portal cliente. Guard `require_admin` para endpoints sensibles. Verificado en navegador y curl.
**Falta:** Nada. (Nota: un psicólogo no puede convertirse en cliente ni viceversa por diseño — están en tablas separadas.)

### 3. PANEL CLÍNICO (Dashboard, Pacientes, Emails, Sesiones)
**Estado:** 🟡 EN PROGRESO ~85%
**Hecho:** Las 4 vistas existen y cargan. Pacientes lista leads reales, detalle con timeline/notas/sesiones/emails, búsqueda. Emails muestra la cola. Login carga el panel sin romperse.
**Falta:** El **Dashboard muestra `undefined`** en 5 tarjetas (ver Sección 4). La vista Sesiones es solo texto placeholder. Detalle de paciente espera campos que el backend no siempre envía (risk_level, percentile).

### 4. MÓDULO USUARIOS (gestión desde admin)
**Estado:** ✅ COMPLETADO (MVP)
**Hecho:** Vista admin con tabla (nombre, email, rol, tipo, estado), buscador, contador. Modal crear/editar. Endpoints `GET/POST/PUT /api/admin/users`. Solo visible para admin. Verificado end-to-end en preview.
**Falta:** Eliminar usuarios (hoy solo activar/desactivar). Permisos por módulo (se descartó para el MVP).

### 5. CAPTURA DE LEADS DESDE WEB PÚBLICA
**Estado:** 🔴 BLOQUEADO / DESCONECTADO
**Hecho:** Backend listo: `POST /api/test-results` (crea lead + guarda test + dispara secuencia de emails) y `POST /api/contact`. El index público tiene el contenido de marketing de los tests.
**Falta (CRÍTICO):** El **`index.html` público NO tiene ningún `fetch` ni llamada a `/api/`** — el formulario no está conectado al backend. Los tests son presentación, no guardan nada. Hay que cablear el frontend público a los endpoints. *(Evidencia: grep de `fetch(`, `psicoatrading.online`, `/api/` en index.html = 0 resultados.)*

### 6. SISTEMA DE EMAILS (SendGrid + automatizaciones)
**Estado:** 🟡 EN PROGRESO ~70%
**Hecho:** Lógica completa en código: secuencia de 5 emails post-test (`EMAIL_SEQUENCES`), cola `email_queue`, job APScheduler cada 5 min (`send_pending_emails`), recordatorio de diario a los 3 días (`send_diary_reminders`, cada 24h). Plantillas escritas.
**Falta:** `SENDGRID_API_KEY` está VACÍO en `/var/www/api/.env` → **no se envía ningún email real**. Los jobs corren pero hacen `return` temprano sin la key. Falta crear cuenta SendGrid y poner la key.

### 7. TESTS PSICOLÓGICOS A Y B
**Estado:** 🟡 EN PROGRESO (backend ✅ / frontend público ❌)
**Hecho:** Backend modela `test_results` (test_type A/B, profile, score) + `dimension_scores`. `POST /api/test-results` guarda todo y agenda emails. Contenido de los tests existe en el index público.
**Falta:** Igual que #5 — el frontend público no envía los resultados al backend. No hay flujo real de "usuario hace test → se guarda".

### 8. PORTAL DEL CLIENTE (vista rol cliente)
**Estado:** ✅ COMPLETADO
**Hecho:** Portal con header propio, navegación Curso/Diario. Reemplaza el placeholder anterior. Verificado en navegador con `carlos@test.com`.
**Falta:** Sección "Recursos" (mencionada en specs, aún no construida).

### 9. MÓDULO CURSO "TRADER CONSCIENTE"
**Estado:** ✅ COMPLETADO
**Hecho:** 7 módulos con contenido real (texto + quizzes). Progresión mixta (1-2-3 secuencial, 4-5-6 libre, 7 final). Quiz con scoring, 80% para aprobar, 3 intentos. Mosaico visual, lectura, quiz interactivo. Verificado: cliente completó M1 → desbloqueó M2 (curl `next_unlocked: [2]`).
**Falta:** Nada del core. Falta certificado "Trader Consciente" al completar los 7.

### 10. MÓDULO DIARIO DE TRADING PSICOLÓGICO
**Estado:** ✅ COMPLETADO
**Hecho:** 3 tablas, 6 endpoints. Preguntas dinámicas según progreso del curso, campos base, calendario por color emocional, estadísticas con Chart.js, vista psicólogo de solo lectura. Edición solo del día actual. Verificado end-to-end (cliente crea entrada → psicólogo la ve con stats).
**Falta:** Recordatorio por email depende de SendGrid (ver #6). Vista de estadísticas del psicólogo podría llevar la misma gráfica que el cliente.

### 11. CI/CD GITHUB ACTIONS → VPS
**Estado:** 🟡 CONFIGURADO PERO NO VERIFICADO (probablemente no dispara)
**Hecho:** `deploy.yml` existe y está bien escrito (pull + cp a docroots + pip install + restart). Usa secrets SSH.
**Falta:** **Evidencia indica que NO se ejecuta automáticamente** — en cada deploy hubo que copiar archivos manualmente (`\cp -f ...`). Si el CI/CD funcionara, no haría falta. Probable causa: secrets `SSH_HOST/SSH_USER/SSH_PRIVATE_KEY` no configurados en GitHub. **Requiere verificar la pestaña Actions del repo.**

### 12. INTEGRACIÓN DE PAGOS (Bold + Stripe)
**Estado:** 🔴 NO INICIADO
**Hecho:** Nada. Cero endpoints, cero código, cero tablas relacionadas a pagos en el repo de producción.
**Falta:** Todo. (Nota: hay docs antiguos de Stripe en el prototipo viejo `Psicoatrading/APP`, pero ese código NO está en producción ni es el mismo proyecto.)

---

## SECCIÓN 2 — BASE DE DATOS

> ⚠️ Los counts exactos requieren correr SQL en el servidor. Abajo: lo CONFIRMADO en pruebas + los comandos para el dato exacto.

**Tablas confirmadas (de los schemas aplicados):**
`psychologists, leads, test_results, dimension_scores, email_queue, sessions, clinical_notes, clients, courses_modules, courses_quizzes, courses_progress, diary_questions, diary_entries, diary_entry_answers`

**No existe tabla `users`** — la spec original la asumía; en realidad los usuarios viven en `psychologists` (equipo) y `clients` (clientes).

**Counts confirmados en pruebas:**
- `psychologists`: 1 (admin `psicoatrading@gmail.com`)
- `clients`: ≥1 (`carlos@test.com`)
- `leads`: 2 (vistos en dashboard)
- `courses_modules`: 7 (con 5/5/5/5/5/5/10 preguntas)
- `diary_questions`: 7 (una por módulo)
- `diary_entries`: 1 (entrada de prueba de Carlos)

**Comandos para los datos exactos (correr en servidor):**
```sql
SHOW TABLES;
DESCRIBE psychologists; DESCRIBE clients;
SELECT COUNT(*) FROM clients;
SELECT COUNT(*) FROM leads;
SELECT COUNT(*) FROM test_results;
SELECT COUNT(*) FROM email_queue;
SELECT role, COUNT(*) FROM psychologists GROUP BY role;
SELECT role, COUNT(*) FROM clients GROUP BY role;
```

---

## SECCIÓN 3 — ENDPOINTS ACTIVOS (listado real, no resumen)

> Extraído del `main.py` real (commit `08c37b0`). 25 endpoints.

**Públicos (sin auth):**
- `[GET] /api/health` — healthcheck — NO auth
- `[POST] /api/test-results` — crea lead + guarda test + agenda emails — NO auth
- `[POST] /api/contact` — registra lead de contacto — NO auth
- `[POST] /api/auth/login` — autentica (psicólogo o cliente) — NO auth
- `[POST] /api/auth/register` — registra cliente nuevo (role=cliente) — NO auth

**Panel clínico (requieren token):**
- `[GET] /api/dashboard/stats` — KPIs — auth
- `[GET] /api/leads` — lista leads (paginado, búsqueda) — auth
- `[GET] /api/leads/{id}` — detalle lead + tests/notas/sesiones/emails — auth
- `[POST] /api/clinical-notes` — crea nota clínica — auth (psicólogo)
- `[POST] /api/sessions` — crea sesión — auth (psicólogo)
- `[GET] /api/email-queue` — cola de emails — auth

**Admin usuarios (require_admin):**
- `[GET] /api/admin/users` — lista psicólogos + clientes — auth ADMIN
- `[POST] /api/admin/users` — crea usuario — auth ADMIN
- `[PUT] /api/admin/users/{tipo}/{id}` — edita usuario — auth ADMIN

**Curso (clientes + vista psicólogo):**
- `[GET] /api/course/modules` — 7 módulos con estado del cliente — auth (cliente)
- `[GET] /api/course/modules/{id}` — contenido + quiz — auth (cliente)
- `[POST] /api/course/modules/{id}/complete` — califica quiz, desbloquea — auth (cliente)
- `[GET] /api/course/progress` — progreso de clientes — auth (admin/psicólogo)

**Diario:**
- `[GET] /api/diary/questions` — preguntas activas según progreso — auth (cliente)
- `[POST] /api/diary/entries` — crea entrada del día — auth (cliente)
- `[GET] /api/diary/entries` — historial propio — auth (cliente)
- `[GET] /api/diary/entries/{id}` — entrada + respuestas — auth (cliente)
- `[PATCH] /api/diary/entries/{id}` — edita (solo día actual) — auth (cliente)
- `[GET] /api/diary/client/{id}` — diario completo de un cliente — auth (admin/psicólogo)

---

## SECCIÓN 4 — BUGS Y PROBLEMAS PENDIENTES

**1. Dashboard muestra `undefined` en 5 tarjetas** — CONFIRMADO, sigue pendiente
- **Severidad:** Media (es cosmético pero se ve mal en el panel principal)
- **Causa identificada:** SÍ. El endpoint `/api/dashboard/stats` devuelve `{total_leads, new_leads, converted, conversion_rate, total_tests, pending_emails, sent_emails, upcoming_sessions, recent_leads_7d}` pero el frontend espera `{tests_a, tests_b, alerts_danger, alerts_warning, avg_percentile, pending_sessions, emails_sent, emails_pending, profile_distribution, funnel_distribution}`. Los nombres no coinciden → undefined.
- **Solución propuesta:** Reescribir el endpoint para devolver exactamente los campos que el frontend consume (incluye agregaciones de test_results por perfil y de leads por funnel_stage). ~1-2h.

**2. Captura de leads / tests desconectada del backend** — CONFIRMADO
- **Severidad:** Alta (es el embudo de entrada del negocio)
- **Causa:** El `index.html` público no tiene código que llame a `/api/test-results` ni `/api/contact`.
- **Solución:** Cablear los formularios del index público a los endpoints existentes.

**3. Emails no se envían** — CONFIRMADO
- **Severidad:** Alta para producción (media mientras no haya clientes reales)
- **Causa:** `SENDGRID_API_KEY` vacío en `.env`.
- **Solución:** Crear cuenta SendGrid, validar dominio, poner la key.

**4. CI/CD no auto-despliega** — PROBABLE (no verificado)
- **Severidad:** Baja (deploy manual funciona)
- **Causa probable:** secrets SSH no configurados en GitHub.
- **Solución:** Revisar pestaña Actions; configurar secrets o documentar deploy manual como oficial.

**5. FK `unlocks_diary_question_id` en registros viejos = null** — Menor
- **Severidad:** Baja (no afecta funcionalidad; las preguntas se calculan por módulos completados)
- **Causa:** El progreso de Carlos se creó antes de existir `diary_questions`.
- **Solución:** Ninguna urgente.

---

## SECCIÓN 5 — DIFERENCIAS LOCALHOST vs PRODUCCIÓN

1. **¿Mismo código?** SÍ, idéntico. El preview local (`localhost:5177`) sirve EL MISMO archivo `PsicoatradingPROD/app/index.html` que se despliega a producción. No hay divergencia.
2. **Diferencias:** Solo el puerto del preview (5177). El código es bit a bit el mismo archivo.
3. **¿BD local?** NO existe BD local. El preview local consume la **API de producción** (`https://psicoatrading.online`), que usa la **MySQL de Hostinger**. Nunca se apunta a BD local (regla del proyecto).
4. **¿Backend local?** NO hay backend local corriendo para este flujo. El HTML local llama directo a la API de producción (CORS permite `localhost:5177`).

---

## SECCIÓN 6 — DEPLOY Y CI/CD

1. **Último deploy:** 2026-06-19 (módulo Diario, commit `08c37b0`), aplicado manualmente en el servidor.
2. **¿Cambios pendientes de subir?** NO. `git status` limpio, local sincronizado con `origin/main` (0 adelante, 0 atrás).
3. **¿Branches abiertas?** NO. Solo `main`.
4. **¿GitHub Actions funciona?** Sin confirmar — la evidencia sugiere que NO dispara (siempre hizo falta `cp` manual). Requiere revisar la pestaña Actions del repo.

---

## SECCIÓN 7 — TRABAJO Y SIGUIENTE TAREA

1. **Esta semana se trabajó en:** Sistema de roles → Panel admin de usuarios → Curso completo (7 módulos) → Diario de trading. Todo desplegado y verificado.
2. **Horas:** No tengo registro de horas; trabajo por sesión de chat, no por tiempo. No voy a inventar una cifra.
3. **Siguiente tarea sugerida (en orden de impacto de negocio):**
   - **a)** Conectar captura de leads/tests del index público (es el embudo de entrada — sin esto no entran clientes).
   - **b)** Arreglar el dashboard `undefined` (rápido, mejora percepción del panel).
   - **c)** Configurar SendGrid (activa toda la automatización de emails ya escrita).
   - **d)** Pagos (Bold/Stripe) — necesario para monetizar, pero más grande.
4. **¿Bloqueado por algo?** Para SendGrid y pagos necesito que TÚ crees las cuentas y me pases las keys. Para el resto, no hay bloqueo.

---

## SECCIÓN 8 — DUDAS / DECISIONES QUE NECESITO DE TI

1. **¿Prioridad de la próxima tarea?** — Importa porque define qué construyo. Opciones: leads/tests (entrada de clientes), dashboard (cosmético rápido), SendGrid (emails), o pagos.
2. **Pagos: ¿Bold, Stripe, o ambos?** — Bold es ideal para Colombia (PSE, tarjetas locales); Stripe para internacional. Importa porque cambia toda la integración. Necesito saber el mercado objetivo.
3. **¿Tienes cuenta SendGrid?** — Si no, hay que crearla y validar el dominio `psicoatrading.online` (toma ~1 día por DNS). Importa para activar todos los emails ya programados.
4. **¿Quieres que documente el deploy manual como oficial, o arreglamos el CI/CD?** — Importa para no depender de copiar archivos a mano cada vez.
