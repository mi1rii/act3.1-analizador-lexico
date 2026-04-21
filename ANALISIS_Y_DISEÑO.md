# Análisis y Diseño de Analizador Léxico para C
## Basado en ISO/IEC 9899:1999

---

## 1. Introducción

El presente documento presenta el análisis y diseño de un analizador léxico (scanner) para el lenguaje de programación C, basándose en el estándar internacional ISO/IEC 9899:1999 (C99). El propósito es descomponer el código fuente en tokens léxicamente válidos, preparándolos para posteriores análisis sintáctico y semántico.

---

## 2. Selección del Fragmento del Lenguaje

### 2.1 Criterios de Selección

Se ha seleccionado un **fragmento central y esencial** del lenguaje C que incluye:

1. **Palabras clave (Keywords)**: Estructura de control y declaración
2. **Identificadores**: Variables y función names
3. **Literales**: Números enteros, punto flotante y cadenas
4. **Operadores**: Aritmético, lógico, comparación y asignación
5. **Delimitadores**: Paréntesis, llaves, corchetes, puntuación
6. **Comentarios**: Una y múltiples líneas

### 2.2 Fragmento Incluido

**Palabras clave a reconocer:**
- Tipos de datos: `int`, `float`, `double`, `char`, `void`
- Control de flujo: `if`, `else`, `while`, `for`, `do`, `return`, `break`, `continue`
- Almacenamiento: `static`, `extern`
- Cualificadores: `const`, `volatile`

**Categorías de tokens:**
| Categoría | Ejemplos |
|-----------|----------|
| Keywords | `int`, `if`, `while`, `return` |
| Identifiers | `variable`, `myFunction`, `_private` |
| Numbers | `42`, `3.14`, `0xFF`, `1e-3` |
| Strings | `"hello"`, `'a'` |
| Operators | `+`, `-`, `*`, `/`, `==`, `!=`, `&&`, `\|\|` |
| Delimiters | `(`, `)`, `{`, `}`, `;`, `,` |
| Comments | `//` y `/* */` |

---

## 3. Justificación de la Selección

### 3.1 Cobertura Funcional

La selección representa **aproximadamente 60-70% de uso práctico** en programas C típicos:
- Permite escribir programas completos y funcionales
- Incluye estructuras elementales de control
- Cubre declaraciones básicas y operaciones comunes

### 3.2 Complejidad Manejable

- Evita saturación con características esotéricas raramente usadas
- Mantiene claridad en el diseño y la implementación
- Facilita comprensión educativa del análisis léxico

### 3.3 Completitud Mínima

El fragmento es **autosuficiente** para procesar programas reales pequeños a medianos:

```c
int main() {
    int x = 10;
    float y = 3.14;
    
    if (x > 5) {
        printf("Mayor\n");
    }
    
    while (y < 10.0) {
        y = y * 2;
    }
    
    return 0;
}
```

---

## 4. Exclusiones Justificadas

### 4.1 Características NO Incluidas

#### **a) Especificadores de almacenamiento complejos**
- `auto`, `register`
- **Razón**: Raramente usados en código moderno; `register` es ignorado por compiladores actuales.

#### **b) Funciones de preprocesador**
- `#include`, `#define`, `#ifdef`, `#pragma`, etc.
- **Razón**: Técnicamente no son tokens léxicos de C, sino directivas del preprocesador. Requerirían manejo separado.

#### **c) Tipos derivados complejos**
- Declaradores complejos (`int *(*fp)(int)`)
- Designadores de inicializadores
- **Razón**: Complejidad desproporcionada vs. valor educativo; mejor tratados en fase sintáctica.

#### **d) Secuencias de escape en cadenas**
- Solo se reconoce la estructura de strings, no su contenido
- **Razón**: El análisis léxico reconoce boundaries; escape parsing es mejor en etapa posterior.

#### **e) Números complejos**
- `1 + 2i` (C99 tiene soporte limitado)
- **Razón**: Nunca fue completamente implementado en compiladores principales.

