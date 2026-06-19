-- ============================================
-- PsicoaTrading — Curso "Trader Consciente"
-- Migración: 3 tablas nuevas
-- Aplicar en MySQL Hostinger (psicoatrading_crm)
-- ============================================

CREATE TABLE IF NOT EXISTS courses_modules (
  id                        INT AUTO_INCREMENT PRIMARY KEY,
  module_number             INT NOT NULL UNIQUE,           -- 1..7
  title                     VARCHAR(200) NOT NULL,
  content_md                TEXT,
  is_sequential             TINYINT(1) NOT NULL DEFAULT 1, -- 1: módulos 1,2,3,7 | 0: 4,5,6
  unlocks_diary_question_id INT NULL,                      -- FK lógico al diario (sin constraint por ahora)
  created_at                DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at                DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses_quizzes (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  module_id      INT NOT NULL,
  question       TEXT NOT NULL,
  option_a       VARCHAR(500),
  option_b       VARCHAR(500),
  option_c       VARCHAR(500),
  option_d       VARCHAR(500),
  correct_option CHAR(1) NOT NULL,   -- 'a','b','c','d'
  question_order INT DEFAULT 1,
  CONSTRAINT fk_quiz_module FOREIGN KEY (module_id)
    REFERENCES courses_modules(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses_progress (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  client_id    INT NOT NULL,
  module_id    INT NOT NULL,
  status       VARCHAR(20) NOT NULL DEFAULT 'locked', -- locked|available|in_progress|completed
  quiz_score   INT NULL,
  attempts     INT NOT NULL DEFAULT 0,
  completed_at DATETIME NULL,
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_client_module (client_id, module_id),
  CONSTRAINT fk_progress_client FOREIGN KEY (client_id)
    REFERENCES clients(id) ON DELETE CASCADE,
  CONSTRAINT fk_progress_module FOREIGN KEY (module_id)
    REFERENCES courses_modules(id) ON DELETE CASCADE
);

-- Estructura base de los 7 módulos (SIN contenido real ni quizzes).
-- El contenido y los quizzes se cargan con el seed que generaré desde tus
-- plantillas Markdown. Estas filas solo fijan la estructura/progresión.
INSERT INTO courses_modules (module_number, title, is_sequential) VALUES
  (1, 'Módulo 1', 1),
  (2, 'Módulo 2', 1),
  (3, 'Módulo 3', 1),
  (4, 'Módulo 4', 0),
  (5, 'Módulo 5', 0),
  (6, 'Módulo 6', 0),
  (7, 'Módulo 7', 1)
ON DUPLICATE KEY UPDATE module_number = module_number;  -- no duplica si ya existen
