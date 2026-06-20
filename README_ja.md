<div align="center">

# ✨ RollLux

**参照画像から Blender のライティングをワンクリックで再現**

*手続き型プリセット · LuxPro 方向 · デュアルトーン gel · ライブ調整 · ビューポートオーバーレイ*

<br>

[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-2ea043)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-5.0%2B-f5792a?logo=blender&logoColor=white)](https://www.blender.org/)
[![Release](https://img.shields.io/github/v/release/AIGODLIKE/RollLux?label=RollLux)](https://github.com/AIGODLIKE/RollLux/releases/latest)
[![Python](https://img.shields.io/badge/python-pure%20%2B%20numpy-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Offline](https://img.shields.io/badge/network-offline%20ready-success)]()

<br>

<a href="README.md">English</a> · <a href="README_zh-CN.md">中文</a> · **日本語**

<br>

<img src="./assets/logo.png" alt="RollLux logo" width="120" onerror="this.style.display='none'">

</div>

---

## はじめに

**RollLux** は **Blender 5.0+** 向けの参照画像ライティングアドオンです。写真を解析し、**キー / フィル / リム / アクセント / 環境光** からなる調整可能なライトリグを自動生成。シネマティック、ポートレート、プロダクト、スタイライズドルックを素早く再現できます。

**ストラテジーのサムネイルも分布ライブラリの参照画像も、すべてコードで手続き的に生成**されます（シェーディング球・グラデーション・光斑など）。固定枚数の素材集ではありません。**ランダム**を押すたびに新しい組み合わせが得られ、名前付きプリセットは同じ生成パイプラインの起点です。

参照画像を読み込み → **Generate** → スライダーでライブ調整。**Cycles / Eevee** 対応、**完全オフライン**、pip 不要。

| | |
|:--|:--|
| **作者** | ACGGIT |
| **Blender** | 5.0.0 以降 |
| **エンジン** | Cycles · Eevee |
| **依存** | なし（Blender 同梱 NumPy） |

---

## ✨ 機能ハイライト

| 機能 | 内容 |
|:--|:--|
| 🎯 **参照解析** | キー / フィル / 環境色、コントラスト、ムード、色温度 |
| 🧭 **LuxPro 方向** | ポートレート向け打光方向（左 / 右 / 上 / 逆光など）と信頼度 |
| 🎨 **デュアルトーン gel** | 青 + マゼンタなど、飽和した 2 色を **アクセント** SPOT として分離 |
| ⚡ **スプリット / ハード光** | シャープな明暗境界 → SPOT キー、弱フィル、コントラスト自動シード |
| 🎛️ **ライブ調整** | 強度、露出、距離、回転、彩度、シャドウ、ハイライト、コントラスト |
| 📸 **自動露出** | Rendered ビューポートサンプリング；TRIM / LOG / P60 測光、EV 補正、高速収束、LIGHT_RIG ベイク |
| 🧩 **Quick / Pro UI** | Quick コンパクトワークフロー、または Pro フルパネル（高度 AE、rig、個別ライト） |
| 🎲 **手続き型プリセット** | ストラテジーサムネ & 分布参照を **コード生成** — ランダムで毎回新しいルック |
| 🗂️ **ストラテジー** | 名前付き起点 + **ランダム** · 手続き型シェーディング球プレビュー · ステップ移動 |
| 🖼️ **分布ライブラリ** | 内蔵参照画像を **手続き合成**（グラデ・光斑・リム・ビネット等） |
| 💡 **1–8 灯** | 色相多様サンプリングでライト数に同期 |
| 🔧 **個別ライト編集** | オン/オフ、色、エネルギー、ソフト、削除 |
| 🪟 **フロート参照** | ビューポートに参照画像を固定 |
| 📋 **クリップボード貼付** | システムクリップボードから画像 |
| 🌐 **3 言語 UI** | English / 中文 / 日本語 |

<details>
<summary><b>📊 手動布光 vs RollLux</b></summary>

| | 手動 | RollLux |
|:--|:--:|:--:|
| 参照写真から開始 | ❌ | ✅ |
| 方向 + 色の自動化 | ❌ | ✅ |
| デュアル gel / アクセント | ❌ | ✅ |
| ランダム生成 | ❌ | ✅ |
| プリセット & 参照の手続き生成 | ❌ | ✅ |
| スライダーライブ更新 | — | ✅ |
| 完全オフライン | ✅ | ✅ |

</details>

---

## 📷 スクリーンショット & デモ

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<strong>参照 → 結果</strong><br><br>
<img src="./assets/demo-before-after.png" alt="Before and after" width="95%"><br>
<em>スプリットライト参照を 3D ヘッドにマッチ</em>
</td>
<td align="center" width="50%">
<strong>デュアルトーン gel</strong><br><br>
<img src="./assets/demo-dual-gel.png" alt="Dual gel lighting" width="95%"><br>
<em>高飽和参照からキー + アクセントを分離</em>
</td>
</tr>
<tr>
<td align="center" width="50%">
<strong>N パネル UI</strong><br><br>
<img src="./assets/demo-panel.png" alt="RollLux panel" width="95%"><br>
<em>プリセット、調整スライダー、LuxPro 表示</em>
</td>
<td align="center" width="50%">
<strong>ワークフロー GIF</strong><br><br>
<img src="./assets/demo-workflow.gif" alt="Workflow GIF" width="95%"><br>
<em>参照読込 → 生成 → 調整</em>
</td>
</tr>
</table>

<sub>📁 キャプチャは <code>./assets/</code> に配置（上記ファイル名）。</sub>

</div>

---

## 🚀 クイックスタート

### インストール

1. [Releases](https://github.com/AIGODLIKE/RollLux/releases/latest) から **`rolllux-5.0.0.zip`** をダウンロード。
2. Blender → **編集 → プリファレンス → 拡張機能を取得 → ▼ → ディスクからインストール…**
3. zip を選択 → **RollLux** を有効化。

<details>
<summary><b>🛠️ ソースからビルド</b></summary>

```bash
cd rolllux
py gen_assets.py    # 任意：サムネイル・参照 PNG 再生成
py build.py         # 出力 -> ../dist/rolllux-<version>.zip
```

</details>

### 基本ワークフロー

1. **3D ビューポート** → **N** → **RollLux** タブ。
2. **参照画像**を読み込みまたは貼り付け（初回は手続き生成のデフォルト画像）。
3. **ストラテジー**を選ぶか **🔄 ランダム** で新しいスタイルを生成。
4. 任意：**照明分布**（手続きライブラリ）を変更、または独自の写真を使用。
5. 被写体を選択 → **Generate Lighting**。
6. **Intensity**、**Contrast**、**Shadows**、**Highlights**、**Saturation** を調整 — ライブ反映。
7. **Advanced** で rig 設定、ライト一覧、LuxPro、分析スウォッチ。

---

## 📖 使い方

<details>
<summary><b>メインパネル</b></summary>

| 項目 | 説明 |
|:--|:--|
| 参照画像 | ブラウザ、貼付、手続き生成ライブラリ |
| ストラテジー | **手続き生成**プリセット + **ランダム**（ロールごとに新サムネ） |
| 照明分布 | **手続き生成**参照画像 + **ランダム** |
| Generate / Analyze / Clear | rig 構築 · 解析のみ · 削除 |
| 調整スライダー | 強度、露出、AE、距離、回転、高さ、色、トーン |
| Auto Generate | タイマー再生成 |

</details>

<details>
<summary><b>Advanced パネル</b></summary>

| 項目 | 説明 |
|:--|:--|
| モード | Portrait / Scene / Auto |
| Aim At / Orient By | ターゲットと軸 |
| Light Count | 1–8 |
| LuxPro | 方向検出 |
| Lights | 個別色、エネルギー、削除 |
| Analysis | サンプル色、LuxPro ラベル、ムード、K |

</details>

<details>
<summary><b>ヒント</b></summary>

- **ポートレート** — 顔を中央に、背景の過曝に注意。
- **ハード / スプリット** — **Contrast** と **Shadows** の自動シードを活用（ロック解除）。
- **gel / ネオン** — **Light Count ≥ 3**（キー + アクセント + リム）。
- **方向** — LuxPro オン、**Rotate** で rig を微調整。

</details>

---

## 🗺️ ロードマップ

- [ ] 参照 vs レンダー比較オーバーレイ
- [ ] 現在の rig からプリセット export / import
- [ ] ショットリスト一括生成
- [ ] オフライン・ヒューリスティックによる参照タグ（将来）

---

## 🤝 コントリビューション

`py test_offline.py` を実行（Blender 不要）。任意：`blender --background --python test_blender.py`。UI / ライティング変更時はスクリーンショットを添付。

---

## 📄 ライセンス

[GNU General Public License v3.0 or later](LICENSE)
