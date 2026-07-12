from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateItem:
    category: str
    item_id: str
    title: str
    url: str
    date: str = ""
    summary: str = ""
    subcategory: str = ""
    level: str = ""

    def fingerprint(self) -> str:
        return f"{self.category}:{self.item_id}"
