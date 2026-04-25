# Carpeta core

Esta carpeta concentra la logica principal del comparador de similitud para programas Python.

## Proposito

Aqui se resuelven las tareas centrales del modulo:

- cargar archivos fuente
- tokenizar codigo Python
- generalizar tokens para la tecnica inspirada en Baker
- construir suffix array y buscar subcadenas comunes largas
- ejecutar comparaciones con `difflib`
- calcular similitud y preparar rangos para resaltado

## Archivos principales

- `file_loader.py`: carga la carpeta de entrada y valida que solo haya archivos `.py`
- `tokenizer.py`: usa `tokenize` del estandar de Python y conserva posiciones
- `generalizer.py`: transforma identificadores y literales a categorias mas comparables
- `suffix_array.py`: construye suffix array y LCP
- `lcs_matcher.py`: encuentra coincidencias contiguas suficientemente largas
- `difflib_matcher.py`: obtiene bloques coincidentes con `SequenceMatcher`
- `similarity.py`: orquesta las cuatro tecnicas y calcula el porcentaje
- `highlight_mapper.py`: traduce bloques coincidentes a rangos del texto original
- `comparison_engine.py`: conecta la logica de comparacion con la interfaz

## Relacion con el resto del proyecto

`core/` trabaja como el nucleo del modulo `analisis-similitud-python`. La interfaz de `ui/` consume estos archivos y los modelos de `models/` sirven para transportar los resultados de forma ordenada.
