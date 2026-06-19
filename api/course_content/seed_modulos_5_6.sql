-- ============================================================
-- PsicoaTrading — Seed Módulos 5 y 6 del Curso Trader Consciente
-- Aplicar DESPUÉS de course_schema.sql y seeds anteriores
-- Base: psicoatrading_crm
-- ============================================================

DELETE FROM courses_quizzes WHERE module_id IN (
  SELECT id FROM courses_modules WHERE module_number IN (5, 6)
);

-- ============================================================
-- MÓDULO 5 — ENTORNO Y SOLEDAD: EL CAMINO INDIVIDUAL
-- ============================================================
UPDATE courses_modules
SET
  title      = 'Entorno y Soledad: El Camino Individual',
  content_md = '## Introducción

Hay dos fuerzas externas que casi ningún curso de trading menciona, y que sin embargo determinan si vas a durar o no en este oficio: el entorno que te rodea y la soledad que vas a habitar. La primera puede sabotearte sin que te des cuenta. La segunda puede consumirte si no aprendes a estar bien contigo mismo.

Tu pareja, tus padres, tus amigos, tus compañeros de trabajo — todos ellos tienen una opinión sobre lo que haces. La mayoría no entiende este oficio. Algunos te van a desanimar sin querer. Otros, con la mejor intención, te van a presionar a "buscar algo serio". Y al mismo tiempo, vas a pasar horas frente a una pantalla, solo, tomando decisiones que nadie va a validar contigo. Este módulo es para aprender a manejar ambos frentes — el de afuera y el de adentro.

## Las verdades del módulo

**1. Tu entorno opina con o sin permiso.** No puedes evitar que la gente que te rodea tenga una opinión sobre tu trading. Lo que sí puedes controlar es cuánto peso le das. Hay opiniones que te suman (te cuestionan con respeto, te ayudan a pensar mejor) y opiniones que te restan (te desaniman, te comparan, te presionan a abandonar). Saber distinguirlas es supervivencia.

**2. La gente cercana entiende cuando ganas, no antes.** Mientras estás en el proceso de aprender — perdiendo, dudando, sin resultados — la mayoría no va a entender qué haces. Te van a sugerir que busques un empleo "estable". Te van a comparar con primos exitosos. Cuando empieces a ganar dinero de verdad, mágicamente todos van a entender. No esperes validación temprana: no va a llegar.

**3. La presión comercial es invisible pero real.** Vivimos en una sociedad que mide el éxito en velocidad: cuánto, cuán pronto, cuán visible. El trading va en contra de eso. No tienes salario fijo, no tienes ascensos, no tienes a quién mostrarle un cargo en LinkedIn. Esa presión te va a empujar a forzar resultados — y forzar resultados es la forma más rápida de quebrar.

**4. La soledad del trader no es estar solo. Es decidir solo.** Puedes estar rodeado de gente, en una oficina, en un café, con tu familia en casa — y aún así, cuando aprietas el botón, estás solo. Nadie va a tomar esa decisión por ti. Nadie va a cargar la pérdida por ti. Nadie va a celebrar contigo de la misma forma. Habitar esa soledad sin colapsar es una habilidad — no un castigo.

**5. Aislarse no es lo mismo que estar solo.** El trader que se encierra, que deja de ver gente, que abandona su vida social "para concentrarse", está cavando su propia tumba mental. La soledad del trader es operativa, no existencial. Operar solo, sí. Vivir solo, no.

## El espejo

- ¿Quiénes de mi entorno cercano realmente apoyan lo que hago (no solo dicen apoyarlo)?
- ¿Quién me presiona — directa o indirectamente — a buscar algo más estable?
- Cuando opero, ¿estoy realmente solo, o cargo con la opinión de otros sin darme cuenta?
- ¿Cuándo fue la última vez que vi a un amigo, hice deporte, salí de casa por algo que no fuera trading?

## Herramienta práctica — Doble ejercicio

**A. Auditoría del entorno (5 personas)**

Lista las 5 personas con quienes más interactúas (familia, pareja, amigos cercanos, compañeros). Para cada una, analiza: cuando le cuento de mi trading, ¿qué hace? ¿Suma o resta? ¿Cómo gestiono su influencia?

*Ejemplo:* Mi pareja → Me pregunta cuánto gané esta semana → Resta (genera presión) → Acordamos hablar de eso solo mensualmente.

Honestidad brutal: esto no se trata de cortar relaciones. Se trata de saber con quién compartes qué.

**B. Carta a tu yo de hace 1 año**

Escribe una carta corta (máximo 1 página) a la persona que eras hace un año cuando empezaste a tomarte el trading en serio. Incluye:

- Lo que aprendiste en solitario que no esperabas aprender.
- El momento más duro que viviste solo.
- Lo que le dirías hoy para que aguante.
- Lo que NO le dirías (porque tiene que descubrirlo por sí mismo).

Esta carta es solo para ti. Guárdala y vuelve a leerla en 6 meses. Vas a ver cuánto te transformó habitar tu propia soledad con consciencia.

