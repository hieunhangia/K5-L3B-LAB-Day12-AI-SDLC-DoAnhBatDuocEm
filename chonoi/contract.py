"""Đọc game.contract.json và kiểm dải hợp lệ của tuning (PRD-0 -> v1.1)."""

import json
import math
import os

from .errors import BadInput

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")

NODE_KINDS_V11 = ("bong_dien_dien", "bong_sung", "keo_neo")
FISH_KINDS_V11 = ("ca_linh", "ca_loc", "ca_keo")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    ext = c.get("extensions", [])
    if not isinstance(ext, list) or any(not isinstance(x, str) for x in ext):
        raise BadInput("extensions phải là mảng chuỗi")
    if c.get("contract_version") == "1.3":
        for cmd_key in ("bench_cmd", "soak_cmd"):
            v = c.get(cmd_key)
            if not isinstance(v, str) or not v.strip():
                raise BadInput(f"thiếu hoặc sai {cmd_key} ở contract v1.3")
    validate_tuning(c.get("tuning"), extensions=ext)
    return c


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_monsters(m, g):
    if not isinstance(m, dict):
        raise BadInput("tuning.gather.monsters phải là object")
    _int_between("gather.monsters.invuln_ticks", m.get("invuln_ticks"), 0, 600)
    _between("gather.monsters.loss_ratio", m.get("loss_ratio"), 0, 1)
    species = m.get("species")
    if not isinstance(species, dict) or "ca_sau" not in species:
        raise BadInput("tuning.gather.monsters.species phải có ca_sau")
    b = g["bounds"]
    for sk, sp in species.items():
        if not isinstance(sp, dict):
            raise BadInput(f"monsters.species.{sk} phải là object")
        for key in ("patrol_speed", "chase_speed", "detect_radius", "exit_radius", "hit_radius", "recoil_dist"):
            if not _num(sp.get(key)) or sp[key] <= 0:
                raise BadInput(f"monsters.species.{sk}.{key} phải dương")
        _int_between(f"gather.monsters.species.{sk}.recoil_ticks", sp.get("recoil_ticks"), 1, 600)
        depths = sp.get("depths")
        if not (isinstance(depths, list) and len(depths) == 2 and all(_num(c) for c in depths) and b["d"][0] <= depths[0] < depths[1] <= b["d"][1]):
            raise BadInput(f"monsters.species.{sk}.depths không hợp lệ")
    spawns = m.get("spawns")
    if not isinstance(spawns, list) or not spawns:
        raise BadInput("tuning.gather.monsters.spawns phải là mảng")
    seen = set()
    for s in spawns:
        if not isinstance(s, dict):
            raise BadInput("tuning.gather.monsters.spawns: mỗi phần tử phải là object")
        sid = s.get("id")
        if not isinstance(sid, str) or sid in seen:
            raise BadInput("tuning.gather.monsters.spawns cần id duy nhất")
        seen.add(sid)
        if s.get("kind") not in species:
            raise BadInput(f"spawns.{sid}: kind lạ")
        _pos_in(f"gather.monsters.spawns.{sid}.pos", s.get("pos"), b, ("x", "d"))
        dlo, dhi = species[s["kind"]]["depths"]
        if not dlo <= s["pos"][1] <= dhi:
            raise BadInput(f"spawns.{sid}.pos.d ngoài vùng loài")
        wps = s.get("waypoints")
        if not isinstance(wps, list) or len(wps) != 2:
            raise BadInput(f"spawns.{sid}.waypoints phải gồm đúng 2 điểm")
        for idx, wp in enumerate(wps):
            _pos_in(f"gather.monsters.spawns.{sid}.waypoints[{idx}]", wp, b, ("x", "d"))
            if not dlo <= wp[1] <= dhi:
                raise BadInput(f"spawns.{sid}.waypoints[{idx}].d ngoài vùng loài")
        _int_between(f"gather.monsters.spawns.{sid}.from_day", s.get("from_day"), 1, 5)


