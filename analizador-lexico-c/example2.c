#include <stdio.h>
#include "mi_header.h"

#define MAX 100
#define SQUARE(x) ((x) * (x))

// Comentario de una sola línea

/*
   Comentario multilínea
*/

int global_var = 42;
static const double PI = 3.14159;

typedef struct {
    int id;
    char name[50];
} Student;

int sum(int a, int b) {
    return a + b;
}

int main(void) {
    int i = 0;
    long hexVal = 0x1A3F;
    unsigned int octVal = 0755;
    float f = 1.23e-4f;
    double d = .5E+2;
    char c = 'A';
    char newline = '\n';

    // String literals (incluye concatenación)
    char *msg = "Hola, " "mundo!";
    char *wide = L"Texto ancho";

    Student s;
    s.id = 1;
    
    // Uso de operadores
    for (i = 0; i < MAX; i++) {
        if (i % 2 == 0 && i != 10) {
            printf("i = %d\n", i);
        } else {
            continue;
        }
    }

    int result = SQUARE(5);
    
    // Operadores compuestos
    result += 10;
    result <<= 1;

    // Uso de punteros
    int *ptr = &result;
    *ptr = *ptr + 1;

    // Operador ternario
    int min = (result < 50) ? result : 50;

    // Switch-case
    switch (min) {
        case 10:
            printf("Diez\n");
            break;
        case 20:
            printf("Veinte\n");
            break;
        default:
            printf("Otro valor\n");
    }

    return 0;
}