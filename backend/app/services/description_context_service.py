from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from app.config import DESCRIPTION_DATA_DIR


@dataclass
class DescriptionRecord:
    name: str
    normalized_name: str
    category: str
    summary: str
    best_time_hint: str
    entry_fee: str
    source_url: str
    aliases: list[str]


_INDEX_READY = False
_RECORDS: list[DescriptionRecord] = []
_ALIAS_TO_RECORD_INDEXES: dict[str, list[int]] = {}
_ALL_ALIASES: list[tuple[str, int]] = []


def _normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_text(text: str, max_len: int = 420) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text[:max_len].rstrip()


def _extract_slug(url: str) -> str:
    parts = (url or "").rstrip("/").split("/")
    if not parts:
        return ""
    return parts[-1]


def _best_time_hint(data: dict[str, Any], category: str) -> str:
    timing = data.get("timing_info")
    if isinstance(timing, str) and timing.strip():
        return _clean_text(timing, max_len=120)
    category_lower = (category or "").lower()
    if "beach" in category_lower:
        return "Late afternoon or sunset is usually best."
    if "waterfall" in category_lower:
        return "Morning visits are typically more comfortable."
    if "fort" in category_lower:
        return "Visit in cooler morning or late afternoon hours."
    return "Visit during open hours and avoid peak heat."


def _load_record(path: Path) -> DescriptionRecord | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if isinstance(data, dict) and data.get("error"):
        return None

    metadata = data.get("metadata") or {}
    heading = str(metadata.get("main_heading") or metadata.get("page_title") or "")
    url = str(data.get("url") or "")
    slug = _extract_slug(url) or path.stem
    name = heading.strip() or slug.replace("-", " ").title()
    desc = str(data.get("description") or "")
    headers = data.get("headers") or []
    header_line = ""
    if isinstance(headers, list) and headers:
        header_line = " ".join(str(x) for x in headers[:2])
    summary = _clean_text(desc or header_line or name)
    category = str(data.get("category") or path.parent.name)
    entry_fee = _clean_text(str(data.get("entry_fee") or "Not specified"), max_len=80)

    aliases_raw = [name, heading, slug, path.stem]
    aliases = sorted({_normalize(a) for a in aliases_raw if _normalize(a)})
    if not aliases:
        return None

    return DescriptionRecord(
        name=name,
        normalized_name=_normalize(name),
        category=category,
        summary=summary,
        best_time_hint=_best_time_hint(data, category),
        entry_fee=entry_fee,
        source_url=url,
        aliases=aliases,
    )


def _build_index() -> None:
    global _INDEX_READY
    if _INDEX_READY:
        return

    records: list[DescriptionRecord] = []
    alias_map: dict[str, list[int]] = {}
    all_aliases: list[tuple[str, int]] = []

    for path in DESCRIPTION_DATA_DIR.rglob("*.json"):
        rec = _load_record(path)
        if not rec:
            continue
        idx = len(records)
        records.append(rec)
        for alias in rec.aliases:
            alias_map.setdefault(alias, []).append(idx)
            all_aliases.append((alias, idx))

    _RECORDS.extend(records)
    _ALIAS_TO_RECORD_INDEXES.update(alias_map)
    _ALL_ALIASES.extend(all_aliases)
    _INDEX_READY = True


def _best_match_index(place_name: str) -> tuple[int | None, float]:
    _build_index()
    query = _normalize(place_name)
    if not query:
        return None, 0.0

    if query in _ALIAS_TO_RECORD_INDEXES:
        return _ALIAS_TO_RECORD_INDEXES[query][0], 1.0

    best_idx = None
    best_score = 0.0
    for alias, idx in _ALL_ALIASES:
        if not alias:
            continue
        score = SequenceMatcher(None, query, alias).ratio()
        if score > best_score:
            best_idx = idx
            best_score = score
    if best_score < 0.72:
        return None, best_score
    return best_idx, best_score


def get_place_context(place_name: str, categories: list[str] | None = None) -> dict[str, Any]:
    idx, score = _best_match_index(place_name)
    if idx is None:
        return {
            "matched": False,
            "name": place_name,
            "summary": "",
            "best_time_hint": "",
            "entry_fee": "",
            "source_url": "",
            "match_score": round(float(score), 3),
        }

    rec = _RECORDS[idx]
    return {
        "matched": True,
        "name": rec.name,
        "category": rec.category,
        "summary": rec.summary,
        "best_time_hint": rec.best_time_hint,
        "entry_fee": rec.entry_fee,
        "source_url": rec.source_url,
        "match_score": round(float(score), 3),
        "input_categories": categories or [],
    }


def get_many_place_contexts(places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for place in places:
        output.append(
            get_place_context(
                str(place.get("name", "")),
                categories=place.get("categories") if isinstance(place.get("categories"), list) else [],
            )
        )
    return output
