<div align="center">

# ✨ RollLux

**参照画像から Blender のライティングをワンクリックで再現**

*手続き型プリセット · LuxPro 方向 · ビューポート自動露出 · ライブ調整 · オーバーレイ*

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
| ビューポート自動露出 | ❌ | ✅ |
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
7. 3D ビューを **Rendered** シェーディングに切り替え、**Auto Exposure** をオン（デフォルト ON）— [自動露出](#-自動露出) を参照。
8. パネル上部の **UI Mode** で **Quick**（コンパクト）と **Pro**（AE・rig 全機能）を切替。

---

## 📸 自動露出

RollLux **5.0** のビューポート自動露出（AE）は、3D ビューのピクセルを直接サンプリングし、シーン輝度を目標値付近に保ちます。ディスクへのレンダーや外部ツールは不要です。

### 動作の流れ

1. AE オン中、タイマーでビューポートフレームバッファを読み取り（**Material** または **Rendered** シェーディングが必要。**Rendered** 推奨）。
2. 測光領域で **10×10 サンプルグリッド** を収集。**中心重み** と任意の **グリッドジッター** でモアレ誤読を低減。
3. 輝度に変換し、選択した **測光モード** で集約。
4. 目標との EV 差を **カラーマネジメント露出** または **ライトリグエネルギー**（`Intensity × 2^EV`）に反映。
5. **Apply（✓）** で現在の AE オフセットを **ベイク** し、AE をオフ。

> **ヒント:** ビューポートが Rendered でない場合は手動で切り替えるか、パネルの **Set Rendered** を使用してください。

### Quick と Pro UI

| | **Quick** | **Pro** |
|:--|:--|:--|
| AE 操作 | カメラアイコン + **EV Bias** + **Apply** | 露出行に **AE Mode** も表示 |
| 高度 AE | 非表示 | **Auto Exposure** ボックス全項目：適用先、サンプリング、速度、gamma、ジッター、高速収束、ライブ EV |

パネル上部 **UI Mode** で Quick / Pro を切替。

### 測光モード

| モード | 向いている用途 |
|:--|:--|
| **Average** | 汎用；サンプル領域の平均輝度 |
| **Median** | ノイズ・高コントラスト；外れ値に強い |
| **60th Percentile (P60)** | 中央値よりやや明るめ — ポートレート向け |
| **Trim Mean** | 上下 10% を除外して平均 — 背景が混在するシーン |
| **Log Average** | HDR 寄りの混合；対数域の幾何平均 |
| **Highlight** | ハイライト保護；85 パーセンタイル付近 |
| **Reference** | 目標 = **参照画像** の平均輝度（未取得時は 18% グレー） |

全モードで **Center Weight（0–100%）** により全画面と中心サンプルをブレンド。

### 露出の適用先

| **Apply to** | 動作 |
|:--|:--|
| **Color Management** | `scene.view_settings.exposure` をライブ更新。AE 中は **Parameter Correction（gamma）** も可。**Apply** で CM にベイクして AE オフ。 |
| **Light Rig** | `ae_value` を更新し **Intensity** 経由で全ライトをスケール（`× 2^EV`）。AE 中は **Exposure** スライダー固定。**Apply** で EV を **Intensity** に乗算して AE オフ。 |

**Light Rig** モードは Cycles 向けに輝度 **安定待ち**、適応 **レート制限**、エンジンノイズに応じた待機時間でフリッカーを抑制。

### サンプリング領域プリセット

| プリセット | 説明 |
|:--|:--|
| **Full Frame** | ビューポート全体を等重み |
| **Balanced** | 中心 70% 重み（デフォルト） |
| **Center** | 中心グリッドのみ測光 |
| **Subject Frame** | カメラビューはカメラ枠、自由ビューは中心 60% |
| **Custom** | **Center Weight** スライダー手動 |

カメラビューでは **Subject Frame** 以外でも **カメラ枠** 内に自動クロップして測光。

### コントロール（Pro パネル）

| 項目 | 用途 |
|:--|:--|
| **EV Bias** | 計算目標に加算する露出補正（ストップ） |
| **AE Speed** | EV が目標へ近づく速度（Light Rig は上限を自動調整） |
| **Parameter Correction** | CM 駆動時の gamma 微調整 |
| **Jitter** | フレームごとにグリッド回転 — モアレ低減 |
| **Fast Converge** | 残差または次 EV ステップが **0.1** ストップ未満で停止 |
| **ライブ表示** | 実行中の CM 露出または Light Rig EV |
| **Apply（✓）** | AE を CM 露出または **Intensity** にベイクして AE オフ |

### おすすめワークフロー

<details>
<summary><b>ポートレート / プロダクト（CM 経路）</b></summary>

1. ライト生成 → ビューを **Rendered** に。
2. **Apply to**: Color Management · Mode: **P60** または **Trim Mean** · Sampling: **Balanced**。
3. **EV Bias** で顔の明るさを微調整。
4. 問題なければ **Apply** で露出をベイク。

</details>

<details>
<summary><b>ライトを反復調整（Light Rig 経路）</b></summary>

1. **Apply to**: Light Rig · **Fast Converge** をオン。
2. 色や rig スライダーを触りながら AE が全体輝度を維持。
3. 完了後 **Apply** で EV を **Intensity** に取り込み、手動調整へ。

</details>

<details>
<summary><b>参照画像の明るさに合わせる</b></summary>

1. 参照読込 → **Analyze**（または **Generate**）。
2. AE Mode: **Reference** — 目標輝度は参照解析から。
3. **EV Bias** で仕上げ。

</details>

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
| UI Mode | **Quick** コンパクトまたは **Pro** 全 AE ブロック |
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
| Auto Exposure | 適用先、測光、サンプリング、速度、ベイク — [自動露出](#-自動露出) 参照 |

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
