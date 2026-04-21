# Analizador Léxico de C - Basado en ISO/IEC 9899:1999

Un analizador léxico (tokenizador) completo para el lenguaje de programación C, implementado en Python puro sin dependencias externas.

## 📋 Contenido del Proyecto

```
act3.1-analizador-lexico/
├── ANALISIS_Y_DISEÑO.md          # Documento completo de análisis y justificación
├── lexer.py                       # Implementación del analizador léxico
├── main.py                        # Herramienta interactiva
├── test_lexer.py                  # Suite de pruebas unitarias
├── ejemplo1.c                     # Ejemplo simple
├── ejemplo2.c                     # Ejemplo con estructuras de control
├── ejemplo3.c                     # Ejemplo con diversos tipos de números
└── README.md                      # Este archivo
```

## 🎯 Características Principales

### Tokens Reconocidos

El analizador reconoce:

- **29 Palabras clave** de C99
- **Identificadores** válidos en C
- **Números**: decimales, hexadecimales (0xFF) y punto flotante (1.5e-3)
- **Cadenas de caracteres** con soporte para escapes
- **Literales de carácter** ('a', '\\n')
- **25+ Operadores** (aritméticos, lógicos, bitwise, etc.)
- **Delimitadores** (paréntesis, llaves, corchetes, puntuación)
- **Comentarios** de una y múltiples líneas
- **Posición** en el código (línea y columna)

### Características Técnicas

✅ **Análisis completo**: Preserva información de línea y columna para cada token  
✅ **Manejo de comentarios**: Reconoce y filtra automáticamente comentarios  
✅ **Números en múltiples formatos**: Decimal, hexadecimal, exponencial  
✅ **Escape sequences**: Maneja secuencias de escape en cadenas y caracteres  
✅ **Validación**: Detecta tokens inválidos como categoría UNKNOWN  
✅ **Escalable**: Estructura modular para agregar nuevos patrones fácilmente  
✅ **Bien documentado**: Código con docstrings en español  
✅ **Testeado**: Suite completa con 9 pruebas unitarias  

## 🚀 Uso

### Opción 1: Herramienta Interactiva

```bash
python3 main.py
```

Ofrece un menú con opciones para:
- Analizar un archivo .c específico
- Escribir código C directamente en la consola
- Analizar los archivos de ejemplo incluidos
- Ver información del analizador

### Opción 2: Desde Línea de Comandos

```bash
python3 main.py ruta/al/archivo.c
```

### Opción 3: Importar como Módulo Python

```python
from lexer import Lexer, print_tokens

# Analizar código
code = "int main() { return 0; }"
lexer = Lexer(code)
tokens = lexer.get_tokens()  # Excluye comentarios por defecto

# Imprimir resultados
print_tokens(tokens)

# O procesarlos manualmente
for token in tokens:
    print(f"{token.type.value}: {token.value}")
```

### Opción 4: Ejecutar Pruebas

```bash
python3 test_lexer.py
```

Ejecuta 9 pruebas unitarias que verifican:
1. Reconocimiento de palabras clave
2. Reconocimiento de identificadores
3. Reconocimiento de números
4. Reconocimiento de cadenas
5. Reconocimiento de literales de carácter
6. Reconocimiento de operadores
7. Reconocimiento de delimitadores
8. Reconocimiento de comentarios
9. Análisis de programa completo

## 📊 Ejemplo de Salida

### Entrada (entrada.c):
```c
// Comentario simple
int main() {
    int x = 42;
    return 0;
}
```

### Salida:
```
================================================================================
ANÁLISIS LÉXICO - TOKENS IDENTIFICADOS
================================================================================

  1. Token(KEYWORD, 'int', L1:1)
  2. Token(IDENTIFIER, 'main', L1:5)
  3. Token(DELIMITER, '(', L1:9)
  4. Token(DELIMITER, ')', L1:10)
  5. Token(DELIMITER, '{', L1:12)
  6. Token(KEYWORD, 'int', L2:5)
  7. Token(IDENTIFIER, 'x', L2:9)
  8. Token(OPERATOR, '=', L2:11)
  9. Token(NUMBER, '42', L2:13)
 10. Token(DELIMITER, ';', L2:15)
 11. Token(KEYWORD, 'return', L3:5)
 12. Token(NUMBER, '0', L3:12)
 13. Token(DELIMITER, ';', L3:13)
 14. Token(DELIMITER, '}', L4:1)
 15. Token(EOF, '', L4:2)

================================================================================
Total de tokens: 15
================================================================================
```

## 📚 Estructura de Clases

