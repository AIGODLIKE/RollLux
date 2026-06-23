# Changelog

All notable changes to RollLux since **5.0.0**.  
For the 5.0 baseline (viewport auto exposure, Quick/Pro UI, trilingual UI), see tag [`v5.0.0`](https://github.com/AIGODLIKE/RollLux/releases/tag/v5.0.0).

---

## [5.5.5] — 2026-06-23

### Extension Platform (Marketplace)

- Dedicated marketplace build: `py build_marketplace.py` → `rolllux-<version>-marketplace.zip`
- Marketplace manifest: `support`, `website`, `files` permission, CC0 for bundled PNGs, maintainer contact via GitHub
- Marketplace zip excludes README and dev-only entry points; strips optional dev-only code blocks at build time
- Removed legacy `bl_info` from `__init__.py` (extension metadata lives in `blender_manifest.toml`)

### Changed

- Operator IDs use Blender namespaces: `wm.rolllux_generate`, `wm.rolllux_clear`, etc. (shortcut-friendly)
- `load_post` handler registers only when the user first opens RollLux (not at extension load)
- `gen_assets.py` documented and packaged as a **runtime** module (random preset/reference generation); asset batch rebuild moved to `dev/gen_assets_main.py`
- Maintainer contact points to https://github.com/AIGODLIKE/RollLux

### Fixed

- Random preset / random reference no longer fail when `gen_assets` is missing from the install zip
- `rolllux.auto_timer` includes `bl_options = {"REGISTER", "UNDO"}`

---

## [5.5.3] — 2026-06-18

### Added

- **Lock light colors** — keep the current palette when re-generating or stepping presets (lock icon in the Lights section)

### Changed

- UI strings follow **Blender’s global language** via `bpy.app.translations` (removed in-panel language dropdown)
- Dev-only `if __name__ == "__main__"` blocks moved out of shipped modules into `dev/`

### Removed

- Clipboard paste operator (platform policy; use **Open Reference Image** instead)

### Fixed

- Translations register/unregister correctly on enable/disable
- Background random-preview path no longer references an undefined variable
- Removed `Animation` tag from manifest (lighting-only extension)

---

## [5.5.0 – 5.5.2] — 2026-06

### Added

- Expanded **LuxPro** direction analysis and portrait/scene mode handling
- Broader offline test coverage (`test_offline.py`, `audit_i18n.py`)

### Changed

- Tagline: **Perceptive Full-Auto Metering Lighting**
- README overhaul: logo, demo videos, screenshot layout, Auto Exposure documentation
- Analysis pipeline improvements for dual-tone gels, split/hard light, and palette strategies

---

## Summary vs 5.0.0

| Area | 5.0.0 | 5.5.5 |
|------|-------|-------|
| Auto exposure | ✓ viewport AE, Quick/Pro | ✓ unchanged core; LIGHT_RIG bake & metering modes retained |
| Reference input | File + clipboard paste | File + built-in library + random procedural refs |
| i18n | Custom language picker + TR dict | Blender native translations (EN / 中文 / 日本語) |
| Random roll | ✓ | ✓ runtime procedural preset & reference generation |
| Light colors | Re-roll on every generate | Optional **lock palette** across re-generates |
| Operators | `rolllux.*` ids | `wm.rolllux_*` ids |
| Extension manifest | Minimal | Full support URL, permissions, asset licensing |
| Install zip | Single build | Full zip (`build.py`) + Marketplace zip (`build_marketplace.py`) |
