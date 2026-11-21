"""Đầu vào headless (Contract B / v1.3): hỗ trợ --mode gather|quan|day, --days 1..5 và --leaderboard."""

import argparse
import math
import os
import sys

from .contract import load_contract
from .errors import BadInput
from .inputs import BUTTONS_V11, load_frames
from .inventory import read_inventory
from .leaderboard import record_entry, validate_player_name
from .runner import run
from .scenario import load_scenario


def _int_exact(s):
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"cần số nguyên: {s}")
    if str(v) != s.lstrip("+") and not (s.startswith("-0") and v == 0):
        raise argparse.ArgumentTypeError(f"số nguyên không hợp lệ: {s}")
    return v


def _exact_json_int(v):
    if -(2**53 - 1) <= v <= (2**53 - 1):
        return v
    raise BadInput(f"seed {v} vượt phạm vi số nguyên chính xác trong JSON")


class _Parser(argparse.ArgumentParser):
    def error(self, msg):
        sys.stderr.write(f"lỗi tham số: {msg}\n")
        raise SystemExit(2)


def main(argv=None) -> int:
    p = _Parser(prog="chonoi.headless")
    p.add_argument("--mode", required=True, choices=["gather", "quan", "day"])
    p.add_argument("--seed", required=True, type=_int_exact)
    p.add_argument("--ticks", required=True, type=_int_exact)
    p.add_argument("--out", required=True)
    p.add_argument("--scenario")
    p.add_argument("--inputs")
    p.add_argument("--inventory")
    p.add_argument("--inventory-out", dest="inventory_out")
    p.add_argument("--days", type=_int_exact, default=None)
    p.add_argument("--snapshot-every", dest="snapshot_every", type=_int_exact, default=10)
    p.add_argument("--leaderboard", default=None)
    p.add_argument("--player-name", dest="player_name", default=None)
    a = p.parse_args(argv)
    try:
        _exact_json_int(a.seed)
        if a.ticks < 0:
            raise BadInput("--ticks phải >= 0")
        if a.snapshot_every <= 0:
            raise BadInput("--snapshot-every phải > 0")
        if a.inventory and a.mode != "quan":
            raise BadInput("--inventory chỉ dùng với quan")
        if a.inventory_out and a.mode != "gather":
            raise BadInput("--inventory-out chỉ dùng với gather")
        if a.days is not None and a.mode != "day":
            raise BadInput("--days chỉ dùng với --mode day")
        days = 1 if a.days is None else a.days
        if not (1 <= days <= 5):
            raise BadInput("--days phải là số nguyên từ 1 đến 5")

        if (a.leaderboard is None) != (a.player_name is None):
            raise BadInput("cần truyền đủ cả --leaderboard và --player-name")
        if a.leaderboard is not None:
            if a.mode != "day":
                raise BadInput("--leaderboard chỉ dùng với --mode day")
            validate_player_name(a.player_name)

        outs = [x for x in (a.out, a.inventory_out) if x]
        ins = [x for x in (a.scenario, a.inputs, a.inventory) if x]
        if len(set(outs)) != len(outs) or set(outs) & set(ins):
            raise BadInput("đường dẫn ghi phải tách biệt nhau và tách biệt đầu vào")
        if a.leaderboard and os.path.abspath(a.leaderboard) in {os.path.abspath(x) for x in outs + ins}:
            raise BadInput("đường dẫn --leaderboard phải tách khỏi đầu vào/ra JSONL")

        tuning = load_contract()["tuning"]
        scenario = load_scenario(a.scenario, a.mode, tuning)
        frames = load_frames(a.inputs, buttons=BUTTONS_V11, allow_buy=True)
        inventory = read_inventory(a.inventory) if a.inventory else None
        if inventory is not None and "stock" in scenario:
            raise BadInput("vừa có quan.stock vừa có --inventory")

        sim = run(
            a.mode,
            tuning,
            scenario,
            a.seed,
            frames,
            a.ticks,
            a.out,
            a.snapshot_every,
            inventory=inventory,
            inventory_out=a.inventory_out,
            days=days,
        )

        if (
            a.leaderboard is not None
            and a.mode == "day"
            and days == 5
            and a.scenario is None
            and sim.done
            and sim.reason == "days_complete"
            and getattr(sim, "days_completed", 0) == 5
        ):
            mult = tuning["score"]["reputation_multiplier"]
            score = int(sim.earned + mult * math.floor(sim.reputation))
            record_entry(a.leaderboard, a.player_name, score, 5, a.seed)
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"lỗi đọc/ghi file: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