### `TokenType` (Enumeración)
Define los tipos de tokens posibles:
- KEYWORD, IDENTIFIER, NUMBER, STRING, CHAR_LITERAL
- OPERATOR, DELIMITER, COMMENT, WHITESPACE, UNKNOWN, EOF

### `Token` (Dataclass)
Representa un token individual con:
- `type`: TokenType
- `value`: str (contenido del token)
- `line`: int (número de línea)
- `column`: int (número de columna)

### `Lexer` (Clase Principal)
Realiza el análisis léxico:

**Métodos públicos:**
- `__init__(source: str)`: Inicializa con código fuente
- `tokenize()`: Realiza análisis completo
- `get_tokens()`: Retorna tokens (opcionalmente filtrando comentarios)

**Métodos privados:**
- `_current_char()`: Retorna carácter actual
- `_advance()`: Avanza una posición
- `_skip_whitespace()`: Salta espacios en blanco
- `_read_number()`: Reconoce números
- `_read_identifier()`: Reconoce identificadores/keywords
- `_read_string()`: Reconoce cadenas de caracteres
- `_read_char_literal()`: Reconoce literales de carácter
- `_read_operator()`: Reconoce operadores
- `_read_line_comment()`: Reconoce comentarios //
- `_read_block_comment()`: Reconoce comentarios /* */

## 📝 Documento de Análisis y Justificación

Ver archivo: **ANALISIS_Y_DISEÑO.md**

Este documento contiene:

1. **Selección del Fragmento del Lenguaje**
   - Criterios de selección
   - Cobertura funcional (60-70% de uso práctico)
   - Completitud mínima

2. **Justificación Detallada**
   - Por qué se incluyen ciertas características
   - Por qué se excluyen otras (especificadores complejos, preprocesador, etc.)

3. **Exclusiones Justificadas**
   - Especificadores de almacenamiento raramente usados
   - Directivas del preprocesador (no son tokens léxicos)
   - Tipos derivados complejos
   - Características de compilador específico
   - Atributos de C11 (posteriores a C99)

4. **Diseño de la Solución**
   - Arquitectura del analizador
   - Componentes principales
   - Patrones de tokens (regex)

5. **Ejemplo de Ejecución**

## 🔧 Extensibilidad

Para agregar nuevos patrones de tokens, modifique la clase `Lexer`:

### Agregar Nueva Palabra Clave:
```python
Lexer.KEYWORDS.add('mi_palabra_clave')
```

### Agregar Nuevo Operador:
```python
Lexer.MULTI_CHAR_OPERATORS.add('@@')
```

### Agregar Nuevo Tipo de Token:
```python
class TokenType(Enum):
    # ... tipos existentes ...
    MI_TIPO = "MI_TIPO"
```

## 📖 Estándar Utilizado

**ISO/IEC 9899:1999 (Standard C99)**

Referencias:
- Secciones 6.4 (Lexical elements)
- Secciones 6.5 (Expressions)
- Secciones 6.7 (Declarations)

## 🧪 Evidencia de Funcionamiento

### Pruebas Ejecutadas:

```
[TEST 1] Reconocimiento de palabras clave ✓
[TEST 2] Reconocimiento de identificadores ✓
[TEST 3] Reconocimiento de números ✓
[TEST 4] Reconocimiento de cadenas ✓
[TEST 5] Reconocimiento de caracteres ✓
[TEST 6] Reconocimiento de operadores ✓
[TEST 7] Reconocimiento de delimitadores ✓
[TEST 8] Reconocimiento de comentarios ✓
[TEST 9] Análisis de programa completo ✓

Resultado: 9/9 pruebas pasadas
```

## 📂 Archivos de Ejemplo

### `ejemplo1.c`
Programa simple con:
- Declaración de variables
- Comentarios de una y múltiples líneas
- Bucle while
- Función printf

### `ejemplo2.c`
Programa con:
- Función recursiva (Fibonacci)
- Estructura if-else compleja
- Bucle for
- Operadores lógicos (&&)
- Break statement

### `ejemplo3.c`
Ejemplos de números:
- Decimales positivos y negativos
- Números hexadecimales
- Punto flotante
- Notación científica

## 🐍 Requisitos

- **Python 3.6+** (no requiere bibliotecas externas)

## 📄 Licencia

Proyecto educativo - Análisis de Lenguajes de Programación

## 👤 Autor

Estudiante de Análisis de Lenguajes

## 🔗 Referencias Adicionales

- Flex & Bison: https://www.gnu.org/software/flex/manual/
- Dragon Book: "Compilers: Principles, Techniques, and Tools" (Aho et al, 2006)
- ISO/IEC 9899:1999 Standard

---

**Última actualización**: Abril 2026
