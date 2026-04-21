"""
Herramienta interactiva para analizar archivos C
Permite analizar archivos de código C y visualizar los tokens identificados
"""

import sys
import os
from lexer import Lexer, TokenType, print_tokens, analyze_file
from pathlib import Path


def print_header():
    """Imprime el encabezado de bienvenida"""
    print("\n" + "="*80)
    print(" ANALIZADOR LÉXICO DE C - Basado en ISO/IEC 9899:1999")
    print("="*80 + "\n")


def print_menu():
    """Imprime el menú principal"""
    print("Opciones:")
    print("  1. Analizar un archivo .c")
    print("  2. Escribir código y analizar")
    print("  3. Analizar archivos de ejemplo")
    print("  4. Ver información sobre el analizador")
    print("  5. Salir")
    print()


def analyze_interactive():
    """Permite al usuario escribir código C directamente"""
    print("\nEscriba código C (presione Enter dos veces para terminar):")
    print("-" * 80)
    
    lines = []
    empty_count = 0
    
    while empty_count < 2:
        try:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    code = "\n".join(lines)
    
    if code.strip():
        lexer = Lexer(code)
        tokens = lexer.get_tokens()
        print_tokens(tokens)
    else:
        print("No se ingresó código.")


def analyze_file_interactive():
    """Permite al usuario seleccionar un archivo para analizar"""
    print("\nIngrese la ruta del archivo .c a analizar:")
    filepath = input().strip()
    
    if not filepath:
        print("Ruta vacía.")
        return
    
    if not os.path.exists(filepath):
        print(f"El archivo '{filepath}' no existe.")
        return
    
    if not filepath.endswith('.c'):
        print("Advertencia: El archivo no tiene extensión .c")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        lexer = Lexer(code)
        tokens = lexer.get_tokens()
        print_tokens(tokens)
        
    except Exception as e:
        print(f"Error al leer el archivo: {e}")


def analyze_examples():
    """Analiza los archivos de ejemplo disponibles"""
    example_dir = Path(__file__).parent
    examples = sorted(example_dir.glob("ejemplo*.c"))
    
    if not examples:
        print("\nNo se encontraron archivos de ejemplo (ejemplo1.c, ejemplo2.c, etc.)")
        return
    
    print(f"\nEncontrados {len(examples)} archivo(s) de ejemplo:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example.name}")
    
    print(f"  {len(examples) + 1}. Analizar todos")
    print(f"  0. Cancelar")
    
    choice = input("\nSeleccione un archivo: ").strip()
    
    try:
        choice = int(choice)
        
        if choice == 0:
            return
        elif choice == len(examples) + 1:
            # Analizar todos
            for example in examples:
                print("\n" + "="*80)
                print(f"Analizando: {example.name}")
                print("="*80)
                analyze_file(str(example))
                print()
        elif 1 <= choice <= len(examples):
            analyze_file(str(examples[choice - 1]))
        else:
            print("Opción inválida.")
    
    except ValueError:
        print("Entrada inválida.")


def show_info():
    """Muestra información sobre el analizador"""
    info = """
ANALIZADOR LÉXICO DE C
======================

Este analizador reconoce los siguientes tokens:

1. PALABRAS CLAVE (29)
   - Tipos: int, float, double, char, void
   - Control: if, else, while, for, do, switch, case, break, continue, return
   - Almacenamiento: static, extern, auto, register, const, volatile, restrict
   - Otros: struct, union, enum, typedef, sizeof, inline, _Bool, _Complex, _Imaginary

2. IDENTIFICADORES
   - Nombres de variables y funciones
   - Formato: [a-zA-Z_][a-zA-Z0-9_]*

3. NÚMEROS
   - Decimales: 42, 100, -5
   - Hexadecimales: 0xFF, 0x20
   - Punto flotante: 3.14, 1.5e-3, 6.02e23

4. CADENAS
   - Formato: "texto" con soporte para escapes como \\n, \\t

5. LITERALES DE CARÁCTER
   - Formato: 'a', '\\n', ecc.

6. OPERADORES
   - Aritméticos: +, -, *, /, %
   - Relacionales: ==, !=, <, >, <=, >=
   - Lógicos: &&, ||, !
   - Bitwise: &, |, ^, ~, <<, >>
   - Asignación: =, +=, -=, *=, /=, %=, &=, |=, ^=, <<=, >>=
   - Otros: ++, --, ->, ?:

7. DELIMITADORES
   - Paréntesis, llaves, corchetes: ( ) { } [ ]
   - Puntuación: ; , . #

8. COMENTARIOS
   - Una línea: // comentario
   - Múltiples líneas: /* comentario */

BASADO EN: ISO/IEC 9899:1999 (C99 Standard)
"""
    print(info)


def main():
    """Función principal"""
    print_header()
    
    while True:
        print_menu()
        choice = input("Seleccione una opción: ").strip()
        
        if choice == "1":
            analyze_file_interactive()
        elif choice == "2":
            analyze_interactive()
        elif choice == "3":
            analyze_examples()
        elif choice == "4":
            show_info()
        elif choice == "5":
            print("\n¡Hasta luego!\n")
            break
        else:
            print("Opción inválida. Intente de nuevo.\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Modo de línea de comandos
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            print_header()
            tokens = analyze_file(filepath)
            print_tokens(tokens)
        else:
            print(f"Error: El archivo '{filepath}' no existe.")
    else:
        # Modo interactivo
        try:
            main()
        except KeyboardInterrupt:
            print("\n\n¡Programa interrumpido por el usuario!")
