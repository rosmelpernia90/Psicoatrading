-- ============================================================
-- PsicoaTrading — Seed Módulos 3 y 4 del Curso Trader Consciente
-- Aplicar DESPUÉS de course_schema.sql y seed_modulos_1_2.sql
-- Base: psicoatrading_crm
-- ============================================================

DELETE FROM courses_quizzes WHERE module_id IN (
  SELECT id FROM courses_modules WHERE module_number IN (3, 4)
);

-- ============================================================
-- MÓDULO 3 — LA AVARICIA Y EL EGO: LOS SABOTEADORES INTERNOS
-- ============================================================
UPDATE courses_modules
SET
  title      = 'La Avaricia y el Ego: Los Saboteadores Internos',
  content_md = '## Introducción

Los traders no quiebran por no saber leer un gráfico. Quiebran porque, justo cuando todo iba bien, hicieron una operación más. Porque después de una racha buena se sintieron invencibles. Porque después de una pérdida quisieron "recuperar". Porque creían tener razón cuando el mercado les estaba gritando lo contrario.

La avaricia y el ego son los dos saboteadores que viven dentro de ti. No te atacan cuando estás mal — te atacan cuando estás bien. Y por eso son tan peligrosos: aparecen disfrazados de confianza, de oportunidad, de "tengo razón". Este módulo es para reconocerlos antes de que te muerdan.

## Las verdades del módulo

**1. La avaricia no es querer ganar dinero. Es no saber parar.** Querer ganar es legítimo. Querer una operación más cuando ya cumpliste tu objetivo del día, es avaricia. La diferencia es invisible para quien no está entrenado a verla.

**2. La avaricia aparece después de ganar, no de perder.** Es el momento más peligroso del día. Acabas de tener 3 operaciones buenas, te sientes en racha, sientes que "hoy puedo más" — y ahí es donde devuelves lo ganado y un extra. Las mejores rachas se mueren por una operación de más.

**3. El ego distorsiona lo que ves.** Cuando estás casado con una idea ("el precio tiene que subir"), tu mente filtra: ve solo lo que confirma tu tesis, ignora lo que la contradice. El mercado te está mostrando una cosa, pero tú ves otra. El ego te hace ciego con los ojos abiertos.

**4. El ego te hace pedir consejo para no seguirlo.** Le preguntas a alguien con más experiencia, te da una respuesta, y haces lo contrario porque "tú lo ves mejor". Esto no es independencia — es ego. La independencia consciente escucha, evalúa, y a veces concede. El ego solo busca confirmación.

**5. Avaricia y ego son hermanos.** La avaricia es "quiero más de lo que el plan dice". El ego es "yo sé más que el plan". Ambos te sacan del sistema. Ambos te hacen creer que esta vez es diferente. Nunca lo es.

## El espejo

- ¿Cuántas veces en el último mes hice una operación que no estaba en mi plan?
- ¿Después de qué tipo de día aparece más la avaricia: tras un día bueno o tras uno malo? *(La respuesta honesta sorprende.)*
- ¿Cuándo fue la última vez que el mercado me dio razón y aún así me costó admitir que tuve suerte?
- ¿Cuándo fue la última vez que el mercado me contradijo y seguí defendiendo mi tesis "esperando"?

## Herramienta práctica — Doble ejercicio

**A. Registro de operaciones impulsivas (última semana)**

Para cada operación fuera de tu plan, anota: la fecha, qué operaste, qué sentiste antes de entrar, el resultado real, y qué te dijo el ego para justificarla.

*Ejemplo:* Lunes — Compra extra en EUR/USD — Sentí euforia (venía de 2 ganadas) — Perdí lo ganado — El ego dijo: "Hoy estoy en racha, no puede fallar."

Si tu lista está vacía, eres del 5% que ya domina esto. Si tiene más de 3 entradas, este módulo es exactamente para ti.

**B. Diario del Ego (7 días)**

Durante 7 días, al final de cada sesión de trading, anota:

- ¿Hubo un momento donde creía tener razón y el mercado me mostró que no?
- ¿Qué hice: cerré rápido o "esperé"?

