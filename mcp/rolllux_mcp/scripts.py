"""Python snippets executed inside Blender via the MCP bridge."""

from __future__ import annotations

import json
from typing import Any


def _json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def check_setup_script() -> str:
    return """
import json
import bpy

out = {
    "blender_version": ".".join(str(v) for v in bpy.app.version),
    "scene": bpy.context.scene.name if bpy.context.scene else None,
    "rolllux_installed": hasattr(bpy.types.Scene, "rolllux"),
    "object_count": len(bpy.context.scene.objects) if bpy.context.scene else 0,
}
print(json.dumps(out))
"""


def list_objects_script(limit: int = 50) -> str:
    return f"""
import json
import bpy

items = []
for obj in bpy.context.scene.objects:
    if obj.type not in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
        continue
    items.append({{
        "name": obj.name,
        "type": obj.type,
        "visible": obj.visible_get(),
    }})
    if len(items) >= {int(limit)}:
        break
print(json.dumps({{"objects": items}}))
"""


def light_object_script(
    object_name: str,
    *,
    reference_path: str | None = None,
    reference_preset: str | None = None,
    preset: str = "auto",
    light_count: int = 3,
    intensity: float = 0.2,
    auto_exposure: bool = True,
    clear_existing: bool = True,
    use_luxpro: bool = True,
) -> str:
    params = {
        "object_name": object_name,
        "reference_path": reference_path,
        "reference_preset": reference_preset,
        "preset": preset,
        "light_count": light_count,
        "intensity": intensity,
        "auto_exposure": auto_exposure,
        "clear_existing": clear_existing,
        "use_luxpro": use_luxpro,
    }
    return f"""
import json
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux extension is not enabled. Install rolllux-5.0.0.zip in Blender Preferences.")

scene = bpy.context.scene
obj = bpy.data.objects.get(PARAMS["object_name"])
if obj is None:
    fail(f"Object not found: {{PARAMS['object_name']}}")
if obj.name not in scene.objects:
    fail(f"Object {{obj.name}} is not in the active scene")

for o in bpy.context.selected_objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

s = scene.rolllux
if PARAMS["clear_existing"]:
    try:
        bpy.ops.rolllux.clear()
    except Exception:
        pass

if PARAMS.get("reference_path"):
    path = PARAMS["reference_path"]
    try:
        img = bpy.data.images.load(path, check_existing=True)
    except RuntimeError as exc:
        fail(f"Could not load reference image: {{exc}}")
    s.reference_image = img
elif PARAMS.get("reference_preset"):
    preset_id = PARAMS["reference_preset"]
    try:
        s.reference_preset = preset_id
    except Exception as exc:
        fail(f"Unknown reference preset {{preset_id}}: {{exc}}")
# else: rolllux.generate() auto-loads a random/default reference when missing

s.lighting_preset = PARAMS["preset"]
s.light_count = max(1, min(8, int(PARAMS["light_count"])))
s.intensity = float(PARAMS["intensity"])
s.use_luxpro = bool(PARAMS["use_luxpro"])
s.auto_exposure = bool(PARAMS["auto_exposure"])
s.target_mode = "SELECTED"

try:
    bpy.ops.rolllux.generate()
except Exception as exc:
    fail(str(exc))

lights = []
coll = bpy.data.collections.get("RollLux")
if coll:
    for lo in coll.objects:
        if lo.type == "LIGHT":
            lights.append(lo.name)

result = scene.rolllux_result
out = {{
    "ok": True,
    "object": obj.name,
    "lights_created": len(lights),
    "light_names": lights,
    "preset": s.lighting_preset,
    "reference": s.reference_image.name if s.reference_image else None,
    "analysis_valid": bool(result.valid),
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
}}
print(json.dumps(out))
"""


def light_selection_script(
    *,
    reference_path: str | None = None,
    reference_preset: str | None = None,
    preset: str = "auto",
    light_count: int = 3,
    intensity: float = 0.2,
    auto_exposure: bool = True,
    clear_existing: bool = True,
    use_luxpro: bool = True,
) -> str:
    params = {
        "reference_path": reference_path,
        "reference_preset": reference_preset,
        "preset": preset,
        "light_count": light_count,
        "intensity": intensity,
        "auto_exposure": auto_exposure,
        "clear_existing": clear_existing,
        "use_luxpro": use_luxpro,
    }
    return f"""
import json
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux extension is not enabled.")

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if not sel:
        fail("No mesh-like object selected. Select a target in the 3D View first.")
    obj = sel[0]
    bpy.context.view_layer.objects.active = obj

if obj.name not in bpy.context.scene.objects:
    fail(f"Object {{obj.name}} is not in the active scene")

s = bpy.context.scene.rolllux
if PARAMS["clear_existing"]:
    try:
        bpy.ops.rolllux.clear()
    except Exception:
        pass

if PARAMS.get("reference_path"):
    img = bpy.data.images.load(PARAMS["reference_path"], check_existing=True)
    s.reference_image = img
elif PARAMS.get("reference_preset"):
    s.reference_preset = PARAMS["reference_preset"]

s.lighting_preset = PARAMS["preset"]
s.light_count = max(1, min(8, int(PARAMS["light_count"])))
s.intensity = float(PARAMS["intensity"])
s.use_luxpro = bool(PARAMS["use_luxpro"])
s.auto_exposure = bool(PARAMS["auto_exposure"])
s.target_mode = "SELECTED"
bpy.ops.rolllux.generate()

lights = []
coll = bpy.data.collections.get("RollLux")
if coll:
    lights = [lo.name for lo in coll.objects if lo.type == "LIGHT"]

result = bpy.context.scene.rolllux_result
print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "lights_created": len(lights),
    "light_names": lights,
    "preset": s.lighting_preset,
    "reference": s.reference_image.name if s.reference_image else None,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
}}))
"""


def _blender_rolllux_import() -> str:
    return "bl_ext.user_default.rolllux"


def light_diagonal_golden_script(
    *,
    intensity: float = 0.55,
    contrast_boost: float = 4.5,
) -> str:
    """Top-left to bottom-right golden light with strong shadows."""
    params = {"intensity": intensity, "contrast_boost": contrast_boost}
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

GOLD = (1.08, 0.76, 0.22)
lin = gen_assets.make_ref(gen_assets.REF_SIZE,
    base=0.012, grad=(0.0, 0.0), tint=(0.55, 0.42, 0.18),
    blobs=[(-0.78, 0.68, 2.6, 1.45, GOLD)], rim=0.0, vignette=0.72)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_tlbr_gold_split.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_TLBR_Gold"
s.reference_image = img
s.reference_preset = "random"
s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.28
s.intensity = PARAMS["intensity"]
s.exposure = 3
s.lighting_preset = "split"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = 2
s.auto_exposure = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if not sel:
        fail("No object selected")
    obj = sel[0]
    bpy.context.view_layer.objects.active = obj

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass
bpy.ops.rolllux.generate()

coll = bpy.data.collections.get("RollLux")
key_obj = fill_obj = None
if coll:
    for lo in coll.objects:
        if lo.type != "LIGHT":
            continue
        if lo.rolllux_light.role == "key":
            key_obj = lo
        elif lo.rolllux_light.role == "fill":
            fill_obj = lo

if key_obj:
    info = key_obj.rolllux_light
    info.direction = (-0.82, 0.72, 0.48)
    info.base_color = GOLD
    info.e0 = max(info.e0, 1.0) * 1.35
    info.softness = 0.14
    key_obj.data.type = "SPOT"
    key_obj.data.spot_size = 0.45
    key_obj.data.spot_blend = 0.08
if fill_obj:
    fill_obj.rolllux_light.enabled = False

lighting.live_update(bpy.context)
result = bpy.context.scene.rolllux_result
print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "luxpro_direction": result.dir_label if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "mood": result.mood if result.valid else "",
    "intensity": s.intensity,
}}))
"""


def light_apple_product_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 1.05,
    light_count: int = 5,
    key_energy: float = 0.12,
    fill_energy: float = 0.10,
    rim_energy: float = 3.6,
    side_rim_energy: float = 3.0,
) -> str:
    """Backlight-first product lighting: strong rear rim strips, weak front/side fill."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "rim_energy": rim_energy,
        "side_rim_energy": side_rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

COOL_WHITE = (0.98, 0.99, 1.02)
RIM_WHITE = (1.08, 1.08, 1.12)
FRONT_HINT = (0.94, 0.95, 0.98)
# Backlight-first reference: dark core, bright rear edge ring, only a hint of front light.
dist_params = dict(
    base=0.05,
    grad=(0.0, -0.06),
    tint=COOL_WHITE,
    blobs=[
        (0.0, 0.18, 0.55, 0.10, FRONT_HINT),
        (-0.72, 0.52, 1.55, 0.58, RIM_WHITE),
        (0.72, 0.52, 1.55, 0.58, RIM_WHITE),
        (0.0, 0.62, 1.40, 0.50, RIM_WHITE),
        (-0.35, 0.45, 1.20, 0.38, RIM_WHITE),
        (0.35, 0.45, 1.20, 0.38, RIM_WHITE),
    ],
    rim=1.55,
    rim_color=RIM_WHITE,
    vignette=0.32,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_backlight_product.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_BacklightProduct"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.92
s.tone_highlights = 1.08
s.color_strength = 0.58
s.color_saturation = 0.88
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 3.0

s.lighting_preset = "backlight"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(3, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_16.002",):
        candidate = bpy.data.objects.get(name)
        if candidate and candidate.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = candidate
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

bpy.ops.rolllux.generate()

BACK_RIM_DIRS = [
    (-0.82, 0.30, -0.82),
    (0.82, 0.30, -0.82),
]

def _back_rim_strip(lo, direction, energy, color=RIM_WHITE):
    info = lo.rolllux_light
    info.enabled = True
    info.direction = direction
    info.base_color = color
    info.e0 = energy
    info.softness = 0.08
    lo.data.type = "AREA"

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    if info.role == "key":
        info.enabled = PARAMS["key_energy"] > 0.01
        info.base_color = FRONT_HINT
        info.direction = (0.0, 0.18, 0.90)
        info.e0 = PARAMS["key_energy"]
        info.softness = 2.8
        lo.data.type = "AREA"
    elif info.role == "fill":
        info.enabled = PARAMS["fill_energy"] > 0.01
        info.base_color = (0.93, 0.94, 0.98)
        info.e0 = PARAMS["fill_energy"]
        info.softness = 3.2
        lo.data.type = "AREA"
    elif info.role == "rim":
        _back_rim_strip(lo, (0.0, 0.42, -1.0), PARAMS["rim_energy"])
    elif info.role == "extra":
        if extra_idx < len(BACK_RIM_DIRS):
            _back_rim_strip(lo, BACK_RIM_DIRS[extra_idx], PARAMS["side_rim_energy"])
        extra_idx += 1
    elif info.role == "sky":
        info.enabled = False

lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    role = lo.rolllux_light.role
    if role not in ("rim", "extra"):
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    ld.size = 0.30
    if hasattr(ld, "size_y"):
        ld.size_y = 3.4 if role == "rim" else 3.0

result = bpy.context.scene.rolllux_result
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "backlight_product",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "backlit": result.backlit if result.valid else False,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "lights": lights,
}}))
"""


def light_xiaomi_product_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 0.78,
    light_count: int = 5,
    key_energy: float = 0.42,
    fill_energy: float = 0.26,
    rim_energy: float = 1.2,
    side_rim_energy: float = 2.0,
) -> str:
    """Xiaomi-style product: high-key white studio, soft front, crisp side edge highlights."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "rim_energy": rim_energy,
        "side_rim_energy": side_rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

