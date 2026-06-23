-- ============================================================
-- PsicoaTrading — FASE 1: Roles, Asignación Cliente-Psicólogo, Suscripciones
-- Modelo de 2 tablas (psychologists + clients) — NO se usa tabla `users`
-- Base: psicoatrading_crm
-- Aplicar tras backup:  mysqldump psicoatrading_crm > backup_$(date +%Y%m%d).sql
-- ============================================================
-- Nota de nomenclatura: el rol del equipo clínico en producción es
-- 'psychologist' (no 'psicologo'). Los clientes viven en `clients`.
-- ============================================================

-- ------------------------------------------------------------
-- 1) Perfil profesional del psicólogo  (1:1 con psychologists)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS psicologos_profile (
  psychologist_id     INT PRIMARY KEY,
  bio                 TEXT NULL,
  especialidad        VARCHAR(255) NULL,
  idiomas             VARCHAR(255) NULL,           -- ej: "Español, Inglés"
  max_pacientes       INT NOT NULL DEFAULT 20,
  tarjeta_profesional VARCHAR(100) NULL,
  esta_disponible     TINYINT(1) NOT NULL DEFAULT 1,
  created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_pp_psych FOREIGN KEY (psychologist_id)
    REFERENCES psychologists(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 2) Relación psicólogo ↔ paciente (cliente)
--    Regla: solo UN psicólogo activo por paciente a la vez.
--    Se fuerza con columna generada + UNIQUE (truco portable MySQL/MariaDB).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS psicologo_paciente (
  id                   INT AUTO_INCREMENT PRIMARY KEY,
  psicologo_id         INT NOT NULL,          -- FK psychologists.id
  paciente_id          INT NOT NULL,          -- FK clients.id
  assigned_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
  assigned_by_admin_id INT NULL,              -- FK psychologists.id (admin)
  is_active            TINYINT(1) NOT NULL DEFAULT 1,
  ended_at             DATETIME NULL,
  end_reason           TEXT NULL,
  -- columna generada: igual al paciente solo si la asignación está activa
  active_paciente      INT AS (IF(is_active = 1, paciente_id, NULL)) STORED,
  CONSTRAINT fk_pp2_psico  FOREIGN KEY (psicologo_id) REFERENCES psychologists(id) ON DELETE CASCADE,
  CONSTRAINT fk_pp2_pac    FOREIGN KEY (paciente_id)  REFERENCES clients(id)       ON DELETE CASCADE,
  CONSTRAINT fk_pp2_admin  FOREIGN KEY (assigned_by_admin_id) REFERENCES psychologists(id) ON DELETE SET NULL,
  CONSTRAINT uq_un_psico_activo UNIQUE (active_paciente)
);

-- ------------------------------------------------------------
-- 3) Solicitudes de cambio de psicólogo (las aprueba el admin)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cambio_psicologo_requests (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  paciente_id           INT NOT NULL,                 -- FK clients.id
  current_psicologo_id  INT NULL,                     -- FK psychologists.id
  reason_category       VARCHAR(50) NOT NULL,         -- no_conecto | horarios | enfoque | personal | otro
  reason_text           TEXT NULL,
  share_reason_with_new TINYINT(1) NOT NULL DEFAULT 0,
  status                ENUM('pendiente','aprobada','rechazada') NOT NULL DEFAULT 'pendiente',
  resolved_by_admin_id  INT NULL,                     -- FK psychologists.id
  resolved_at           DATETIME NULL,
  admin_notes           TEXT NULL,
  created_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_cpr_pac   FOREIGN KEY (paciente_id)          REFERENCES clients(id)       ON DELETE CASCADE,
  CONSTRAINT fk_cpr_psico FOREIGN KEY (current_psicologo_id) REFERENCES psychologists(id) ON DELETE SET NULL,
  CONSTRAINT fk_cpr_admin FOREIGN KEY (resolved_by_admin_id) REFERENCES psychologists(id) ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- 4) Sesiones cliente↔psicólogo  (NUEVA — no toca la tabla `sessions`
--    existente, que es de leads. Se llama client_sessions para no romperla.)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS client_sessions (
  id                INT AUTO_INCREMENT PRIMARY KEY,
  paciente_id       INT NOT NULL,            -- FK clients.id
  psicologo_id      INT NOT NULL,            -- FK psychologists.id
  fecha_programada  DATETIME NOT NULL,
  duracion_min      INT NOT NULL DEFAULT 60,
  link_videollamada VARCHAR(500) NULL,
  status            ENUM('agendada','completada','cancelada','no_show') NOT NULL DEFAULT 'agendada',
  notas_clinicas    TEXT NULL,               -- solo psicólogo asignado + admin
  notas_paciente    TEXT NULL,               -- visible para el cliente
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_cs_pac   FOREIGN KEY (paciente_id)  REFERENCES clients(id)       ON DELETE CASCADE,
  CONSTRAINT fk_cs_psico FOREIGN KEY (psicologo_id) REFERENCES psychologists(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 5) Suscripciones (define el plan del cliente → si tiene psicólogo/sesiones)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscriptions (
  id                      INT AUTO_INCREMENT PRIMARY KEY,
  client_id               INT NOT NULL,        -- FK clients.id
  plan                    ENUM('trader_consciente','asesoria','transformacion') NOT NULL,
  gateway                 ENUM('bold','stripe','manual') NOT NULL DEFAULT 'manual',
  gateway_subscription_id VARCHAR(255) NULL,
  status                  ENUM('active','past_due','cancelled','expired') NOT NULL DEFAULT 'active',
  started_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
  current_period_end      DATETIME NULL,
  cancelled_at            DATETIME NULL,
  CONSTRAINT fk_sub_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 6) Tokens de setup del admin (Fase 2 — establecer contraseña por link)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_setup_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  psychologist_id INT NOT NULL,                 -- a qué admin pertenece
  token       VARCHAR(128) NOT NULL UNIQUE,
  expires_at  DATETIME NOT NULL,
  used_at     DATETIME NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ast_psych FOREIGN KEY (psychologist_id) REFERENCES psychologists(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 7) leads — agregar columnas que pide el plan (sin borrar nada)
--    (IF NOT EXISTS soportado en MariaDB; si es MySQL 8 sin soporte,
--     correr cada ALTER por separado e ignorar las que ya existan.)
-- ------------------------------------------------------------
ALTER TABLE leads ADD COLUMN IF NOT EXISTS whatsapp        VARCHAR(40)  NULL;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS stage           VARCHAR(40)  NOT NULL DEFAULT 'nuevo';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_contact_at DATETIME     NULL;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS converted_client_id INT      NULL;

-- ============================================================
-- Verificación
-- ============================================================
SHOW TABLES LIKE 'psicologos_profile';
SHOW TABLES LIKE 'psicologo_paciente';
SHOW TABLES LIKE 'cambio_psicologo_requests';
SHOW TABLES LIKE 'client_sessions';
SHOW TABLES LIKE 'subscriptions';
SHOW TABLES LIKE 'admin_setup_tokens';
DESCRIBE leads;