Al final de los 7 días, cuenta cuántas veces "esperaste". Esa cifra es tu ego operando.

## Cierre PsicoaTrading

*"El mercado no te castiga por equivocarte. Te castiga por defender que tenías razón. Suelta el ego, suelta la operación de más, y el mercado dejará de cobrarte la lección."*'
WHERE module_number = 3;

-- Quiz módulo 3
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La avaricia en el trading suele aparecer:',
  'Después de una pérdida fuerte',
  'Después de ganancias consecutivas, cuando te sientes "en racha"',
  'Solo en principiantes',
  'Únicamente con cuentas grandes',
  'b', 1
FROM courses_modules WHERE module_number = 3;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Cuál es la diferencia entre querer ganar y avaricia?',
  'No hay diferencia',
  'La avaricia es no saber parar cuando ya cumpliste tu objetivo',
  'Querer ganar es para profesionales, avaricia para amateurs',
  'La avaricia solo aplica a operaciones grandes',
  'b', 2
FROM courses_modules WHERE module_number = 3;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'El ego en el trading provoca que:',
  'Tomes decisiones más rápido',
  'Filtres la información del mercado: ves lo que confirma tu tesis e ignoras lo que la contradice',
  'Operes con más capital',
  'Confíes más en tu broker',
  'b', 3
FROM courses_modules WHERE module_number = 3;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Cuando pides consejo a alguien con experiencia y haces lo contrario, generalmente es:',
  'Independencia de pensamiento',
  'Análisis crítico',
  'Ego buscando confirmación, no consejo real',
  'Estrategia de diversificación',
  'c', 4
FROM courses_modules WHERE module_number = 3;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La frase "esta vez es diferente" suele ser:',
  'Una intuición valiosa',
  'Una señal de que avaricia o ego están operando',
  'Análisis técnico avanzado',
  'Una validación de tu sistema',
  'b', 5
FROM courses_modules WHERE module_number = 3;

-- Diario M3: "¿Hice alguna operación 'extra' fuera del plan hoy? ¿En qué momento creí tener razón cuando el mercado me mostraba lo contrario?"


-- ============================================================
-- MÓDULO 4 — CONFIANZA Y DISCIPLINA: TU BASE OPERATIVA
-- ============================================================
UPDATE courses_modules
SET
  title      = 'Confianza y Disciplina: Tu Base Operativa',
  content_md = '## Introducción

Si los módulos anteriores fueron diagnóstico (cómo me saboteo), este es el primero de construcción: con qué reemplazo el sabotaje. La confianza y la disciplina son las dos columnas que sostienen al trader que dura. Sin confianza real, dudas en cada trade y pierdes oportunidades. Sin disciplina, tu confianza se vuelve arrogancia y rompes tu plan.

La buena noticia: ambas se construyen. No nacen contigo, no se heredan, no las da el dinero. Se entrenan como un músculo, día a día. Aquí te muestro cómo.

## Las verdades del módulo

**1. Confianza real ≠ optimismo ciego.** El optimismo dice "todo va a salir bien". La confianza dice "tengo datos que respaldan mi decisión, y si sale mal sé qué hacer". Una se basa en deseos, la otra en evidencia. Solo la segunda sostiene operativa.

**2. La confianza no viene de los aciertos. Viene de las decisiones bien tomadas.** Puedes tener una operación exitosa por suerte (decisión mala, resultado bueno) o una operación fallida por mala suerte (decisión correcta, resultado malo). Lo que construye confianza no es el resultado — es saber que tomaste la decisión correcta dado lo que sabías en ese momento.

**3. La disciplina es hacer lo que tienes que hacer aunque no quieras.** No es motivación. La motivación va y viene. La disciplina opera incluso cuando estás cansado, frustrado, dudando. Es lo único que sostiene tu sistema cuando todo lo demás falla.

**4. Sin trading plan no hay disciplina posible.** Si no tienes reglas claras escritas, no puedes ser disciplinado — porque no hay nada que cumplir. La disciplina exige primero un plan: entradas, salidas, stops, gestión de riesgo, tamaño de posición. Sin eso, lo que llamas "operar" es improvisar.