## Cierre PsicoaTrading

*"El entorno opina, el mercado decide, tú aprietas el botón. Aprende a filtrar el ruido de afuera y a habitar el silencio de adentro — ahí, en ese silencio, vive el trader que serás."*'
WHERE module_number = 5;

-- Quiz módulo 5
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La actitud más sana frente al entorno que no entiende tu trading es:',
  'Cortar a todos los que dudan de ti',
  'Convencerlos con argumentos hasta que acepten',
  'Aceptar que la mayoría no entenderá hasta que veas resultados, y proteger tu foco mientras tanto',
  'Esconderles lo que haces',
  'c', 1
FROM courses_modules WHERE module_number = 5;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La presión comercial de la sociedad afecta al trader porque:',
  'Le obliga a pagar impuestos altos',
  'Lo empuja a forzar resultados rápidos, y forzar resultados rompe la consistencia',
  'Le exige certificaciones formales',
  'Lo limita a operar en horarios específicos',
  'b', 2
FROM courses_modules WHERE module_number = 5;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La soledad del trader se refiere principalmente a:',
  'No tener amigos',
  'Operar sin internet',
  'El momento en que aprietas el botón: nadie decide por ti, nadie carga la pérdida por ti',
  'Trabajar desde casa',
  'c', 3
FROM courses_modules WHERE module_number = 5;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, '¿Cuál es la diferencia entre soledad operativa y aislamiento?',
  'No hay diferencia',
  'La soledad operativa es decidir solo; el aislamiento es abandonar tu vida social',
  'La soledad es buena, el aislamiento es necesario',
  'Son lo mismo en distintos contextos',
  'b', 4
FROM courses_modules WHERE module_number = 5;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La validación de tu entorno cercano:',
  'Debes buscarla activamente para mantener motivación',
  'Suele llegar tarde, cuando ya ganas — no la esperes temprano',
  'Es esencial para operar bien',
  'Llega siempre que muestres tu plan',
  'b', 5
FROM courses_modules WHERE module_number = 5;

-- Diario M5: "¿Qué de mi entorno me sumó o me restó hoy? ¿Cómo manejé los momentos en que estuve solo decidiendo?"


-- ============================================================
-- MÓDULO 6 — DESARROLLO Y FOCO: DE APRENDIZ A PROFESIONAL
-- ============================================================
UPDATE courses_modules
SET
  title      = 'Desarrollo y Foco: De Aprendiz a Profesional',
  content_md = '## Introducción

Llegado este punto, ya identificaste lo que te sabotea (miedo, dinero, avaricia, ego), construiste tus bases (confianza, disciplina), y aprendiste a manejar tu entorno y tu soledad. Ahora viene la pregunta más incómoda del curso: ¿en qué etapa del desarrollo estás realmente? No donde crees estar. No donde te gustaría estar. Donde estás.

Y junto a eso, una habilidad operativa concreta que separa a los que duran de los que no: el foco. Centrarse en el aquí, el ahora, el trade que tienes delante. Sin distracciones, sin proyecciones, sin recriminaciones. Este módulo te da las dos herramientas: el mapa de dónde estás y el ritual para estar presente.

## Las verdades del módulo

**1. Hay 4 etapas en el desarrollo de un trader.** La mayoría cree que avanza por dinero — no es así. Se avanza por cómo piensas, por cómo decides, por cómo te recuperas. Identificar tu etapa real es el primer paso para avanzar honestamente:

- **Etapa 1 — Inconsciencia entusiasta:** Crees que sabes. Operas con confianza falsa. Suerte del principiante. Casi todos arrancan aquí.
- **Etapa 2 — Consciencia dolorosa:** Te das cuenta de que no sabes nada. Pierdes. Dudas. Muchos abandonan aquí.
- **Etapa 3 — Aprendizaje estructurado:** Estudias, pruebas, registras, mides. Empiezas a entender de verdad. Es la etapa más larga.
- **Etapa 4 — Consistencia operativa:** Aplicas tu sistema con disciplina. Ganas y pierdes, pero el resultado neto es positivo. Esta no es la meta final — es donde el oficio empieza.

**2. Subir de etapa duele. Bajar de etapa también.** Pasar de la 1 a la 2 duele porque rompe tu autoimagen. Pasar de la 3 a la 4 duele porque exige soltar el control. Y a veces, después de una crisis, retrocedes de etapa. No es fracaso — es parte del oficio.

**3. El foco no es concentración. Es presencia.** Concentrarse es esforzarse en mirar algo. Estar presente es habitar el momento sin que tu mente te lleve al pasado (recriminación) ni al futuro (ansiedad). El foco operativo es presencia: estás aquí, en este gráfico, en este trade, ahora.

**4. La mente se dispersa por defecto. Hay que entrenarla.** Tu mente quiere irse: a la operación anterior que perdiste, a lo que vas a hacer con la ganancia, a lo que dirá tu pareja, a la noticia que viste. Eso es normal — es lo que hace una mente no entrenada. Lo que separa al profesional es que nota la dispersión y vuelve al trade. Una y otra vez.

