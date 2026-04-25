# Repositorio de Practicas de Analisis Lexico

Este repositorio reune practicas y modulos desarrollados para una materia del area de ciencias computacionales. El trabajo se centra en analisis lexico, comparacion de codigo fuente y construccion de herramientas academicas para estudiar como un lenguaje define y procesa sus tokens.

El repositorio no busca presentar productos generales ni compiladores completos. La idea principal es documentar entregas universitarias que implementan fragmentos funcionales, explicables y suficientes para demostrar los conceptos vistos en clase.

## Contexto academico

**Materia:** desarrollo de aplicaciones avanzadas de ciencias computacionales

**Integrantes:**
- Estefania Antonio Villaseca - A01736897
- Miranda Eugenia Colorado Arroniz - A01737023
- Alejandro Kong Montoya - A01734271
- Restituto Lara Larios - A01737216

## Estructura general del repositorio

- `analisis-similitud-python/`: aplicacion de escritorio en Python con PySide6 para comparar programas Python usando tecnicas lexicas y de texto plano
- `analizador-lexico-c/`: modulo de analizador lexico para C construido en Python con PLY, enfocado en un subconjunto didactico del lenguaje
- `.venv/`: entorno virtual local del equipo de trabajo

## Modulos incluidos

### 1. Analisis de similitud en Python

Este modulo compara programas Python lado a lado y calcula similitud con cuatro tecnicas:

- tokenizacion con el lexer estandar de Python, generalizacion lexico estructural, suffix array y busqueda de subcadenas comunes largas
- longest common substring en texto plano
- `difflib` sobre codigo tokenizado
- `difflib` sobre texto plano

La interfaz permite elegir un archivo base, compararlo contra los demas archivos del conjunto de entrada, ordenar el ranking de similitud y resaltar bloques relacionados en ambos editores.

### 2. Analizador lexico de C

Este modulo analiza archivos `.c` y reconoce un conjunto representativo de elementos lexicos inspirados en C99. El objetivo no es cubrir todo el lenguaje ni implementar un preprocesador completo, sino trabajar con un fragmento suficiente para programas basicos e intermedios y para explicar la construccion de tokens de forma clara.

Entre los elementos contemplados estan:

- palabras reservadas
- identificadores
- constantes numericas
- literales de cadena
- constantes de caracter
- comentarios
- signos de puntuacion y operadores
- soporte parcial de preprocesamiento en casos sencillos de `#include`, `PP_NUMBER` y `PP_OTHER`

## Referencia conceptual general

La referencia formal mas importante del repositorio aparece en el modulo `analizador-lexico-c`, porque ahi se documenta con detalle la base teorica usada para seleccionar y explicar el fragmento de C implementado. En el `README` de esa carpeta se incluye la relacion con el documento `n1124.pdf` y con la seccion `6.4` del estandar.

## Relacion entre carpetas

- `analisis-similitud-python/` reutiliza la idea de trabajar con representaciones lexicas para comparar programas Python y resaltar coincidencias
- `analizador-lexico-c/` se concentra en la fase de reconocimiento de tokens en C, con reglas definidas sobre un fragmento representativo del lenguaje
- ambos modulos comparten un enfoque academico: implementar lo necesario para explicar el problema con claridad, sin intentar cubrir todas las etapas de un compilador real

## Notas de uso

- cada carpeta importante incluye su propio `README.md`
- los detalles de ejecucion de cada modulo estan dentro de su carpeta correspondiente
- las decisiones especificas de implementacion se documentan a nivel de modulo para no mezclar la informacion general del repositorio con la de cada practica