NEUTRAL_WHITE = (1.0, 1.0, 1.0)
SOFT_WHITE = (0.97, 0.98, 1.0)
EDGE_WHITE = (1.06, 1.06, 1.10)
# High-key white studio: bright core, soft front, left/right edge gleam.
dist_params = dict(
    base=0.52,
    grad=(0.0, 0.10),
    tint=NEUTRAL_WHITE,
    blobs=[
        (0.0, 0.06, 1.15, 0.92, SOFT_WHITE),
        (-0.78, 0.02, 0.38, 1.05, EDGE_WHITE),
        (0.78, 0.02, 0.38, 1.05, EDGE_WHITE),
        (0.0, 0.58, 1.05, 0.42, NEUTRAL_WHITE),
    ],
    rim=0.28,
    rim_color=EDGE_WHITE,
    vignette=0.04,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_xiaomi_product.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_XiaomiProduct"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.lock_color_strength = True
s.lock_color_saturation = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.72
s.tone_highlights = 1.02
s.color_strength = 0.52
s.color_saturation = 0.82
s.color_strategy = "SOFT"
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 2.8

s.lighting_preset = "product"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(3, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

SIDE_RIM_DIRS = [
    (-0.88, 0.02, -0.42),
    (0.88, 0.02, -0.42),
]

def _side_rim_strip(lo, direction, energy, color=EDGE_WHITE):
    info = lo.rolllux_light
    info.enabled = True
    info.direction = direction
    info.base_color = color
    info.e0 = energy
    info.softness = 0.12
    lo.data.type = "AREA"

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    if info.role == "key":
        info.enabled = PARAMS["key_energy"] > 0.01
        info.base_color = SOFT_WHITE
        info.direction = (0.0, 0.10, 0.92)
        info.e0 = PARAMS["key_energy"]
        info.softness = 2.4
        lo.data.type = "AREA"
    elif info.role == "fill":
        info.enabled = PARAMS["fill_energy"] > 0.01
        info.base_color = NEUTRAL_WHITE
        info.direction = (-0.18, -0.06, 0.84)
        info.e0 = PARAMS["fill_energy"]
        info.softness = 2.8
        lo.data.type = "AREA"
    elif info.role == "rim":
        info.enabled = PARAMS["rim_energy"] > 0.01
        info.base_color = EDGE_WHITE
        info.direction = (0.0, 0.38, -0.90)
        info.e0 = PARAMS["rim_energy"]
        info.softness = 0.35
        lo.data.type = "AREA"
    elif info.role == "extra":
        if extra_idx < len(SIDE_RIM_DIRS):
            _side_rim_strip(lo, SIDE_RIM_DIRS[extra_idx], PARAMS["side_rim_energy"])
        extra_idx += 1
    elif info.role == "accent":
        info.enabled = False
    elif info.role == "sky":
        info.enabled = False

lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.72
        if hasattr(ld, "size_y"):
            ld.size_y = 0.88
    elif role == "fill":
        ld.size = 0.58
        if hasattr(ld, "size_y"):
            ld.size_y = 0.68
    elif role == "rim":
        ld.size = 0.42
        if hasattr(ld, "size_y"):
            ld.size_y = 1.6
    elif role == "extra":
        ld.size = 0.22
        if hasattr(ld, "size_y"):
            ld.size_y = 3.2

result = bpy.context.scene.rolllux_result
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "xiaomi_product",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "backlit": result.backlit if result.valid else False,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "lights": lights,
}}))
"""


def light_clean_tech_product_script(
    *,
    intensity: float = 0.26,
    contrast_boost: float = 0.70,
    light_count: int = 5,
    key_energy: float = 0.46,
    fill_energy: float = 0.24,
    rim_energy: float = 0.95,
    side_rim_energy: float = 1.35,
) -> str:
    """Clean cool tech product: high-key ice-white studio, soft front, crisp cool edge strips."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "rim_energy": rim_energy,
        "side_rim_energy": side_rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

ICE_WHITE = (0.92, 0.96, 1.06)
COOL_FILL = (0.88, 0.93, 1.04)
EDGE_CYAN = (0.78, 0.90, 1.14)
RIM_COOL = (0.82, 0.88, 1.10)

dist_params = dict(
    base=0.50,
    grad=(0.0, 0.08),
    tint=(0.90, 0.94, 1.06),
    blobs=[
        (0.0, 0.08, 1.10, 0.88, ICE_WHITE),
        (0.0, 0.46, 0.82, 0.55, ICE_WHITE),
        (-0.76, 0.04, 0.34, 0.98, EDGE_CYAN),
        (0.76, 0.04, 0.34, 0.98, EDGE_CYAN),
        (0.0, 0.58, 0.95, 0.40, RIM_COOL),
    ],
    rim=0.24,
    rim_color=RIM_COOL,
    vignette=0.03,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_clean_tech_product.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_CleanTech"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.lock_color_strength = True
s.lock_color_saturation = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.68
s.tone_highlights = 1.03
s.color_strength = 0.58
s.color_saturation = 0.78
s.color_strategy = "SOFT"
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 2.6

s.lighting_preset = "product"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(3, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

SIDE_RIM_DIRS = [
    (-0.84, 0.04, -0.40),
    (0.84, 0.04, -0.40),
]

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    if role == "key":
        info.enabled = True
        info.base_color = ICE_WHITE
        info.direction = (0.0, 0.10, 0.90)
        info.e0 = PARAMS["key_energy"]
        info.softness = 2.2
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = PARAMS["fill_energy"] > 0.01
        info.base_color = COOL_FILL
        info.direction = (-0.20, -0.16, 0.82)
        info.e0 = PARAMS["fill_energy"]
        info.softness = 2.6
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = PARAMS["rim_energy"] > 0.01
        info.base_color = RIM_COOL
        info.direction = (0.0, 0.36, -0.88)
        info.e0 = PARAMS["rim_energy"]
        info.softness = 0.28
        lo.data.type = "AREA"
    elif role == "extra":
        if extra_idx < len(SIDE_RIM_DIRS):
            info.enabled = True
            info.base_color = EDGE_CYAN
            info.direction = SIDE_RIM_DIRS[extra_idx]
            info.e0 = PARAMS["side_rim_energy"]
            info.softness = 0.14
            lo.data.type = "AREA"
        else:
            info.enabled = False
        extra_idx += 1
    elif role == "accent":
        info.enabled = False
    elif role == "sky":
        info.enabled = False

lighting.live_update(bpy.context)

extra_size_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.68
        if hasattr(ld, "size_y"):
            ld.size_y = 0.82
    elif role == "fill":
        ld.size = 0.52
        if hasattr(ld, "size_y"):
            ld.size_y = 0.62
    elif role == "rim":
        ld.size = 0.36
        if hasattr(ld, "size_y"):
            ld.size_y = 1.5
    elif role == "extra":
        ld.size = 0.18
        if hasattr(ld, "size_y"):
            ld.size_y = 2.8
        extra_size_idx += 1

result = bpy.context.scene.rolllux_result
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "clean_tech_product",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "backlit": result.backlit if result.valid else False,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "lights": lights,
}}))
"""


def light_tang_dynasty_product_script(
    *,
    intensity: float = 0.24,
    contrast_boost: float = 1.28,
    light_count: int = 5,
    key_energy: float = 0.88,
    fill_energy: float = 0.30,
    accent_energy: float = 0.72,
    rim_energy: float = 1.45,
    silk_glow_energy: float = 0.55,
) -> str:
    """Tang dynasty product mood: imperial gold key, vermillion accent, warm lantern fill."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
        "silk_glow_energy": silk_glow_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

GOLD = (1.2, 0.82, 0.30)
VERMILLION = (1.3, 0.08, 0.06)
AMBER = (1.0, 0.58, 0.20)
SILK = (1.0, 0.86, 0.58)
DEEP_GOLD = (0.88, 0.52, 0.16)

