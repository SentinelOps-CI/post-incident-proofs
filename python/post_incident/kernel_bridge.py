"""Bridge to Rust post-incident-kernel with pure-Python fallbacks.

Prefer the Rust binary when available; fall back to equivalent Python
implementations so CI can run without a prebuilt kernel. Both paths must
agree on conformance vectors.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections import defaultdict, deque
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _python_dag_is_acyclic(edges: Sequence[tuple[str, str]]) -> bool:
    nodes: set[str] = set()
    indeg: dict[str, int] = defaultdict(int)
    adj: dict[str, list[str]] = defaultdict(list)
    for a, b in edges:
        nodes.add(a)
        nodes.add(b)
        adj[a].append(b)
        indeg[b] += 1
        indeg.setdefault(a, indeg.get(a, 0))
    q = deque([n for n in nodes if indeg[n] == 0])
    seen = 0
    while q:
        n = q.popleft()
        seen += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    return seen == len(nodes)


def _python_is_retained_subsequence(full: Sequence[str], retained: Sequence[str]) -> bool:
    if not retained:
        return True
    i = 0
    for item in full:
        if item == retained[i]:
            i += 1
            if i == len(retained):
                return True
    return False


@lru_cache(maxsize=1)
def _kernel_bin() -> str | None:
    env = os.environ.get("POST_INCIDENT_KERNEL")
    if env and Path(env).is_file():
        return env
    which = shutil.which("post-incident-kernel")
    if which:
        return which
    # Common cargo target locations
    for rel in (
        "rust/post-incident-kernel/target/release/post-incident-kernel",
        "rust/post-incident-kernel/target/debug/post-incident-kernel",
        "rust/post-incident-kernel/target/release/post-incident-kernel.exe",
        "rust/post-incident-kernel/target/debug/post-incident-kernel.exe",
    ):
        candidate = REPO_ROOT / rel
        if candidate.is_file():
            return str(candidate)
    return None


def _run_kernel(args: list[str], payload: dict) -> dict | None:
    """Invoke Rust kernel. Returns parsed OK payload, or None to trigger Python fallback."""
    binary = _kernel_bin()
    if not binary:
        return None
    try:
        proc = subprocess.run(
            [binary, *args],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    # Fail-closed kernel errors must not be treated as successful checks.
    if parsed.get("status") == "error" or proc.returncode not in (0,):
        return None
    return parsed


def dag_is_acyclic(edges: Sequence[tuple[str, str]]) -> bool:
    payload = {"edges": [{"from": a, "to": b} for a, b in edges]}
    result = _run_kernel(["dag-check"], payload)
    if result is not None and "acyclic" in result:
        return bool(result["acyclic"])
    return _python_dag_is_acyclic(edges)


def is_retained_subsequence(full: Sequence[str], retained: Sequence[str]) -> bool:
    payload = {"full": list(full), "retained": list(retained)}
    result = _run_kernel(["order-check"], payload)
    if result is not None and "preserved" in result:
        return bool(result["preserved"])
    return _python_is_retained_subsequence(full, retained)


def sha256_hex(data: bytes) -> str:
    import base64
    import hashlib

    payload = {"data_b64": base64.b64encode(data).decode("ascii")}
    result = _run_kernel(["digest"], payload)
    if result is not None and "digest" in result:
        return str(result["digest"])
    return "sha256:" + hashlib.sha256(data).hexdigest()
