"""Punto de entrada de la aplicación PySide6."""

from __future__ import annotations

import sys

from ui.main_window import launch_app


def main() -> int:
    return launch_app()


if __name__ == "__main__":
    raise SystemExit(main())