dist_params = dict(
    base=0.03,
    grad=(0.0, 0.14),
    tint=(0.55, 0.40, 0.28),
    blobs=[
        (-0.58, 0.24, 1.55, 1.15, GOLD),
        (0.62, 0.18, 1.75, 1.45, VERMILLION),
        (0.0, -0.30, 1.10, 0.75, AMBER),
        (0.0, 0.52, 0.92, 0.55, DEEP_GOLD),
        (-0.32, 0.42, 0.75, 0.45, SILK),
    ],
    rim=0.45,
    rim_color=DEEP_GOLD,
    vignette=0.28,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_tang_dynasty_product.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_TangDynasty"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.46
    s.tone_highlights = 1.10
    s.color_strength = 1.12
    s.color_saturation = 1.18
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.5

    s.lighting_preset = "rembrandt"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [tuple(item.color) for item in result.sampled_colors]

EXTRA_DIRS = [
    (-0.78, 0.34, -0.52),
    (0.64, 0.16, 0.62),
]
EXTRA_ENERGIES = [
    PARAMS["silk_glow_energy"],
    PARAMS["accent_energy"],
]
_role_energy = {{
    "key": PARAMS["key_energy"],
    "fill": PARAMS["fill_energy"],
    "accent": PARAMS["accent_energy"],
    "rim": PARAMS["rim_energy"],
}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    if role in _role_energy:
        info.gain = float(_role_energy[role])
        info.e0 = 1.0
    if role == "key":
        info.direction = (-0.60, 0.22, 0.78)
        info.softness = 0.55
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = PARAMS["fill_energy"] > 0.01
        info.direction = (0.12, -0.28, 0.76)
        info.softness = 2.4
        lo.data.type = "AREA"
    elif role == "accent":
        info.direction = (0.64, 0.16, 0.62)
        info.softness = 0.48
        lo.data.type = "AREA"
    elif role == "rim":
        info.direction = (0.0, 0.36, -0.88)
        info.softness = 0.22
        lo.data.type = "AREA"
    elif role == "extra":
        if extra_idx < len(EXTRA_DIRS):
            info.enabled = EXTRA_ENERGIES[extra_idx] > 0.01
            info.gain = float(EXTRA_ENERGIES[extra_idx])
            info.e0 = 1.0
            info.direction = EXTRA_DIRS[extra_idx]
            info.softness = 1.6 if extra_idx == 0 else 0.48
            lo.data.type = "AREA"
        else:
            info.enabled = False
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.42
        if hasattr(ld, "size_y"):
            ld.size_y = 0.78
    elif role == "fill":
        ld.size = 0.62
        if hasattr(ld, "size_y"):
            ld.size_y = 0.55
    elif role == "accent":
        ld.size = 0.34
        if hasattr(ld, "size_y"):
            ld.size_y = 1.8
    elif role == "rim":
        ld.size = 0.30
        if hasattr(ld, "size_y"):
            ld.size_y = 1.7
    elif role == "extra":
        ld.size = 0.48 if lo.rolllux_light.base_color[1] > 0.7 else 0.34
        if hasattr(ld, "size_y"):
            ld.size_y = 1.2 if lo.rolllux_light.base_color[1] > 0.7 else 1.8

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "tang_dynasty_product",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "backlit": result.backlit if result.valid else False,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_xuanniao_black_amber_script(
    *,
    intensity: float = 0.18,
    contrast_boost: float = 4.2,
    light_count: int = 4,
    key_energy: float = 1.35,
    accent_energy: float = 1.05,
    rim_energy: float = 0.42,
    edge_kick_energy: float = 0.78,
) -> str:
    """Xuan-bird black stage with sharp orange-yellow highlights and strong contrast."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
        "edge_kick_energy": edge_kick_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

XUAN_BLACK = (0.04, 0.045, 0.07)
AMBER = (1.42, 0.70, 0.04)
GOLD = (1.28, 0.88, 0.10)
DEEP_EDGE = (1.02, 0.48, 0.02)
REF_COLORS = [AMBER, GOLD, DEEP_EDGE, AMBER]

dist_params = dict(
    base=0.005,
    grad=(0.0, 0.06),
    tint=XUAN_BLACK,
    blobs=[
        (0.62, 0.16, 2.35, 1.82, AMBER),
        (0.42, 0.46, 1.75, 1.08, GOLD),
        (-0.70, 0.10, 1.35, 0.42, DEEP_EDGE),
    ],
    vignette=0.68,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_xuanniao_black_amber.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_XuanBirdBlackAmber"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.16
    s.tone_highlights = 1.22
    s.color_strength = 1.35
    s.color_saturation = 1.42
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 0
    s.distance = 2.55

    s.lighting_preset = "low_key"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_03.002",):
        o = bpy.data.objects.get(name)
        if o and o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = o
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [
    analysis_mod.apply_color_strategy(c, "VIVID")
    for c in REF_COLORS[:s.light_count]
]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["key_energy"],
    "accent": PARAMS["accent_energy"],
    "rim": PARAMS["rim_energy"],
}}
_role_dir = {{
    "key": (0.68, 0.14, 0.72),
    "accent": (0.18, 0.62, 0.66),
    "rim": (-0.08, 0.28, -0.92),
}}
_role_soft = {{
    "key": 0.18,
    "accent": 0.14,
    "rim": 0.22,
}}
_color_idx = {{"key": 0, "fill": 0, "accent": 1, "rim": 2, "extra": 3, "sky": 3}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 3 if extra_idx == 0 else 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else AMBER
    if role == "key":
        info.enabled = True
        info.base_color = pal_color
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.0
        info.softness = _role_soft["key"]
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = False
    elif role == "accent":
        info.enabled = True
        info.base_color = palette[1] if len(palette) > 1 else GOLD
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.0
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = PARAMS["rim_energy"] > 0.01
        info.base_color = palette[2] if len(palette) > 2 else DEEP_EDGE
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.0
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1 and PARAMS["edge_kick_energy"] > 0.01
        if info.enabled:
            info.base_color = palette[3] if len(palette) > 3 else AMBER
            info.direction = (-0.76, 0.08, 0.58)
            info.gain = float(PARAMS["edge_kick_energy"])
            info.e0 = 1.0
            info.softness = 0.12
            lo.data.type = "AREA"
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.26
        if hasattr(ld, "size_y"):
            ld.size_y = 0.42
    elif role == "accent":
        ld.size = 0.22
        if hasattr(ld, "size_y"):
            ld.size_y = 0.36
    elif role == "rim":
        ld.size = 0.24
        if hasattr(ld, "size_y"):
            ld.size_y = 1.6
    elif role == "extra":
        ld.size = 0.18
        if hasattr(ld, "size_y"):
            ld.size_y = 1.4

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "xuanniao_black_amber",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_black_red_even_script(
    *,
    intensity: float = 0.26,
    contrast_boost: float = 0.88,
    light_count: int = 4,
    key_energy: float = 0.90,
    fill_energy: float = 0.92,
    accent_energy: float = 0.86,
    rim_energy: float = 0.80,
) -> str:
    """Black-red even lighting: dark base, balanced soft red wrap from multiple directions."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

BLACK = (0.035, 0.03, 0.045)
CRIMSON = (1.28, 0.08, 0.08)
DEEP_RED = (1.12, 0.05, 0.06)
SOFT_RED = (1.02, 0.16, 0.14)
CORE_RED = (1.22, 0.10, 0.09)
REF_COLORS = [CRIMSON, DEEP_RED, SOFT_RED, CORE_RED]

dist_params = dict(
    base=0.018,
    grad=(0.0, 0.06),
    tint=BLACK,
    blobs=[
        (-0.56, 0.10, 0.95, 0.82, CRIMSON),
        (0.56, 0.10, 0.95, 0.82, CRIMSON),
        (0.0, 0.42, 0.88, 0.78, DEEP_RED),
        (0.0, -0.32, 0.88, 0.74, DEEP_RED),
        (0.0, 0.02, 0.75, 0.52, SOFT_RED),
    ],
    vignette=0.32,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_black_red_even.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_BlackRedEven"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.48
    s.tone_highlights = 1.04
    s.color_strength = 1.22
    s.color_saturation = 1.28
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 0
    s.distance = 2.65

    s.lighting_preset = "soft_even"
    s.mode = "SCENE"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_03.002",):
        o = bpy.data.objects.get(name)
        if o and o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = o
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [
    analysis_mod.apply_color_strategy(c, "VIVID")
    for c in REF_COLORS[:s.light_count]
]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["key_energy"],
    "fill": PARAMS["fill_energy"],
    "accent": PARAMS["accent_energy"],
    "rim": PARAMS["rim_energy"],
}}
_role_dir = {{
    "key": (0.12, 0.08, 0.88),
    "fill": (-0.10, 0.06, 0.86),
    "accent": (0.58, 0.12, 0.62),
    "rim": (-0.58, 0.10, 0.62),
}}
_role_soft = {{
    "key": 2.8,
    "fill": 3.2,
    "accent": 2.6,
    "rim": 2.4,
}}
_color_idx = {{"key": 0, "fill": 1, "accent": 2, "rim": 3, "extra": 1, "sky": 2}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 1 if extra_idx == 0 else 2
        extra_idx += 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else CRIMSON
    if role in _role_energy:
        info.enabled = True
        info.base_color = pal_color
        info.direction = _role_dir.get(role, (0.0, 0.1, 0.9))
        info.gain = float(_role_energy[role])
        info.e0 = 1.0
        info.softness = _role_soft.get(role, 2.8)
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1
        if info.enabled:
            info.base_color = palette[min(idx, len(palette) - 1)]
            info.direction = (0.0, 0.52, 0.58)
            info.gain = float(PARAMS["accent_energy"])
            info.e0 = 1.0
            info.softness = 2.5
            lo.data.type = "AREA"
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    ld.size = 0.72
    if hasattr(ld, "size_y"):
        ld.size_y = 0.68 if role in ("key", "fill") else 0.58

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "black_red_even",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_wuwei_july_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 2.85,
    light_count: int = 4,
    sun_energy: float = 1.18,
    sky_fill_energy: float = 0.38,
    ground_bounce_energy: float = 0.48,
    rim_energy: float = 0.58,
) -> str:
    """Wuwei July: blazing Hexi Corridor midsummer sun, dry sky, loess ground bounce."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "sun_energy": sun_energy,
        "sky_fill_energy": sky_fill_energy,
        "ground_bounce_energy": ground_bounce_energy,
        "rim_energy": rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

SUN = (1.38, 1.12, 0.78)
SKY = (0.58, 0.74, 1.05)
LOESS = (1.08, 0.86, 0.48)
Haze = (0.95, 0.88, 0.72)
REF_COLORS = [SUN, SKY, LOESS, SUN]

dist_params = dict(
    base=0.20,
    grad=(0.12, 0.52),
    tint=Haze,
    blobs=[
        (0.10, 0.70, 2.85, 1.48, SUN),
        (-0.58, 0.34, 1.55, 0.78, SUN),
        (0.0, -0.52, 1.05, 0.68, LOESS),
        (0.0, 0.80, 0.82, 0.36, SKY),
    ],
    vignette=0.16,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_wuwei_july.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_WuweiJuly"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.52
    s.tone_highlights = 1.12
    s.color_strength = 1.08
    s.color_saturation = 1.12
    s.color_strategy = "DEFAULT"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 3.05

    s.lighting_preset = "outdoor"
    s.mode = "SCENE"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_03.002",):
        o = bpy.data.objects.get(name)
        if o and o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = o
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [
    analysis_mod.apply_color_strategy(c, s.color_strategy)
    for c in REF_COLORS[:s.light_count]
]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["sun_energy"],
    "fill": PARAMS["sky_fill_energy"],
    "accent": PARAMS["ground_bounce_energy"],
    "rim": PARAMS["rim_energy"],
}}
_role_dir = {{
    "key": (0.38, 0.58, 0.66),
    "fill": (0.0, 0.78, 0.52),
    "accent": (0.0, -0.44, 0.70),
    "rim": (0.72, 0.28, 0.56),
}}
_role_soft = {{
    "key": 0.12,
    "fill": 2.4,
    "accent": 2.8,
    "rim": 0.18,
}}
_color_idx = {{"key": 0, "fill": 1, "accent": 2, "rim": 0, "extra": 1, "sky": 1}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 1 if extra_idx == 0 else 2
        extra_idx += 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else SUN
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else SUN
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.0
        info.softness = _role_soft["key"]
        lo.data.type = "SUN"
    elif role == "fill":
        info.enabled = PARAMS["sky_fill_energy"] > 0.01
        info.base_color = palette[1] if len(palette) > 1 else SKY
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 1.0
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = PARAMS["ground_bounce_energy"] > 0.01
        info.base_color = palette[2] if len(palette) > 2 else LOESS
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.0
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = PARAMS["rim_energy"] > 0.01
        info.base_color = palette[0] if palette else SUN
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.0
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1 and PARAMS["sky_fill_energy"] > 0.01
        if info.enabled:
            info.base_color = palette[1] if len(palette) > 1 else SKY
            info.direction = (0.0, 0.62, 0.68)
            info.gain = float(PARAMS["sky_fill_energy"] * 0.85)
            info.e0 = 1.0
            info.softness = 2.2
            lo.data.type = "AREA"
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    ld = lo.data
    if role == "key" and ld.type == "SUN":
        if hasattr(ld, "angle"):
            ld.angle = 0.045
        continue
    if ld.type != "AREA":
        lo.data.type = "AREA"
        ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "fill":
        ld.size = 1.05
        if hasattr(ld, "size_y"):
            ld.size_y = 0.55
    elif role == "accent":
        ld.size = 0.82
        if hasattr(ld, "size_y"):
            ld.size_y = 0.48
    elif role == "rim":
        ld.size = 0.34
        if hasattr(ld, "size_y"):
            ld.size_y = 1.6
    elif role == "extra":
        ld.size = 0.75
        if hasattr(ld, "size_y"):
            ld.size_y = 0.62

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "wuwei_july",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_russian_style_script(
    *,
    intensity: float = 0.24,
    contrast_boost: float = 1.38,
    light_count: int = 4,
    sun_energy: float = 0.82,
    snow_fill_energy: float = 0.68,
    sky_energy: float = 0.52,
    warm_accent_energy: float = 0.42,
) -> str:
    """Russian winter light: low pale sun, icy sky, snow bounce, faint warm accent."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "sun_energy": sun_energy,
        "snow_fill_energy": snow_fill_energy,
        "sky_energy": sky_energy,
        "warm_accent_energy": warm_accent_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

WINTER_SUN = (0.94, 0.96, 1.0)
SKY_ICE = (0.52, 0.66, 0.86)
SNOW_BOUNCE = (0.80, 0.84, 0.96)
GOLD_GLOW = (1.0, 0.82, 0.48)
REF_COLORS = [WINTER_SUN, SKY_ICE, SNOW_BOUNCE, GOLD_GLOW]

dist_params = dict(
    base=0.12,
    grad=(0.0, 0.32),
    tint=SKY_ICE,
    blobs=[
        (-0.52, -0.02, 1.35, 0.92, WINTER_SUN),
        (0.0, 0.28, 0.88, 0.50, SKY_ICE),
        (0.0, -0.46, 1.05, 0.74, SNOW_BOUNCE),
        (0.48, 0.06, 1.25, 0.44, GOLD_GLOW),
    ],
    vignette=0.24,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_russian_style.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_RussianStyle"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.56
    s.tone_highlights = 1.02
    s.color_strength = 0.92
    s.color_saturation = 0.88
    s.color_strategy = "SOFT"
    s.intensity = PARAMS["intensity"]
    s.exposure = 0
    s.distance = 2.85

    s.lighting_preset = "twilight"
    s.mode = "SCENE"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_03.002",):
        o = bpy.data.objects.get(name)
        if o and o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = o
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [
    analysis_mod.apply_color_strategy(c, s.color_strategy)
    for c in REF_COLORS[:s.light_count]
]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["sun_energy"],
    "fill": PARAMS["snow_fill_energy"],
    "accent": PARAMS["warm_accent_energy"],
    "rim": PARAMS["sky_energy"],
}}
_role_dir = {{
    "key": (-0.62, -0.06, 0.74),
    "fill": (0.0, -0.40, 0.78),
    "accent": (0.58, 0.08, 0.66),
    "rim": (0.0, 0.62, 0.58),
}}
_role_soft = {{
    "key": 1.05,
    "fill": 3.0,
    "accent": 0.85,
    "rim": 2.2,
}}
_color_idx = {{"key": 0, "fill": 2, "accent": 3, "rim": 1, "extra": 1, "sky": 1}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 1 if extra_idx == 0 else 3
        extra_idx += 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else WINTER_SUN
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else WINTER_SUN
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.0
        info.softness = _role_soft["key"]
        lo.data.type = "SUN"
    elif role == "fill":
        info.enabled = PARAMS["snow_fill_energy"] > 0.01
        info.base_color = palette[2] if len(palette) > 2 else SNOW_BOUNCE
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 1.0
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = PARAMS["warm_accent_energy"] > 0.01
        info.base_color = palette[3] if len(palette) > 3 else GOLD_GLOW
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.0
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = PARAMS["sky_energy"] > 0.01
        info.base_color = palette[1] if len(palette) > 1 else SKY_ICE
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.0
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1 and PARAMS["sky_energy"] > 0.01
        if info.enabled:
            info.base_color = palette[1] if len(palette) > 1 else SKY_ICE
            info.direction = (0.0, 0.48, 0.72)
            info.gain = float(PARAMS["sky_energy"] * 0.75)
            info.e0 = 1.0
            info.softness = 2.0
            lo.data.type = "AREA"
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    ld = lo.data
    if role == "key" and ld.type == "SUN":
        if hasattr(ld, "angle"):
            ld.angle = 0.12
        continue
    if ld.type != "AREA":
        lo.data.type = "AREA"
        ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "fill":
        ld.size = 0.95
        if hasattr(ld, "size_y"):
            ld.size_y = 0.52
    elif role == "accent":
        ld.size = 0.28
        if hasattr(ld, "size_y"):
            ld.size_y = 1.4
    elif role == "rim":
        ld.size = 0.88
        if hasattr(ld, "size_y"):
            ld.size_y = 0.48
    elif role == "extra":
        ld.size = 0.72
        if hasattr(ld, "size_y"):
            ld.size_y = 0.55

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "russian_winter",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_keynote_launch_script(
    *,
    intensity: float = 0.25,
    contrast_boost: float = 2.0,
    light_count: int = 6,
    key_energy: float = 1.15,
    fill_energy: float = 0.10,
    accent_energy: float = 1.05,
    rim_energy: float = 2.6,
    side_beam_energy: float = 2.1,
    top_beam_energy: float = 1.85,
) -> str:
    """Dramatic launch keynote: dark stage, hero spotlight, warm/cool accents, layered rims."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
        "side_beam_energy": side_beam_energy,
        "top_beam_energy": top_beam_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

SPOT_WHITE = (1.08, 1.04, 0.98)
ORANGE = (1.35, 0.48, 0.04)
CYAN = (0.12, 0.78, 1.18)
RIM_COOL = (0.82, 0.88, 1.22)
FLOOR_WARM = (1.05, 0.55, 0.18)
REF_KEY = SPOT_WHITE
REF_ACCENT = ORANGE
REF_RIM = CYAN

dist_params = dict(
    base=0.05,
    grad=(0.0, 0.20),
    tint=(0.82, 0.86, 1.02),
    blobs=[
        (0.0, 0.10, 0.92, 0.58, SPOT_WHITE),
        (-0.64, 0.20, 1.65, 0.92, ORANGE),
        (0.64, 0.20, 1.65, 0.92, CYAN),
        (0.0, 0.58, 1.30, 0.52, RIM_COOL),
        (-0.38, -0.28, 1.05, 0.42, FLOOR_WARM),
        (0.38, -0.22, 0.88, 0.38, CYAN),
    ],
    rim=1.42,
    rim_color=RIM_COOL,
    vignette=0.74,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_keynote_launch.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_KeynoteLaunch"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.lock_color_strength = True
s.lock_color_saturation = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.30
s.tone_highlights = 1.16
s.color_strength = 1.45
s.color_saturation = 1.55
s.color_strategy = "VIVID"
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 2.7

s.lighting_preset = "cinematic"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(4, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [tuple(item.color) for item in result.sampled_colors]

analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])
try:
    rgb = analysis_mod.image_to_rgb(s.reference_image)
    profile = analysis_mod.analyze_rgb(
        rgb, mode=s.mode, luxpro=s.use_luxpro,
        palette_size=s.light_count, color_strategy=s.color_strategy,
    )
    if hasattr(analysis_mod, "rig_colors_in_order"):
        palette = analysis_mod.rig_colors_in_order(profile, s.light_count)
except Exception:
    pass

def _looks_flat_neutral(colors):
    if len(colors) < 2:
        return True
    span = 0.0
    for c in colors[:3]:
        span = max(span, max(c) - min(c))
    return span < 0.12

if not palette or _looks_flat_neutral(palette):
    palette = [REF_KEY, REF_ACCENT, REF_RIM, RIM_COOL, ORANGE, CYAN]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

def _color_for_role(role, fallback_index):
    role_idx = {{"key": 0, "fill": 0, "accent": 1, "rim": 2, "sky": 3, "extra": 3}}
    idx = role_idx.get(role, fallback_index)
    if idx < len(palette):
        return palette[idx]
    if palette:
        return palette[min(idx, len(palette) - 1)]
    return REF_KEY

EXTRA_DIRS = [
    (0.84, 0.08, -0.46),
    (0.0, 0.62, -0.80),
]
EXTRA_ENERGIES = [
    PARAMS["side_beam_energy"],
    PARAMS["top_beam_energy"],
]

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    pal_color = _color_for_role(role, extra_idx)
    if role == "key":
        info.enabled = True
        info.base_color = SPOT_WHITE
        info.direction = (0.0, 0.14, 0.88)
        info.e0 = PARAMS["key_energy"]
        info.softness = 0.32
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = PARAMS["fill_energy"] > 0.01
        info.base_color = FLOOR_WARM
        info.direction = (0.0, -0.44, 0.70)
        info.e0 = PARAMS["fill_energy"]
        info.softness = 3.0
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = ORANGE
        info.direction = (-0.74, 0.16, 0.60)
        info.e0 = PARAMS["accent_energy"]
        info.softness = 0.22
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = True
        info.base_color = RIM_COOL
        info.direction = (0.0, 0.34, -0.92)
        info.e0 = PARAMS["rim_energy"]
        info.softness = 0.18
        lo.data.type = "AREA"
    elif role == "extra":
        if extra_idx < len(EXTRA_DIRS):
            info.enabled = True
            info.base_color = CYAN if extra_idx == 0 else RIM_COOL
            info.direction = EXTRA_DIRS[extra_idx]
            info.e0 = EXTRA_ENERGIES[extra_idx]
            info.softness = 0.10
            lo.data.type = "AREA"
        else:
            info.enabled = False
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

lighting.live_update(bpy.context)

extra_size_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.36
        if hasattr(ld, "size_y"):
            ld.size_y = 0.50
    elif role == "fill":
        ld.size = 0.95
        if hasattr(ld, "size_y"):
            ld.size_y = 0.55
    elif role == "accent":
        ld.size = 0.28
        if hasattr(ld, "size_y"):
            ld.size_y = 2.4
    elif role == "rim":
        ld.size = 0.34
        if hasattr(ld, "size_y"):
            ld.size_y = 2.8
    elif role == "extra":
        ld.size = 0.20
        if hasattr(ld, "size_y"):
            ld.size_y = 3.6 if extra_size_idx >= 1 else 3.2
        extra_size_idx += 1

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "keynote_launch",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "backlit": result.backlit if result.valid else False,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_cyberpunk_script(
    *,
    intensity: float = 0.26,
    contrast_boost: float = 2.5,
    light_count: int = 3,
) -> str:
    """Cyberpunk neon: magenta vs orange-yellow clash, high saturation, 2 active lights."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

MAGENTA = (1.50, 0.0, 1.20)
ORANGE = (1.42, 0.68, 0.02)
REF_KEY = (1.0, 0.0, 1.0)
REF_ACCENT = (1.0, 0.65, 0.0)
dist_params = dict(
    base=0.008,
    grad=(0.0, 0.0),
    tint=(1.0, 1.0, 1.0),
    blobs=[
        (-0.58, 0.16, 1.70, 1.55, MAGENTA),
        (0.60, 0.14, 1.60, 1.45, ORANGE),
    ],
    vignette=0.55,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_cyberpunk_v51.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_Cyberpunk"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.lock_color_strength = True
s.lock_color_saturation = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.42
s.tone_highlights = 1.08
s.color_strength = 2.0
s.color_saturation = 2.0
s.color_strategy = "VIVID"
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 2.6

s.lighting_preset = "auto"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(3, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [tuple(item.color) for item in result.sampled_colors]

analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])
try:
    rgb = analysis_mod.image_to_rgb(s.reference_image)
    profile = analysis_mod.analyze_rgb(
        rgb, mode=s.mode, luxpro=s.use_luxpro,
        palette_size=s.light_count, color_strategy=s.color_strategy,
    )
    if hasattr(analysis_mod, "rig_colors_in_order"):
        palette = analysis_mod.rig_colors_in_order(profile, s.light_count)
except Exception:
    pass

def _looks_all_cool(colors):
    if len(colors) < 2:
        return False
    cool = 0
    for c in colors[:2]:
        if c[2] >= c[0] and c[2] >= c[1] - 0.05:
            cool += 1
    return cool >= 2

if not palette or _looks_all_cool(palette):
    palette = [REF_KEY, REF_ACCENT, REF_ACCENT]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

def _color_for_role(role, fallback_index):
    role_idx = {{"key": 0, "fill": 1, "accent": 1, "rim": 2, "sky": 2}}
    idx = role_idx.get(role, fallback_index)
    if idx < len(palette):
        return palette[idx]
    if palette:
        return palette[min(idx, len(palette) - 1)]
    return (1.0, 1.0, 1.0)

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    pal_color = _color_for_role(role, extra_idx)
    if role == "key":
        info.enabled = True
        info.base_color = pal_color
        info.direction = (-0.68, 0.18, 0.78)
        info.e0 = 1.25
        info.softness = 0.68
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = pal_color
        info.direction = (0.68, 0.16, 0.80)
        info.e0 = 1.30
        info.softness = 0.70
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = False
    else:
        info.enabled = False
    if role == "extra":
        extra_idx += 1

lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if role not in ("key", "accent"):
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.34
        if hasattr(ld, "size_y"):
            ld.size_y = 2.0
    elif role == "accent":
        ld.size = 0.30
        if hasattr(ld, "size_y"):
            ld.size_y = 2.1

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "cyberpunk_magenta_orange",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_jinx_script(
    *,
    intensity: float = 0.24,
    contrast_boost: float = 2.85,
    light_count: int = 4,
    pink_energy: float = 1.32,
    cyan_energy: float = 1.28,
    violet_energy: float = 0.42,
    spark_energy: float = 0.68,
) -> str:
    """Arcane Jinx: chaotic hot-pink vs electric cyan neon clash on a dark base."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "pink_energy": pink_energy,
        "cyan_energy": cyan_energy,
        "violet_energy": violet_energy,
        "spark_energy": spark_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

JINX_PINK = (1.48, 0.06, 0.82)
JINX_CYAN = (0.06, 0.94, 1.38)
JINX_VIOLET = (0.28, 0.08, 0.52)
JINX_SPARK = (0.92, 1.02, 0.18)
REF_COLORS = [JINX_PINK, JINX_CYAN, JINX_VIOLET, JINX_SPARK]

dist_params = dict(
    base=0.012,
    grad=(0.0, 0.0),
    tint=(0.72, 0.58, 1.05),
    blobs=[
        (-0.62, 0.18, 1.75, 1.58, JINX_PINK),
        (0.64, 0.14, 1.68, 1.52, JINX_CYAN),
        (0.08, -0.22, 1.12, 0.95, JINX_VIOLET),
        (-0.38, 0.52, 0.78, 0.62, JINX_SPARK),
    ],
    vignette=0.62,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_jinx.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_Jinx"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.34
    s.tone_highlights = 1.12
    s.color_strength = 2.15
    s.color_saturation = 2.25
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.45

    s.lighting_preset = "auto"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [analysis_mod.apply_color_strategy(c, "VIVID") for c in REF_COLORS[:s.light_count]]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["pink_energy"],
    "fill": PARAMS["violet_energy"],
    "accent": PARAMS["cyan_energy"],
    "rim": PARAMS["spark_energy"],
    "sky": PARAMS["violet_energy"] * 0.5,
}}
_role_dir = {{
    "key": (-0.70, 0.20, 0.78),
    "fill": (0.08, -0.12, 0.82),
    "accent": (0.72, 0.18, 0.80),
    "rim": (-0.42, 0.46, -0.74),
    "sky": (0.0, 0.62, 0.55),
}}
_role_soft = {{
    "key": 0.62,
    "fill": 2.8,
    "accent": 0.66,
    "rim": 1.8,
    "sky": 3.2,
}}
_color_idx = {{"key": 0, "fill": 2, "accent": 1, "rim": 3, "extra": 3, "sky": 2}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 3 if extra_idx == 0 else 1
        extra_idx += 1
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else JINX_PINK
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.28
        info.softness = _role_soft["key"]
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = PARAMS["violet_energy"] > 0.05
        info.base_color = palette[2] if len(palette) > 2 else JINX_VIOLET
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 0.55
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = palette[1] if len(palette) > 1 else JINX_CYAN
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.34
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = PARAMS["spark_energy"] > 0.05
        info.base_color = palette[3] if len(palette) > 3 else JINX_SPARK
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 0.95
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "sky":
        info.enabled = False
    elif role == "extra":
        info.enabled = extra_idx <= 1
        if info.enabled:
            info.base_color = palette[min(idx, len(palette) - 1)]
            info.direction = (0.52, 0.38, -0.68)
            info.gain = float(PARAMS["spark_energy"] * 0.75)
            info.e0 = 0.88
            info.softness = 1.6
            lo.data.type = "AREA"
        extra_idx += 1

for lo in (coll.objects if coll else []):
    if lo.type == "LIGHT":
        lo.rolllux_light.is_sun = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if role not in ("key", "accent", "rim"):
        if role == "fill" and lo.rolllux_light.gain > 0.1:
            pass
        else:
            continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role in ("key", "accent"):
        ld.size = 0.32
        if hasattr(ld, "size_y"):
            ld.size_y = 2.05
    elif role == "rim":
        ld.size = 0.28
        if hasattr(ld, "size_y"):
            ld.size_y = 1.6
    elif role == "fill":
        ld.size = 1.1
        if hasattr(ld, "size_y"):
            ld.size_y = 1.1

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "jinx",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_arcane_script(
    *,
    intensity: float = 0.22,
    contrast_boost: float = 2.15,
    light_count: int = 4,
    amber_energy: float = 1.05,
    teal_energy: float = 0.68,
    magenta_energy: float = 0.72,
    rim_energy: float = 0.92,
) -> str:
    """Arcane (双城之战) painterly cinematic: teal undercity haze, amber key, magenta accent, orange rim."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "amber_energy": amber_energy,
        "teal_energy": teal_energy,
        "magenta_energy": magenta_energy,
        "rim_energy": rim_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

ARCANE_TEAL = (0.08, 0.70, 0.90)
ARCANE_AMBER = (1.20, 0.56, 0.16)
ARCANE_MAGENTA = (0.92, 0.16, 0.50)
ARCANE_VIOLET = (0.20, 0.08, 0.38)
ARCANE_RIM = (1.08, 0.40, 0.10)
REF_COLORS = [ARCANE_AMBER, ARCANE_TEAL, ARCANE_MAGENTA, ARCANE_RIM, ARCANE_VIOLET]

dist_params = dict(
    base=0.018,
    grad=(0.0, -0.12),
    tint=(0.55, 0.62, 0.95),
    blobs=[
        (-0.55, 0.12, 1.65, 1.45, ARCANE_TEAL),
        (0.58, 0.20, 1.55, 1.35, ARCANE_AMBER),
        (0.22, 0.38, 0.85, 0.72, ARCANE_MAGENTA),
        (-0.35, 0.48, 0.95, 0.68, ARCANE_RIM),
        (0.05, -0.28, 1.20, 1.05, ARCANE_VIOLET),
    ],
    vignette=0.58,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_arcane.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_Arcane"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.36
    s.tone_highlights = 1.10
    s.color_strength = 1.95
    s.color_saturation = 1.88
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.50

    s.lighting_preset = "cinematic"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [analysis_mod.apply_color_strategy(c, "VIVID") for c in REF_COLORS[:s.light_count]]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["amber_energy"],
    "fill": PARAMS["teal_energy"],
    "accent": PARAMS["magenta_energy"],
    "rim": PARAMS["rim_energy"],
    "sky": PARAMS["teal_energy"] * 0.45,
}}
_role_dir = {{
    "key": (0.62, 0.18, 0.72),
    "fill": (-0.58, 0.08, 0.76),
    "accent": (-0.18, 0.42, 0.68),
    "rim": (0.48, 0.22, -0.78),
    "sky": (0.0, 0.68, 0.52),
}}
_role_soft = {{
    "key": 1.05,
    "fill": 2.6,
    "accent": 1.15,
    "rim": 1.65,
    "sky": 3.4,
}}
_color_idx = {{"key": 0, "fill": 1, "accent": 2, "rim": 3, "extra": 2, "sky": 1}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 2 if extra_idx == 0 else 1
        extra_idx += 1
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else ARCANE_AMBER
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.12
        info.softness = _role_soft["key"]
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = True
        info.base_color = palette[1] if len(palette) > 1 else ARCANE_TEAL
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 0.72
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = palette[2] if len(palette) > 2 else ARCANE_MAGENTA
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 0.88
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = True
        info.base_color = palette[3] if len(palette) > 3 else ARCANE_RIM
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.02
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "sky":
        info.enabled = PARAMS["teal_energy"] > 0.08
        info.base_color = palette[1] if len(palette) > 1 else ARCANE_TEAL
        info.direction = _role_dir["sky"]
        info.gain = float(_role_energy["sky"])
        info.e0 = 0.55
        info.softness = _role_soft["sky"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1
        if info.enabled:
            info.base_color = palette[min(idx, len(palette) - 1)]
            info.direction = (0.38, 0.35, -0.62)
            info.gain = float(PARAMS["magenta_energy"] * 0.65)
            info.e0 = 0.78
            info.softness = 1.4
            lo.data.type = "AREA"
        extra_idx += 1

for lo in (coll.objects if coll else []):
    if lo.type == "LIGHT":
        lo.rolllux_light.is_sun = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    role = lo.rolllux_light.role
    if role in ("key", "accent"):
        ld.size = 0.48
        if hasattr(ld, "size_y"):
            ld.size_y = 1.35
    elif role == "rim":
        ld.size = 0.38
        if hasattr(ld, "size_y"):
            ld.size_y = 1.55
    else:
        ld.size = 0.92
        if hasattr(ld, "size_y"):
            ld.size_y = 0.95

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "arcane",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_cool_beauty_portrait_script(
    *,
    intensity: float = 0.24,
    contrast_boost: float = 0.65,
    light_count: int = 3,
) -> str:
    """Cool high-key beauty portrait: soft butterfly key, clamshell fill, subtle cool rim."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])

COOL_KEY = (0.90, 0.95, 1.10)
COOL_FILL = (0.86, 0.92, 1.06)
COOL_RIM = (0.74, 0.84, 1.14)
REF_KEY = (0.92, 0.96, 1.08)
REF_FILL = (0.88, 0.93, 1.05)
REF_RIM = (0.78, 0.86, 1.12)

dist_params = dict(
    base=0.48,
    grad=(0.0, -0.08),
    tint=(0.90, 0.95, 1.08),
    blobs=[
        (0.0, 0.52, 1.35, 1.05, COOL_KEY),
        (0.0, -0.38, 1.05, 0.82, COOL_FILL),
        (0.0, 0.22, 0.72, 0.55, COOL_RIM),
    ],
    rim=0.22,
    vignette=0.06,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_cool_beauty_v51.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_CoolBeauty"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"

s.lock_contrast_boost = True
s.lock_tone_shadows = True
s.lock_color_strength = True
s.lock_color_saturation = True
s.contrast_boost = PARAMS["contrast_boost"]
s.tone_shadows = 0.58
s.tone_highlights = 1.04
s.color_strength = 0.65
s.color_saturation = 0.72
s.color_strategy = "SOFT"
s.intensity = PARAMS["intensity"]
s.exposure = 1
s.distance = 2.2

s.lighting_preset = "beauty"
s.mode = "PORTRAIT"
s.orient_mode = "CAMERA"
s.use_luxpro = True
s.light_count = max(3, min(8, int(PARAMS["light_count"])))
s.auto_exposure = True
s.use_world = False
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [tuple(item.color) for item in result.sampled_colors]

analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])
try:
    rgb = analysis_mod.image_to_rgb(s.reference_image)
    profile = analysis_mod.analyze_rgb(
        rgb, mode=s.mode, luxpro=s.use_luxpro,
        palette_size=s.light_count, color_strategy=s.color_strategy,
    )
    if hasattr(analysis_mod, "rig_colors_in_order"):
        palette = analysis_mod.rig_colors_in_order(profile, s.light_count)
except Exception:
    pass

if not palette or len(palette) < 2:
    palette = [REF_KEY, REF_FILL, REF_RIM]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

def _color_for_role(role, fallback_index):
    role_idx = {{"key": 0, "fill": 1, "accent": 1, "rim": 2, "sky": 2}}
    idx = role_idx.get(role, fallback_index)
    if idx < len(palette):
        return palette[idx]
    if palette:
        return palette[min(idx, len(palette) - 1)]
    return REF_KEY

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    pal_color = _color_for_role(role, extra_idx)
    if role == "key":
        info.enabled = True
        info.base_color = pal_color
        info.direction = (0.02, 0.48, 0.88)
        info.e0 = 0.92
        info.softness = 0.82
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = True
        info.base_color = pal_color
        info.direction = (0.0, -0.36, 0.78)
        info.e0 = 0.58
        info.softness = 0.88
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = True
        info.base_color = pal_color
        info.direction = (0.0, 0.28, -0.86)
        info.e0 = 0.42
        info.softness = 0.78
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = False
    else:
        info.enabled = False
    if role == "extra":
        extra_idx += 1

lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    role = lo.rolllux_light.role
    if role not in ("key", "fill", "rim"):
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    if role == "key":
        ld.size = 0.55
        if hasattr(ld, "size_y"):
            ld.size_y = 0.72
    elif role == "fill":
        ld.size = 0.48
        if hasattr(ld, "size_y"):
            ld.size_y = 0.62
    elif role == "rim":
        ld.size = 0.38
        if hasattr(ld, "size_y"):
            ld.size_y = 1.4

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "cool_beauty_portrait",
    "reference_image": s.reference_image.name,
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_ghibli_vivid_script(
    *,
    intensity: float = 0.27,
    contrast_boost: float = 0.82,
    light_count: int = 5,
    sun_energy: float = 0.95,
    sky_energy: float = 0.78,
    meadow_energy: float = 0.72,
    cloud_energy: float = 0.68,
    magic_energy: float = 0.62,
) -> str:
    """Miyazaki/Ghibli vivid pastoral light: cerulean sky, meadow green, golden sun, pink-lavender magic."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "sun_energy": sun_energy,
        "sky_energy": sky_energy,
        "meadow_energy": meadow_energy,
        "cloud_energy": cloud_energy,
        "magic_energy": magic_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

SKY = (0.42, 0.78, 1.28)
MEADOW = (0.32, 1.18, 0.58)
SUN = (1.28, 1.06, 0.52)
CLOUD = (1.18, 0.70, 0.86)
MAGIC = (0.70, 0.62, 1.20)
REF_COLORS = [SUN, SKY, MEADOW, CLOUD, MAGIC]

dist_params = dict(
    base=0.34,
    grad=(0.0, 0.62),
    tint=(0.58, 0.80, 1.10),
    blobs=[
        (0.12, 0.58, 0.82, 0.92, SKY),
        (-0.56, 0.06, 0.95, 0.85, MEADOW),
        (0.64, 0.18, 1.05, 1.02, SUN),
        (-0.18, 0.40, 0.88, 0.70, CLOUD),
        (0.38, -0.12, 0.92, 0.62, MAGIC),
    ],
    vignette=0.06,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_ghibli_vivid.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_GhibliVivid"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.62
    s.tone_highlights = 1.08
    s.color_strength = 1.65
    s.color_saturation = 1.85
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.75

    s.lighting_preset = "outdoor"
    s.mode = "SCENE"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [analysis_mod.apply_color_strategy(c, "VIVID") for c in REF_COLORS[:s.light_count]]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["sun_energy"],
    "fill": PARAMS["meadow_energy"],
    "accent": PARAMS["cloud_energy"],
    "rim": PARAMS["magic_energy"],
    "sky": PARAMS["sky_energy"],
}}
_role_dir = {{
    "key": (0.58, 0.22, 0.68),
    "fill": (-0.52, 0.04, 0.72),
    "accent": (-0.12, 0.48, 0.64),
    "rim": (0.42, 0.18, -0.78),
    "sky": (0.0, 0.82, 0.48),
}}
_role_soft = {{
    "key": 2.2,
    "fill": 3.4,
    "accent": 2.8,
    "rim": 2.6,
    "sky": 3.8,
}}
_color_idx = {{"key": 0, "fill": 2, "accent": 3, "rim": 4, "extra": 1, "sky": 1}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 1 if extra_idx == 0 else 4
        extra_idx += 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else SUN
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else SUN
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.0
        info.softness = _role_soft["key"]
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = True
        info.base_color = palette[2] if len(palette) > 2 else MEADOW
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 1.0
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = palette[3] if len(palette) > 3 else CLOUD
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.0
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = True
        info.base_color = palette[4] if len(palette) > 4 else MAGIC
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.0
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "sky":
        info.enabled = PARAMS["sky_energy"] > 0.01
        info.base_color = palette[1] if len(palette) > 1 else SKY
        info.direction = _role_dir["sky"]
        info.gain = float(_role_energy["sky"])
        info.e0 = 1.0
        info.softness = _role_soft["sky"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1
        if info.enabled:
            info.base_color = palette[min(idx, len(palette) - 1)]
            info.direction = (0.0, 0.55, 0.62)
            info.gain = float(PARAMS["magic_energy"] * 0.9)
            info.e0 = 1.0
            info.softness = 2.5
            lo.data.type = "AREA"
        extra_idx += 1

for lo in (coll.objects if coll else []):
    if lo.type == "LIGHT":
        lo.rolllux_light.is_sun = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    ld.size = 0.85
    if hasattr(ld, "size_y"):
        ld.size_y = 0.72 if lo.rolllux_light.role in ("key", "sky", "fill") else 0.58

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "ghibli_vivid",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_doraemon_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 0.72,
    light_count: int = 4,
    blue_energy: float = 1.05,
    white_energy: float = 0.88,
    red_energy: float = 0.72,
    yellow_energy: float = 0.58,
    sky_energy: float = 0.62,
) -> str:
    """Doraemon palette: signature cyan-blue body, white belly fill, red nose accent, yellow bell."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "blue_energy": blue_energy,
        "white_energy": white_energy,
        "red_energy": red_energy,
        "yellow_energy": yellow_energy,
        "sky_energy": sky_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

DORA_BLUE = (0.04, 0.52, 0.98)
DORA_WHITE = (0.98, 0.99, 1.0)
DORA_RED = (1.0, 0.10, 0.20)
DORA_YELLOW = (1.0, 0.86, 0.12)
SKY_BLUE = (0.48, 0.80, 1.0)
REF_COLORS = [DORA_BLUE, DORA_WHITE, DORA_RED, DORA_YELLOW, SKY_BLUE]

dist_params = dict(
    base=0.44,
    grad=(0.0, 0.55),
    tint=(0.62, 0.82, 1.08),
    blobs=[
        (0.18, 0.22, 1.02, 0.96, DORA_BLUE),
        (-0.48, 0.08, 0.88, 0.78, DORA_WHITE),
        (0.58, 0.28, 0.72, 0.58, DORA_RED),
        (-0.22, 0.42, 0.68, 0.52, DORA_YELLOW),
        (0.02, 0.72, 0.92, 0.82, SKY_BLUE),
    ],
    vignette=0.05,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_doraemon.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_Doraemon"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_tone_highlights = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.58
    s.tone_highlights = 1.06
    s.color_strength = 1.55
    s.color_saturation = 1.72
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.65

    s.lighting_preset = "auto"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [analysis_mod.apply_color_strategy(c, "VIVID") for c in REF_COLORS[:s.light_count]]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

_role_energy = {{
    "key": PARAMS["blue_energy"],
    "fill": PARAMS["white_energy"],
    "accent": PARAMS["red_energy"],
    "rim": PARAMS["yellow_energy"],
    "sky": PARAMS["sky_energy"],
}}
_role_dir = {{
    "key": (0.56, 0.20, 0.70),
    "fill": (-0.54, 0.06, 0.74),
    "accent": (0.62, 0.24, 0.76),
    "rim": (-0.38, 0.36, -0.72),
    "sky": (0.0, 0.78, 0.50),
}}
_role_soft = {{
    "key": 2.4,
    "fill": 3.6,
    "accent": 2.0,
    "rim": 2.2,
    "sky": 3.5,
}}
_color_idx = {{"key": 0, "fill": 1, "accent": 2, "rim": 3, "extra": 3, "sky": 4}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    idx = _color_idx.get(role, 0)
    if role == "extra":
        idx = 3 if extra_idx == 0 else 4
        extra_idx += 1
    pal_color = palette[min(idx, len(palette) - 1)] if palette else DORA_BLUE
    if role == "key":
        info.enabled = True
        info.base_color = palette[0] if palette else DORA_BLUE
        info.direction = _role_dir["key"]
        info.gain = float(_role_energy["key"])
        info.e0 = 1.0
        info.softness = _role_soft["key"]
        lo.data.type = "AREA"
    elif role == "fill":
        info.enabled = True
        info.base_color = palette[1] if len(palette) > 1 else DORA_WHITE
        info.direction = _role_dir["fill"]
        info.gain = float(_role_energy["fill"])
        info.e0 = 1.0
        info.softness = _role_soft["fill"]
        lo.data.type = "AREA"
    elif role == "accent":
        info.enabled = True
        info.base_color = palette[2] if len(palette) > 2 else DORA_RED
        info.direction = _role_dir["accent"]
        info.gain = float(_role_energy["accent"])
        info.e0 = 1.0
        info.softness = _role_soft["accent"]
        lo.data.type = "AREA"
    elif role == "rim":
        info.enabled = True
        info.base_color = palette[3] if len(palette) > 3 else DORA_YELLOW
        info.direction = _role_dir["rim"]
        info.gain = float(_role_energy["rim"])
        info.e0 = 1.0
        info.softness = _role_soft["rim"]
        lo.data.type = "AREA"
    elif role == "sky":
        info.enabled = PARAMS["sky_energy"] > 0.01
        info.base_color = palette[4] if len(palette) > 4 else SKY_BLUE
        info.direction = _role_dir["sky"]
        info.gain = float(_role_energy["sky"])
        info.e0 = 1.0
        info.softness = _role_soft["sky"]
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx <= 1
        if info.enabled:
            info.base_color = palette[min(idx, len(palette) - 1)]
            info.direction = (-0.12, 0.52, 0.64)
            info.gain = float(PARAMS["yellow_energy"] * 0.85)
            info.e0 = 1.0
            info.softness = 2.4
            lo.data.type = "AREA"
        extra_idx += 1

for lo in (coll.objects if coll else []):
    if lo.type == "LIGHT":
        lo.rolllux_light.is_sun = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    ld.size = 0.82
    if hasattr(ld, "size_y"):
        ld.size_y = 0.70 if lo.rolllux_light.role in ("key", "fill", "sky") else 0.56

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "doraemon",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_vivid_colors_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 1.15,
    light_count: int = 5,
    key_energy: float = 1.0,
    fill_energy: float = 0.92,
    accent_energy: float = 0.98,
    rim_energy: float = 0.88,
    extra_energy: float = 0.85,
) -> str:
    """Bright high-key vivid colors (极色彩): hue-separated gels on a luminous base."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
        "extra_energy": extra_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])
analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

import random
dist_params = gen_assets.build_random_reference_params("VIVID", random.Random(11))
dist_params["base"] = 0.30
dist_params["tint"] = (0.52, 0.68, 1.02)
dist_params["vignette"] = 0.10
REF_FALLBACK = list(gen_assets._VIVID_GEL)

lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_vivid_colors.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_VividColors"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.55
    s.tone_highlights = 1.10
    s.color_strength = 1.95
    s.color_saturation = 2.10
    if hasattr(s, "color_strategy"):
        s.color_strategy = "DISTINCT" if "DISTINCT" in analysis_mod.COLOR_STRATEGIES else "VIVID"
    else:
        s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.6

    s.lighting_preset = "high_key"
    s.mode = "SCENE"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [analysis_mod.apply_color_strategy(c, "VIVID") for c in REF_FALLBACK[:s.light_count]]

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

ROLE_ENERGY = {{
    "key": PARAMS["key_energy"],
    "fill": PARAMS["fill_energy"],
    "accent": PARAMS["accent_energy"],
    "rim": PARAMS["rim_energy"],
    "extra": PARAMS["extra_energy"],
}}
ROLE_DIR = {{
    "key": (-0.55, 0.16, 0.74),
    "fill": (0.58, 0.12, 0.76),
    "accent": (0.06, 0.62, 0.64),
    "rim": (0.0, 0.20, -0.88),
    "extra": (-0.36, -0.32, 0.68),
}}
ROLE_SOFT = {{
    "key": 1.8,
    "fill": 2.4,
    "accent": 1.6,
    "rim": 1.5,
    "extra": 1.7,
}}
ROLE_IDX = {{"key": 0, "fill": 1, "accent": 2, "rim": 3, "extra": 4, "sky": 1}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    if role in ROLE_ENERGY:
        idx = ROLE_IDX.get(role, 0)
        info.enabled = True
        info.base_color = palette[min(idx, len(palette) - 1)] if palette else (1.0, 1.0, 1.0)
        info.direction = ROLE_DIR.get(role, (0.0, 0.2, 0.9))
        info.gain = float(ROLE_ENERGY[role])
        info.e0 = 1.0
        info.softness = ROLE_SOFT.get(role, 1.7)
        lo.data.type = "AREA"
    elif role == "extra":
        info.enabled = extra_idx < 2
        if info.enabled:
            idx = 4 if extra_idx == 0 else 2
            info.base_color = palette[min(idx, len(palette) - 1)] if palette else (1.0, 1.0, 1.0)
            info.direction = ROLE_DIR["extra"]
            info.gain = float(PARAMS["extra_energy"])
            info.e0 = 1.0
            info.softness = ROLE_SOFT["extra"]
            lo.data.type = "AREA"
        extra_idx += 1
    elif role == "sky":
        info.enabled = False

scene_name = bpy.context.scene.name
lighting._REGEN_PENDING.discard(scene_name)
props_mod._GENERATE_SCHEDULED.discard(scene_name)
props_mod._SUSPEND = False
lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig
lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    ld.size = 0.55
    if hasattr(ld, "size_y"):
        ld.size_y = 0.85

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.gain, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "vivid_colors",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_vivid_rainbow_script(
    *,
    intensity: float = 0.28,
    contrast_boost: float = 2.2,
    light_count: int = 5,
    key_energy: float = 1.05,
    fill_energy: float = 0.95,
    accent_energy: float = 1.10,
    rim_energy: float = 1.25,
    extra_energy: float = 0.88,
) -> str:
    """Full-spectrum vivid lighting: five hue-separated gel colors, neon mood."""
    params = {
        "intensity": intensity,
        "contrast_boost": contrast_boost,
        "light_count": light_count,
        "key_energy": key_energy,
        "fill_energy": fill_energy,
        "accent_energy": accent_energy,
        "rim_energy": rim_energy,
        "extra_energy": extra_energy,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__("bl_ext.user_default.rolllux.gen_assets", fromlist=["gen_assets"])
presets = __import__("bl_ext.user_default.rolllux.presets", fromlist=["presets"])
lighting = __import__("bl_ext.user_default.rolllux.lighting", fromlist=["lighting"])
props_mod = __import__("bl_ext.user_default.rolllux.properties", fromlist=["properties"])

_sched_noop = lambda ctx: None
_sched_orig = lighting.schedule_analyze_and_generate
_sched_only_orig = lighting.schedule_analyze_only
_gen_sched_orig = props_mod.schedule_generate_after_custom_load
lighting.schedule_analyze_and_generate = _sched_noop
lighting.schedule_analyze_only = _sched_noop
props_mod.schedule_generate_after_custom_load = _sched_noop

import random
dist_params = gen_assets.build_random_reference_params("VIVID", random.Random(7))
REF_FALLBACK = list(gen_assets._VIVID_GEL)

lin = gen_assets.make_ref(gen_assets.REF_SIZE, **dist_params)
path = os.path.join(tempfile.gettempdir(), "rolllux_random", "ref_vivid_rainbow.png")
os.makedirs(os.path.dirname(path), exist_ok=True)
gen_assets.write_png(path, gen_assets._gamma(lin))
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_VividRainbow"

props_mod._REFERENCE_BUSY = True
props_mod._SUSPEND = True
try:
    s.reference_image = img
    s.reference_user_cleared = False
    s.reference_is_custom = False
    s.reference_preset = "random"
    if hasattr(s, "distribution_color_mode"):
        s.distribution_color_mode = "VIVID"

    s.lock_contrast_boost = True
    s.lock_tone_shadows = True
    s.lock_color_strength = True
    s.lock_color_saturation = True
    s.contrast_boost = PARAMS["contrast_boost"]
    s.tone_shadows = 0.38
    s.tone_highlights = 1.14
    s.color_strength = 2.15
    s.color_saturation = 2.25
    s.color_strategy = "VIVID"
    s.intensity = PARAMS["intensity"]
    s.exposure = 1
    s.distance = 2.5

    s.lighting_preset = "neon"
    s.mode = "PORTRAIT"
    s.orient_mode = "CAMERA"
    s.use_luxpro = True
    s.light_count = max(3, min(8, int(PARAMS["light_count"])))
    s.auto_exposure = True
    s.use_world = False
    s.target_mode = "SELECTED"
finally:
    props_mod._REFERENCE_BUSY = False
    props_mod._SUSPEND = False

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if sel:
        obj = sel[0]
if obj is None:
    for name in ("bathroom_set05_03.002",):
        o = bpy.data.objects.get(name)
        if o and o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}:
            obj = o
            break
if obj is None:
    for o in bpy.context.scene.objects:
        if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}} and o.visible_get():
            obj = o
            break
