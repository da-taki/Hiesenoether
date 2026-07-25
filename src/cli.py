from __future__ import annotations

import argparse
from pathlib import Path

from src.main import repl
from src.runtime import run_program


def run_file(filepath: str) -> None:
    path = Path(filepath)
    if not path.exists():
        raise SystemExit(f"Error: File '{filepath}' not found")
    source = path.read_text(encoding="utf-8-sig")
    run_program(source)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="hiesenoether",
        description="Run Hiesenoether .hn programs or start the REPL.",
    )
    parser.add_argument("program", nargs="?", help="Path to a Hiesenoether program file")
    parser.add_argument("--repl", action="store_true", help="Start the interactive REPL")
    args = parser.parse_args(argv)

    if args.repl:
        repl()
        return

    if args.program is None:
        parser.error("provide a program path or use --repl")

    run_file(args.program)


if __name__ == "__main__":
    main()
