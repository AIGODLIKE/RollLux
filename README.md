<div align="center">

# ✨ RollLux

**Match your Blender scene lighting to any reference image — in one click.**

*Procedural presets · LuxPro direction · dual-tone gel lights · live tuning · viewport overlay*

<br>

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-2ea043)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0%2B-f5792a?logo=blender&logoColor=white)](https://www.blender.org/)
[![Python](https://img.shields.io/badge/python-pure%20%2B%20numpy-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/network-offline%20ready-success)]()

<br>

**English** · [中文](README_zh-CN.md) · [日本語](README_ja.md)

<br>

<!-- Replace with your logo: ./assets/logo.png -->
<img src="./assets/logo.png" alt="RollLux logo" width="120" onerror="this.style.display='none'">

</div>

---

## Introduction

**RollLux** is a Blender 5.0+ extension that analyzes a reference photo and builds a **ready-to-tune light rig** — key, fill, rim, accent, and world ambient — so you can replicate cinematic, portrait, product, and stylized looks without hand-placing every light.

**Every strategy thumbnail and library reference is procedurally generated in code** — shaded spheres, gradient maps, and light blobs — not hand-picked stock photos. Roll **Random** anytime for a fresh combo, or step through named starting points that share the same generative pipeline.

Drop in a reference, hit **Generate**, and refine with real-time sliders. Works with **Cycles** and **Eevee**, fully **offline**, zero pip installs.

| | |
|:--|:--|
| **Author** | ACGGIT |
| **Blender** | 5.0.0 or newer |
| **Engines** | Cycles · Eevee |
| **Dependencies** | None (uses Blender’s bundled NumPy) |

---

## ✨ Features

| Feature | What you get |
|:--|:--|
| 🎯 **Reference analysis** | Key / fill / ambient colors, contrast, mood, color temperature |
| 🧭 **LuxPro direction** | Portrait-tuned light direction (left, right, top, backlight…) with confidence |
| 🎨 **Dual-tone gel lights** | Blue + red/magenta (and similar) each get their own **accent** SPOT |
| ⚡ **Split & hard light** | Sharp terminators → SPOT key, minimal fill, auto contrast / shadow seeding |
| 🎛️ **Live tuning** | Intensity, exposure, distance, rotation, saturation, shadows, highlights, contrast |
| 📸 **Auto exposure** | Four metering modes + EV bias; optional reference luminance match |
| 🎲 **Procedural presets** | Strategy thumbnails & distribution refs **generated in code** — random roll yields new looks every time |
| 🗂️ **Strategy picker** | Named starting styles + **Random** · procedural shaded-sphere previews · step navigation |
| 🖼️ **Distribution library** | Built-in reference images **procedurally synthesized** (gradients, blobs, rim, vignette…) |
| 💡 **1–8 lights** | Hue-diverse k-means palette matched to light count |
| 🔧 **Per-light edit** | Toggle, recolor, energy, softness, delete |
| 🪟 **Floating overlay** | Pin reference in viewport (opacity, scale, corner) |
| 📋 **Clipboard paste** | Paste reference image from system clipboard |
| 🌐 **Trilingual UI** | English / 中文 / 日本語 |

<details>
<summary><b>📊 RollLux vs manual lighting setup</b></summary>

| | Manual rig | RollLux |
|:--|:--:|:--:|
| Start from reference photo | ❌ | ✅ |
| Auto direction + color | ❌ | ✅ |
| Dual gel / accent detection | ❌ | ✅ |
| Random roll | ❌ | ✅ |
| Procedural preset & ref generation | ❌ | ✅ |
| Live slider updates | — | ✅ |
| Fully offline | ✅ | ✅ |

</details>

---

## 📷 Screenshots & Demo

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<strong>Reference → Result</strong><br><br>
<img src="./assets/demo-before-after.png" alt="Before and after lighting match" width="95%"><br>
<em>Portrait split-light reference matched to a 3D head</em>
</td>
<td align="center" width="50%">
<strong>Dual-tone gel lighting</strong><br><br>
<img src="./assets/demo-dual-gel.png" alt="Blue and magenta gel lights" width="95%"><br>
<em>Separate key + accent colors from saturated references</em>
</td>
</tr>
<tr>
<td align="center" width="50%">
<strong>N-panel workflow</strong><br><br>
<img src="./assets/demo-panel.png" alt="RollLux N-panel UI" width="95%"><br>
<em>Strategy presets, tuning sliders, LuxPro read-out</em>
</td>
<td align="center" width="50%">
<strong>Animated workflow</strong><br><br>
<img src="./assets/demo-workflow.gif" alt="RollLux workflow GIF" width="95%"><br>
<em>Load reference → Generate → Tune</em>
</td>
</tr>
</table>

<sub>📁 Add your own captures to <code>./assets/</code> — filenames above are the expected paths.</sub>

</div>

---

## 🚀 Quick Start

### Install

1. Obtain **`rolllux-4.0.0.zip`** (extension package).
2. Blender → **Edit → Preferences → Get Extensions → ▼ → Install from Disk…**
3. Select the zip → enable **RollLux**.

<details>
<summary><b>🛠️ Build from source</b></summary>

```bash
cd rolllux
py gen_assets.py    # optional: regenerate thumbnails & reference PNGs
py build.py         # -> ../dist/rolllux-<version>.zip
```

</details>

### Basic workflow

1. **3D Viewport** → **N** → **RollLux** tab.
2. Load or paste a **reference image** (a procedurally generated default is applied on first open).
3. Pick a **Strategy** preset or tap **🔄 Random** for a freshly generated style.
4. Optionally change **Lighting Distribution** (procedural library) or use your own photo.
5. Select your subject → **Generate Lighting**.
6. Tune **Intensity**, **Contrast**, **Shadows**, **Highlights**, **Saturation** — updates apply live.
7. Expand **Advanced** for rig setup, per-light list, LuxPro direction, and analysis swatches.

---

## 📖 Usage

<details>
<summary><b>Main panel</b></summary>

| Control | Description |
|:--|:--|
| Reference image | File browser, paste, or procedural library |
| Strategy | **Procedurally generated** style presets + **Random** (new thumbnail each roll) |
| Lighting Distribution | **Procedurally generated** reference images + **Random** |
| Generate / Analyze / Clear | Build rig · analyze only · remove rig |
| Tuning sliders | Intensity, exposure, AE, distance, rotation, height, colors, tone |
| Auto Generate | Timer-based re-roll (interval slider) |

</details>

<details>
<summary><b>Advanced panel</b></summary>

| Control | Description |
|:--|:--|
| Mode | Portrait / Scene / Auto |
| Aim At / Orient By | Target & axis mapping |
| Light Count | 1–8 lights |
| LuxPro | Enable direction detection |
| Lights list | Per-light color, energy, delete |
| Analysis | Sampled colors, LuxPro label, mood, Kelvin |

</details>

<details>
<summary><b>Tips for best results</b></summary>

- **Portraits** — keep the face centered; avoid blown-out backgrounds.
- **Split / hard light** — let RollLux seed **Contrast** and **Shadows** (unlock sliders first).
- **Gel / neon** — use **Light Count ≥ 3** so key + accent + rim are all created.
- **Direction** — enable **LuxPro**; use **Rotate** to fine-tune the rig orbit.

</details>

---

## 🗺️ Roadmap

- [ ] Viewport comparison overlay (reference vs render)
- [ ] Preset export / import from current rig
- [ ] Batch generate for shot lists
- [ ] Optional AI reference tagging (offline heuristics first)

---

## 🤝 Contributing

Run `py test_offline.py` (no Blender required). Optional: `blender --background --python test_blender.py`. UI or lighting changes should include screenshots.

---

## 📄 License

[GNU General Public License v3.0 or later](LICENSE)
