"""
Suite de pruebas unitarias para el analizador léxico de C
Verifica que todos los tipos de tokens se reconozcan correctamente
"""

from lexer import Lexer, TokenType, Token
import sys


def test_keywords():
    """Prueba el reconocimiento de palabras clave"""
    print("\n[TEST 1] Reconocimiento de palabras clave")
    code = "int if while for return void const"
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    expected_keywords = ['int', 'if', 'while', 'for', 'return', 'void', 'const']
    
    success = True
    for token, expected in zip(tokens, expected_keywords):
        if token.type != TokenType.KEYWORD or token.value != expected:
            print(f"  ✗ Esperado: {expected}, Obtenido: {token.value}")
            success = False
    
    if success:
        print(f"  ✓ Todas las palabras clave reconocidas correctamente")
    return success


def test_identifiers():
    """Prueba el reconocimiento de identificadores"""
    print("\n[TEST 2] Reconocimiento de identificadores")
    code = "variable _private my_var x123 contador"
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    expected_ids = ['variable', '_private', 'my_var', 'x123', 'contador']
    
    success = True
    for token, expected in zip(tokens, expected_ids):
        if token.type != TokenType.IDENTIFIER or token.value != expected:
            print(f"  ✗ Esperado: {expected}, Obtenido: {token.value}")
            success = False
    
    if success:
        print(f"  ✓ Todos los identificadores reconocidos correctamente")
    return success


def test_numbers():
    """Prueba el reconocimiento de números"""
    print("\n[TEST 3] Reconocimiento de números")
    code = "42 0xFF 3.14 1.5e-3 100 0x10 2.0"
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    expected_numbers = ['42', '0xFF', '3.14', '1.5e-3', '100', '0x10', '2.0']
    
    success = True
    for token, expected in zip(tokens, expected_numbers):
        if token.type != TokenType.NUMBER or token.value != expected:
            print(f"  ✗ Esperado: {expected}, Obtenido: {token.value}")
            success = False
    
    if success:
        print(f"  ✓ Todos los números reconocidos correctamente")
    return success


def test_strings():
    """Prueba el reconocimiento de cadenas"""
    print("\n[TEST 4] Reconocimiento de cadenas de caracteres")
    code = '"hola" "mundo" "hello\\nworld"'
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    success = True
    if tokens[0].type != TokenType.STRING or tokens[0].value != "hola":
        print(f"  ✗ Primera cadena no reconocida")
        success = False
    
    if tokens[1].type != TokenType.STRING or tokens[1].value != "mundo":
        print(f"  ✗ Segunda cadena no reconocida")
        success = False
    
    if tokens[2].type != TokenType.STRING or "hello\\nworld" not in tokens[2].value:
        print(f"  ✗ Cadena con escape no reconocida")
        success = False
    
    if success:
        print(f"  ✓ Todas las cadenas reconocidas correctamente")
    return success


def test_char_literals():
    """Prueba el reconocimiento de caracteres"""
    print("\n[TEST 5] Reconocimiento de literales de carácter")
    code = "'a' 'b' '\\n' '0'"
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    success = True
    if tokens[0].type != TokenType.CHAR_LITERAL or tokens[0].value != "a":
        print(f"  ✗ Primer carácter no reconocido")
        success = False
    
    if success:
        print(f"  ✓ Los literales de carácter se reconocieron correctamente")
    return success


def test_operators():
    """Prueba el reconocimiento de operadores"""
    print("\n[TEST 6] Reconocimiento de operadores")
    code = "+ - * / == != <= >= && ||"
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    expected_ops = ['+', '-', '*', '/', '==', '!=', '<=', '>=', '&&', '||']
    
    success = True
    for token, expected in zip(tokens, expected_ops):
        if token.type != TokenType.OPERATOR or token.value != expected:
            print(f"  ✗ Esperado operador: {expected}, Obtenido: {token.value}")
            success = False
    
    if success:
        print(f"  ✓ Todos los operadores reconocidos correctamente")
    return success


def test_delimiters():
    """Prueba el reconocimiento de delimitadores"""
    print("\n[TEST 7] Reconocimiento de delimitadores")
    code = "() {} [] ; , ."
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    expected_delims = ['(', ')', '{', '}', '[', ']', ';', ',', '.']
    
    success = True
    for token, expected in zip(tokens, expected_delims):
        if token.type != TokenType.DELIMITER or token.value != expected:
            print(f"  ✗ Esperado: {expected}, Obtenido: {token.value}")
            success = False
    
    if success:
        print(f"  ✓ Todos los delimitadores reconocidos correctamente")
    return success


def test_comments():
    """Prueba el reconocimiento de comentarios"""
    print("\n[TEST 8] Reconocimiento de comentarios")
    code = """
    // Comentario de una línea
    int x; /* Comentario de bloque */ int y;
    """
    
    lexer = Lexer(code)
    all_tokens = lexer.tokenize()
    
    comment_tokens = [t for t in all_tokens if t.type == TokenType.COMMENT]
    
    success = True
    if len(comment_tokens) != 2:
        print(f"  ✗ Se esperaban 2 comentarios, se encontraron {len(comment_tokens)}")
        success = False
    
    if success:
        print(f"  ✓ Los comentarios fueron reconocidos correctamente")
    return success


def test_full_program():
    """Prueba con un programa completo"""
    print("\n[TEST 9] Análisis de programa completo")
    code = """
    int main() {
        int x = 42;
        float pi = 3.14;
        
        if (x > 10 && pi < 4.0) {
            printf("Condición verdadera\\n");
            return 0;
        }
        
        return 1;
    }
    """
    
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    
    # Verificar que se reconozcan tipos específicos
    types_found = set(t.type for t in tokens)
    
    required_types = {TokenType.KEYWORD, TokenType.IDENTIFIER, TokenType.NUMBER, 
                     TokenType.OPERATOR, TokenType.DELIMITER, TokenType.STRING}
    
    success = required_types.issubset(types_found)
    
    if success:
        print(f"  ✓ Programa completo analizado correctamente")
        print(f"    Total tokens: {len(tokens)}")
        print(f"    Tipos encontrados: {', '.join(str(t.value) for t in types_found if t != TokenType.EOF)}")
    else:
        missing = required_types - types_found
        print(f"  ✗ Tipos no encontrados: {missing}")
    
    return success


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*70)
    print("SUITE DE PRUEBAS - ANALIZADOR LÉXICO DE C")
    print("="*70)
    
    tests = [
        test_keywords,
        test_identifiers,
        test_numbers,
        test_strings,
        test_char_literals,
        test_operators,
        test_delimiters,
        test_comments,
        test_full_program
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Error en prueba: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print(f"RESULTADOS: {sum(results)}/{len(results)} pruebas pasadas")
    print("="*70 + "\n")
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
