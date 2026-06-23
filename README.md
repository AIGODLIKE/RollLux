<div align="center">

# ✨ RollLux

**Perceptive Full-Auto Metering Lighting**

*Procedural presets · LuxPro direction · viewport auto exposure · live tuning · viewport overlay*

<br>

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-2ea043)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0%2B-f5792a?logo=blender&logoColor=white)](https://www.blender.org/)
[![Release](https://img.shields.io/github/v/release/AIGODLIKE/RollLux?label=RollLux)](https://github.com/AIGODLIKE/RollLux/releases/latest)
[![Python](https://img.shields.io/badge/python-pure%20%2B%20numpy-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/network-offline%20ready-success)]()

<br>

**English** · [中文](README_zh-CN.md) · [日本語](README_ja.md)

<br>

<img src="./assets/logo.png" alt="RollLux logo" width="420">

</div>

---

## Introduction

**RollLux** is a Blender 5.0+ extension that analyzes a reference photo and builds a **ready-to-tune light rig** — key, fill, rim, accent, and world ambient — so you can replicate cinematic, portrait, product, and stylized looks without hand-placing every light.



https://github.com/user-attachments/assets/183dd506-389f-4b7c-b474-8ebf130bed49



https://github.com/user-attachments/assets/2ef10f8a-98b2-41c1-9983-3c481e25c905



https://github.com/user-attachments/assets/801ae6c6-3112-40cc-8e00-fa09bf9785eb





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
| 📸 **Auto exposure** | Viewport sampling in Rendered mode; TRIM / LOG / P60 metering, EV bias, fast converge, LIGHT_RIG bake |
| 🧩 **Quick / Pro UI** | Compact Quick workflow or full Pro panel with advanced AE, rig, and per-light controls |
| 🎲 **Procedural presets** | Strategy thumbnails & distribution refs **generated in code** — random roll yields new looks every time |
| 🗂️ **Strategy picker** | Named starting styles + **Random** · procedural shaded-sphere previews · step navigation |
| 🖼️ **Distribution library** | Built-in reference images **procedurally synthesized** (gradients, blobs, rim, vignette…) |
| 💡 **1–8 lights** | Hue-diverse k-means palette matched to light count |
| 🔧 **Per-light edit** | Toggle, recolor, energy, softness, delete |
| 🪟 **Floating overlay** | Pin reference in viewport (opacity, scale, corner) |
| 📂 **Open image** | Load a reference image from disk |
| 🌐 **Localized UI** | English / 中文 / 日本語 via Blender language preferences |

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
| Viewport auto exposure | ❌ | ✅ |
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

1. Download **`rolllux-5.5.3.zip`** from [Releases](https://github.com/AIGODLIKE/RollLux/releases/latest).
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
2. Load a **reference image** (a procedurally generated default is applied on first open).
3. Pick a **Strategy** preset or tap **🔄 Random** for a freshly generated style.
4. Optionally change **Lighting Distribution** (procedural library) or use your own photo.
5. Select your subject → **Generate Lighting**.
6. Tune **Intensity**, **Contrast**, **Shadows**, **Highlights**, **Saturation** — updates apply live.
7. Switch the 3D View to **Rendered** shading and enable **Auto Exposure** (on by default) — see [Auto Exposure](#-auto-exposure) below.
8. Use **Quick** for a compact panel, or **Pro** for full AE and rig controls.

---

## 📸 Auto Exposure

RollLux **5.0** ships a viewport-based auto exposure (AE) system that reads live pixels from the 3D View and keeps your scene at a stable luminance target — without leaving Blender or rendering to disk.

### How it works

1. While AE is on, RollLux samples the viewport framebuffer on a timer (requires **Material** or **Rendered** shading; **Rendered** is preferred).
2. A **10×10 sample grid** is collected over the metering region, with optional **center weighting** and per-frame **grid jitter** to reduce moiré misreads.
3. Samples are converted to luminance and aggregated with your chosen **metering mode**.
4. The plugin computes the EV gap to the target and applies it either to **Color Management exposure** or **light rig energy** (via `intensity × 2^EV`).
5. Tap **Apply** (✓) to **bake** the current AE offset into permanent settings and turn AE off.

> **Tip:** If the viewport is not in Rendered mode, use the panel’s **Set Rendered** control or switch shading manually before expecting AE to react.

### Quick vs Pro UI

| | **Quick** | **Pro** |
|:--|:--|:--|
| AE toggle | Camera icon + **EV Bias** + **Apply** | Same in the exposure row, plus **AE Mode** |
| Advanced AE | Hidden | Full **Auto Exposure** box: apply target, sampling, speed, gamma, jitter, fast converge, live EV readout |

Switch **UI Mode** at the top of the panel between Quick and Pro.

### Metering modes

| Mode | Best for |
|:--|:--|
| **Average** | General-purpose; mean luminance of the sample region |
| **Median** | Noisy or high-contrast scenes; resists outliers |
| **60th Percentile (P60)** | Slightly brighter than median — good for portraits |
| **Trim Mean** | Drops top/bottom 10% before averaging — robust for mixed backgrounds |
| **Log Average** | HDR-ish mixes; geometric mean in log space |
| **Highlight** | Protect highlights; meters toward the 85th percentile |
| **Reference** | Target = mean luminance of your **reference image** (falls back to 18% grey if unavailable) |

All modes blend **full-frame** and **center** samples according to **Center Weight** (0–100%).

### Where exposure is applied

| **Apply to** | Behavior |
|:--|:--|
| **Color Management** | Writes `scene.view_settings.exposure` live; optional **Parameter Correction (gamma)** while AE is active. **Apply** bakes exposure into CM and disables AE. |
| **Light Rig** | Adjusts `ae_value` and scales all light energy through **Intensity** (`× 2^EV`). Manual **Exposure** slider is locked while active. **Apply** multiplies **Intensity** by the accumulated EV and disables AE. |

**Light Rig** mode includes Cycles-aware safeguards: luminance must **settle** between steps, adaptation is **rate-limited**, and timing scales with render engine noise — reducing flicker when Cycles is still converging.

### Sampling region presets

| Preset | Description |
|:--|:--|
| **Full Frame** | Entire viewport weighted equally |
| **Balanced** | 70% center weight (default) |
| **Center** | Meters only the dense center grid |
| **Subject Frame** | Camera border in camera view, or center 60% in free view |
| **Custom** | Manual **Center Weight** slider |

In camera view without **Subject Frame**, the plugin can also crop to the **camera frame** automatically.

### Controls (Pro panel)

| Control | Purpose |
|:--|:--|
| **EV Bias** | Exposure compensation in stops added on top of the computed target |
| **AE Speed** | How quickly EV moves toward the target (Light Rig mode caps speed adaptively) |
| **Parameter Correction** | CM gamma tweak while AE drives Color Management |
| **Jitter** | Rotate the sample grid each frame to reduce moiré misreads |
| **Fast Converge** | Stop when remaining error or the next EV step is below **0.1** stops |
| **Live readout** | Current CM exposure or Light Rig EV while AE is running |
| **Apply (✓)** | Bake AE → CM exposure or **Intensity**, then turn AE off |

### Recommended workflows

<details>
<summary><b>Portrait / product (CM path)</b></summary>

1. Generate lighting → switch viewport to **Rendered**.
2. AE **Apply to**: **Color Management** · Mode: **P60** or **Trim Mean** · Sampling: **Balanced**.
3. Set **EV Bias** if the face should sit slightly brighter or darker.
4. When happy, click **Apply** to bake exposure into the scene.

</details>

<details>
<summary><b>Iterative light tuning (Light Rig path)</b></summary>

1. AE **Apply to**: **Light Rig** · enable **Fast Converge** for quicker settling.
2. Tweak colors and rig sliders while AE keeps overall brightness stable.
3. **Apply** when done to fold EV into **Intensity** and continue manual tuning.

</details>

<details>
<summary><b>Match reference brightness</b></summary>

1. Load reference → **Analyze** (or **Generate**).
2. AE Mode: **Reference** — target luminance comes from the reference image analysis.
3. Use **EV Bias** for fine matching.

</details>

---

## 📖 Usage

<details>
<summary><b>Main panel</b></summary>

| Control | Description |
|:--|:--|
| Reference image | File browser or procedural library |
| Strategy | **Procedurally generated** style presets + **Random** (new thumbnail each roll) |
| Lighting Distribution | **Procedurally generated** reference images + **Random** |
| Generate / Analyze / Clear | Build rig · analyze only · remove rig |
| Tuning sliders | Intensity, exposure, AE, distance, rotation, height, colors, tone |
| UI Mode | **Quick** compact layout or **Pro** with full Auto Exposure block |
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
| Auto Exposure | Apply target, metering mode, sampling preset, speed, bake — see [Auto Exposure](#-auto-exposure) |

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
