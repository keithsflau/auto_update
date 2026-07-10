from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from monitor.dashboard import build_snapshot, load_snapshot, save_snapshot
from monitor.main import collect_all_items, pick_new_items
from monitor.state import load_state, log

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = Flask(__name__)


@app.get("/")
def index():
    return send_from_directory(WEB_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    if filename.startswith("api/"):
        return jsonify({"error": "not found"}), 404
    target = WEB_DIR / filename
    if target.exists() and target.is_file():
        return send_from_directory(WEB_DIR, filename)
    return jsonify({"error": "not found"}), 404


@app.get("/api/data")
def api_data():
    snapshot = load_snapshot()
    if snapshot is None:
        return jsonify({"error": "尚未有資料，請按「重新整理」"}), 404
    return jsonify(snapshot)


@app.post("/api/refresh")
def api_refresh():
    try:
        all_items = collect_all_items()
        state = load_state()
        seen = set(state.get("seen", []))
        new_items = pick_new_items(all_items, seen)
        snapshot = build_snapshot(all_items, new_items)
        save_snapshot(snapshot)
        return jsonify(snapshot)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="香港教育更新儀表板")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args(argv)

    snapshot = load_snapshot()
    if snapshot is None:
        log("儀表板：首次啟動，正在擷取資料…")
        try:
            all_items = collect_all_items()
            state = load_state()
            new_items = pick_new_items(all_items, set(state.get("seen", [])))
            save_snapshot(build_snapshot(all_items, new_items))
        except Exception as exc:  # noqa: BLE001
            log(f"儀表板初始擷取失敗: {exc}")

    print(f"儀表板：http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
