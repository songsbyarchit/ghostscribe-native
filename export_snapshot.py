import os

IGNORE_FOLDERS = {'.git', '__pycache__', '.venv', 'node_modules', '.idea', '.DS_Store', '.mypy_cache'}
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.html', '.css', '.txt', '.env', '.sh'}

output_file = "project_snapshot.txt"

def should_include(file, path):
    if not any(file.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        return False
    if "typing" in path or "site-packages" in path or "venv" in path:
        return False
    return True

with open(output_file, "w") as out:
    for root, dirs, files in os.walk("."):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]

        level = root.count(os.sep)
        indent = "  " * level
        out.write(f"{indent}{os.path.basename(root)}/\n")

        for file in sorted(files):
            filepath = os.path.join(root, file)
            if file.startswith(".") or not should_include(file, filepath):
                continue

            file_indent = "  " * (level + 1)
            
            if os.path.getsize(filepath) > 100_000:
                out.write(f"{file_indent}{file} [Skipped: too large > 100KB]\n\n")
                continue

            out.write(f"{file_indent}{file}\n")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    out.write(f"{file_indent}--- BEGIN {file} ---\n")
                    for line in content.splitlines():
                        out.write(f"{file_indent}{line}\n")
                    out.write(f"{file_indent}--- END {file} ---\n\n")
            except Exception as e:
                out.write(f"{file_indent}[Could not read file: {e}]\n\n")


print(f"✅ Snapshot saved to {output_file}")