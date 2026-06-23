# RollLux MCP Bridge — minimal socket server for Cursor / MCP clients.
# RollLux 5.5+ includes this bridge in the main extension (header button).
# This file remains for manual install if you use an older RollLux build.

bl_info = {
    "name": "RollLux MCP Bridge",
    "author": "ACGGIT",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > RollLux MCP",
    "description": "Socket bridge so RollLux MCP can run bpy commands in Blender",
    "category": "System",
}

import io
import json
import socket
import threading
import traceback
from contextlib import redirect_stdout

import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import AddonPreferences, Operator, Panel

DEFAULT_PORT = 9886


class RollLuxMCPServer:
    def __init__(self, host="localhost", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.running = False
        self.sock = None
        self.thread = None

    def start(self):
        if self.running:
            return
        if getattr(bpy.app, "background", False):
            print("RollLux MCP Bridge: requires Blender GUI (not background mode)")
            return
        self.running = True
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

    def _serve(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            print(f"RollLux MCP Bridge listening on {self.host}:{self.port}")
            while self.running:
                self.sock.settimeout(1.0)
                try:
                    client, _addr = self.sock.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=self._handle, args=(client,), daemon=True).start()
        except Exception as exc:
            print(f"RollLux MCP Bridge server error: {exc}")
            traceback.print_exc()
        finally:
            self.running = False

    def _handle(self, client):
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

    def execute(self, command):
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


_server = RollLuxMCPServer()


class RLLX_MCP_OT_connect(Operator):
    bl_idname = "rolllux_mcp.connect"
    bl_label = "Connect MCP Bridge"
    bl_description = "Start the RollLux MCP socket server"

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        global _server
        _server.stop()
        _server = RollLuxMCPServer(port=int(prefs.port))
        _server.start()
        prefs.is_connected = True
        self.report({"INFO"}, f"RollLux MCP Bridge on port {prefs.port}")
        return {"FINISHED"}


class RLLX_MCP_OT_disconnect(Operator):
    bl_idname = "rolllux_mcp.disconnect"
    bl_label = "Disconnect MCP Bridge"

    def execute(self, context):
        global _server
        _server.stop()
        context.preferences.addons[__name__].preferences.is_connected = False
        self.report({"INFO"}, "RollLux MCP Bridge stopped")
        return {"FINISHED"}


class RLLX_MCP_AddonPreferences(AddonPreferences):
    bl_idname = __name__

    port: IntProperty(name="Port", default=DEFAULT_PORT, min=1024, max=65535)
    is_connected: BoolProperty(name="Connected", default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "port")
        layout.label(text="Default MCP port: 9877 (set BLENDER_PORT in Cursor if changed)")


class RLLX_MCP_PT_panel(Panel):
    bl_label = "RollLux MCP"
    bl_idname = "RLLX_MCP_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RollLux MCP"

    def draw(self, context):
        prefs = context.preferences.addons[__name__].preferences
        layout = self.layout
        rolllux_ok = hasattr(bpy.types.Scene, "rolllux")
        layout.label(text="RollLux: OK" if rolllux_ok else "RollLux: not enabled", icon="CHECKMARK" if rolllux_ok else "ERROR")
        if prefs.is_connected:
            layout.operator("rolllux_mcp.disconnect", icon="CANCEL")
            layout.label(text=f"Port {prefs.port} — waiting for Cursor")
        else:
            layout.operator("rolllux_mcp.connect", icon="LINKED")


classes = (
    RLLX_MCP_AddonPreferences,
    RLLX_MCP_OT_connect,
    RLLX_MCP_OT_disconnect,
    RLLX_MCP_PT_panel,
)


def register():
    if hasattr(bpy.types, "RLLX_MT_mcp"):
        print("RollLux MCP Bridge: built into RollLux extension — standalone addon skipped.")
        return
    for cls in classes:
        bpy.utils.register_class(cls)

    def _auto_connect():
        try:
            prefs = bpy.context.preferences.addons[__name__].preferences
            if not prefs.is_connected:
                bpy.ops.rolllux_mcp.connect()
        except Exception as exc:
            print(f"RollLux MCP Bridge auto-connect skipped: {exc}")
        return None

    if not getattr(bpy.app, "background", False):
        bpy.app.timers.register(_auto_connect, first_interval=0.5)


def unregister():
    global _server
    _server.stop()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
