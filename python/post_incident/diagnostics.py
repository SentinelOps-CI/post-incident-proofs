"""Stable JSON diagnostics. Fail closed: never invent pass."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    PASS = "pass"
    ERROR = "error"
    INDETERMINATE = "indeterminate"


@dataclass
class Diagnostic:
    status: Status
    code: str
    path: str
    message: str
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class Report:
    command: str
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.diagnostics) and all(
            d.status == Status.PASS for d in self.diagnostics
        )

    def add(self, diag: Diagnostic) -> None:
        self.diagnostics.append(diag)

    def to_dict(self) -> dict[str, Any]:
        diagnostics = list(self.diagnostics)
        overall = Status.PASS
        for d in diagnostics:
            if d.status == Status.ERROR:
                overall = Status.ERROR
                break
            if d.status == Status.INDETERMINATE and overall == Status.PASS:
                overall = Status.INDETERMINATE
        if not diagnostics:
            # Fail closed without mutating report state.
            overall = Status.ERROR
            diagnostics = [
                Diagnostic(
                    status=Status.ERROR,
                    code="no_diagnostics",
                    path="",
                    message="Fail closed: validator produced no diagnostics",
                )
            ]
        return {
            "command": self.command,
            "status": overall.value,
            "diagnostics": [d.to_dict() for d in diagnostics],
        }

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"

    def exit_code(self) -> int:
        data = self.to_dict()
        return 0 if data["status"] == Status.PASS.value else 1
