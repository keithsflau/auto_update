from __future__ import annotations

import argparse
import sys

from monitor.config import INITIAL_RUN_NOTIFY
from monitor.models import UpdateItem
from monitor.sources.edb_circular import fetch_edb_circular_items
from monitor.sources.edb_news import fetch_edb_news_items
from monitor.sources.qef import fetch_qef_items
from monitor.sources.steam_competition import fetch_steam_competition_items
from monitor.sources.tcs_calendar import fetch_tcs_teacher_items
from monitor.state import load_state, log, save_state
from monitor.dashboard import build_snapshot, save_snapshot
from monitor.notify import notify_items, send_test_notification
from monitor.tcs_email import maybe_send_tcs_daily_email


def collect_all_items() -> list[UpdateItem]:
    collectors = [
        fetch_steam_competition_items,
        fetch_tcs_teacher_items,
        fetch_qef_items,
        fetch_edb_circular_items,
        fetch_edb_news_items,
    ]

    found: dict[str, UpdateItem] = {}
    for collector in collectors:
        try:
            for item in collector():
                found[item.fingerprint()] = item
        except Exception as exc:  # noqa: BLE001 - keep monitor running
            log(f"來源 {collector.__name__} 失敗: {exc}")
    return list(found.values())


def pick_new_items(all_items: list[UpdateItem], seen: set[str]) -> list[UpdateItem]:
    return [item for item in all_items if item.fingerprint() not in seen]


def run(force_notify: bool = False, dry_run: bool = False) -> int:
    state = load_state()
    seen = set(state.get("seen", []))
    initialized = bool(state.get("initialized"))

    all_items = collect_all_items()
    new_items = pick_new_items(all_items, seen)

    log(f"檢查完成：共 {len(all_items)} 項，新增 {len(new_items)} 項")

    should_notify = new_items and (force_notify or INITIAL_RUN_NOTIFY or initialized)
    if new_items and not should_notify:
        log("首次執行：已記錄現有項目，不發送通知（可在 .env 設 INITIAL_RUN_NOTIFY=true）")

    if should_notify and not dry_run:
        sent = notify_items(new_items)
        log(f"已發送 {sent} 則通知")
    elif dry_run and new_items:
        for item in new_items:
            log(f"[DRY RUN] {item.category} | {item.title} | {item.url}")

    tcs_courses = [item for item in all_items if item.category == "tcs_teacher"]
    try:
        maybe_send_tcs_daily_email(tcs_courses, state, dry_run=dry_run)
    except Exception as exc:  # noqa: BLE001
        log(f"TCS 每日電郵失敗: {exc}")

    seen.update(item.fingerprint() for item in all_items)
    save_state({"seen": sorted(seen), "initialized": True})
    save_snapshot(build_snapshot(all_items, new_items))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="香港教育更新監察 + 通知")
    parser.add_argument("--dry-run", action="store_true", help="只檢查，不發通知")
    parser.add_argument("--force-notify", action="store_true", help="即使是首次執行也發通知")
    parser.add_argument("--test-notify", action="store_true", help="發送測試通知")
    parser.add_argument("--test-tcs-email", action="store_true", help="發送 TCS 每日電郵測試")
    args = parser.parse_args(argv)
    try:
        if args.test_notify:
            channels = send_test_notification()
            log(f"測試通知已發送：{', '.join(channels)}")
            return 0
        if args.test_tcs_email:
            all_items = collect_all_items()
            tcs_courses = [item for item in all_items if item.category == "tcs_teacher"]
            state = load_state()
            state.pop("last_tcs_daily_email", None)
            maybe_send_tcs_daily_email(tcs_courses, state, dry_run=False)
            save_state(state)
            return 0
        return run(force_notify=args.force_notify, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001
        log(f"執行失敗: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
