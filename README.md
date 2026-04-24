# Analizador Léxico y Comparador de Similitud

Aplicación de escritorio en Python con PySide6 para comparar programas Python lado a lado usando cuatro técnicas de similitud. El proyecto usa el lexer estándar de Python mediante `tokenize` para las técnicas léxicas.

## Características

- Carga automática de archivos fuente desde `top-20-python`.
- Selección de archivo base y técnica de comparación.
- Ranking de similitud contra los demás archivos.
- Vista lado a lado con resaltado de bloques coincidentes.
- Números de línea en ambos editores.
- Panel de detalles con coincidencias, longitud común y líneas asociadas.
- Validación estricta para trabajar solo con archivos `.py`.

## Fórmula de similitud

```text
similitud = (suma total de longitudes comunes relevantes / longitud del programa más corto) * 100
```

- En técnicas tokenizadas, la longitud se mide en tokens.
- En técnicas de texto plano, la longitud se mide en caracteres.
- Los rangos solapados se fusionan antes de sumar la longitud común total.

## Requisitos

- Python 3.10 o superior.
- `pip`.
- PySide6.
- Una carpeta `top-20-python` con archivos `.py`.

## Estructura del proyecto

```text
main.py
ui/main_window.py
core/file_loader.py
core/tokenizer.py
core/generalizer.py
core/suffix_array.py
core/lcs_matcher.py
core/difflib_matcher.py
core/similarity.py
core/highlight_mapper.py
models/match_models.py
top-20-python/
```

## Estructura esperada de entrada

```text
act3.1-analizador-lexico/
├── main.py
├── top-20-python/
│   ├── programa_01.py
│   ├── programa_02.py
│   └── ...
```

La aplicación busca por defecto la carpeta `top-20-python` en la raíz del proyecto y solo carga archivos `.py`.

## Arquitectura breve

- `core/file_loader.py`: descubre y carga la carpeta de entrada, aceptando solo `.py`.
- `core/tokenizer.py`: usa `tokenize.tokenize(...)` y conserva posiciones originales.
- `core/generalizer.py`: reemplaza identificadores por `ID`, números por `NUM`, strings por `STR`, y conserva keywords, operadores y signos estructurales.
- `core/suffix_array.py`: implementa suffix array y LCP en Python puro.
- `core/lcs_matcher.py`: encuentra substrings contiguos comunes con umbral mínimo.
- `core/difflib_matcher.py`: obtiene bloques coincidentes con `difflib.SequenceMatcher`.
- `core/highlight_mapper.py`: traduce bloques a offsets absolutos para resaltarlos en PySide6.
- `core/similarity.py`: orquesta las cuatro técnicas y calcula el porcentaje final.
- `ui/main_window.py`: interfaz, ranking, detalle y resaltado visual.

## Las 4 técnicas implementadas

### 1. Baker tokenizado + generalización + suffix array + LCS

Flujo:

1. Tokenización con el lexer estándar de Python usando `tokenize`.
2. Generalización léxica:
   - identificadores `NAME` no reservados -> `ID`
   - números -> `NUM`
   - strings -> `STR`
   - keywords, operadores y puntuación se conservan
3. Construcción de secuencias lineales de tokens generalizados.
4. Construcción de suffix array sobre la secuencia concatenada de ambos archivos.
5. Cálculo de LCP para detectar substrings contiguos comunes.
6. Reconstrucción de rangos originales a partir del mapeo token -> posiciones.

Por qué sigue la idea de Baker:

- abstrae renombrados y cambios de literales
- conserva la estructura sintáctica visible
- compara secuencias tokenizadas en vez de texto crudo
- detecta clones contiguos por coincidencias de substrings en secuencias generalizadas

### 2. LCS en texto plano

- Compara ambos archivos como secuencias de caracteres.
- Usa suffix array + LCP para detectar bloques contiguos comunes.
- La longitud se mide en caracteres.

