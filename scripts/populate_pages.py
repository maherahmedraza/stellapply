import os

root_dir = "frontend/src/app"
content = """export default function Page() {
  return <div className="p-4">Placeholder Page</div>
}
"""

for dirpath, dirnames, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename == "page.tsx":
            filepath = os.path.join(dirpath, filename)
            if os.path.getsize(filepath) == 0:
                with open(filepath, "w") as f:
                    f.write(content)
                print(f"Populated {filepath}")
