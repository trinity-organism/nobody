"""Rites: deterministic step sequences, executed identically every time and sealed.

A rite's body declares its liturgy as lines starting with `$ `. Execution stops at
the first failing step. Each step can be sealed into a hash-chained witness file —
"as above, so below": every plan step maps to a trace record, or the rite lies.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path


def parse_steps(concept) -> list:
    return [
        line.strip()[2:].strip()
        for line in concept.body.splitlines()
        if line.strip().startswith("$ ")
    ]


def _last_hash(witness: Path) -> str:
    if not witness.is_file():
        return ""
    lines = [l for l in witness.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        return ""
    try:
        return json.loads(lines[-1]).get("hash", "")
    except json.JSONDecodeError:
        return ""


def _seal(witness: Path, record: dict) -> dict:
    record["prev"] = _last_hash(witness)
    body = json.dumps(record, sort_keys=True)
    record["hash"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    with open(witness, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def verify_witness(witness: Path):
    """Recompute the chain. Returns (ok, records_checked)."""
    if not witness.is_file():
        return True, 0
    prev = ""
    n = 0
    for line in witness.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        claimed = rec.pop("hash", "")
        if rec.get("prev", "") != prev:
            return False, n
        if hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()[:16] != claimed:
            return False, n
        prev = claimed
        n += 1
    return True, n


def run_rite(brain, concept, witness: str = "", timeout: int = 120):
    """Execute a rite. Returns (exit_code, results). Stops at first failure."""
    steps = parse_steps(concept)
    results = []
    wpath = Path(witness) if witness else None
    for idx, cmd in enumerate(steps, start=1):
        try:
            r = subprocess.run(
                cmd,
                shell=True,
                cwd=str(brain.root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            code = r.returncode
            detail = (r.stderr or r.stdout or "").strip().splitlines()
            detail = detail[-1] if detail else ""
        except subprocess.TimeoutExpired:
            code, detail = 124, f"timed out after {timeout}s"
        rec = {
            "rite": concept.name,
            "step": idx,
            "cmd": cmd,
            "exit": code,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        if wpath:
            rec = _seal(wpath, dict(rec))
        results.append({**rec, "detail": detail})
        if code != 0:
            return code, results
    return 0, results