### 3. difflib tokenizado

- Tokeniza con `tokenize`.
- Compara la secuencia de tokens comparables con `difflib.SequenceMatcher`.
- La longitud se mide en tokens.

### 4. difflib en texto plano

- Compara directamente el texto original con `difflib.SequenceMatcher`.
- La longitud se mide en caracteres.

## Cómo ejecutar

### Windows

#### PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install PySide6
python main.py
```

Si PowerShell bloquea la activación del entorno virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

#### CMD

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install PySide6
python main.py
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install PySide6
python main.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install PySide6
python main.py
```

Si `venv` no está disponible en Linux, instala el paquete correspondiente. En Debian/Ubuntu:

```bash
sudo apt install python3-venv
```

## Uso básico

1. Abre la aplicación.
2. Elige una técnica de comparación.
3. Elige el archivo base.
4. Pulsa `Analizar`.
5. Revisa el ranking de similitud.
6. Haz clic en un archivo del ranking para verlo lado a lado con el archivo base.
7. Observa los fragmentos resaltados y la sección `Detalles`.

## Qué muestra la interfaz

- `Archivo base`: el programa principal que vas a comparar.
- `Archivo comparado`: el archivo seleccionado en el ranking.
- `Ranking de similitud`: lista ordenada del más parecido al menos parecido.
- `Detalles`: técnica usada, porcentaje, bloques detectados y líneas donde aparece cada coincidencia.

## Solución de problemas

- `No se encontraron archivos fuente en la carpeta configurada`
  Verifica que exista `top-20-python` y que contenga archivos `.py`.
- `No module named PySide6`
  Instala la dependencia con `pip install PySide6` dentro del entorno virtual.
- El entorno virtual no activa en Windows
  Usa `activate.bat` en CMD o ajusta la policy temporalmente en PowerShell.
- La ventana no abre en Linux
  Asegúrate de tener entorno gráfico y dependencias de Qt instaladas.
- No aparecen similitudes con técnicas tokenizadas
  Puede deberse al umbral mínimo de coincidencia o a que los archivos son realmente distintos.

## Cómo cerrar el entorno virtual

```text
deactivate
```

## Cómo demostrar en clase que sí se usa el lexer estándar de Python

- Muestra `core/tokenizer.py`.
- Señala que la tokenización se hace con `tokenize.tokenize(stream)`.
- Señala que los tipos de token se leen desde el módulo estándar `token`.
- Explica que no hay lexer manual ni expresiones regulares para la técnica tokenizada; el proyecto delega la separación léxica al lexer oficial de Python.

Fragmento clave:

```python
stream = BytesIO(text.encode("utf-8")).readline
generator = tokenize.tokenize(stream)
```

## Cómo defender la técnica 1 como una variante Baker

- No compara texto crudo, compara secuencias léxicas.
- Generaliza identificadores y literales para ignorar cambios cosméticos.
- Conserva keywords y operadores para retener la forma del algoritmo.
- Usa suffix array y LCP para hallar substrings contiguos comunes largos.
- Reconstruye las coincidencias sobre el código original para explicarlas visualmente.

Esa combinación mantiene el núcleo metodológico de Baker aunque la implementación esté adaptada a Python y a un proyecto académico de escritorio.

## Nota sobre el dataset

La carpeta esperada por defecto es `top-20-python` y la aplicación solo carga archivos `.py`.

## Referencias

- Python Docs, `tokenize`: https://docs.python.org/3/library/tokenize.html
- Python Docs, `token`: https://docs.python.org/3/library/token.html
- Python Docs, `difflib`: https://docs.python.org/3/library/difflib.html
- Brenda S. Baker, *On Finding Duplication and Near-Duplication in Large Software Systems*:
  https://plg.uwaterloo.ca/~migod/846/papers/wcre95-baker.pdf
- U. Manber, G. Myers, *Suffix arrays: A new method for on-line string searches*.
