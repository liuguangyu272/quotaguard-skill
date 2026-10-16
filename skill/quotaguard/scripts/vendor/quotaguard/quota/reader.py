"""Fail-open orchestration across real quota sources."""

from __future__ import annotations

from typing import Literal

from quotaguard.quota.app_server import AppServerQuotaReader
from quotaguard.quota.models import QuotaStatus
from quotaguard.quota.session import SessionQuotaReader

QuotaSource = Literal["auto", "app-server", "session"]


class QuotaReader:
    def __init__(
        self,
        app_server: AppServerQuotaReader | None = None,
        session: SessionQuotaReader | None = None,
    ) -> None:
        self.app_server = app_server or AppServerQuotaReader()
        self.session = session or SessionQuotaReader()

    def read(self, source: QuotaSource = "auto") -> QuotaStatus:
        warnings: list[str] = []
        if source in {"auto", "app-server"}:
            try:
                return self.app_server.read()
            except Exception as exc:
                warnings.append(f"App Server unavailable: {exc}")
                if source == "app-server":
                    return QuotaStatus.unavailable(warnings)

        if source in {"auto", "session"}:
            try:
                return self.session.read().with_warnings(warnings)
            except Exception as exc:
                warnings.append(f"Session quota unavailable: {exc}")

        return QuotaStatus.unavailable(warnings)

