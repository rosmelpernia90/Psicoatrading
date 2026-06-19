-- ============================================================
-- PsicoaTrading — Seed Módulos 1 y 2 del Curso Trader Consciente
-- Aplicar DESPUÉS de course_schema.sql
-- Base: psicoatrading_crm
-- ============================================================

-- Eliminar quizzes existentes de módulos 1 y 2 (para evitar duplicados en reproceso)
DELETE FROM courses_quizzes WHERE module_id IN (
  SELECT id FROM courses_modules WHERE module_number IN (1, 2)
);

-- ============================================================
-- MÓDULO 1 — EL CAMINO REAL DEL TRADER
-- ============================================================
UPDATE courses_modules
SET
  title      = 'El Camino Real del Trader',
  content_md = '## Introducción

Antes de hablar de gráficos, de estrategias o de capital, hay algo que la mayoría de los traders descubre tarde — y por eso quiebran o abandonan. Lo descubren después de perder dinero, después de creer que iban a "vivir del trading en 3 meses", después de comparar su cuenta con la de gente que probablemente miente. La verdad es esta: el trading no es un sprint, es una carrera de fondo. Y nadie te lo cuenta antes porque vender un sprint emociona, vender una maratón no.

Este módulo es el cimiento de todo lo que viene. Si lo interiorizas, todo lo demás encaja. Si no, vas a recaer una y otra vez en la misma trampa: querer atajos donde no los hay.

## Las verdades del módulo

**1. Lo que te vendieron es una caricatura.** "Trabaja una hora desde casa", "duplica tu cuenta en un mes", "deja tu empleo en 90 días". Todo eso son anzuelos comerciales. La realidad: los traders consistentes tardaron entre 2 y 5 años en serlo. Los que abandonaron antes son la mayoría — y no porque fueran tontos, sino porque les vendieron una expectativa imposible.

**2. El éxito en otras áreas no se transfiere.** Puedes ser médico exitoso, empresario, ingeniero brillante. Al llegar al trading vas a sentir que no sirves para nada. Eso no es porque seas malo: es porque ninguna habilidad previa te prepara para perder dinero de forma sistemática y seguir adelante. El trading rompe el cableado mental con el que llegaste.

**3. Tu cerebro está diseñado para sabotearte.** Evolutivamente, el ser humano evita las pérdidas y huye del dolor. El trading exige aceptar pérdidas regulares y seguir operando. Vas en contra de tu biología — por eso es tan difícil, no porque sea técnicamente complejo.

**4. La consistencia es el verdadero objetivo, no el dinero.** El dinero es la consecuencia. Si pones el dinero como meta, vas a forzar, a operar de más, a romper tu plan. Si pones la consistencia como meta, el dinero llega como subproducto. Cambia el foco y cambia el resultado.

**5. Solo sobrevive el que se levanta.** No el más inteligente, no el más informado, no el más capitalizado. El que sigue cuando los demás abandonan. Esa es la única regla real del juego.

## El espejo

Tómate 10 minutos en silencio y responde con honestidad:

- ¿Cuándo empecé, en qué tiempo esperaba ser rentable?
- ¿Cuántas veces he pensado en abandonar en los últimos 6 meses?
- ¿Estoy buscando un atajo o estoy construyendo un oficio?
- Si tuviera que estar 3 años más así (sin grandes ganancias, solo aprendiendo y siendo cada vez más consistente), ¿lo aguantaría?

No hay respuestas correctas. Hay respuestas tuyas.

## Herramienta práctica — Tu Línea de Tiempo Real

En una hoja en blanco, dibuja una línea horizontal. Marca tres puntos:

- **Punto A:** dónde estabas cuando empezaste a operar (fecha y mentalidad).
- **Punto B:** dónde creías que estarías hoy (qué te imaginabas).
- **Punto C:** dónde estás realmente hoy (sin maquillar).

Debajo de la línea, escribe una sola frase: *"La distancia entre B y C es la realidad que no me contaron."*

