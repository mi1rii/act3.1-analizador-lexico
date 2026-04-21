import ply.lex as lex
import ply.yacc as yacc

keywords = {
    'while': 'WHILE',
    'if': 'IF',
}

tokens = [
    'INT',
    'ID',
    'LE',
    'PP'
] + list(keywords.values())

t_ignore = ' \t\n'

t_LE = r'<='

literals = '+*-(){},;='

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in keywords.keys():
        t.type = keywords[t.value]
    return t

def t_INT(t):
    r'[0-9](_?[0-9])*'
    t.value = int(t.value)
    return t   
lexer = lex.lex()

# lexer.input("""
#             int main() {
#                 int i = 0;
#                 while (a <= 5){
#                     return 1 + 1;
#                     }
#             }
#             """)

# while True:
#     tok = lexer.token()
#     if not tok:
#         break
#     print(tok)

"""
E -> E + T | T
T -> T * F | F
F -> ( E ) | INT
"""
def p_E(p):
    """
    E : E '+' T
      | T
    """
    if len(p) > 2:
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1]

def p_T(p):
    """
    T : T '*' F
      | F
    """
    if len(p) > 2:
        p[0] = p[1] * p[3]
    else:
        p[0] = p[1]

def p_F_with_parentheses(p):
    """
    F : '(' E ')'
    """
    p[0] = p[2]

def p_F_integer(p):
    """
    F : INT
    """
    p[0] = p[1]
        
    
parser = yacc.yacc()   
print(parser.parse("(1 + 10) * 3"))