def _validate_gather(g):
    """Dải hợp lệ v1.1 theo PRD-0 + TICKET-02."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    if not isinstance(fy, dict) or set(fy) != set(FISH_KINDS_V11):
        raise BadInput("tuning.gather.fish_yield phải có đủ ca_linh, ca_loc, ca_keo")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BadInput("tuning.gather.nodes phải là mảng không rỗng")
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if n.get("kind") not in NODE_KINDS_V11:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: kind không hợp lệ")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if kinds != set(NODE_KINDS_V11):
        raise BadInput("tuning.gather.nodes phải có đủ cả 3 loại cây")

    _int_between("gather.fish_initial", g.get("fish_initial"), 1, 30)
    _between("gather.fish_speed", g.get("fish_speed"), 0.1, 10)
    _int_between("gather.fish_turn_ticks", g.get("fish_turn_ticks"), 1, 10_000)
    _int_between("gather.fish_max", g.get("fish_max"), g["fish_initial"], 30)
    _int_between("gather.fish_spawn_ticks", g.get("fish_spawn_ticks"), 1, 10_000)
    _between("gather.fish_spawn_clearance", g.get("fish_spawn_clearance"), 0, 20)
    fx = g.get("fish_x")
    if not (isinstance(fx, list) and len(fx) == 2 and all(_num(c) for c in fx) and b["x"][0] <= fx[0] < fx[1] <= b["x"][1]):
        raise BadInput("tuning.gather.fish_x không hợp lệ")
    if not isinstance(g.get("fish_spawn_x"), list) or not g["fish_spawn_x"]:
        raise BadInput("tuning.gather.fish_spawn_x phải là danh sách x")
    for x in g["fish_spawn_x"]:
        _between("gather.fish_spawn_x", x, fx[0], fx[1])
    for key in ("fish_depths", "fish_spawn_depths", "fish_weights"):
        if not isinstance(g.get(key), dict):
            raise BadInput(f"tuning.gather.{key} phải là object")
    for fk in FISH_KINDS_V11:
        fd = (g.get("fish_depths") or {}).get(fk)
        sd = (g.get("fish_spawn_depths") or {}).get(fk)
        w = (g.get("fish_weights") or {}).get(fk)
        if not (isinstance(fd, list) and len(fd) == 2 and all(_num(d) for d in fd) and g["surface_depth"] < fd[0] < fd[1] <= b["d"][1]):
            raise BadInput(f"tuning.gather.fish_depths.{fk} không hợp lệ")
        if not (isinstance(sd, list) and len(sd) >= 1 and all(_num(d) and fd[0] <= d <= fd[1] for d in sd)):
            raise BadInput(f"tuning.gather.fish_spawn_depths.{fk} không hợp lệ")
        if not _num(w) or w <= 0:
            raise BadInput(f"tuning.gather.fish_weights.{fk} phải > 0")
    _validate_monsters(g.get("monsters"), g)


def _validate_day_plan_and_shop(t, menu):
    plans = t.get("day_plan")
    if not isinstance(plans, list) or len(plans) != 5:
        raise BadInput("tuning.day_plan phải có đúng 5 ngày")
    for idx, p in enumerate(plans, 1):
        if p.get("day") != idx or not isinstance(p.get("dishes"), dict) or not p["dishes"]:
            raise BadInput(f"tuning.day_plan[{idx-1}] sai day hoặc dishes")
        expected = {}
        for did, cnt in p["dishes"].items():
            if did not in menu:
                raise BadInput(f"day_plan[{idx}]: món lạ {did}")
            _int_between(f"day_plan[{idx}].dishes.{did}", cnt, 1, 99)
            for k, amt in menu[did]["recipe"].items():
                expected[k] = expected.get(k, 0) + amt * cnt
        if p.get("ingredients") != expected:
            raise BadInput(f"day_plan[{idx}].ingredients không khớp công thức món")
    shop = t.get("shop")
    if not isinstance(shop, dict):
        raise BadInput("thiếu tuning.shop")
    _int_between("shop.max_ticks", shop.get("max_ticks"), 1, 10_000)
    up = shop.get("upgrades")
    if not isinstance(up, dict) or not {"oxygen", "hp"} <= set(up):
        raise BadInput("tuning.shop.upgrades phải có oxygen và hp")


def validate_tuning(t, extensions=()):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    _validate_gather(g)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if "burn" in extensions:
        if q.get("burn_s") is not None:
            _between("quan.burn_s", q.get("burn_s"), 1, 600)
    elif q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null khi chưa bật mở rộng burn")
    for dish_id, d in menu.items():
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
    _validate_day_plan_and_shop(t, menu)
    fr = t.get("freshness")
    if not isinstance(fr, dict):
        raise BadInput("thiếu tuning.freshness ở contract v1.2")
    _between("freshness.initial", fr.get("initial"), 1, 100)
    if not _num(fr.get("gather_decay_per_s")) or fr["gather_decay_per_s"] <= 0:
        raise BadInput("tuning.freshness.gather_decay_per_s phải > 0")
    if not _num(fr.get("quan_decay_per_s")) or fr["quan_decay_per_s"] <= 0:
        raise BadInput("tuning.freshness.quan_decay_per_s phải > 0")
    _between("freshness.spoiled_below", fr.get("spoiled_below"), 0, fr["initial"] - 1)