**5. El mercado abre con o sin ti.** Esta frase es la base de la disciplina. No espera tu ánimo, no se ajusta a tu nivel de energía, no le importa si dormiste mal. Si vas a operar, vas con todo o no vas. La disciplina es saber decidir entre esas dos cosas honestamente cada día.

## El espejo

- ¿Tengo un trading plan escrito, o lo tengo "en la cabeza"?
- ¿Cuándo mi confianza viene de los resultados (gané = soy bueno) y cuándo de la calidad de mis decisiones?
- ¿En qué momento del día o la semana mi disciplina se rompe más fácil?
- Si hoy alguien viera mi último mes de operaciones, ¿diría que sigo un plan o que improviso?

## Herramienta práctica — Doble ejercicio

**A. Bitácora de 20 decisiones bien tomadas**

Repasa el último mes de operaciones. Identifica 20 decisiones que tomaste bien — independientemente del resultado. Para cada una, anota la fecha, cuál fue la decisión, y por qué fue correcta.

*Ejemplos:*
- 03/06 → Salí cuando se rompió mi stop, aunque dolió → Respeté mi plan.
- 05/06 → No entré aunque "se veía bien", porque no cumplía mis criterios → Disciplina sobre intuición.

Este ejercicio reentrena tu cerebro a medir lo correcto, no lo afortunado.

**B. Tu Trading Plan personal**

Si ya tienes uno, revísalo con honestidad. Si no, créalo ahora. Mínimo debe incluir:

- **Mercados que opero**
- **Horarios de operativa**
- **Criterios de entrada** (3 condiciones obligatorias)
- **Criterios de salida** (objetivo + stop)
- **Riesgo máximo por operación** (%)
- **Riesgo máximo diario** (%)
- **Número máximo de operaciones por día**
- **Condición de "no operar hoy"** (cuándo me retiro)
- **Ritual antes de operar**
- **Revisión post-sesión**

Este documento es tu contrato contigo mismo. Si lo rompes, rompes algo más profundo que una regla técnica: rompes tu palabra.

## Cierre PsicoaTrading

*"La confianza se construye en privado, una decisión bien tomada a la vez. La disciplina es la confianza puesta en acción cuando nadie te ve."*'
WHERE module_number = 4;

-- Quiz módulo 4
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La confianza real del trader se basa en:',
  'Optimismo y mentalidad positiva',
  'Resultados ganadores acumulados',
  'Decisiones bien tomadas, independientemente del resultado',
  'Capital disponible',
  'c', 1
FROM courses_modules WHERE module_number = 4;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Puede una operación exitosa ser una mala decisión?',
  'No, si ganó dinero fue buena',
  'Sí: decisión mala más suerte puede dar resultado bueno',
  'Solo en mercados volátiles',
  'Solo si fue una operación grande',
  'b', 2
FROM courses_modules WHERE module_number = 4;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La diferencia entre motivación y disciplina es:',
  'No hay diferencia',
  'La motivación es constante, la disciplina es variable',
  'La motivación va y viene, la disciplina actúa aunque no haya motivación',
  'La disciplina es solo para principiantes',
  'c', 3
FROM courses_modules WHERE module_number = 4;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Sin un trading plan escrito:',
  'Puedes operar con más libertad',
  'No es posible ser disciplinado, porque no hay nada concreto que cumplir',
  'Se opera mejor por intuición',
  'Solo importa si vas a operar grandes capitales',
  'b', 4
FROM courses_modules WHERE module_number = 4;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '"El mercado abre con o sin ti" significa:',
  'Que siempre debes operar',
  'Que no esperes que el mercado se ajuste a tu estado de ánimo: vas con todo o no vas',
  'Que el horario es lo más importante',
  'Que necesitas más horas de operativa',
  'b', 5
FROM courses_modules WHERE module_number = 4;

-- Diario M4: "¿Cumplí mi trading plan hoy al 100%? ¿En qué decisión confié por datos y en cuál por impulso?"