**5. Un ritual previo cambia tu sesión entera.** Los profesionales no se sientan a operar como quien se sienta a ver Netflix. Tienen un ritual: respiración, revisión del plan, lectura del estado interno, y solo entonces abren la plataforma. 5 minutos antes de operar valen más que 5 horas de análisis.

## El espejo

- Con honestidad brutal: ¿en qué etapa de las 4 estoy realmente?
- ¿En qué etapa creía que estaba antes de leer este módulo?
- Cuando opero, ¿cuántas veces por hora se va mi mente a otro lado?
- ¿Tengo algún ritual antes de operar, o me siento y abro la plataforma sin más?

## Herramienta práctica — Doble ejercicio

**A. Auto-evaluación de etapa**

Marca con honestidad cuál te describe mejor hoy:

- **Etapa 1 — Inconsciencia entusiasta:** "Sé operar, solo necesito más capital"
- **Etapa 2 — Consciencia dolorosa:** "Me di cuenta de que no sé casi nada y me frustra"
- **Etapa 3 — Aprendizaje estructurado:** "Estudio, registro, ajusto, mido. Avanzo lento pero firme"
- **Etapa 4 — Consistencia operativa:** "Mi sistema funciona en el tiempo. Gano y pierdo, pero neto positivo"

Debajo de tu elección, escribe 3 indicadores concretos que te confirmen que estás en esa etapa. Si no puedes escribir 3 con evidencia real, probablemente estás una etapa antes.

**B. Tu Ritual Pre-Sesión (5 minutos)**

Diseña tu ritual personal. Mínimo debe incluir:

- **Respiración consciente (1 min):** 4 segundos inhalar, 4 sostener, 6 exhalar. 6 ciclos.
- **Lectura del estado interno (1 min):** ¿Cómo estoy hoy: cansado, ansioso, eufórico, calmado? Si la respuesta es "ansioso" o "eufórico", considera no operar hoy.
- **Revisión del trading plan (2 min):** Relee tus criterios de entrada, salida, stop, riesgo máximo del día.
- **Intención clara (1 min):** ¿Cuál es tu objetivo realista de hoy? No en dinero — en disciplina. Ejemplo: "voy a respetar mis stops", "no más de 3 operaciones".

Escríbelo. Imprímelo. Pégalo cerca de tu pantalla. El ritual no es opcional — es el switch que separa operar del improvisar.

## Cierre PsicoaTrading

*"Saber dónde estás es más importante que saber a dónde vas. Y estar presente en este trade vale más que haber leído mil libros. Aterriza aquí, ahora, en este gráfico."*'
WHERE module_number = 6;

-- Quiz módulo 6
INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Las 4 etapas del desarrollo del trader son:',
  'Novato, intermedio, avanzado, experto',
  'Inconsciencia entusiasta, consciencia dolorosa, aprendizaje estructurado, consistencia operativa',
  'Demo, real pequeño, real mediano, real grande',
  'Estudiante, practicante, profesional, gurú',
  'b', 1
FROM courses_modules WHERE module_number = 6;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Pasar de la etapa 1 a la 2 duele principalmente porque:',
  'Se pierde mucho dinero de golpe',
  'Rompe la autoimagen de creer que ya sabes operar',
  'Cambia el broker que usas',
  'Las plataformas cambian de interfaz',
  'b', 2
FROM courses_modules WHERE module_number = 6;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'La diferencia entre concentración y presencia operativa es:',
  'No hay diferencia entre ambas',
  'Concentrarse es esforzarse en mirar; estar presente es habitar el momento sin que la mente escape al pasado o futuro',
  'La presencia solo la practican quienes meditan',
  'La concentración es siempre superior a la presencia',
  'b', 3
FROM courses_modules WHERE module_number = 6;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Cuando tu mente se dispersa durante una sesión, lo correcto es:',
  'Forzarla a concentrarse de nuevo con esfuerzo',
  'Notar la dispersión y volver al trade, una y otra vez, sin juicio',
  'Cerrar la plataforma inmediatamente',
  'Tomar una decisión rápida para salir del estado',
  'b', 4
FROM courses_modules WHERE module_number = 6;

INSERT INTO courses_quizzes (module_id, question, option_a, option_b, option_c, option_d, correct_option, question_order)
SELECT id, 'Un ritual previo a la sesión de trading sirve para:',
  'Ocupar el tiempo antes de que abra el mercado',
  'Llegar centrado, con estado interno revisado y plan releído — separar operar de improvisar',
  'Sustituir el análisis técnico del día',
  'Demostrar profesionalismo a otros traders',
  'b', 5
FROM courses_modules WHERE module_number = 6;

-- Diario M6: "¿En qué etapa de desarrollo me sentí hoy? ¿Hice mi ritual pre-sesión? ¿Cuántas veces se me fue la mente y supe volver?"