Esta hoja la vas a guardar. La vas a mirar dentro de 6 meses. Vas a ver que tu B y tu C empiezan a parecerse — no porque hayas alcanzado el B fantasía, sino porque tu B se volvió realista.

## Cierre PsicoaTrading

*"No es lento. Es el ritmo correcto. Y el que aguanta el ritmo correcto, gana."*'
WHERE module_number = 1;

-- Quiz módulo 1
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La principal razón por la que la mayoría de traders abandonan es:',
  'Falta de capital inicial',
  'Expectativas irreales sobre el tiempo necesario para ser rentables',
  'No tener acceso a buenas plataformas',
  'Mala suerte con el mercado',
  'b', 1
FROM courses_modules WHERE module_number = 1;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Según el módulo, el objetivo real del trader debería ser:',
  'Ganar dinero rápidamente',
  'Duplicar la cuenta cada mes',
  'Ser consistente en el tiempo',
  'Tener razón en cada operación',
  'c', 2
FROM courses_modules WHERE module_number = 1;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Por qué tu cerebro juega en tu contra al operar?',
  'Porque no entiende los gráficos',
  'Porque evolutivamente está diseñado para evitar pérdidas, no para aceptarlas',
  'Porque le falta entrenamiento técnico',
  'Porque necesita más descanso',
  'b', 3
FROM courses_modules WHERE module_number = 1;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Qué pasa si pones el dinero como meta principal?',
  'Lo alcanzas más rápido',
  'Operas con más enfoque',
  'Tiendes a forzar, sobreoperar y romper tu plan',
  'Tu rendimiento mejora automáticamente',
  'c', 4
FROM courses_modules WHERE module_number = 1;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La diferencia entre quien lo logra y quien no lo logra es:',
  'El nivel de inteligencia',
  'El capital disponible',
  'La persistencia: levantarse cuando otros abandonan',
  'La cantidad de cursos tomados',
  'c', 5
FROM courses_modules WHERE module_number = 1;

-- Pregunta de diario del módulo 1 (se conectará a diary_questions en el próximo entregable)
-- Texto: "¿En qué etapa del proceso me sentí hoy: sprint impaciente, frustración, o
--          aceptación del maratón? ¿Qué me lo indica?"


-- ============================================================
-- MÓDULO 2 — EL MIEDO Y EL DINERO: LOS DOS ESPEJOS
-- ============================================================
UPDATE courses_modules
SET
  title      = 'El Miedo y el Dinero: Los Dos Espejos',
  content_md = '## Introducción

El miedo y el dinero son los dos espejos donde más se distorsiona el trader. El miedo te paraliza antes del trade, te saca antes de tiempo o te impide entrar cuando deberías. El dinero, por su parte, no es solo el resultado de tus operaciones: es una proyección de toda tu historia personal con él — lo que aprendiste en tu casa, lo que viviste, lo que crees que mereces.

Aquí vamos a desarmar los dos. Porque no puedes operar bien si tienes miedo, y no puedes tener una relación sana con las ganancias y las pérdidas si tu relación con el dinero está rota desde antes de empezar.

## Las verdades del módulo

**1. El miedo no es debilidad. Es información.** El problema no es sentir miedo — es no saber qué te está diciendo. Hay miedos útiles (te avisan que estás operando fuera de tu plan) y miedos saboteadores (te paralizan ante una operación válida). Aprender a distinguirlos cambia tu operativa.

**2. Hay 3 miedos principales en el trader:** miedo a perder dinero, miedo a equivocarse (ego), y miedo a apretar el botón (parálisis). Cada uno tiene un origen distinto y se trabaja distinto. Confundirlos es mantenerse atrapado.

**3. El miedo a perder es proporcional a lo que el dinero representa para ti.** Si para ti el dinero es seguridad existencial, perder $100 se siente como morir. Si es energía que va y viene, perder $100 es información. La cantidad no cambia — cambia tu relación.

