/*
    Ejemplo 3: Números en diferentes formatos
    Demuestra decimales, hexadecimales y notación científica
*/

int main() {
    // Números enteros en decimal
    int decimal = 42;
    int negative = -100;
    
    // Números hexadecimales
    int hex1 = 0xFF;           // 255 en decimal
    int hex2 = 0x10;           // 16 en decimal
    int hex3 = 0xDEADBEEF;     // Color o ID
    
    // Números de punto flotante
    float f1 = 3.14;
    float f2 = 0.001;
    float f3 = 1e10;           // Notación científica (10 billones)
    
    double d1 = 2.71828;
    double d2 = 1.5e-3;        // 0.0015
    double d3 = 6.02e23;       // Número de Avogadro
    
    // Operaciones
    int result = decimal + hex1;
    float calc = f1 * f2 + f3;
    
    if (hex1 >= 0xFF && d1 != 0.0) {
        return 0;
    }
    
    return 1;
}
