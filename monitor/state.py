from __future__ import annotations

import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

from monitor.config import LOG_FILE, STATE_FILE


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"seen": [], "initialized": False}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    _ensure_parent(STATE_FILE)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def log(message: str) -> None:
    _configure_stdout()
    _ensure_parent(LOG_FILE)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    try:
        print(line)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or "utf-8"
        sys.stdout.buffer.write((line + "\n").encode(enc, errors="replace"))
        sys.stdout.flush()
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()