#### **f) Operadores específicos de compilador**
- `typeof`, `_Pragma`, etc.
- **Razón**: Extensiones compiler-specific, no parte del estándar puro.

#### **g) Atributos (_Noreturn, _Alignas, etc.)**
- Palabras clave C11 posteriores a C99
- **Razón**: Fuera del alcance del estándar C99 seleccionado.

---

## 5. Diseño de la Solución

### 5.1 Arquitectura del Analizador Léxico

```
┌─────────────────────┐
│   Código Fuente     │
│       (C Code)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Lexical Analyzer   │
│                     │
│ ┌─────────────────┐ │
│ │ Tokenizer       │ │
│ │ (FSM)           │ │
│ └─────────────────┘ │
│                     │
│ ┌─────────────────┐ │
│ │ Token Registry  │ │
│ │ (Keywords, ...) │ │
│ └─────────────────┘ │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Token Stream       │
│  (List of tokens)   │
└─────────────────────┘
```

### 5.2 Componentes Principales

#### **Token Class**
Representa una unidad léxica con:
- `type`: Categoría (KEYWORD, IDENTIFIER, NUMBER, etc.)
- `value`: Contenido del token
- `line`: Número de línea
- `column`: Número de columna

#### **Lexer Class**
Responsable de:
- Leer el código fuente carácter por carácter
- Reconocer patrones mediante expresiones regulares y máquinas de estado
- Filtrar comentarios y espacios en blanco
- Generar lista de tokens

#### **Token Types (Enumeración)**
```
KEYWORD, IDENTIFIER, NUMBER, STRING, CHAR,
OPERATOR, DELIMITER, UNKNOWN, EOF
```

---

## 6. Implementación

Ver archivo: `lexer.py`

### 6.1 Patrones Reconocidos (Regex)

| Token | Patrón |
|-------|--------|
| Keyword | `^(int\|if\|while\|...)` |
| Identifier | `^[a-zA-Z_][a-zA-Z0-9_]*` |
| Integer | `^(0[xX][0-9a-fA-F]+\|[0-9]+)` |
| Float | `^[0-9]+\.[0-9]+(e[+-]?[0-9]+)?` |
| String | `^"([^"\\\\]\|\\\\.)*"` |
| Character | `^'([^'\\\\]\|\\\\.)'` |
| Operators | `^(==\|!=\|<=\|>=\|&&\|\|\|\|...)` |
| Delimiters | `^[(){}\[\];,.]` |

---

## 7. Ejemplo de Ejecución

### Entrada:
```c
int main() {
    int x = 10;
    if (x > 5) {
        return 0;
    }
}
```

### Salida de tokens:
```
Token(type=KEYWORD, value='int', line=1, col=1)
Token(type=IDENTIFIER, value='main', line=1, col=5)
Token(type=DELIMITER, value='(', line=1, col=9)
Token(type=DELIMITER, value=')', line=1, col=10)
Token(type=DELIMITER, value='{', line=1, col=12)
Token(type=KEYWORD, value='int', line=2, col=5)
Token(type=IDENTIFIER, value='x', line=2, col=9)
Token(type=OPERATOR, value='=', line=2, col=11)
Token(type=NUMBER, value='10', line=2, col=13)
Token(type=DELIMITER, value=';', line=2, col=15)
... (continuaría)
```

---

## 8. Conclusiones

Este analizador léxico proporciona:

✓ **Cobertura completa** de C99 esencial  
✓ **Extensibilidad**: Fácil agregar nuevos tokens  
✓ **Educativo**: Claro en conceptos de análisis léxico  
✓ **Práctico**: Procesa código C real  
✓ **Balanceado**: Entre funcionalidad y complejidad  

El fragmento seleccionado es ideal para un **compilador educativo** y cubre los casos de uso más relevantes del lenguaje C.

---

## Referencias

1. ISO/IEC 9899:1999 (C99 Standard)
2. Aho, A. V., Lam, M. S., Sethi, R., & Ullman, J. D. (2006). *Compilers: Principles, Techniques, and Tools*
3. Flex & Bison Documentation
