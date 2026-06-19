-- ============================================================
-- PsicoaTrading — Seed Módulo 7 del Curso Trader Consciente
-- Aplicar DESPUÉS de course_schema.sql y seeds 1-6
-- Base: psicoatrading_crm
-- ============================================================

DELETE FROM courses_quizzes WHERE module_id IN (
  SELECT id FROM courses_modules WHERE module_number = 7
);

-- ============================================================
-- MÓDULO 7 — LA FLEXIBILIDAD: ADAPTARSE SIN ROMPERSE
-- ============================================================
UPDATE courses_modules
SET
  title      = 'La Flexibilidad: Adaptarse sin Romperse',
  content_md = '## Introducción

Llegaste hasta aquí. Reconociste tus saboteadores, construiste tus bases, manejaste tu entorno, identificaste tu etapa. Ahora viene el módulo que cierra y al mismo tiempo abre — porque la flexibilidad no es una técnica, es una forma de habitar este oficio para siempre.

El mercado cambia. Tú cambias. Tu sistema, que hoy funciona, en seis meses puede dejar de hacerlo. La pregunta del trader maduro no es "¿cuál es el sistema perfecto?", sino "¿soy capaz de adaptarme cuando el mercado me lo pida — sin romperme, sin abandonar lo que sí funciona?" Este módulo te entrega ese discernimiento.

## Las verdades del módulo

**1. Flexibilidad no es cambiar cada semana. Es saber cuándo cambiar.** El trader principiante cambia de sistema cada vez que pierde tres operaciones. El profesional sostiene su sistema en las rachas malas porque sabe que son parte del modelo, y lo cambia solo cuando hay evidencia estructural de que el mercado cambió. La diferencia entre lo uno y lo otro es la diferencia entre quebrar y durar.

**2. Aferrarse a una idea fija te ciega.** "El precio tiene que subir." "Esta es la mejor estrategia." "Siempre opero a esta hora." Cada vez que dices "siempre" o "nunca", el ego está hablando. El mercado no se ajusta a tus reglas — son tus reglas las que se ajustan al mercado, dentro de un marco con disciplina.

**3. Hay flexibilidad sana y flexibilidad disfrazada.** La sana ajusta el sistema con datos: tres meses de evidencia, métricas claras, decisión fría. La disfrazada cambia el sistema en caliente, después de una pérdida fuerte, buscando salvarse. La primera te hace crecer. La segunda te quiebra dos veces.

**4. El mercado evoluciona. Tú también debes hacerlo.** Lo que funcionó en volatilidad alta no funciona en lateralización. Lo que servía con tu capital de antes no sirve con el de ahora. Lo que aprendiste hace dos años puede estar obsoleto. El trader que se queda quieto ideológicamente va a quebrar — aunque tenga disciplina.

**5. La flexibilidad final es contigo mismo.** No solo con el sistema. Vas a tener semanas malas, vas a recaer en miedo o ego, vas a romper tu plan algún día. Cuando eso pase, no te castigues — analiza, ajusta, vuelve. La rigidez consigo mismo es el atajo más rápido al abandono.

## El espejo

- ¿Cuántas veces cambié de sistema en el último año? ¿Por evidencia o por frustración?
- ¿En qué creencia operativa me he aferrado, aunque los datos me digan otra cosa?
- ¿Soy más rígido conmigo mismo cuando pierdo o cuando gano?
- Si tuviera que enseñar este módulo a alguien que recién empieza, ¿qué les diría que yo no aprendí a tiempo?

## Herramienta práctica — Análisis trimestral del sistema

Toma tus últimos 3 meses de operaciones y responde estas preguntas con datos reales:

- ¿Qué reglas del sistema cumplí al 100%?
- ¿Qué reglas rompí más de 3 veces?
- ¿Qué condición del mercado cambió en este periodo?
- ¿Qué métrica mejoró? (winrate, ratio riesgo/beneficio, drawdown)
- ¿Qué métrica empeoró?
- ¿Qué decisión voy a mantener exactamente igual?
- ¿Qué decisión voy a ajustar y bajo qué criterio?
- ¿Qué decisión NO voy a tocar aunque me duela?

Este análisis se hace cada 90 días. Es el ritual de revisión que separa al que va creciendo del que va girando en círculos.

## Síntesis personal — Tu manifiesto del trader consciente

