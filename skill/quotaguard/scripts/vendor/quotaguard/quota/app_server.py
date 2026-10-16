"""Read Codex quota through the documented App Server JSONL protocol."""

from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Sequence

from quotaguard.quota.models import QuotaStatus, normalize_quota_payload


class AppServerError(RuntimeError):
    """A concise, recoverable App Server sensing failure."""


def find_codex_executable() -> str:
    override = os.environ.get("QUOTAGUARD_CODEX_COMMAND")
    if override:
        return override

    executable = shutil.which("codex.exe")
    if executable:
        return executable

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates = sorted(
            Path(local_app_data).glob("OpenAI/Codex/bin/*/codex.exe"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return str(candidates[0])

    executable = shutil.which("codex")
    if executable:
        return executable
    raise AppServerError("Codex executable was not found")


class AppServerQuotaReader:
    def __init__(
        self,
        timeout: float = 12.0,
        command: Sequence[str] | None = None,
    ) -> None:
        self.timeout = timeout
        self.command = list(command) if command else None

    @staticmethod
    def _send(proc: subprocess.Popen[str], message: dict[str, Any]) -> None:
        if proc.stdin is None:
            raise AppServerError("App Server stdin is unavailable")
        proc.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
        proc.stdin.flush()

    @staticmethod
    def _wait_for_id(
        messages: "queue.Queue[dict[str, Any]]",
        request_id: int,
        deadline: float,
        proc: subprocess.Popen[str],
    ) -> dict[str, Any]:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AppServerError(
                    f"timed out waiting for App Server request {request_id}"
                )
            try:
                message = messages.get(timeout=min(remaining, 0.25))
            except queue.Empty:
                if proc.poll() is not None:
                    raise AppServerError(
                        f"App Server exited before request {request_id} completed"
                    )
                continue
            if message.get("id") == request_id:
                return message

    def read(self) -> QuotaStatus:
        command = self.command or [
            find_codex_executable(),
            "app-server",
            "--listen",
            "stdio://",
        ]
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                creationflags=creationflags,
            )
        except (OSError, ValueError) as exc:
            raise AppServerError(f"cannot start App Server: {exc}") from exc

        messages: "queue.Queue[dict[str, Any]]" = queue.Queue()
        stderr_lines: list[str] = []

        def read_stdout() -> None:
            assert proc.stdout is not None
            for line in proc.stdout:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(value, dict):
                    messages.put(value)

        def read_stderr() -> None:
            assert proc.stderr is not None
            for line in proc.stderr:
                if len(stderr_lines) < 40:
                    stderr_lines.append(line.strip())

        threading.Thread(target=read_stdout, daemon=True).start()
        threading.Thread(target=read_stderr, daemon=True).start()
        deadline = time.monotonic() + self.timeout

        try:
            self._send(
                proc,
                {
                    "method": "initialize",
                    "id": 1,
                    "params": {
                        "clientInfo": {
                            "name": "quotaguard",
                            "title": "QuotaGuard",
                            "version": "0.1.0",
                        }
                    },
                },
            )
            initialized = self._wait_for_id(messages, 1, deadline, proc)
            if initialized.get("error"):
                raise AppServerError(
                    f"initialize failed: {initialized['error'].get('message', initialized['error'])}"
                )

            self._send(proc, {"method": "initialized", "params": {}})
            self._send(proc, {"method": "account/rateLimits/read", "id": 2})
            response = self._wait_for_id(messages, 2, deadline, proc)
            if response.get("error"):
                raise AppServerError(
                    "quota request failed: "
                    + str(response["error"].get("message", response["error"]))
                )
            result = response.get("result")
            if not isinstance(result, dict):
                raise AppServerError("quota response did not contain an object result")
            return normalize_quota_payload(result, source="app_server")
        except AppServerError:
            raise
        except Exception as exc:
            detail = next((line for line in reversed(stderr_lines) if line), "")
            suffix = f" ({detail})" if detail else ""
            raise AppServerError(f"App Server protocol failed: {exc}{suffix}") from exc
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()


