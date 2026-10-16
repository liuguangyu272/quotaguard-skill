"""Stable internal model for changing Codex quota payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


class QuotaParseError(ValueError):
    """Raised when a candidate payload has no usable quota window."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get(mapping: dict[str, Any], camel: str, snake: str) -> Any:
    return mapping.get(camel, mapping.get(snake))


def _clamp_percent(value: Any) -> float:
    if isinstance(value, bool):
        raise QuotaParseError("percentage cannot be boolean")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise QuotaParseError(f"invalid percentage: {value!r}") from exc
    return max(0.0, min(100.0, number))


@dataclass(frozen=True)
class QuotaWindow:
    used_percent: float
    window_minutes: int | None
    resets_at: int | None

    @property
    def remaining_percent(self) -> float:
        return max(0.0, 100.0 - self.used_percent)

    def to_dict(self) -> dict[str, Any]:
        return {
            "used_percent": self.used_percent,
            "remaining_percent": self.remaining_percent,
            "window_minutes": self.window_minutes,
            "resets_at": self.resets_at,
        }


@dataclass(frozen=True)
class QuotaStatus:
    five_hour: QuotaWindow | None
    weekly: QuotaWindow | None
    source: str
    timestamp: str = field(default_factory=utc_now)
    quota_unknown: bool = False
    warnings: tuple[str, ...] = ()
    limit_id: str | None = None

    @classmethod
    def unavailable(cls, warnings: list[str] | tuple[str, ...] = ()) -> "QuotaStatus":
        return cls(
            five_hour=None,
            weekly=None,
            source="unavailable",
            quota_unknown=True,
            warnings=tuple(warnings),
        )

    def with_warnings(self, warnings: list[str]) -> "QuotaStatus":
        return QuotaStatus(
            five_hour=self.five_hour,
            weekly=self.weekly,
            source=self.source,
            timestamp=self.timestamp,
            quota_unknown=self.quota_unknown,
            warnings=tuple(warnings) + self.warnings,
            limit_id=self.limit_id,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "five_hour": self.five_hour.to_dict() if self.five_hour else None,
            "weekly": self.weekly.to_dict() if self.weekly else None,
            "source": self.source,
            "timestamp": self.timestamp,
            "quota_unknown": self.quota_unknown,
            "warnings": list(self.warnings),
            "limit_id": self.limit_id,
        }


def _normalize_window(raw: Any) -> QuotaWindow | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise QuotaParseError("quota window must be an object")
    used = _get(raw, "usedPercent", "used_percent")
    minutes = _get(raw, "windowDurationMins", "window_minutes")
    resets = _get(raw, "resetsAt", "resets_at")
    used_percent = _clamp_percent(used)
    try:
        window_minutes = int(minutes) if minutes is not None else None
        resets_at = int(resets) if resets is not None else None
    except (TypeError, ValueError) as exc:
        raise QuotaParseError("window duration and reset must be integers") from exc
    return QuotaWindow(used_percent, window_minutes, resets_at)


def _select_bucket(payload: dict[str, Any]) -> dict[str, Any]:
    by_id = _get(payload, "rateLimitsByLimitId", "rate_limits_by_limit_id")
    if isinstance(by_id, dict) and by_id:
        candidate = by_id.get("codex")
        if isinstance(candidate, dict):
            return candidate
        first = next((value for value in by_id.values() if isinstance(value, dict)), None)
        if first is not None:
            return first

    single = _get(payload, "rateLimits", "rate_limits")
    if isinstance(single, dict):
        return single
    return payload


def normalize_quota_payload(
    payload: dict[str, Any], *, source: str, observed_at: str | None = None
) -> QuotaStatus:
    if not isinstance(payload, dict):
        raise QuotaParseError("quota payload must be an object")
    bucket = _select_bucket(payload)
    primary = _normalize_window(bucket.get("primary"))
    secondary = _normalize_window(bucket.get("secondary"))
    windows = [window for window in (primary, secondary) if window is not None]
    if not windows:
        raise QuotaParseError("no usable primary or secondary quota window")

    five_hour = next((item for item in windows if item.window_minutes == 300), primary)
    weekly = next((item for item in windows if item.window_minutes == 10080), secondary)
    if five_hour is weekly and len(windows) == 1:
        if five_hour and five_hour.window_minutes == 10080:
            five_hour, weekly = None, five_hour
        elif five_hour and five_hour.window_minutes == 300:
            weekly = None

    limit_id = _get(bucket, "limitId", "limit_id")
    return QuotaStatus(
        five_hour=five_hour,
        weekly=weekly,
        source=source,
        timestamp=observed_at or utc_now(),
        quota_unknown=five_hour is None,
        limit_id=str(limit_id) if limit_id is not None else None,
    )

