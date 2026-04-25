int fibonacci(int n) {
    if (n <= 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    }
    
    int a = 0, b = 1, c;
    
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    
    return b;
}

int main() {
    int limit = 10;
    
    for (int i = 0; i < limit; i++) {
        int fib = fibonacci(i);
        
        if (fib >= 0 && fib < 100) {
            // Válido
        } else if (fib >= 100) {
            break;
        }
    }
    
    return 0;
}
