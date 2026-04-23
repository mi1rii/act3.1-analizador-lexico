"""Carga de archivos fuente Python desde una carpeta configurable."""

from __future__ import annotations

from pathlib import Path

from models.match_models import SourceFile


DEFAULT_SOURCE_DIR = Path("top-20-python")
PYTHON_EXTENSION = ".py"


def discover_source_files(
    source_dir: Path = DEFAULT_SOURCE_DIR,
) -> tuple[list[SourceFile], list[str]]:
    """Carga únicamente archivos fuente Python."""

    warnings: list[str] = []
    root = source_dir.resolve()
    if not root.exists():
        return [], [f"La carpeta de entrada no existe: {root}"]

    files = sorted(
        path for path in root.iterdir() if path.is_file() and not path.name.startswith(".")
    )
    selected = [path for path in files if path.suffix.lower() == PYTHON_EXTENSION]

    if not selected:
        warnings.append(
            "No se encontraron archivos .py en la carpeta de entrada. "
            "La aplicación solo admite programas Python."
        )

    loaded: list[SourceFile] = []
    for path in selected:
        try:
            text = path.read_text(encoding="utf-8")
            loaded.append(SourceFile(path=path, text=text))
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
            loaded.append(
                SourceFile(
                    path=path,
                    text=text,
                    warnings=["El archivo se leyó con latin-1 por problemas de codificación UTF-8."],
                )
            )
        except OSError as exc:
            loaded.append(SourceFile(path=path, text="", load_error=str(exc)))

    return loaded, warnings