if obj is None:
    fail("No object selected")
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

obj_name = obj.name

try:
    bpy.ops.rolllux.clear()
except Exception:
    pass

obj = bpy.data.objects.get(obj_name)
if obj is None:
    fail("Target object missing after clear: " + obj_name)
for o in bpy.context.scene.objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.rolllux.generate()

result = bpy.context.scene.rolllux_result
palette = [tuple(item.color) for item in result.sampled_colors]

analysis_mod = __import__("bl_ext.user_default.rolllux.analysis", fromlist=["analysis"])
try:
    rgb = analysis_mod.image_to_rgb(s.reference_image)
    profile = analysis_mod.analyze_rgb(
        rgb, mode=s.mode, luxpro=s.use_luxpro,
        palette_size=s.light_count, color_strategy=s.color_strategy,
    )
    if hasattr(analysis_mod, "rig_colors_in_order"):
        palette = analysis_mod.rig_colors_in_order(profile, s.light_count)
except Exception:
    pass

def _looks_flat(colors):
    if len(colors) < 2:
        return True
    hues = []
    for c in colors:
        mx, mn = max(c), min(c)
        if mx - mn < 0.08:
            continue
        hues.append(mx - mn)
    return len(hues) < 2

if not palette or _looks_flat(palette):
    palette = [tuple(c) for c in REF_FALLBACK[:s.light_count]]

