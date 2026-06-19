<!--
PLANTILLA DE MÓDULO — Curso "Trader Consciente"
================================================
Crea un archivo por módulo: modulo_1.md, modulo_2.md, ... modulo_7.md
Llena las secciones marcadas. NO cambies los encabezados ===CONTENIDO===, ===QUIZ===, ===DIARIO===.
Yo convierto estos archivos al SQL seed que carga courses_modules + courses_quizzes.

Reglas:
- Módulos 1-6: el QUIZ debe tener exactamente 5 preguntas.
- Módulo 7: el QUIZ debe tener exactamente 10 preguntas.
- Cada pregunta: 4 opciones (a,b,c,d) y marca la correcta con [x].
-->

===META===
module_number: 1
title: Título del módulo aquí

===CONTENIDO===
# Encabezado principal

Aquí va el texto del módulo en **Markdown**. Puedes usar:

## Subtítulos
### Sub-subtítulos

Párrafos normales, **negrita**, *cursiva*, y listas:

- Punto uno
- Punto dos
- Punto tres

(Escribe todo el contenido teórico del módulo aquí.)

===QUIZ===
1. ¿Texto de la primera pregunta?
a) Opción A
b) Opción B [x]
c) Opción C
d) Opción D

2. ¿Texto de la segunda pregunta?
a) Opción A [x]
b) Opción B
c) Opción C
d) Opción D

3. ¿Texto de la tercera pregunta?
a) Opción A
b) Opción B
c) Opción C [x]
d) Opción D

4. ¿Texto de la cuarta pregunta?
a) Opción A
b) Opción B
c) Opción C
d) Opción D [x]

5. ¿Texto de la quinta pregunta?
a) Opción A [x]
b) Opción B
c) Opción C
d) Opción D

===DIARIO===
Pregunta del diario que se desbloquea al completar este módulo.
(Texto libre. Cuando construyamos el módulo de Diario en el próximo prompt,
conectaremos esta pregunta vía unlocks_diary_question_id.)
