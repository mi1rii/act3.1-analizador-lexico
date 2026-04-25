# Carpeta top-20-python

Esta carpeta contiene el conjunto de programas Python que se usa como entrada del comparador de similitud.

## Proposito

Servir como dataset base para que la aplicacion:

- cargue automaticamente archivos `.py`
- permita elegir un archivo base
- compare ese archivo contra los demas
- calcule porcentajes y bloques coincidentes

## Contenido

Los archivos de esta carpeta funcionan como ejemplos reales de entrada para las cuatro tecnicas del proyecto.

## Relacion con el resto del proyecto

`core/file_loader.py` lee esta carpeta por defecto y `ui/main_window.py` muestra sus archivos dentro de la aplicacion.
