"""Soak headless nhiều ngày liên tiếp trong một tiến trình (TICKET-04, contract v1.3).

Chạy:
    python3 -m chonoi.soak --seed 7 --days 10 --out docs/proof/phase-4/soak.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
import time

from .contract import load_contract
from .errors import BadInput
from .ids import IdAllocator, id_key
from .inputs import InputState
from .rng import Streams
from .sim.day import DaySim


def _dir_toward(src, dst):
    dx = dst[0] - src[0]
    dy = dst[1] - src[1]
    d = math.hypot(dx, dy)
    if d <= 1e-6:
        return (0.0, 0.0)
    return (dx / d, dy / d)


class _SoakBot:
    """Bot tất định chơi lặp Ngày 1..N (D1..D5 xoay vòng)."""

    def __init__(self, tuning: dict):
        self.tuning = tuning
        self._last_interact = False
        self._last_shop_done = False

    def next_input(self, snap: dict, phase: str) -> InputState:
        move = (0.0, 0.0)
        edges = set()
        buy = None

        if phase == "gather":
            pos = snap["player"]["pos"]
            ready_nodes = [n for n in snap["nodes"] if n["ready"]]
            if snap["hold_count"] >= 2 or snap["time_left_ticks"] < 2000 or snap["player"]["hp"] <= 1 or not ready_nodes:
                dock = self.tuning["gather"]["dock_pos"]
                if math.dist(pos, dock) <= float(self.tuning["gather"]["dock_radius"]) - 0.1:
                    if not self._last_interact:
                        edges.add("interact")
                        self._last_interact = True
                else:
                    move = _dir_toward(pos, dock)
                    self._last_interact = False
            else:
                target = ready_nodes[0]
                if math.dist(pos, target["pos"]) <= float(self.tuning["gather"]["interact_radius"]) - 0.1:
                    if not self._last_interact:
                        edges.add("interact")
                        self._last_interact = True
                else:
                    move = _dir_toward(pos, target["pos"])
                    self._last_interact = False
            self._last_shop_done = False

        elif phase == "quan":
            pos = snap["player"]["pos"]
            radius = float(self.tuning["quan"]["interact_radius"]) - 0.05
            target_pos = None
            want_interact = False

            hand = snap["hand"]
            if hand is not None:
                c = next((x for x in snap["customers"] if x["id"] == hand["order_id"]), None)
                if c is not None:
                    tb = next(t for t in snap["tables"] if t["id"] == c["table_id"])
                    target_pos = tb["pos"]
                    want_interact = math.dist(pos, target_pos) <= radius
            else:
                ready_st = [s for s in snap["stoves"] if s["state"] == "ready"]
                idle_st = [s for s in snap["stoves"] if s["state"] == "idle"]
                reserved_waiting = [c for c in snap["customers"] if c["state"] == "waiting" and c["order_status"] == "reserved"]
                if ready_st:
                    target_pos = ready_st[0]["pos"]
                    want_interact = math.dist(pos, target_pos) <= radius
                elif idle_st and reserved_waiting:
                    target_pos = idle_st[0]["pos"]
                    want_interact = math.dist(pos, target_pos) <= radius

            if target_pos is not None:
                if want_interact:
                    if not self._last_interact:
                        edges.add("interact")
                        self._last_interact = True
                else:
                    move = _dir_toward(pos, target_pos)
                    self._last_interact = False
            else:
                self._last_interact = False
            self._last_shop_done = False

        else:  # shop
            money = snap.get("money", 0)
            ups = snap.get("upgrades", {})
            shop_up = self.tuning["shop"]["upgrades"]
            for kind in ("oxygen", "hp"):
                cur_lv = int(ups.get(kind, 0))
                nxt = next((e for e in shop_up[kind] if int(e["level"]) == cur_lv + 1), None)
                if nxt is not None and money >= int(nxt["price"]):
                    buy = kind
                    break
            if not self._last_shop_done:
                edges.add("shop_done")
                self._last_shop_done = True
            self._last_interact = False

        held = {
            "interact": self._last_interact,
            "catch": False,
            "pause": False,
            "shop_done": self._last_shop_done,
        }
        return InputState(move, held, edges, buy=buy)


def run_soak(seed: int, days: int, tuning: dict) -> dict:
    t0 = time.perf_counter()
    sim = DaySim(tuning, {}, Streams(seed), IdAllocator(), days=days)
    bot = _SoakBot(tuning)
    mult = int(tuning["score"]["reputation_multiplier"])

    results = []
    crashes = 0
    try:
        while not sim.done:
            snap = sim.snapshot()
            snap.setdefault("time_left_ticks", sim.time_left_ticks)
            snap.setdefault("money", sim.money)
            snap.setdefault("earned", sim.earned)
            inp = bot.next_input(snap, sim.phase)
            events = sim.step(inp)
            for _ph, day_num, name, _data in events:
                if name == "shop_end":
                    score = sim.earned + mult * math.floor(sim.reputation)
                    results.append({
                        "day": day_num,
                        "earned": sim.earned,
                        "reputation": round(sim.reputation, 3),
                        "score": score,
                    })
    except Exception:
        crashes += 1
        raise

    return {
        "days": int(days),
        "days_completed": sim.days_completed,
        "crashes": crashes,
        "results": results,
        "duration_s": round(time.perf_counter() - t0, 3),
    }


def _write_json_atomic(path: str, payload: dict):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".soak-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.soak", description="Chạy soak N ngày liên tiếp không restart (v1.3).")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--days", type=int, default=10)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    try:
        if a.days <= 0:
            raise BadInput("--days phải là số nguyên dương")
        tuning = load_contract()["tuning"]
        out_data = run_soak(a.seed, a.days, tuning)
        _write_json_atomic(a.out, out_data)
    except BadInput as e:
        sys.stderr.write(f"lỗi tham số soak: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"lỗi ghi file soak: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
