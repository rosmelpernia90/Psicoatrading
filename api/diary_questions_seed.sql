-- ============================================================
-- PsicoaTrading — Seed: 7 preguntas del diario (una por módulo)
-- Aplicar DESPUÉS de diary_schema.sql
-- ============================================================

INSERT INTO diary_questions (question_text, unlocked_by_module_id, is_active, display_order)
VALUES
  ('¿En qué etapa del proceso me sentí hoy: sprint impaciente, frustración, o aceptación del maratón? ¿Qué me lo indica?',
   (SELECT id FROM courses_modules WHERE module_number = 1), 1, 10),

  ('¿Qué miedo apareció hoy en mi operativa? ¿Qué creencia sobre el dinero se activó cuando gané o perdí?',
   (SELECT id FROM courses_modules WHERE module_number = 2), 1, 20),

  ('¿Hice alguna operación extra fuera del plan hoy? ¿En qué momento creí tener razón cuando el mercado me mostraba lo contrario?',
   (SELECT id FROM courses_modules WHERE module_number = 3), 1, 30),

  ('¿Cumplí mi trading plan hoy al 100%? ¿En qué decisión confié por datos y en cuál por impulso?',
   (SELECT id FROM courses_modules WHERE module_number = 4), 1, 40),

  ('¿Qué de mi entorno me sumó o me restó hoy? ¿Cómo manejé los momentos en que estuve solo decidiendo?',
   (SELECT id FROM courses_modules WHERE module_number = 5), 1, 50),

  ('¿En qué etapa de desarrollo me sentí hoy? ¿Hice mi ritual pre-sesión? ¿Cuántas veces se me fue la mente y supe volver?',
   (SELECT id FROM courses_modules WHERE module_number = 6), 1, 60),

  ('¿Qué del sistema mantengo, qué ajusto y por qué — basado en datos, no en emoción? ¿Qué de mí mismo necesito flexibilizar esta semana?',
   (SELECT id FROM courses_modules WHERE module_number = 7), 1, 70);

-- Conectar cada módulo con su pregunta de diario
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 10) WHERE module_number = 1;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 20) WHERE module_number = 2;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 30) WHERE module_number = 3;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 40) WHERE module_number = 4;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 50) WHERE module_number = 5;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 60) WHERE module_number = 6;
UPDATE courses_modules SET unlocks_diary_question_id =
  (SELECT id FROM diary_questions WHERE display_order = 70) WHERE module_number = 7;

-- Verificar
SELECT m.module_number, m.title, dq.question_text
FROM courses_modules m
JOIN diary_questions dq ON dq.id = m.unlocks_diary_question_id
ORDER BY m.module_number;
