import os
import re
import subprocess


def find_conflicted_files():
    try:
        # Use grep to find files with conflict markers, excluding common non-source dirs
        cmd = [
            "grep",
            "-rl",
            "<<<<<<< HEAD",
            ".",
            "--exclude-dir=.git",
            "--exclude-dir=node_modules",
            "--exclude-dir=venv",
            "--exclude-dir=.next",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip().split("\n")
    except Exception as e:
        print(f"Error finding files: {e}")
        return []


def resolve_file(file_path):
    if file_path == "./scripts/resolve_conflicts.py":
        return

    # special case for lock files, we'll try to pick theirs but they might need regeneration
    # for now we fix markers so they can be parsed

    with open(file_path, "r") as f:
        content = f.read()

    # Pick 'theirs' as it contains the new aesthetic/features
    pattern = re.compile(
        r"<<<<<<< HEAD\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n", re.DOTALL
    )

    new_content = pattern.sub(r"\2\n", content)

    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Resolved: {file_path}")


files = find_conflicted_files()
print(f"Found {len(files)} files to resolve.")
for f in files:
    if f:
        resolve_file(f)
