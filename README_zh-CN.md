<div align="center">

# ✨ RollLux

**一键让 Blender 场景灯光匹配参考图**

*程序生成预设 · LuxPro 方向 · 双色 gel 光 · 实时调参 · 视口浮层参考*

<br>

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-2ea043)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0%2B-f5792a?logo=blender&logoColor=white)](https://www.blender.org/)
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
| 📸 **自动曝光** | 视口渲染/材质模式下 AE（可选） |
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

1. 获取 **`rolllux-4.0.0.zip`** 扩展包。
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
7. 展开 **Advanced（高级）** 查看 rig 设置、灯光列表、LuxPro 方向与分析色块。

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
