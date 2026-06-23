"""TCP client for the RollLux MCP Bridge Blender addon."""

from __future__ import annotations

import json
import os
import socket
from typing import Any


DEFAULT_HOST = os.environ.get("BLENDER_HOST", "localhost")
DEFAULT_PORT = int(os.environ.get("BLENDER_PORT", "9886"))


class BlenderConnection:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None

    def connect(self) -> bool:
        if self._sock is not None:
            return True
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            self._sock = sock
            return True
        except OSError:
            self._sock = None
            return False

    def close(self) -> None:
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def _recv_json(self) -> dict[str, Any]:
        assert self._sock is not None
        chunks: list[bytes] = []
        self._sock.settimeout(180.0)
        while True:
            chunk = self._sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            data = b"".join(chunks)
            try:
                return json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                continue
        raise RuntimeError("Incomplete or empty response from Blender")

    def send_command(self, command_type: str, params: dict[str, Any] | None = None) -> Any:
        if not self.connect():
            raise ConnectionError(
                f"Cannot connect to Blender MCP bridge at {self.host}:{self.port}. "
                "Open Blender, enable the RollLux MCP Bridge addon, and click Connect."
            )
        assert self._sock is not None
        payload = json.dumps({"type": command_type, "params": params or {}}).encode("utf-8")
        try:
            self._sock.sendall(payload)
            response = self._recv_json()
        except (OSError, json.JSONDecodeError) as exc:
            self.close()
            raise RuntimeError(f"Blender communication error: {exc}") from exc

        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Unknown Blender error"))
        return response.get("result")


_connection: BlenderConnection | None = None


def get_connection() -> BlenderConnection:
    global _connection
    if _connection is None:
        _connection = BlenderConnection()
    elif _connection._sock is None:
        _connection.connect()
    return _connection


def execute_code(code: str) -> str:
    result = get_connection().send_command("execute_code", {"code": code})
    if isinstance(result, dict):
        return str(result.get("result", ""))
    return str(result)
