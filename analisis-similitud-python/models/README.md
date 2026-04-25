# Carpeta models

Esta carpeta guarda las estructuras de datos del modulo de similitud en Python.

## Proposito

Definir objetos simples para representar tokens, bloques coincidentes, resultados de comparacion y datos de resaltado sin mezclar esa informacion con la logica de interfaz o con los algoritmos.

## Archivo principal

- `match_models.py`: contiene las clases y dataclasses que el resto del modulo usa para compartir informacion

## Relacion con el resto del proyecto

`core/` genera estos objetos y `ui/` los consume para mostrar ranking, porcentajes, detalles y bloques resaltados.
