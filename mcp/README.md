# RollLux MCP

Natural-language lighting in Blender via Cursor. Say e.g. **「给 Suzanne 打光」** or **「Light the Cube with portrait preset」**.

## One-time setup

### 1. Blender extensions

1. Install **RollLux** (`rolllux-5.5.3.zip`) — Preferences → Get Extensions → Install from Disk.
2. Install **RollLux MCP Bridge** (不需要 BlenderMCP)：
   - **编辑 → 偏好设置 → 插件**（Add-ons，不是 Get Extensions）
   - 右上角 **Install from Disk…**
   - 选择：`rolllux/mcp/bridge_addon.py`
   - 搜索 **RollLux MCP Bridge** → 勾选启用
3. 回到 3D 视口，按 **N** 打开侧栏 → 标签页 **RollLux MCP**（不是 BlenderMCP）
4. 点击 **Connect MCP Bridge**（启用插件后会尝试自动连接）

### 2. MCP Python package

```powershell
cd rolllux/mcp
py -m pip install -e .
```

### 3. Cursor

Project `.cursor/mcp.json` is already configured. Restart Cursor after install.

### 4. Connect

1. Open Blender (with your scene).
2. Press **N** → sidebar tab **RollLux MCP** → **Connect MCP Bridge**.
3. In Cursor, ask: *「给 Monkey 打光」* — the agent calls `light_object`.

## MCP tools

| Tool | Purpose |
|------|---------|
| `check_blender` | Connection + RollLux status |
| `list_scene_objects` | List mesh targets |
| `light_object` | Main: light a named object |
| `clear_rolllux_lighting` | Remove RollLux rig |

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `BLENDER_HOST` | `localhost` | Bridge host |
| `BLENDER_PORT` | `9877` | Bridge port (change in addon prefs + env) |

Compatible with **BlenderMCP** on port 9876: set `BLENDER_PORT=9876` if you prefer that bridge (still use RollLux MCP tools for lighting).

## Troubleshooting

- **Cannot connect** — Blender open? Bridge connected? Port matches?
- **RollLux not enabled** — Install/enable the RollLux extension.
- **Object not found** — Run `list_scene_objects` for exact names.
- Save your `.blend` before automation; MCP runs Python inside Blender.
