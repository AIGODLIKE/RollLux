"""In-Blender smoke test for RollLux.

Run headless:
    "D:\\Program Files\\Blender\\blender-5.1.0-windows-x64\\blender.exe" \
        --background --factory-startup --python rolllux/test_blender.py
"""

import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import rolllux  # noqa: E402
from rolllux import translations, presets, lighting  # noqa: E402


def _fail(msg):
    print("SMOKE TEST FAILED:", msg)
    sys.exit(1)


def main():
    rolllux.register()
    print("register() OK")

    scene = bpy.context.scene

    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 0))
    monkey = bpy.context.active_object
    monkey_name = monkey.name
    bpy.ops.object.camera_add(location=(0, -5, 1), rotation=(1.4, 0, 0))
    scene.camera = bpy.context.active_object
    bpy.context.view_layer.objects.active = monkey
    monkey.select_set(True)

    settings = scene.rolllux

    # Feature 1: default reference (broad light) keeps Generate enabled.
    from rolllux import properties as _props
    _props.ensure_default_reference(scene, bpy.context)
    if settings.reference_image is None:
        _fail("default reference not loaded (Generate would be greyed)")
    if settings.reference_preset != presets.DEFAULT_REFERENCE:
        _fail(f"default preset expected {presets.DEFAULT_REFERENCE}, got {settings.reference_preset}")
    print("default reference OK:", settings.reference_image.name)

    settings.reference_image = None
    settings.reference_user_cleared = True
    if _props.needs_default_reference(scene):
        _fail("cleared reference should not request default reload")
    _props.ensure_default_reference(scene, bpy.context)
    if settings.reference_image is not None:
        _fail("ensure_default_reference should respect user clear")
    print("user clear reference OK")

    settings.reference_preset = "golden_hour"
    if settings.reference_is_custom:
        _fail("built-in preset load should not mark reference as custom")
    if settings.reference_preset != "golden_hour":
        _fail(f"preset should stay golden_hour, got {settings.reference_preset}")
    settings.reference_preset = "sunset"
    if settings.reference_is_custom:
        _fail("stepping reference preset should not mark custom")
    if settings.reference_preset != "sunset":
        _fail(f"preset should be sunset after step, got {settings.reference_preset}")
    print("reference preset step OK")

    manual = bpy.data.images.new("RollLux_ManualTest", 16, 16)
    settings.reference_image = manual
    if not settings.reference_is_custom:
        _fail("manually assigned reference should mark custom")
    if settings.reference_preset != presets.CUSTOM_REFERENCE:
        _fail(f"manual reference should select custom slot, got {settings.reference_preset}")
    print("custom reference flag OK")

    settings.reference_image = None
    settings.reference_user_cleared = True
    settings.reference_preset = presets.DEFAULT_REFERENCE
    lighting.clear_previous(bpy.context)
    bpy.ops.rolllux.generate()
    if settings.reference_image is None:
        _fail("generate with no image should auto-load random reference")
    if settings.reference_preset != "random":
        _fail(f"generate with no image should select random preset, got {settings.reference_preset}")
    if len(lighting.list_lights()) < 1:
        _fail("generate with no image should build a light rig")
    print("generate auto-random reference OK")

    # New scene must also receive the default reference after ensure.
    bpy.ops.scene.new()
    ns = bpy.context.scene.rolllux
    _props.ensure_default_reference(bpy.context.scene, bpy.context)
    if ns.reference_image is None:
        _fail("new scene: default reference not loaded")
    if ns.reference_preset != presets.DEFAULT_REFERENCE:
        _fail(f"new scene preset expected {presets.DEFAULT_REFERENCE}, got {ns.reference_preset}")
    print("new scene default reference OK")
    bpy.context.window.scene = scene
    settings = scene.rolllux

    # Previews.
    presets.load_previews()
    n_icons = sum(1 for p in presets.PRESET_ORDER if p in presets._preset_previews)
    n_refs = sum(1 for r in presets.REFERENCE_ORDER if r in presets._ref_previews)
    if n_icons < len(presets.PRESET_ORDER) or n_refs < len(presets.REFERENCE_ORDER):
        _fail("missing thumbnails")
    print(f"previews OK: {n_icons} presets, {n_refs} refs")

    # Preset library coverage: >= 20 presets, each fully wired (params, icon,
    # trilingual name + description).
    if len(presets.PRESET_ORDER) < 20:
        _fail(f"only {len(presets.PRESET_ORDER)} presets (need >= 20)")
    for pid in presets.PRESET_ORDER:
        if pid not in presets.PRESET_PARAMS:
            _fail(f"preset {pid} missing params")
        for lng in ("EN", "ZH", "JA"):
            for suffix in ("", "_desc"):
                key = f"preset_{pid}{suffix}"
                if not translations.TR[key][lng] or translations.TR[key][lng] == key:
                    _fail(f"preset {pid} missing {lng} translation '{key}'")
    print(f"preset coverage OK: {len(presets.PRESET_ORDER)} presets fully wired")

    # Reference library coverage: >= 40 images, each fully wired.
    if len(presets.REFERENCE_ORDER) < 40:
        _fail(f"only {len(presets.REFERENCE_ORDER)} references (need >= 40)")
    for rid in presets.REFERENCE_ORDER:
        if not os.path.isfile(presets.reference_path(rid)):
            _fail(f"reference {rid} missing image")
        for lng in ("EN", "ZH", "JA"):
            for suffix in ("", "_desc"):
                key = f"ref_{rid}{suffix}"
                if not translations.TR[key][lng] or translations.TR[key][lng] == key:
                    _fail(f"reference {rid} missing {lng} translation '{key}'")
    if not hasattr(bpy.ops.rolllux, "reference_step"):
        _fail("reference_step operator not registered")
    print(f"reference coverage OK: {len(presets.REFERENCE_ORDER)} references fully wired")

    # Translation dictionary coverage.
    for lang in ("EN", "ZH", "JA"):
        if translations.TR["preset_portrait"][lang] != {
            "EN": "Portrait", "ZH": "\u4eba\u50cf", "JA": "\u30dd\u30fc\u30c8\u30ec\u30fc\u30c8",
        }[lang]:
            _fail(f"preset_portrait label {lang}")
    print("translation dict OK")

    # Enum tooltips: property-level description empty; item text from tr().
    from rolllux.properties import RLLM_Settings
    if RLLM_Settings.bl_rna.properties["mode"].description:
        _fail("mode property description should be empty for i18n tooltips")
    portrait_desc = next(
        desc for ident, _name, desc in translations.mode_items(settings, bpy.context)
        if ident == "PORTRAIT"
    )
    if portrait_desc != translations.TR["mode_portrait_desc"]["EN"]:
        _fail(f"mode item desc EN: {portrait_desc!r}")
    print("enum i18n OK")

    # Origin-offset robustness: geometry sits at x=5 but origin is at world 0.
    bpy.ops.mesh.primitive_cube_add(location=(5.0, 0.0, 0.0))
    cube = bpy.context.active_object
    scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")  # origin -> 0, geometry stays at 5
    center, radius = lighting._world_aabb(bpy.context, cube)
    print(f"origin-offset target center={tuple(round(c,2) for c in center)} r={radius:.2f}"
          f" (object origin={tuple(round(c,2) for c in cube.location)})")
    if abs(center.x - 5.0) > 0.6:
        _fail(f"target used origin, not geometry: {tuple(center)}")
    bpy.data.objects.remove(cube, do_unlink=True)
    bpy.context.view_layer.objects.active = monkey
    monkey.select_set(True)
    print("origin-offset OK (geometry-based)")

    # Reference library load + analyze (LuxPro).
    settings.live = False
    settings.reference_preset = "golden_hour"
    if settings.reference_image is None or not scene.rolllux_result.valid:
        _fail("reference library load/analyze failed")
    res = scene.rolllux_result
    print(f"LuxPro direction: {res.dir_label} ({int(res.dir_confidence*100)}%) "
          f"backlit={res.backlit}")
    if not res.dir_label:
        _fail("LuxPro produced no direction")

    # Generate via preset; active object must stay the monkey.
    settings.live = True
    settings.light_count = 5
    settings.lighting_preset = "cinematic"
    if not lighting.has_rig():
        bpy.ops.rolllux.generate()
    if len(lighting.list_lights()) != 5:
        _fail(f"light_count=5 produced {len(lighting.list_lights())} lights")
    print("light_count=5 OK")
    settings.light_count = 2
    bpy.ops.rolllux.generate()
    if len(lighting.list_lights()) != 2:
        _fail(f"light_count=2 produced {len(lighting.list_lights())} lights")
    print("light_count=2 OK")

    # Sampled colors must track light count: a 4-color reference + 6 lights
    # should yield clearly more than the old fixed 3 distinct colors.
    import numpy as _np
    nn = 64
    marr = _np.zeros((nn, nn, 4), dtype=_np.float32)
    marr[..., 3] = 1.0
    hh = nn // 2
    marr[:hh, :hh, :3] = (1.0, 0.05, 0.05)
    marr[:hh, hh:, :3] = (0.05, 1.0, 0.05)
    marr[hh:, :hh, :3] = (0.05, 0.05, 1.0)
    marr[hh:, hh:, :3] = (1.0, 1.0, 0.05)
    mimg = bpy.data.images.new("RollLux_MultiTest", nn, nn, alpha=True,
                               float_buffer=True)
    mimg.pixels.foreach_set(marr.reshape(-1))
    prev_ref = settings.reference_image
    prev_preset = settings.lighting_preset
    settings.reference_image = mimg
    settings.lighting_preset = "auto"
    settings.light_count = 6
    bpy.ops.rolllux.generate()
    mcols = {tuple(round(c, 2) for c in lt.rolllux_light.base_color)
             for lt in lighting.list_lights()}
    print(f"multicolor sampling: {len(lighting.list_lights())} lights, "
          f"{len(mcols)} distinct colors")
    if len(mcols) < 4:
        _fail(f"sampled colors did not track light count: {mcols}")
    settings.reference_image = prev_ref
    settings.lighting_preset = prev_preset
    bpy.data.images.remove(mimg)
    print("multicolor sampling OK")

    settings.light_count = 3
    bpy.ops.rolllux.generate()
    active = bpy.context.view_layer.objects.active
    if active is None or active.name != monkey_name:
        _fail(f"active object not preserved: {active.name if active else None}")
    print("keep-active OK:", active.name)

    lights = lighting.list_lights()
    print("cinematic lights:", sorted(l.name for l in lights))
    key = next((l for l in lights if l.rolllux_light.role == "key"), None)
    if key is None:
        _fail("no key light")

    # Live intensity doubling.
    settings.intensity = 0.2
    lighting.live_update(context)
    e1 = key.data.energy
    settings.intensity = 0.4
    e2 = key.data.energy
    if abs(e2 - e1 * 2.0) > max(0.5, e1 * 0.05):
        _fail(f"live intensity {e1}->{e2}")
    print(f"live tuning OK: {e1:.1f} -> {e2:.1f}")

    # Rig rotation.
    settings.rig_rotation = math.radians(45)
    ctrl = lighting.get_controller(bpy.context)
    if abs(ctrl.rotation_euler.z - math.radians(45)) > 1e-3:
        _fail(f"rig rotation not applied: {ctrl.rotation_euler.z}")
    print("rotate rig OK:", round(math.degrees(ctrl.rotation_euler.z)), "deg")

    # Rig height (Z slide).
    base_z = ctrl.location.z
    settings.rig_height = 2.0
    ctrl = lighting.get_controller(bpy.context)
    if abs(ctrl.location.z - (settings.cache_target[2] + 2.0)) > 1e-3:
        _fail(f"rig height not applied: {ctrl.location.z}")
    print("rig height OK:", round(ctrl.location.z - base_z, 2))
    settings.rig_height = 0.0

    # Feature 2a: distance compensation (energy scales with distance^2).
    key = next(l for l in lighting.list_lights() if l.rolllux_light.role == "key")
    settings.distance = 2.5
    e_near = key.data.energy
    settings.distance = 5.0
    e_far = key.data.energy
    ratio = e_far / max(e_near, 1e-6)
    if abs(ratio - 4.0) > 0.3:  # (5/2.5)^2 = 4
        _fail(f"distance compensation off: ratio {ratio:.2f}")
    print(f"distance compensation OK: x{ratio:.1f} at 2x distance")
    settings.distance = 2.5

    # Feature 3: auto-generate timer operator registered + headless-safe.
    if not hasattr(bpy.ops.rolllux, "auto_timer"):
        _fail("auto_timer operator missing")
    if abs(settings.timer_interval - 0.3) > 1e-6:
        _fail(f"timer interval default {settings.timer_interval}")
    print("auto timer OK (interval", settings.timer_interval, "s)")

    # Preset step operator.
    settings.lock_intensity = True
    settings.intensity = 9.99
    locked_intensity = settings.intensity
    before = settings.lighting_preset
    bpy.ops.rolllux.preset_step(direction=1)
    if settings.lighting_preset == before:
        _fail("preset_step did not change preset")
    if abs(settings.intensity - locked_intensity) > 0.01:
        _fail(f"locked intensity changed {locked_intensity} -> {settings.intensity}")
    settings.lock_intensity = False
    print("tuning lock OK")
    print("preset step OK:", before, "->", settings.lighting_preset)

    # Random generation: lighting preset + reference image.
    settings.live = True
    bpy.ops.rolllux.random_preset()
    if settings.lighting_preset != "random":
        _fail("random_preset did not select the random slot")
    if "random" not in presets.PRESET_PARAMS:
        _fail("random preset params missing")
    bpy.ops.rolllux.random_preset()  # twice: must not error / must re-roll
    print("random preset OK")

    ref_before = settings.reference_image
    bpy.ops.rolllux.random_reference()
    if settings.reference_image is None or settings.reference_image == ref_before:
        _fail("random_reference did not set a new image")
    if settings.reference_preset != "random":
        _fail("random_reference did not select the random slot")
    if not scene.rolllux_result.valid:
        _fail("random_reference did not analyze")
    bpy.ops.rolllux.random_reference()  # twice: fresh image each roll
    print("random reference OK:", settings.reference_image.name,
          settings.reference_image.size[:])
    settings.light_count = 3

    # Per-light edit (gain) changes only that light.
    n_before = len(lighting.list_lights())
    key = next(l for l in lighting.list_lights() if l.rolllux_light.role == "key")
    ke = key.data.energy
    key.rolllux_light.gain = 2.0  # update -> live
    if abs(key.data.energy - ke * 2.0) > max(1.0, ke * 0.05):
        _fail(f"per-light gain {ke}->{key.data.energy}")
    print("per-light edit OK")

    # Delete a light (add-light feature removed).
    victim = lighting.list_lights()[-1]
    bpy.ops.rolllux.delete_light(name=victim.name)
    if len(lighting.list_lights()) != n_before - 1:
        _fail("delete_light did not remove")
    if "RLLX_OT_add_light" in dir(bpy.types):
        _fail("add_light operator should be removed")
    print("delete light OK; add_light removed")

    # Floating overlay default + toggle.
    if settings.float_corner != "BOTTOM_LEFT":
        _fail("float default corner not bottom-left")
    settings.float_show = True
    settings.float_show = False
    print("overlay default+toggle OK")

    # World restore on clear (no backplate property anymore).
    if hasattr(settings, "add_camera_backplate"):
        _fail("backplate property still present")
    bg1 = next((n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND"), None)
    world_after = tuple(bg1.inputs[0].default_value) if bg1 else None
    bpy.ops.rolllux.clear()
    if lighting.has_rig():
        _fail("clear left lights")
    bg2 = next((n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND"), None) if scene.world else None
    world_restored = tuple(bg2.inputs[0].default_value) if bg2 else None
    print("world after/restored:",
          [tuple(round(c, 3) for c in v) if v else None for v in (world_after, world_restored)])

    rolllux.unregister()
    print("unregister() OK")
    print("\nSMOKE TEST PASSED")


if __name__ == "__main__":
    main()
