# Analizador Lexico de C

Este modulo implementa un analizador lexico para archivos de C usando Python y PLY. La practica toma como referencia conceptual C99, pero no intenta cubrir todo el lenguaje ni todas las fases de traduccion. En su lugar, trabaja con un fragmento representativo y suficiente para analizar programas basicos e intermedios.

## Objetivo del modulo

Reconocer tokens frecuentes y utiles en codigo fuente de C para:

- identificar la estructura lexico basica de un programa
- mostrar la salida en un formato legible para la practica
- distinguir entre tokens normales y tokens mas cercanos al preprocesamiento
- justificar academicamente como se selecciono un subconjunto razonable del lenguaje

## Referencia

Para este modulo se toma como apoyo conceptual el documento:

`https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1124.pdf`

Nosotros aqui usamos ese documento como referencia formal para entender como C define sus tokens, sus reglas lexicas y varias restricciones del lenguaje. La seccion que mas orienta esta practica es la `6.4`, junto con apartados relacionados con:

- elementos lexicos del lenguaje
- identificadores
- palabras reservadas
- constantes
- literales de cadena
- comentarios
- estructura sintactica general
- directivas de preprocesamiento
- conceptos de conformidad y restricciones del lenguaje

Esta referencia sirve como apoyo teorico para:

- justificar el diseño del analizador lexico
- explicar por que ciertas categorias se reconocen como tokens distintos
- defender academicamente que el lexer trabaja sobre un fragmento del lenguaje seleccionado de forma razonada

Tambien es importante aclarar que este proyecto no implementa el estandar completo de C. El documento se usa como base conceptual y formal, pero la implementacion adopta un subconjunto didactico y funcional suficiente para la practica.

## Que reconoce el lexer

El lexer reconoce categorias lexicas como:

- palabras reservadas
- identificadores
- constantes numericas
- literales de cadena
- constantes de caracter
- comentarios
- operadores y signos de puntuacion
- `PP_NUMBER`
- `PP_OTHER`
- `HEADER_NAME` en casos sencillos de `#include`
- `EOF`

## Que si implementa

- analisis lexico de un subconjunto representativo de C
- deteccion de palabras reservadas e identificadores
- reconocimiento de varias formas de constantes enteras y de punto flotante
- reconocimiento de literales de cadena y de caracter
- reconocimiento de comentarios de linea y de bloque
- reconocimiento de operadores y puntuadores comunes del lenguaje
- soporte parcial de preprocesamiento para observar `PP_NUMBER`, `PP_OTHER` y `HEADER_NAME`
- fusion de literales de cadena adyacentes en la vista de tokens normal

## Que no implementa

- un preprocesador completo
- todas las fases de traduccion del estandar de C
- cobertura total del estandar C99 o de versiones posteriores
- validaciones semanticas profundas
- diagnosticos avanzados de errores de compilacion

## Justificacion del fragmento del lenguaje elegido

En la practica se selecciono un fragmento del lenguaje apropiado en lugar de intentar cubrir todo C. Esta decision es coherente con el documento de la actividad y con la implementacion actual del proyecto.

Se incluyeron las categorias lexicas que aparecen con mayor frecuencia y que son suficientes para programas basicos e intermedios, como palabras reservadas, identificadores, constantes, literales, comentarios, operadores y algunos elementos del preprocesamiento. Se dejaron fuera un preprocesador completo, la totalidad del estandar y validaciones semanticas detalladas porque eso ya corresponde a etapas mas amplias de un compilador y excede el objetivo didactico de la practica.

En otras palabras, el modulo busca ser correcto y util dentro de un alcance acotado y defendible academicamente.

## Decisiones de diseno

- se uso PLY para definir reglas lexicas de forma clara y verificable
- se separo el modo normal del modo de preprocesamiento para distinguir tokens como `CONSTANT` y `PP_NUMBER`
- se agrego una combinacion sencilla de `HEADER_NAME` para casos comunes de `#include`
- se privilegio la legibilidad del codigo y de la salida sobre la cobertura total del lenguaje

## Estructura de archivos

- `lexer.py`: implementacion principal del analizador lexico
- `example.c`: archivo de prueba con estructuras basicas del lenguaje
- `example2.c`: archivo de prueba con casos adicionales de literales, comentarios y preprocesamiento
- `example3.c`: archivo de prueba con otros casos utiles para validar el comportamiento del lexer
- `A3.1_AnalizadorLexico.pdf`: documento de la actividad

## Como ejecutarlo

### Windows

```powershell
python -m pip install ply
python lexer.py example.c
```

### macOS o Linux

```bash
python3 -m pip install ply
python3 lexer.py example.c
```

Tambien se puede analizar cualquier otro archivo `.c`:

```bash
python3 lexer.py ruta/al/archivo.c
```

## Uso desde codigo Python

```python
from lexer import Lexer, analyzeFile

tokens = analyzeFile("example.c")

for token in tokens:
    print(token)
```

## Formato de salida

La salida se imprime como un token por linea:

```text
[TIPO] valor
```

Ejemplo:

```text
[KEYWORD] int
[IDENTIFIER] main
[PUNCTUATOR] (
[PUNCTUATOR] )
[PUNCTUATOR] {
```

## Relacion con el resto del repositorio

Este modulo se enfoca solo en reconocimiento lexico de C. Dentro del repositorio convive con el modulo de analisis de similitud en Python, que trabaja sobre tokenizacion y comparacion de programas. Ambos comparten la idea de estudiar el codigo fuente a nivel lexico, pero cada uno tiene un objetivo distinto.
