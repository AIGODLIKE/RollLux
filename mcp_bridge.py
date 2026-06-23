"""Built-in MCP socket bridge for Cursor / external MCP clients."""

from __future__ import annotations

import io
import json
import socket
import threading
import traceback
from contextlib import redirect_stdout

import bpy
from bpy.types import Menu, Operator

from .translations import tr

DEFAULT_PORT = 9886


class RollLuxMCPServer:
    def __init__(self, host: str = "localhost", port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None

    def start(self) -> None:
        if self.running:
            return
        if getattr(bpy.app, "background", False):
            print("RollLux MCP: requires Blender GUI (not background mode)")
            return
        self.running = True
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.running = False
        sock = self.sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
            self.sock = None
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

    def _serve(self) -> None:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock = sock
            sock.bind((self.host, self.port))
            sock.listen(1)
            print(f"RollLux MCP listening on {self.host}:{self.port}")
            while self.running:
                sock.settimeout(1.0)
                try:
                    client, _addr = sock.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if not self.running:
                        break
                    raise
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
        except OSError as exc:
            if self.running:
                print(f"RollLux MCP server error: {exc}")
                traceback.print_exc()
        finally:
            self.running = False
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
            if self.sock is sock:
                self.sock = None

    def _handle(self, client) -> None:
        client.settimeout(None)
        buffer = b""
        try:
            while self.running:
                data = client.recv(8192)
                if not data:
                    break
                buffer += data
                try:
                    command = json.loads(buffer.decode("utf-8"))
                    buffer = b""
                except json.JSONDecodeError:
                    continue

                def run_cmd():
                    try:
                        resp = self.execute(command)
                        client.sendall(json.dumps(resp).encode("utf-8"))
                    except Exception as exc:
                        client.sendall(
                            json.dumps({"status": "error", "message": str(exc)}).encode("utf-8")
                        )
                    return None

                bpy.app.timers.register(run_cmd, first_interval=0.0)
        except Exception:
            pass
        finally:
            try:
                client.close()
            except OSError:
                pass

    def execute(self, command: dict) -> dict:
        cmd_type = command.get("type")
        params = command.get("params") or {}
        if cmd_type == "execute_code":
            code = params.get("code", "")
            namespace = {"bpy": bpy}
            buf = io.StringIO()
            try:
                with redirect_stdout(buf):
                    exec(code, namespace)
            except Exception as exc:
                return {"status": "error", "message": str(exc)}
            return {"status": "success", "result": {"executed": True, "result": buf.getvalue()}}
        if cmd_type == "get_scene_info":
            scene = bpy.context.scene
            return {
                "status": "success",
                "result": {
                    "name": scene.name,
                    "object_count": len(scene.objects),
                    "rolllux": hasattr(bpy.types.Scene, "rolllux"),
                },
            }
        return {"status": "error", "message": f"Unknown command: {cmd_type}"}


_server: RollLuxMCPServer | None = None


def _port(context) -> int:
    try:
        return int(context.scene.rolllux.mcp_port)
    except Exception:
        return DEFAULT_PORT


def is_connected() -> bool:
    return _server is not None and _server.running


def _tag_redraw(context) -> None:
    wm = context.window_manager if context else None
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            area.tag_redraw()


class RLLX_MCP_OT_toggle(Operator):
    bl_idname = "rolllux_mcp.toggle"
    bl_label = "Toggle MCP Service"
    bl_description = "Start or stop the RollLux MCP bridge service"

    def execute(self, context):
        if is_connected():
            bpy.ops.rolllux_mcp.disconnect()
        else:
            bpy.ops.rolllux_mcp.connect()
        _tag_redraw(context)
        return {"FINISHED"}


class RLLX_MCP_OT_connect(Operator):
    bl_idname = "rolllux_mcp.connect"
    bl_label = "Connect MCP"
    bl_description = "Start the RollLux MCP socket server for Cursor"

    def execute(self, context):
        global _server
        port = _port(context)
        if _server is not None:
            _server.stop()
        _server = RollLuxMCPServer(port=port)
        _server.start()
        context.scene.rolllux.mcp_connected = _server.running
        if _server.running:
            self.report({"INFO"}, tr("mcp_msg_connected", port=port))
        else:
            self.report({"WARNING"}, tr("mcp_msg_gui_only"))
        _tag_redraw(context)
        return {"FINISHED"}


class RLLX_MCP_OT_disconnect(Operator):
    bl_idname = "rolllux_mcp.disconnect"
    bl_label = "Disconnect MCP"
    bl_description = "Stop the RollLux MCP socket server"

    def execute(self, context):
        global _server
        if _server is not None:
            _server.stop()
        context.scene.rolllux.mcp_connected = False
        self.report({"INFO"}, tr("mcp_msg_disconnected"))
        _tag_redraw(context)
        return {"FINISHED"}


class RLLX_MT_mcp(Menu):
    bl_idname = "RLLX_MT_mcp"
    bl_label = "MCP Service"

    def draw(self, context):
        settings = context.scene.rolllux
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        if is_connected():
            col.label(
                text=tr("mcp_status_running", port=settings.mcp_port),
                icon="RADIOBUT_ON",
            )
            col.label(text=tr("mcp_status_listening"), icon="LINKED")
        else:
            col.label(text=tr("mcp_status_stopped"), icon="RADIOBUT_OFF")
            col.label(text=tr("mcp_status_idle"), icon="UNLINKED")
        layout.separator()
        col = layout.column(align=True)
        col.prop(settings, "mcp_port")
        col.prop(settings, "mcp_auto_connect", toggle=True)
        layout.separator()
        layout.label(text=tr("mcp_hint"), icon="INFO")


_classes = (
    RLLX_MCP_OT_toggle,
    RLLX_MCP_OT_connect,
    RLLX_MCP_OT_disconnect,
    RLLX_MT_mcp,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    from . import translations
    translations.register_operators_i18n(
        RLLX_MCP_OT_toggle,
        RLLX_MCP_OT_connect,
        RLLX_MCP_OT_disconnect,
    )

    def _auto_connect():
        try:
            scene = bpy.context.scene
            if scene is None or not getattr(scene, "rolllux", None):
                return None
            if scene.rolllux.mcp_auto_connect and not is_connected():
                bpy.ops.rolllux_mcp.connect()
        except Exception as exc:
            print(f"RollLux MCP auto-connect skipped: {exc}")
        return None

    if not getattr(bpy.app, "background", False):
        bpy.app.timers.register(_auto_connect, first_interval=0.5)


def unregister():
    global _server
    if _server is not None:
        _server.stop()
        _server = None
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
