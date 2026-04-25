%:include <stdlib.h>   // equivalente a #include (digraph)
#include <stdio.h>

#define CONCAT(a, b) a ## b
#define TO_STR(x) #x
#define VAR(name, num) CONCAT(name, num)

// Macro que genera variables
int VAR(var_, 1) = 10;
int VAR(var_, 2) = 20;

// Uso de _Bool y tipos menos comunes
_Bool flag = 1;
long long bigNumber = 123456789LL;
unsigned long ul = 4000000000UL;

// Hex float (C99)
double hexFloat = 0x1.8p+2; // 1.5 * 2^2 = 6.0

// Número que podría parecer PP_NUMBER raro
double tricky = 1e+ + 2; // separación intencional

// Caracteres y escapes
char tab = '\t';
char quote = '\'';
char backslash = '\\';

// Strings con escapes y concatenación
char *text = "Linea 1\n"
             "Linea 2\t"
             "Fin";

// Comentario con símbolos raros
/* !! @@ ## $$ %% ^^ && ** (( )) */

// Función con punteros y arrays
void process(int *arr, int size) {
    for (int i = 0; i < size; ++i) {
        arr[i] *= 2;
    }
}

// Uso de estructuras anónimas
struct {
    int x;
    int y;
} point = { .x = 3, .y = 4 };

// Operadores menos comunes
int main(void) {
    int a = 5, b = 3;

    a ^= b;
    a |= b;
    a &= b;

    int shift = (a << 2) >> 1;

    // Ternario anidado
    int res = (a > b) ? ((a > 10) ? a : 10) : b;

    // Uso de goto (raro pero válido)
    goto label;

label:
    printf("Resultado: %d\n", res);

    // Uso de sizeof
    size_t s = sizeof(point);

    // Array y punteros
    int nums[3] = {1,2,3};
    process(nums, 3);

    return 0;
}