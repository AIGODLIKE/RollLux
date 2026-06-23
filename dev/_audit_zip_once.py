import re
import zipfile
from pathlib import Path

ZIP = Path(__file__).resolve().parents[2] / "dist" / "rolllux-5.5.4-marketplace.zip"
z = zipfile.ZipFile(ZIP)
names = sorted(z.namelist())
py_files = [n for n in names if n.endswith(".py")]

print("ZIP", ZIP.name, len(names), "py", len(py_files))
for n in py_files:
    print(" ", n)

props = z.read("properties.py").decode()
ops = z.read("operators.py").decode()
init = z.read("__init__.py").decode()
ga = z.read("gen_assets.py").decode()

print("\nbl_idname rolllux.*:", bool(re.search(r'bl_idname = "rolllux\.', ops)))
print("bl_idname wm.rolllux_*:", len(re.findall(r'bl_idname = "wm\.rolllux_', ops)))
print("auto_timer bl_options:", "bl_options" in ops.split("wm.rolllux_auto_timer")[1][:200])
print("ensure_runtime_hooks:", "ensure_runtime_hooks" in props)
print("register load_post:", "load_post.append" in props.split("def register")[1][:400])
print("optional mcp import:", "mcp_bridge" in init)
print("gen_assets print():", len(re.findall(r"\bprint\s*\(", ga)))
print("gen_assets main() only:", "def main(" in ga and "if __name__" not in ga)

for dead in ("msg_pasted", "mcp_start", '"language"'):
    tr = z.read("translations.py").decode()
    print(f"translations {dead}:", dead in tr)

manifest = z.read("blender_manifest.toml").decode()
print("\nmanifest version:", re.search(r'version = "([^"]+)"', manifest).group(1))