**4. Tus creencias sobre el dinero las heredaste — no las elegiste.** "El dinero es difícil de ganar." "Los ricos son malos." "No merezco tanto." "Ganar dinero sin esfuerzo está mal." Estas frases las absorbiste de niño y siguen operando hoy, dictando inconscientemente cuánto te permites ganar y cuánto te permites perder.

**5. El mercado no te quita dinero. Te lo cobra por aprender.** Cambia esta frase y cambia tu relación con las pérdidas. Una pérdida no es un robo: es la matrícula que pagas por una lección que solo el mercado puede darte.

## El espejo

- Cuando voy a apretar el botón, ¿qué se contrae en mi cuerpo? ¿Dónde lo siento?
- ¿Qué decían en mi casa sobre el dinero cuando era niño?
- ¿Cuál de los 3 miedos (perder, equivocarme, apretar) me visita más?
- Si hoy perdiera el 10% de mi cuenta, ¿qué pensaría sobre mí mismo como persona? *(La respuesta a esta pregunta es donde está tu trabajo real.)*

## Herramienta práctica — Doble ejercicio

**A. Mapa del Miedo (3 columnas)**

Dibuja una tabla con tres columnas: *¿Qué temo? / ¿Cuándo aparece? / ¿Qué hago habitualmente?*

Ejemplo: Perder más de lo planeado → Cuando voy ganando y aparece duda → Cierro antes de tiempo.

Llénala con al menos 5 filas. Sé brutalmente honesto. Nadie lo va a leer salvo tu psicólogo, si tienes el plan que lo incluye.

**B. Auditoría de 10 creencias sobre el dinero**

Escribe 10 frases que recuerdes haber oído sobre el dinero cuando eras niño o adolescente. Luego, al lado de cada una, escribe una versión adulta y consciente.

Ejemplo: *"El dinero no crece en los árboles"* → *"El dinero es resultado de habilidad y constancia, no de suerte."*

Este ejercicio parece tonto. No lo es. Es el ejercicio que más cambia la operativa de los traders que lo hacen con honestidad.

## Cierre PsicoaTrading

*"El miedo es un mensajero. El dinero es un espejo. Lee bien al primero, límpiale el polvo al segundo, y operarás distinto mañana."*'
WHERE module_number = 2;

-- Quiz módulo 2
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'El miedo en el trading es:',
  'Una debilidad que hay que eliminar por completo',
  'Una emoción inútil',
  'Información que hay que aprender a interpretar',
  'Algo que solo sienten los principiantes',
  'c', 1
FROM courses_modules WHERE module_number = 2;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Cuáles son los 3 miedos principales del trader?',
  'Miedo a ganar, miedo al éxito, miedo al fracaso',
  'Miedo a perder dinero, miedo a equivocarse, miedo a apretar el botón',
  'Miedo al mercado, miedo al broker, miedo a la familia',
  'Miedo a los gráficos, miedo a las noticias, miedo a la volatilidad',
  'b', 2
FROM courses_modules WHERE module_number = 2;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿De dónde vienen la mayoría de tus creencias sobre el dinero?',
  'Las elegiste racionalmente de adulto',
  'Las heredaste inconscientemente de tu entorno infantil',
  'Las aprendiste en cursos de finanzas',
  'Las desarrollaste operando',
  'b', 3
FROM courses_modules WHERE module_number = 2;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Una pérdida en el mercado debería interpretarse como:',
  'Un robo del mercado',
  'Una falla personal',
  'Una matrícula por una lección que el mercado te enseña',
  'Una señal de que el trading no es para ti',
  'c', 4
FROM courses_modules WHERE module_number = 2;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Si perder $100 se siente devastador, es porque:',
  'La cantidad es objetivamente grande',
  'El dinero para ti representa algo más profundo que dinero (seguridad, valor personal)',
  'Tu broker es malo',
  'El mercado está manipulado',
  'b', 5
FROM courses_modules WHERE module_number = 2;

-- Pregunta de diario del módulo 2 (se conectará a diary_questions en el próximo entregable)
-- Texto: "¿Qué miedo apareció hoy en mi operativa? ¿Qué creencia sobre el dinero
--          se activó cuando gané o perdí?"