Antes de cerrar el curso, escribe en una sola página tu manifiesto. Una frase por módulo, con lo que TÚ aprendiste:

- **Sobre el camino real:**
- **Sobre el miedo y el dinero:**
- **Sobre la avaricia y el ego:**
- **Sobre la confianza y la disciplina:**
- **Sobre el entorno y la soledad:**
- **Sobre el desarrollo y el foco:**
- **Sobre la flexibilidad:**

Esta hoja la guardas. La revisas cada 6 meses. Vas a ver cómo evoluciona — y esa evolución es la prueba de que dejaste de ser aficionado.

## Cierre PsicoaTrading

*"Ser trader consciente no es llegar. Es caminar. Y caminar conscientemente, con la mente entrenada y el corazón flexible, es lo único que el mercado respeta a largo plazo."*'
WHERE module_number = 7;

-- Quiz módulo 7 (10 preguntas — 80% = 8/10 para aprobar)
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La flexibilidad sana en el trading es:',
  'Cambiar de sistema cada vez que se pierde',
  'Ajustar el sistema basado en datos y evidencia estructural',
  'Mantener el mismo sistema sin importar lo que haga el mercado',
  'Operar sin reglas fijas para adaptarse rápido',
  'b', 1
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Decir "siempre opero a esta hora" o "el precio tiene que subir" es señal de:',
  'Experiencia operativa sólida',
  'Rigidez y ego operando',
  'Disciplina con el sistema',
  'Profesionalismo y consistencia',
  'b', 2
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Cuándo sí se debe ajustar el sistema?',
  'Después de 3 pérdidas seguidas',
  'Cuando emocionalmente te sientes mal con los resultados',
  'Con evidencia de varios meses y métricas claras que muestran un cambio estructural',
  'Cada vez que cambia el broker',
  'c', 3
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La flexibilidad disfrazada es:',
  'Adaptarse al cambio del mercado con disciplina y datos',
  'Cambiar el sistema en caliente después de una pérdida buscando salvarse',
  'Modificar el sistema cada mes con métricas claras',
  'Operar con varios sistemas simultáneamente',
  'b', 4
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La rigidez contigo mismo (castigarte por errores) lleva principalmente a:',
  'Mejorar la disciplina operativa',
  'Aumentar la motivación para no volver a fallar',
  'Abandono y desgaste emocional progresivo',
  'Mayor rendimiento a largo plazo',
  'c', 5
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Un trader que no evoluciona con el tiempo, aunque tenga disciplina:',
  'Será consistente para siempre',
  'Eventualmente quebrará porque el mercado cambia y él no',
  'No necesita ajustar nada si su sistema tiene lógica',
  'Es el modelo ideal de trader profesional',
  'b', 6
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'El análisis trimestral del sistema sirve para:',
  'Cambiar de estrategia cuando algo no funciona',
  'Validar con datos qué mantener, qué ajustar y qué no tocar — con la cabeza fría',
  'Llevar el registro contable de ganancias y pérdidas',
  'Compararse con el rendimiento de otros traders',
  'b', 7
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Cuál es la diferencia clave entre principiante y profesional ante una racha mala?',
  'El principiante opera más, el profesional reduce posiciones',
  'El principiante cambia el sistema; el profesional lo sostiene si la racha es parte del modelo',
  'El principiante busca ayuda externa, el profesional opera solo',
  'No hay diferencia significativa entre ambas respuestas',
  'b', 8
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La frase "este sistema es perfecto" demuestra:',
  'Que el trader alcanzó el nivel de consistencia máximo',
  'Que está en zona ciega: ningún sistema es perfecto, todos requieren evolución',
  'Que tiene suficiente experiencia para no cambiar nada',
  'Que opera con disciplina absoluta y confianza real',
  'b', 9
FROM courses_modules WHERE module_number = 7;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Completar el curso Trader Consciente significa:',
  'Que ya dominas el trading y puedes operar con total seguridad',
  'Que terminaste un punto de partida — el oficio se sigue construyendo cada día',
  'Que puedes dejar de aprender y aplicar solo lo que viste',
  'Que ya no necesitas llevar diario ni hacer revisiones',
  'b', 10
FROM courses_modules WHERE module_number = 7;

-- Diario M7: "¿Qué del sistema mantengo, qué ajusto y por qué — basado en datos, no en emoción?
--              ¿Qué de mí mismo necesito flexibilizar esta semana?"