# Stylized look: always drive lights from the vivid gel set (not merged analysis).
palette = []
for c in REF_FALLBACK[:s.light_count]:
    palette.append(analysis_mod.apply_color_strategy(c, "VIVID"))

for i, item in enumerate(result.sampled_colors):
    if i < len(palette):
        item.color = palette[i]

ROLE_ENERGY = {{
    "key": PARAMS["key_energy"],
    "fill": PARAMS["fill_energy"],
    "accent": PARAMS["accent_energy"],
    "rim": PARAMS["rim_energy"],
    "extra": PARAMS["extra_energy"],
}}
ROLE_DIR = {{
    "key": (-0.70, 0.18, 0.72),
    "fill": (0.72, 0.14, 0.74),
    "accent": (0.04, 0.68, 0.62),
    "rim": (0.0, 0.22, -0.92),
    "extra": (-0.42, -0.38, 0.66),
}}
ROLE_SOFT = {{
    "key": 0.55,
    "fill": 0.62,
    "accent": 0.48,
    "rim": 0.35,
    "extra": 0.58,
}}
ROLE_IDX = {{"key": 0, "fill": 1, "accent": 1, "rim": 3, "sky": 4}}

coll = bpy.data.collections.get("RollLux")
extra_idx = 0
for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT":
        continue
    info = lo.rolllux_light
    role = info.role
    if role == "extra":
        idx = 2 if extra_idx == 0 else 4
        extra_idx += 1
    else:
        idx = ROLE_IDX.get(role, 0)
    if idx < len(palette):
        pal_color = palette[idx]
    elif palette:
        pal_color = palette[min(idx, len(palette) - 1)]
    else:
        pal_color = (1.0, 1.0, 1.0)
    if role in ROLE_ENERGY:
        info.enabled = True
        info.base_color = pal_color
        info.direction = ROLE_DIR.get(role, (0.0, 0.2, 0.9))
        info.e0 = ROLE_ENERGY[role]
        info.softness = ROLE_SOFT.get(role, 0.6)
        lo.data.type = "AREA"
    elif role == "sky":
        info.enabled = False
    elif role == "extra":
        info.enabled = extra_idx < max(1, s.light_count - 4)
        if info.enabled:
            idx = min(4, len(palette) - 1)
            info.base_color = palette[idx] if palette else pal_color
            info.direction = ROLE_DIR["extra"]
            info.e0 = ROLE_ENERGY["extra"]
            info.softness = ROLE_SOFT["extra"]
            lo.data.type = "AREA"
        extra_idx += 1

