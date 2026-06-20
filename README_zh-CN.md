<div align="center">

# ✨ RollLux

**一键让 Blender 场景灯光匹配参考图**

*程序生成预设 · LuxPro 方向 · 视口自动曝光 · 实时调参 · 视口浮层参考*

<br>

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-2ea043)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0%2B-f5792a?logo=blender&logoColor=white)](https://www.blender.org/)
[![Release](https://img.shields.io/github/v/release/AIGODLIKE/RollLux?label=RollLux)](https://github.com/AIGODLIKE/RollLux/releases/latest)
[![Python](https://img.shields.io/badge/python-pure%20%2B%20numpy-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/网络-完全离线-success)]()

<br>

<a href="README.md">English</a> · **中文** · <a href="README_ja.md">日本語</a>

<br>

<img src="./assets/logo.png" alt="RollLux logo" width="120" onerror="this.style.display='none'">

</div>

---

## 简介

**RollLux** 是面向 **Blender 5.0+** 的参考图布光插件：分析照片后自动生成可微调灯光组（主光 / 补光 / 轮廓 / 点缀 / 环境），快速复刻电影、人像、产品与风格化打光，无需从零摆灯。

**所有策略缩略图与分布参考图均由程序自动生成** — 着色球、渐变图、光斑合成，并非固定数量的手工素材库。随时 **随机** 获得新组合，命名策略只是同一套生成管线的不同起点。

导入参考图 → **生成灯光** → 滑块实时微调。支持 **Cycles / Eevee**，**纯离线**，无需 pip 安装。

| | |
|:--|:--|
| **作者** | ACGGIT |
| **Blender** | 5.0.0 及以上 |
| **引擎** | Cycles · Eevee |
| **依赖** | 无（使用 Blender 内置 NumPy） |

---

## ✨ 功能亮点

| 功能 | 说明 |
|:--|:--|
| 🎯 **参考图分析** | 提取主光 / 补光 / 环境色、对比度、氛围、色温 |
| 🧭 **LuxPro 方向** | 人像优化打光方向检测（左 / 右 / 顶 / 逆光等）与置信度 |
| 🎨 **双色 gel 光** | 蓝 + 洋红等饱和双色各自独立 **Accent** SPOT |
| ⚡ **硬光 / 分割光** | 识别清晰明暗交界 → SPOT 主光、弱补光、自动对比 / 阴影参数 |
| 🎛️ **实时调参** | 强度、曝光、距离、旋转、饱和度、阴影、高光、对比度 |
| 📸 **自动曝光** | Rendered 视口采样；TRIM / LOG / P60 测光、EV 补偿、快速收敛、LIGHT_RIG 烘焙 |
| 🧩 **Quick / Pro 界面** | Quick 精简工作流，或 Pro 完整面板（高级 AE、rig、单灯控制） |
| 🎲 **程序生成预设** | 策略缩略图与分布参考图 **代码合成**，随机一次即出新样式 |
| 🗂️ **策略选择** | 命名起点 + **随机** · 程序生成的着色球预览 · 步进切换 |
| 🖼️ **分布参考库** | 内置参考图 **程序合成**（渐变、光斑、轮廓、暗角等） |
| 💡 **1–8 盏灯** | 按色相多样性采样，数量与灯光数对齐 |
| 🔧 **单灯编辑** | 开关、改色、能量、柔化、删除 |
| 🪟 **浮层参考** | 视口固定参考图（透明度、大小、角落） |
| 📋 **剪贴板粘贴** | 直接粘贴系统剪贴板图片 |
| 🌐 **三语界面** | English / 中文 / 日本語 |

<details>
<summary><b>📊 RollLux vs 手动布光</b></summary>

| | 手动摆灯 | RollLux |
|:--|:--:|:--:|
| 从参考图起步 | ❌ | ✅ |
| 自动方向 + 取色 | ❌ | ✅ |
| 双色 gel / 点缀光 | ❌ | ✅ |
| 随机生成 | ❌ | ✅ |
| 预设与参考图程序生成 | ❌ | ✅ |
| 滑块实时更新 | — | ✅ |
| 视口自动曝光 | ❌ | ✅ |
| 完全离线 | ✅ | ✅ |

</details>

---

## 📷 效果展示

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<strong>参考图 → 结果</strong><br><br>
<img src="./assets/demo-before-after.png" alt="布光前后对比" width="95%"><br>
<em>人像分割光参考匹配到 3D 头部</em>
</td>
<td align="center" width="50%">
<strong>双色 gel 光</strong><br><br>
<img src="./assets/demo-dual-gel.png" alt="蓝与洋红双色光" width="95%"><br>
<em>高饱和参考图分离主光与点缀色</em>
</td>
</tr>
<tr>
<td align="center" width="50%">
<strong>N 面板工作流</strong><br><br>
<img src="./assets/demo-panel.png" alt="RollLux 面板" width="95%"><br>
<em>策略预设、调参滑块、LuxPro 读数</em>
</td>
<td align="center" width="50%">
<strong>动图演示</strong><br><br>
<img src="./assets/demo-workflow.gif" alt="RollLux 工作流动图" width="95%"><br>
<em>加载参考 → 生成 → 微调</em>
</td>
</tr>
</table>

<sub>📁 将截图放入 <code>./assets/</code>，文件名与上表路径一致即可显示。</sub>

</div>

---

## 🚀 快速开始

### 安装

1. 从 [Releases](https://github.com/AIGODLIKE/RollLux/releases/latest) 下载 **`rolllux-5.0.0.zip`**。
2. Blender → **编辑 → 偏好设置 → 获取扩展 → ▼ → 从磁盘安装…**
3. 选择 zip → 启用 **RollLux**。

<details>
<summary><b>🛠️ 从源码构建</b></summary>

```bash
cd rolllux
py gen_assets.py    # 可选：重新生成缩略图与参考图
py build.py         # 输出 -> ../dist/rolllux-<version>.zip
```

</details>

### 基础流程

1. **3D 视口** → **N** → **RollLux** 面板。
2. 加载或粘贴 **参考图**（首次打开会自动加载一张程序生成的默认图）。
3. 选择 **策略** 预设，或点 **🔄 随机** 生成全新样式。
4. 可选：切换 **照明分布**（程序参考库）或使用自己的照片。
5. 选中主体 → **生成灯光**。
6. 调节 **强度**、**对比度**、**阴影**、**高光**、**饱和度** — 实时生效。
7. 将 3D 视口切到 **Rendered（渲染）** 着色，开启 **自动曝光**（默认已开）— 详见 [自动曝光](#-自动曝光)。
8. 面板顶部切换 **Quick / Pro**：Quick 精简布局，Pro 显示完整 AE 与 rig 控制。

---

## 📸 自动曝光

RollLux **5.0** 内置基于视口采样的自动曝光（AE）系统：直接读取 3D 视口像素，让场景亮度稳定在目标值附近，无需离屏渲染或外部工具。

### 工作原理

1. 开启 AE 后，插件按定时器采样视口帧缓冲（需要 **Material** 或 **Rendered** 着色，推荐 **Rendered**）。
2. 在测光区域内采集 **10×10 采样网格**，可按 **中心加权**；可选每帧 **网格抖动**，减轻摩尔纹误判。
3. 将采样转为亮度，按所选 **测光模式** 聚合。
4. 计算与目标的 EV 差距，写入 **色彩管理曝光** 或 **灯光组能量**（`强度 × 2^EV`）。
5. 点击 **应用（✓）** 将当前 AE 偏移 **烘焙** 为固定参数，并关闭 AE。

> **提示：** 若视口不在 Rendered 模式，请手动切换或使用面板中的 **Set Rendered**，否则 AE 不会生效。

### Quick 与 Pro 界面

| | **Quick** | **Pro** |
|:--|:--|:--|
| AE 控件 | 相机图标 + **EV 补偿** + **应用** | 曝光行含 **AE 模式** |
| 高级 AE | 隐藏 | 完整 **自动曝光** 区块：应用目标、采样、速度、Gamma、抖动、快速收敛、实时 EV |

在面板顶部 **UI 模式** 中切换 Quick / Pro。

### 测光模式

| 模式 | 适用场景 |
|:--|:--|
| **平均（Average）** | 通用；采样区域算术平均亮度 |
| **中位数（Median）** | 噪点或高对比场景；抗离群值 |
| **60 分位（P60）** | 略偏亮于中位数，适合人像 |
| **截尾平均（Trim Mean）** | 去掉最高/最低 10% 后求平均，背景杂乱时更稳 |
| **对数平均（Log Average）** | HDR 混合场景；对数域几何平均 |
| **高光优先（Highlight）** | 保护高光；以 85 分位附近测光 |
| **参考图（Reference）** | 目标 = **参考图** 分析得到的平均亮度（无数据时回退 18% 灰） |

所有模式按 **中心加权（0–100%）** 混合全画面与中心区域采样。

### 曝光应用目标

| **应用至** | 行为 |
|:--|:--|
| **色彩管理** | 实时写入 `scene.view_settings.exposure`；AE 期间可调 **参数校正（Gamma）**。**应用** 后烘焙到 CM 并关闭 AE。 |
| **灯光组** | 更新 `ae_value`，通过 **强度** 缩放全部灯光能量（`× 2^EV`）。AE 开启时 **曝光** 滑块锁定。**应用** 后将 EV 乘入 **强度** 并关闭 AE。 |

**灯光组** 模式针对 Cycles 做了防闪烁：要求亮度 **收敛稳定**、步进 **限速**，并根据引擎噪声调整等待时间，避免采样未稳时来回跳动。

### 采样区域预设

| 预设 | 说明 |
|:--|:--|
| **全画面** | 整个视口等权采样 |
| **均衡（Balanced）** | 70% 中心加权（默认） |
| **中心** | 仅测视口中心密集网格 |
| **主体框** | 相机视图用相机框；自由视图用中心 60% 区域 |
| **自定义** | 手动调节 **中心加权** 滑块 |

相机视图下（非「主体框」模式）也会自动裁剪到 **相机边框** 内测光。

### 高级控件（Pro 面板）

| 控件 | 作用 |
|:--|:--|
| **EV 补偿** | 在计算目标上叠加曝光补偿（档） |
| **AE 速度** | EV 向目标靠近的速度（灯光组模式会自适应上限） |
| **参数校正** | AE 驱动色彩管理时的 Gamma 微调 |
| **抖动** | 每帧旋转采样网格，减轻摩尔纹 |
| **快速收敛** | 剩余误差或下一步 EV 小于 **0.1** 档时停止 |
| **实时读数** | 运行中显示 CM 曝光或灯光组 EV |
| **应用（✓）** | 烘焙 AE → CM 曝光或 **强度**，并关闭 AE |

### 推荐工作流

<details>
<summary><b>人像 / 产品（色彩管理路径）</b></summary>

1. 生成灯光 → 视口切 **Rendered**。
2. **应用至**：色彩管理 · 模式：**P60** 或 **截尾平均** · 采样：**均衡**。
3. 用 **EV 补偿** 微调面部明暗。
4. 满意后点 **应用** 烘焙曝光。

</details>

<details>
<summary><b>反复调灯（灯光组路径）</b></summary>

1. **应用至**：灯光组 · 开启 **快速收敛**。
2. 调颜色与 rig 滑块，AE 维持整体亮度稳定。
3. 完成后 **应用**，将 EV 并入 **强度** 继续手动微调。

</details>

<details>
<summary><b>匹配参考图亮度</b></summary>

1. 加载参考图 → **分析**（或 **生成**）。
2. 测光模式：**参考图** — 目标亮度来自参考图分析。
3. 用 **EV 补偿** 精调。

</details>

---

## 📖 详细使用

<details>
<summary><b>主面板</b></summary>

| 控件 | 说明 |
|:--|:--|
| 参考图 | 文件浏览、粘贴、程序生成库 |
| 策略 | **程序生成**的风格预设 + **随机**（每次刷新缩略图） |
| 照明分布 | **程序生成**的参考图 + **随机** |
| 生成 / 分析 / 清除 | 构建 rig · 仅分析 · 删除 rig |
| 调参滑块 | 强度、曝光、AE、距离、旋转、高度、颜色、影调 |
| UI 模式 | **Quick** 精简布局或 **Pro** 完整自动曝光区块 |
| 自动生成 | 定时重新生成（间隔可调） |

</details>

<details>
<summary><b>高级面板</b></summary>

| 控件 | 说明 |
|:--|:--|
| 模式 | 人像 / 场景 / 自动 |
| 目标 / 朝向 | 瞄准点与轴向 |
| 灯光数量 | 1–8 盏 |
| LuxPro | 方向检测开关 |
| 灯光列表 | 单灯颜色、能量、删除 |
| 分析 | 采样色、LuxPro 标签、氛围、色温 |
| 自动曝光 | 应用目标、测光模式、采样预设、速度、烘焙 — 见 [自动曝光](#-自动曝光) |

</details>

<details>
<summary><b>使用建议</b></summary>

- **人像** — 主体尽量居中，避免背景过曝抢方向。
- **硬光 / 分割光** — 解锁滑块后让插件自动写入 **对比度** 与 **阴影**。
- **gel / 霓虹** — **灯光数量 ≥ 3**，确保主光 + 点缀 + 轮廓。
- **方向微调** — 开启 LuxPro，用 **Rotate（旋转）** 整体 orbit 灯架。

</details>

---

## 🗺️ 路线图

- [ ] 视口对比浮层（参考 vs 渲染）
- [ ] 从当前 rig 导出 / 导入预设
- [ ] 镜头列表批量生成
- [ ] 可选 AI 参考标签（优先离线启发式）

---

## 🤝 贡献

运行 `py test_offline.py`（无需 Blender）。可选：`blender --background --python test_blender.py`。UI 或布光行为变更请附截图。

---

## 📄 许可证

[GNU General Public License v3.0 or later](LICENSE)
