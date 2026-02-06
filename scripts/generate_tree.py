import os
from pathlib import Path


def print_tree(directory, prefix=""):
    print(f"{directory.name}/")
    _print_tree(directory, prefix)


def _print_tree(directory, prefix=""):
    # Get all files and directories
    entries = sorted(
        [
            x
            for x in directory.iterdir()
            if not x.name.startswith((".", "__"))
            and x.name not in {"node_modules", "dist", "build", "venv", "htmlcov"}
        ]
    )

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            _print_tree(entry, prefix + extension)


if __name__ == "__main__":
    root = Path(".")
    print_tree(root)