lighting.live_update(bpy.context)

for lo in (coll.objects if coll else []):
    if lo.type != "LIGHT" or not lo.rolllux_light.enabled:
        continue
    if lo.data.type != "AREA":
        lo.data.type = "AREA"
    ld = lo.data
    if ld.type != "AREA":
        continue
    ld.shape = "RECTANGLE"
    role = lo.rolllux_light.role
    if role in ("key", "fill", "accent"):
        ld.size = 0.32
        if hasattr(ld, "size_y"):
            ld.size_y = 1.8
    elif role in ("rim", "extra"):
        ld.size = 0.28
        if hasattr(ld, "size_y"):
            ld.size_y = 2.2

lighting.schedule_analyze_and_generate = _sched_orig
lighting.schedule_analyze_only = _sched_only_orig
props_mod.schedule_generate_after_custom_load = _gen_sched_orig

palette_out = [list(c) for c in palette]
lights = []
if coll:
    lights = [{{
        "name": lo.name,
        "role": lo.rolllux_light.role,
        "type": lo.data.type,
        "enabled": lo.rolllux_light.enabled,
        "color": list(lo.rolllux_light.base_color),
        "direction": list(lo.rolllux_light.direction),
        "energy": round(lo.rolllux_light.e0, 3),
    }} for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "style": "vivid_rainbow",
    "reference_image": s.reference_image.name,
    "distribution_color_mode": getattr(s, "distribution_color_mode", "VIVID"),
    "lighting_preset": s.lighting_preset,
    "color_strategy": s.color_strategy,
    "mode": s.mode,
    "light_count": s.light_count,
    "intensity": s.intensity,
    "contrast_boost": s.contrast_boost,
    "mood": result.mood if result.valid else "",
    "contrast_ratio": round(result.contrast_ratio, 2) if result.valid else 0.0,
    "sampled_palette": palette_out,
    "lights": lights,
}}))
"""


def light_from_left_script(
    *,
    preset: str = "portrait",
    light_count: int = 3,
    intensity: float = 0.22,
    clear_existing: bool = True,
) -> str:
    pkg = _blender_rolllux_import()
    params = {
        "preset": preset,
        "light_count": light_count,
        "intensity": intensity,
        "clear_existing": clear_existing,
        "pkg": pkg,
    }
    return f"""
