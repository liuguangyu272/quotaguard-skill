"""Best-effort quota fallback from recent Codex session JSONL tails."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator

from quotaguard.quota.models import (
    QuotaParseError,
    QuotaStatus,
    normalize_quota_payload,
)


class SessionQuotaError(RuntimeError):
    """No usable quota snapshot was found in bounded session data."""


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def _tail_lines(path: Path, max_bytes: int) -> Iterator[str]:
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        start = max(0, size - max_bytes)
        handle.seek(start)
        data = handle.read()
    if start:
        newline = data.find(b"\n")
        data = data[newline + 1 :] if newline >= 0 else b""
    text = data.decode("utf-8", errors="replace")
    yield from reversed(text.splitlines())


class SessionQuotaReader:
    def __init__(
        self,
        codex_home: Path | None = None,
        max_files: int = 8,
        max_bytes_per_file: int = 2 * 1024 * 1024,
    ) -> None:
        self.codex_home = codex_home or default_codex_home()
        self.max_files = max_files
        self.max_bytes_per_file = max_bytes_per_file

    def _recent_files(self) -> list[Path]:
        sessions = self.codex_home / "sessions"
        if not sessions.is_dir():
            raise SessionQuotaError(f"session directory not found: {sessions}")
        try:
            files = list(sessions.rglob("*.jsonl"))
            files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
        except OSError as exc:
            raise SessionQuotaError(f"cannot enumerate session files: {exc}") from exc
        return files[: self.max_files]

    @staticmethod
    def _candidate(record: dict[str, Any]) -> tuple[dict[str, Any], str | None] | None:
        payload = record.get("payload")
        if not isinstance(payload, dict):
            return None
        rate_limits = payload.get("rate_limits")
        if not isinstance(rate_limits, dict):
            return None
        observed_at = record.get("timestamp")
        return {"rate_limits": rate_limits}, str(observed_at) if observed_at else None

    def read(self) -> QuotaStatus:
        errors: list[str] = []
        for path in self._recent_files():
            try:
                lines = _tail_lines(path, self.max_bytes_per_file)
                for line in lines:
                    if '"rate_limits"' not in line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(record, dict):
                        continue
                    candidate = self._candidate(record)
                    if not candidate:
                        continue
                    payload, observed_at = candidate
                    try:
                        return normalize_quota_payload(
                            payload,
                            source="session_jsonl",
                            observed_at=observed_at,
                        )
                    except QuotaParseError as exc:
                        errors.append(f"{path.name}: {exc}")
            except OSError as exc:
                errors.append(f"{path.name}: {exc}")
        detail = f"; last error: {errors[-1]}" if errors else ""
        raise SessionQuotaError(f"no recent session quota snapshot found{detail}")


