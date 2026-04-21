"""
Analizador Léxico para C - Basado en ISO/IEC 9899:1999
Implementación en Python

Autor: Análisis de Lenguajes
Propósito: Tokenizar código fuente en C válido según el estándar C99
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator


class TokenType(Enum):
    """Tipos de tokens reconocidos por el analizador léxico"""
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    CHAR_LITERAL = "CHAR"
    OPERATOR = "OPERATOR"
    DELIMITER = "DELIMITER"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    UNKNOWN = "UNKNOWN"
    EOF = "EOF"


@dataclass
class Token:
    """Representa un token léxico extraído del código fuente"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.value}, '{self.value}', L{self.line}:C{self.column})"
    
    def __str__(self) -> str:
        return f"[{self.type.value:12}] {self.value:20} (Línea: {self.line}, Col: {self.column})"


class Lexer:
    """
    Analizador Léxico para C (C99)
    
    Reconoce:
    - Palabras clave
    - Identificadores
    - Números (int, hex, float)
    - Cadenas de caracteres y caracteres
    - Operadores
    - Delimitadores
    - Comentarios (una y múltiples líneas)
    """
    
    # Palabras clave de C99
    KEYWORDS = {
        'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do',
        'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if',
        'inline', 'int', 'long', 'register', 'restrict', 'return', 'short',
        'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
        'unsigned', 'void', 'volatile', 'while',
        # C99 específicas
        '_Bool', '_Complex', '_Imaginary'
    }
    
    # Operadores de dos caracteres (orden importante: operadores más largos primero)
    MULTI_CHAR_OPERATORS = {
        '==', '!=', '<=', '>=', '&&', '||', '++', '--', '->',
        '<<', '>>', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='
    }
    
    # Operadores de un carácter
    SINGLE_CHAR_OPERATORS = {
        '+', '-', '*', '/', '%', '=', '<', '>', '!', '&', '|', '^', '~', '?', ':'
    }
    
    # Delimitadores
    DELIMITERS = {
        '(', ')', '{', '}', '[', ']', ';', ',', '.', '#'
    }
    
    def __init__(self, source: str):
        """
        Inicializa el analizador léxico
        
        Args:
            source: Código fuente C a analizar
        """
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def _current_char(self) -> Optional[str]:
        """Retorna el carácter actual sin avanzar"""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def _peek_char(self, offset: int = 1) -> Optional[str]:
        """Retorna un carácter futuro sin avanzar"""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def _advance(self) -> Optional[str]:
        """Avanza una posición y retorna el carácter anterior"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def _skip_whitespace(self) -> None:
        """Salta espacios en blanco, tabs y saltos de línea"""
        while self._current_char() and self._current_char() in ' \t\n\r':
            self._advance()
    
    def _read_line_comment(self) -> Token:
        """Lee un comentario de una línea (//...)"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        # Saltar los dos slashes
        self._advance()
        self._advance()
        
        # Leer hasta fin de línea
        while self._current_char() and self._current_char() != '\n':
            value += self._current_char()
            self._advance()
        
        return Token(TokenType.COMMENT, value, start_line, start_col)
    
    def _read_block_comment(self) -> Token:
        """Lee un comentario de bloque (/* ... */)"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        # Saltar /* 
        self._advance()
        self._advance()
        
        # Leer hasta */
        while self._current_char():
            if self._current_char() == '*' and self._peek_char() == '/':
                self._advance()
                self._advance()
                break
            value += self._current_char()
            self._advance()
        
        return Token(TokenType.COMMENT, value, start_line, start_col)
    
    def _read_number(self) -> Token:
        """Lee un número (entero o flotante, decimal o hexadecimal)"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        # Verificar hexadecimal
        if self._current_char() == '0' and self._peek_char() in 'xX':
            value += self._advance()  # 0
            value += self._advance()  # x
            while self._current_char() and self._current_char() in '0123456789abcdefABCDEF':
                value += self._advance()
            return Token(TokenType.NUMBER, value, start_line, start_col)
        
        # Leer parte entera
        while self._current_char() and self._current_char().isdigit():
            value += self._advance()
        
        # Verificar punto decimal
        if self._current_char() == '.' and self._peek_char() and self._peek_char().isdigit():
            value += self._advance()  # punto
            while self._current_char() and self._current_char().isdigit():
                value += self._advance()
        
        # Verificar notación científica (e, E)
        if self._current_char() and self._current_char() in 'eE':
            value += self._advance()
            if self._current_char() and self._current_char() in '+-':
                value += self._advance()
            while self._current_char() and self._current_char().isdigit():
                value += self._advance()
        
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def _read_identifier(self) -> Token:
        """Lee un identificador o palabra clave"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        while self._current_char() and (self._current_char().isalnum() or self._current_char() == '_'):
            value += self._advance()
        
        # Verificar si es palabra clave
        token_type = TokenType.KEYWORD if value in self.KEYWORDS else TokenType.IDENTIFIER
        
        return Token(token_type, value, start_line, start_col)
    
    def _read_string(self) -> Token:
        """Lee una cadena de caracteres ("...")"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        self._advance()  # Saltar comilla inicial
        
        while self._current_char() and self._current_char() != '"':
            if self._current_char() == '\\':
                value += self._advance()
                if self._current_char():
                    value += self._advance()
            else:
                value += self._advance()
        
        if self._current_char() == '"':
            self._advance()  # Saltar comilla final
        
        return Token(TokenType.STRING, value, start_line, start_col)
    
    def _read_char_literal(self) -> Token:
        """Lee un literal de carácter ('...')"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        self._advance()  # Saltar comilla simple inicial
        
        while self._current_char() and self._current_char() != "'":
            if self._current_char() == '\\':
                value += self._advance()
                if self._current_char():
                    value += self._advance()
            else:
                value += self._advance()
        
        if self._current_char() == "'":
            self._advance()  # Saltar comilla simple final
        
        return Token(TokenType.CHAR_LITERAL, value, start_line, start_col)
    
    def _read_operator(self) -> Token:
        """Lee un operador (uno o dos caracteres)"""
        start_line = self.line
        start_col = self.column
        
        # Verificar operadores de dos caracteres
        two_char = self.source[self.position:self.position+2]
        if two_char in self.MULTI_CHAR_OPERATORS:
            self._advance()
            self._advance()
            return Token(TokenType.OPERATOR, two_char, start_line, start_col)
        
        # Operador de un carácter
        value = self._advance()
        return Token(TokenType.OPERATOR, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """
        Realiza el análisis léxico completo del código fuente
        
        Returns:
            Lista de tokens extraídos del código fuente
        """
        self.tokens = []
        
        while self.position < len(self.source):
            self._skip_whitespace()
            
            if self.position >= len(self.source):
                break
            
            current = self._current_char()
            start_line = self.line
            start_col = self.column
            
            # Comentario de una línea
            if current == '/' and self._peek_char() == '/':
                self.tokens.append(self._read_line_comment())
            
            # Comentario de bloque
            elif current == '/' and self._peek_char() == '*':
                self.tokens.append(self._read_block_comment())
            
            # Número
            elif current.isdigit():
                self.tokens.append(self._read_number())
            
            # Identificador o palabra clave
            elif current.isalpha() or current == '_':
                self.tokens.append(self._read_identifier())
            
            # Cadena
            elif current == '"':
                self.tokens.append(self._read_string())
            
            # Carácter
            elif current == "'":
                self.tokens.append(self._read_char_literal())
            
            # Delimitador
            elif current in self.DELIMITERS:
                value = self._advance()
                self.tokens.append(Token(TokenType.DELIMITER, value, start_line, start_col))
            
            # Operador
            elif current in self.SINGLE_CHAR_OPERATORS or (current == '/' and self._peek_char() not in ['/', '*']):
                self.tokens.append(self._read_operator())
            
            # Token desconocido
            else:
                value = self._advance()
                self.tokens.append(Token(TokenType.UNKNOWN, value, start_line, start_col))
        
        # Agregar token EOF
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        
        return self.tokens
    
    def get_tokens(self, skip_comments: bool = True, skip_whitespace_tokens: bool = True) -> List[Token]:
        """
        Retorna los tokens filtrados según criterios
        
        Args:
            skip_comments: Si es True, excluye comentarios
            skip_whitespace_tokens: Si es True, excluye espacios en blanco
        
        Returns:
            Lista filtrada de tokens
        """
        if not self.tokens:
            self.tokenize()
        
        filtered = []
        for token in self.tokens:
            if skip_comments and token.type == TokenType.COMMENT:
                continue
            if skip_whitespace_tokens and token.type == TokenType.WHITESPACE:
                continue
            filtered.append(token)
        
        return filtered


def analyze_file(filename: str) -> List[Token]:
    """
    Analiza un archivo de código C
    
    Args:
        filename: Ruta del archivo a analizar
    
    Returns:
        Lista de tokens del archivo
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        lexer = Lexer(source)
        return lexer.get_tokens()
    except FileNotFoundError:
        print(f"Error: Archivo '{filename}' no encontrado")
        return []


def print_tokens(tokens: List[Token]) -> None:
    """Imprime los tokens de forma legible"""
    print("\n" + "=" * 80)
    print("ANÁLISIS LÉXICO - TOKENS IDENTIFICADOS")
    print("=" * 80 + "\n")
    
    for i, token in enumerate(tokens, 1):
        print(f"{i:3}. {token}")
    
    print("\n" + "=" * 80)
    print(f"Total de tokens: {len(tokens)}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Ejemplo de uso
    test_code = '''
    // Ejemplo de programa en C
    int main() {
        int x = 10;
        float y = 3.14;
        char letra = 'A';
        
        /* Comentario de bloque
           Multi-línea */
        
        if (x > 5) {
            printf("x es mayor que 5\\n");
        } else {
            printf("x es menor o igual a 5\\n");
        }
        
        while (y < 100.0) {
            y = y * 2.0;
        }
        
        for (int i = 0; i < 10; i++) {
            x += i;
        }
        
        return 0;
    }
    '''
    
    lexer = Lexer(test_code)
    tokens = lexer.get_tokens()
    print_tokens(tokens)