import json
import os
import tempfile
import bpy

PARAMS = {json.dumps(params)}

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

gen_assets = __import__(PARAMS["pkg"] + ".gen_assets", fromlist=["gen_assets"])
presets = __import__(PARAMS["pkg"] + ".presets", fromlist=["presets"])

left_params = dict(
    base=0.14,
    grad=(0.0, 0.15),
    tint=(1.0, 0.96, 0.9),
    blobs=[(-0.62, 0.32, 1.1, 0.88, (1.0, 0.95, 0.88))],
    rim=0.35,
    vignette=0.15,
)
lin = gen_assets.make_ref(gen_assets.REF_SIZE, **left_params)
rgb = gen_assets._gamma(lin)
rand_dir = os.path.join(tempfile.gettempdir(), "rolllux_random")
os.makedirs(rand_dir, exist_ok=True)
path = os.path.join(rand_dir, "ref_left_key.png")
gen_assets.write_png(path, rgb)
presets._random_override["reference"] = path
try:
    presets._reload_random_preview("reference")
except Exception:
    pass

s = bpy.context.scene.rolllux
img = bpy.data.images.load(path, check_existing=False)
img.pack()
img.name = "RollLux_LeftKey"
s.reference_image = img
s.reference_user_cleared = False
s.reference_is_custom = False
s.reference_preset = "random"
s.lighting_preset = PARAMS["preset"]
s.mode = "PORTRAIT"
s.use_luxpro = True
s.light_count = max(1, min(8, int(PARAMS["light_count"])))
s.intensity = float(PARAMS["intensity"])
s.auto_exposure = True
s.target_mode = "SELECTED"

obj = bpy.context.active_object
if obj is None:
    sel = [o for o in bpy.context.selected_objects if o.type in {{"MESH", "CURVE", "SURFACE", "META", "FONT"}}]
    if not sel:
        fail("No object selected")
    obj = sel[0]
    bpy.context.view_layer.objects.active = obj

if PARAMS["clear_existing"]:
    try:
        bpy.ops.rolllux.clear()
    except Exception:
        pass

bpy.ops.rolllux.generate()
result = bpy.context.scene.rolllux_result
lights = []
coll = bpy.data.collections.get("RollLux")
if coll:
    lights = [lo.name for lo in coll.objects if lo.type == "LIGHT"]

print(json.dumps({{
    "ok": True,
    "object": obj.name,
    "reference_image": s.reference_image.name,
    "distribution": "procedural left key (blob x=-0.62)",
    "lighting_preset": s.lighting_preset,
    "luxpro_direction": result.dir_label if result.valid else "",
    "dir_confidence": round(result.dir_confidence, 2) if result.valid else 0.0,
    "lights_created": len(lights),
    "light_names": lights,
    "mood": result.mood if result.valid else "",
}}))
"""


def refresh_roll_script(regenerate: bool = True) -> str:
    return f"""
import json
import bpy

def fail(msg):
    raise RuntimeError(msg)

if not hasattr(bpy.types.Scene, "rolllux"):
    fail("RollLux not enabled")

s = bpy.context.scene.rolllux
before = {{
    "lighting_preset": s.lighting_preset,
    "reference_image": s.reference_image.name if s.reference_image else None,
}}

bpy.ops.rolllux.random_preset()
bpy.ops.rolllux.random_reference()

out = {{
    "ok": True,
    "before": before,
    "lighting_preset": s.lighting_preset,
    "reference_image": s.reference_image.name if s.reference_image else None,
}}
print(json.dumps(out))
"""


def clear_lighting_script() -> str:
    return """
import json
import bpy

if not hasattr(bpy.types.Scene, "rolllux"):
    print(json.dumps({"ok": False, "error": "RollLux not enabled"}))
else:
    removed = 0
    try:
        bpy.ops.rolllux.clear()
        removed = 1
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
    else:
        print(json.dumps({"ok": True, "cleared": True}))
"""
