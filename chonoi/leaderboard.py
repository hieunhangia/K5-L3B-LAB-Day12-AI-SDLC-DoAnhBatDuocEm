"""Mở rộng Leaderboard cục bộ top 10 (TICKET-04, contract v1.3).

Lưu nguyên tử {"entries": [{"name", "score", "days_completed", "seed"}]}.
Sắp điểm giảm dần; khi hòa, mục ghi trước đứng trước (kể cả sau khi mở lại).
"""

from __future__ import annotations

import json
import os
import tempfile

from .errors import BadInput

DEFAULT_LEADERBOARD_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".chonoi_leaderboard.json",
)
MAX_ENTRIES = 10


def validate_player_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise BadInput("--player-name phải là chuỗi Unicode không rỗng")
    return name


def load_leaderboard(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được leaderboard {path}: {e}")
    if not isinstance(data, dict) or "entries" not in data or not isinstance(data["entries"], list):
        raise BadInput("file leaderboard phải có dạng {'entries': [...]}")
    out = []
    for i, e in enumerate(data["entries"]):
        if not isinstance(e, dict) or not {"name", "score", "days_completed", "seed"} <= set(e):
            raise BadInput(f"entries[{i}] thiếu trường bắt buộc")
        validate_player_name(e["name"])
        out.append({
            "name": e["name"],
            "score": int(e["score"]),
            "days_completed": int(e["days_completed"]),
            "seed": int(e["seed"]),
        })
    return sorted(out, key=lambda x: -x["score"])[:MAX_ENTRIES]


def save_leaderboard(path: str, entries: list[dict]):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    payload = {"entries": sorted(entries, key=lambda x: -int(x["score"]))[:MAX_ENTRIES]}
    fd, tmp = tempfile.mkstemp(prefix=".lb-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def record_entry(store_path: str, name: str, score: int, days_completed: int, seed: int) -> list[dict]:
    validate_player_name(name)
    entries = load_leaderboard(store_path)
    entries.append({
        "name": name,
        "score": int(score),
        "days_completed": int(days_completed),
        "seed": int(seed),
    })
    entries.sort(key=lambda x: -int(x["score"]))
    entries = entries[:MAX_ENTRIES]
    save_leaderboard(store_path, entries)
    return entries


def export_leaderboard(out_path: str, store_path: str | None = None) -> list[dict]:
    src = store_path or DEFAULT_LEADERBOARD_PATH
    entries = load_leaderboard(src)
    save_leaderboard(out_path, entries)
    return entries
