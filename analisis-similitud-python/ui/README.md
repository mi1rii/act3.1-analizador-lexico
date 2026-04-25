# Carpeta ui

Esta carpeta contiene la interfaz grafica del modulo de similitud en Python.

## Proposito

Mostrar la aplicacion de escritorio, permitir elegir tecnica y archivo base, desplegar el ranking de similitud y resaltar bloques coincidentes en ambos codigos.

## Archivo principal

- `main_window.py`: construye la ventana principal, conecta eventos y pinta el resultado del analisis

## Relacion con el resto del proyecto

La interfaz usa la logica de `core/` para ejecutar comparaciones y los modelos de `models/` para renderizar la informacion de forma consistente.
