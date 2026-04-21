import sys
from pathlib import Path

from lexer import analyze_file, print_tokens


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else "ejemplo1.c"
    filepath = Path(target)

    if not filepath.exists():
        print(f"Error: El archivo '{target}' no existe.")
        return 1

    tokens = analyze_file(str(filepath))
    if not tokens:
        return 1

    print_tokens(tokens)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())