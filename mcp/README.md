# RollLux MCP

Control RollLux in Blender from **Cursor** or **OpenAI Codex** using natural language — e.g. *「给 Suzanne 打 portrait 光」* or *Light the Cube with golden hour reference*.

> **Requires the full GitHub release** (`rolllux-*.zip` from [Releases](https://github.com/AIGODLIKE/RollLux/releases)). The Extension Platform (*-marketplace.zip*) build does not ship the in-Blender bridge.

---

## Architecture

```
┌─────────────┐   stdio    ┌──────────────────┐   TCP :9886   ┌─────────────────────┐
│ Cursor or   │ ◄────────► │  rolllux_mcp     │ ◄───────────► │ Blender + RollLux   │
│ Codex       │  MCP tools │  (Python package)│  execute_code │ MCP bridge (panel)  │
└─────────────┘            └──────────────────┘               └─────────────────────┘
```

1. **Blender** runs RollLux with the built-in MCP bridge (default port **9886**).
2. **`rolllux_mcp`** exposes MCP tools that send Python snippets to the bridge.
3. **Cursor / Codex** calls those tools from chat.

---

## One-time setup

### 1. Blender — RollLux + bridge

1. Install **`rolllux-5.5.5.zip`** (full release) → Preferences → **Get Extensions** → Install from Disk.
2. Enable **RollLux**.
3. Open **3D Viewport** → **N** → **RollLux** panel.
4. Click **▶ Start MCP** in the panel header (or open the ⚙ menu → confirm port **9886**).
5. Status should show **MCP · 9886** (depressed green).

### 2. Python — MCP server package

```powershell
cd rolllux/mcp
py -m pip install -e .
```

Verify:

```powershell
py -m rolllux_mcp --help
```

### 3. Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `BLENDER_HOST` | `localhost` | Bridge host |
| `BLENDER_PORT` | `9886` | Must match RollLux panel port |

---

## Cursor

### Config

If your workspace root is **`magic-world`** (monorepo), use the repo file:

`.cursor/mcp.json` (already present):

```json
{
  "mcpServers": {
    "rolllux": {
      "command": "cmd",
      "args": ["/c", "py", "-m", "rolllux_mcp"],
      "cwd": "rolllux/mcp",
      "env": {
        "PYTHONPATH": "rolllux/mcp",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9886"
      }
    }
  }
}
```

If you cloned **only** the `rolllux` repo, copy [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) to your workspace `.cursor/mcp.json` and set `cwd` to the absolute path of `rolllux/mcp`.

### Enable

1. **Cursor Settings → MCP** — confirm **rolllux** is listed and enabled.
2. Restart Cursor after first install.
3. Blender open with **Start MCP** running.

### Example session

**You (chat):**

> Check Blender, list mesh objects, then light **Suzanne** with the **portrait** strategy and 4 lights.

**Agent (typical tool chain):**

```
check_blender()
→ { "rolllux_installed": true, "scene": "Scene", ... }

list_scene_objects(limit=20)
→ { "objects": [{ "name": "Suzanne", "type": "MESH" }, ...] }

light_object(
    object_name="Suzanne",
    preset="portrait",
    light_count=4,
    intensity=0.22,
    auto_exposure=true,
)
→ { "ok": true, "lights_created": 4, ... }
```

**You:**

> Clear RollLux and relight the selection with reference preset **golden_hour**.

```
clear_rolllux_lighting()
light_selection(reference_preset="golden_hour", preset="cinematic")
```

---

## OpenAI Codex

Codex reads MCP servers from `~/.codex/config.toml` or a trusted project file `.codex/config.toml`.  
Docs: https://developers.openai.com/codex/mcp

### Option A — CLI

```powershell
cd rolllux/mcp
codex mcp add rolllux -- py -m rolllux_mcp
```

Then set env in `~/.codex/config.toml` (port **9886**, `cwd` = path to `rolllux/mcp`).

### Option B — config file

Copy [`.codex/config.toml.example`](../.codex/config.toml.example):

- Replace `ROLLUX_MCP_CWD` with your absolute `...\rolllux\mcp` path.
- Place at `~/.codex/config.toml` **or** `rolllux/.codex/config.toml` (mark project trusted in Codex).

Example block:

```toml
[mcp_servers.rolllux]
command = "py"
args = ["-m", "rolllux_mcp"]
cwd = "C:/Users/you/magic-world/rolllux/mcp"
enabled = true
tool_timeout_sec = 180

[mcp_servers.rolllux.env]
PYTHONPATH = "."
BLENDER_HOST = "localhost"
BLENDER_PORT = "9886"
```

### Verify in Codex

1. Start a Codex session in the project directory.
2. Run **`/mcp`** — **rolllux** should appear with tools listed.
3. Prompt: *Use check_blender to verify RollLux is connected.*

### Example session

**You:**

> List scene objects and apply **Arcane**-style lighting (teal + amber). I already selected the target mesh in Blender.

**Agent:**

```
list_scene_objects()
light_arcane(intensity=0.22, light_count=4)
```

Style tools (`light_jinx`, `light_arcane`, `light_doraemon`, …) operate on the **active object** — select it in Blender first.

**You:**

> Light **Product_Cube** like an Apple product shot with strong rim.

```
light_object(object_name="Product_Cube", preset="product")
light_apple_product(intensity=0.28, rim_energy=3.6)
```

---

## MCP tools (summary)

| Tool | Purpose |
|------|---------|
| `check_blender` | Connection + RollLux installed? |
| `list_scene_objects` | Mesh-like objects in the scene |
| `light_object` | Main entry — light a **named** object |
| `light_selection` | Light the **active** selection |
| `light_from_left` | Quick left-key rig on selection |
| `clear_rolllux_lighting` | Remove RollLux rig |
| `refresh_strategy_and_distribution` | Random preset + reference roll |
| `light_apple_product` / `light_xiaomi_product` / … | Product looks |
| `light_jinx` / `light_arcane` / `light_doraemon` / … | Stylized looks (active object) |
| `light_vivid_rainbow` / `light_cyberpunk` / … | Color / mood presets |

Full list: `rolllux_mcp/server.py`.

### `light_object` parameters (common)

| Parameter | Example | Notes |
|-----------|---------|-------|
| `object_name` | `"Suzanne"` | Exact Blender name |
| `preset` | `"portrait"`, `"cinematic"`, `"random"` | Strategy |
| `reference_preset` | `"golden_hour"`, `"broad_light"` | Built-in library id |
| `reference_image` | `C:/photos/ref.jpg` | Local file path |
| `light_count` | `3`–`8` | |
| `intensity` | `0.2` | Global multiplier |
| `auto_exposure` | `true` | Viewport AE after generate |
| `clear_existing` | `true` | Clear old rig first |

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| **Cannot connect to Blender bridge** | Blender open? **Start MCP** clicked? Port **9886** in panel matches `BLENDER_PORT`? |
| **RollLux not installed** | Use **full** release zip, not *-marketplace.zip*. |
| **Object not found** | Run `list_scene_objects` — names are case-sensitive. |
| **Style tool does nothing** | Select the target object in Blender (active object). |
| **WinError 10038 in console** | Toggle MCP off/on after extension reload; fixed in 5.5.4+. |
| **Codex: server not listed** | Trust project; check `cwd` path; run `/mcp`. |

Save your `.blend` before automation. MCP executes Python inside Blender.
