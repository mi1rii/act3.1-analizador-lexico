# descripcion: carga archivos python desde la carpeta de entrada
# autor: estefania antonio villaseca, miranda eugenia colorado arroniz, alejandro kong montoya, restituto lara larios
# matricula: a01736897, a01737023, a01734271, a01737216
# fecha de modificacion: 2026-04-24

from __future__ import annotations

from pathlib import Path

from models.match_models import SourceFile


DEFAULT_SOURCE_DIR = Path("top-20-python")
PYTHON_EXTENSION = ".py"


# proposito: descubrir y cargar archivos python de la carpeta configurada
# parametros: sourceDir -> carpeta donde se buscan los archivos
# retorno: tupla con lista de archivos cargados y lista de avisos
def discoverSourceFiles(
    sourceDir: Path = DEFAULT_SOURCE_DIR,
) -> tuple[list[SourceFile], list[str]]:
    warnings: list[str] = []
    root = sourceDir.resolve()

    if not root.exists():
        return [], [f"la carpeta de entrada no existe: {root}"]

    visibleFiles = [
        path
        for path in sorted(root.iterdir())
        if path.is_file() and not path.name.startswith(".")
    ]
    pythonFiles = [path for path in visibleFiles if path.suffix.lower() == PYTHON_EXTENSION]

    if not pythonFiles:
        warnings.append(
            "no se encontraron archivos .py en la carpeta de entrada y la aplicacion solo admite programas python"
        )

    sourceFiles: list[SourceFile] = []
    for path in pythonFiles:
        try:
            text = path.read_text(encoding="utf-8")
            sourceFiles.append(SourceFile(path=path, text=text))
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
            sourceFiles.append(
                SourceFile(
                    path=path,
                    text=text,
                    warnings=["el archivo se leyo con latin-1 por problemas de codificacion utf-8"],
                )
            )
        except OSError as error:
            sourceFiles.append(SourceFile(path=path, text="", loadError=str(error)))

    return sourceFiles, warnings
