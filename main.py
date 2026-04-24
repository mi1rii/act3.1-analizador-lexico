# descripcion: punto de entrada de la aplicacion de escritorio
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from ui.main_window import launchApp


# proposito: iniciar la aplicacion
# parametros: ninguno
# retorno: codigo de salida de la aplicacion
def main() -> int:
    return launchApp()


if __name__ == "__main__":
    raise SystemExit(main())
