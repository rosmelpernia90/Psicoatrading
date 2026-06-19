-- ============================================================
-- PsicoaTrading — Diario de Trading Psicológico
-- Migración: 3 tablas nuevas
-- Aplicar en: psicoatrading_crm
-- ============================================================

CREATE TABLE IF NOT EXISTS diary_questions (
  id                    INT AUTO_INCREMENT PRIMARY KEY,
  question_text         TEXT NOT NULL,
  unlocked_by_module_id INT NULL,       -- NULL = siempre activa
  is_active             TINYINT(1) NOT NULL DEFAULT 1,
  display_order         INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_dq_module FOREIGN KEY (unlocked_by_module_id)
    REFERENCES courses_modules(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS diary_entries (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  client_id        INT NOT NULL,
  entry_date       DATE NOT NULL,
  traded_today     TINYINT(1) NOT NULL DEFAULT 0,
  financial_result DECIMAL(12, 2) NULL,
  emotional_score  INT NOT NULL,         -- 1-5
  free_notes       TEXT NULL,
  created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_client_date (client_id, entry_date),
  CONSTRAINT fk_de_client FOREIGN KEY (client_id)
    REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diary_entry_answers (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  entry_id    INT NOT NULL,
  question_id INT NOT NULL,
  answer_text TEXT,
  UNIQUE KEY uq_entry_question (entry_id, question_id),
  CONSTRAINT fk_dea_entry FOREIGN KEY (entry_id)
    REFERENCES diary_entries(id) ON DELETE CASCADE,
  CONSTRAINT fk_dea_question FOREIGN KEY (question_id)
    REFERENCES diary_questions(id) ON DELETE CASCADE
);

-- ============================================================
-- Ahora que diary_questions existe, activar el FK en
-- courses_modules.unlocks_diary_question_id
-- ============================================================
ALTER TABLE courses_modules
  ADD CONSTRAINT fk_cm_diary_q
  FOREIGN KEY (unlocks_diary_question_id)
  REFERENCES diary_questions(id) ON DELETE SET NULL;
