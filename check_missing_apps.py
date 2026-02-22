import ast
import importlib
import json
import pathlib
import sys


p = pathlib.Path("aiarena/settings/default.py")
if not p.exists():
    print("Could not find aiarena/settings/default.py")
    sys.exit(1)
src = p.read_text()
tree = ast.parse(src)
apps = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if getattr(t, "id", None) == "INSTALLED_APPS":
                for elt in getattr(node.value, "elts", []):
                    if hasattr(elt, "s"):
                        apps.append(elt.s)
                break
missing = []
for app in apps:
    try:
        importlib.import_module(app.split(".")[0])
    except Exception as e:
        missing.append((app, str(e)))
print(json.dumps(missing, indent=2))
