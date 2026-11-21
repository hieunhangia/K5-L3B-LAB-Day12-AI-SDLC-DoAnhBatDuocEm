"""Benchmark hiệu năng cảnh lặn 1280x720 (TICKET-04, contract v1.3).

Chạy:
    python3 -m chonoi.bench --seed 42 --duration 30 --out docs/proof/phase-4/bench.json
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
from .ids import IdAllocator
from .inputs import InputState
from .rng import Streams
from .sim.gather import GatherSim

WIDTH = 1280
HEIGHT = 720

KIND_RGB = {
    "ca_loc": (124, 154, 82),
    "ca_linh": (214, 230, 242),
    "ca_keo": (217, 160, 102),
    "bong_dien_dien": (242, 194, 48),
    "bong_sung": (232, 121, 156),
    "keo_neo": (143, 207, 107),
}


def _build_background() -> bytearray:
    bg = bytearray(WIDTH * HEIGHT * 3)
    sky_row = bytes((184, 224, 242)) * WIDTH
    surf_row = bytes((233, 247, 255)) * WIDTH
    sky_h = int(HEIGHT * 0.18)
    row_stride = WIDTH * 3
    for y in range(sky_h):
        off = y * row_stride
        bg[off:off + row_stride] = sky_row
    for y in range(sky_h, sky_h + 3):
        off = y * row_stride
        bg[off:off + row_stride] = surf_row
    water_h = HEIGHT - (sky_h + 3)
    for y in range(sky_h + 3, HEIGHT):
        frac = (y - sky_h) / max(1, water_h)
        r = max(4, int(35 - 26 * frac))
        g = max(20, int(115 - 75 * frac))
        b = max(42, int(155 - 92 * frac))
        row = bytes((r, g, b)) * WIDTH
        off = y * row_stride
        bg[off:off + row_stride] = row
    return bg


class _SceneRasterizer:
    """Rasterizer RGB 1280x720 thuần stdlib dùng pre-baked buffer + slice fills."""

    def __init__(self):
        self.bg = _build_background()
        self.fb = bytearray(len(self.bg))
        self.sky_h = int(HEIGHT * 0.18)
        self.scale_x = WIDTH / 100.0
        self.scale_d = (HEIGHT - self.sky_h - 16) / 30.0
        self._stamp_cache: dict[tuple[int, int, int, int, int], bytes] = {}

    def _stamp(self, w: int, h: int, color: tuple[int, int, int]) -> bytes:
        key = (w, h, color[0], color[1], color[2])
        s = self._stamp_cache.get(key)
        if s is None:
            s = bytes(color) * w
            self._stamp_cache[key] = s
        return s

    def _fill_rect(self, x0: int, y0: int, rw: int, rh: int, color: tuple[int, int, int]):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(WIDTH, x0 + rw)
        y1 = min(HEIGHT, y0 + rh)
        w = x1 - x0
        if w <= 0 or y1 <= y0:
            return
        stamp = self._stamp(w, y1 - y0, color)
        row_stride = WIDTH * 3
        span = w * 3
        col_off = x0 * 3
        fb = self.fb
        for y in range(y0, y1):
            off = y * row_stride + col_off
            fb[off:off + span] = stamp

    def render(self, snap: dict):
        self.fb[:] = self.bg
        sx = self.scale_x
        sd = self.scale_d
        sky = self.sky_h

        # Bến ghe
        self._fill_rect(int(2 * sx - 24), sky - 22, 48, 20, (185, 80, 58))

        # Nút hái
        for n in snap["nodes"]:
            px = int(n["pos"][0] * sx) - 10
            py = int(sky + n["pos"][1] * sd) - 10
            col = KIND_RGB.get(n["kind"], (220, 220, 220)) if n["ready"] else (85, 100, 110)
            self._fill_rect(px, py, 20, 10, col)

        # Đàn cá
        for f in snap["fish"]:
            px = int(f["pos"][0] * sx) - 12
            py = int(sky + f["pos"][1] * sd) - 6
            self._fill_rect(px, py, 24, 12, KIND_RGB.get(f["kind"], (214, 230, 242)))

        # Cá Sấu
        for m in snap.get("monsters", []):
            px = int(m["pos"][0] * sx) - 18
            py = int(sky + m["pos"][1] * sd) - 8
            col = (229, 57, 53) if m["state"] == "chase" else (74, 107, 58)
            self._fill_rect(px, py, 36, 16, col)

        # Út Sen tại bến + HUD oxy / HP / đồng hồ
        p = snap["player"]
        ux = int(p["pos"][0] * sx) - 8
        uy = int(sky + p["pos"][1] * sd) - 8
        self._fill_rect(ux, uy, 16, 16, (255, 138, 61))

        oxy_ratio = p["oxygen_ticks"] / max(1, p["oxygen_max_ticks"])
        self._fill_rect(24, 18, 220, 18, (30, 45, 58))
        self._fill_rect(24, 18, int(220 * oxy_ratio), 18, (79, 195, 247))
        for i in range(p["hp_max"]):
            col = (229, 57, 53) if i < p["hp"] else (70, 80, 90)
            self._fill_rect(24 + i * 24, 44, 18, 16, col)


def _write_json_atomic(path: str, payload: dict):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".bench-", suffix=".tmp", dir=d)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def run_benchmark(seed: int, duration_s: float, warmup_s: float, tuning: dict) -> dict:
    proc_t0 = time.perf_counter()
    idle = InputState((0.0, 0.0), {"interact": False, "catch": False, "pause": False, "shop_done": False}, set())

    def make_sim():
        return GatherSim(tuning, {}, Streams(seed), IdAllocator(), day=1)

    sim = make_sim()
    raster = _SceneRasterizer()

    # Frame đầu tiên của cảnh đo -> xác định load_ms
    raster.render(sim.snapshot())
    load_ms = round((time.perf_counter() - proc_t0) * 1000.0, 2)

    warm_end = time.perf_counter() + warmup_s
    while time.perf_counter() < warm_end:
        if sim.done:
            sim = make_sim()
        sim.step(idle)
        raster.render(sim.snapshot())

    frame_times = []
    measure_start = time.perf_counter()
    measure_end = measure_start + duration_s
    while True:
        t0 = time.perf_counter()
        if t0 >= measure_end and frame_times:
            break
        if sim.done:
            sim = make_sim()
        sim.step(idle)
        raster.render(sim.snapshot())
        t1 = time.perf_counter()
        frame_times.append(max(1e-7, t1 - t0))
        if t1 >= measure_end:
            break

    measured_s = round(sum(frame_times), 4)
    frames = len(frame_times)
    avg_fps = round(frames / measured_s, 2)
    k = max(1, math.ceil(0.01 * frames))
    slowest = sorted(frame_times, reverse=True)[:k]
    p1_low_fps = round(k / sum(slowest), 2)
    return {
        "avg_fps": avg_fps,
        "p1_low_fps": p1_low_fps,
        "frames": frames,
        "measured_s": measured_s,
        "load_ms": load_ms,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.bench", description="Benchmark render 1280x720 (v1.3).")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--duration", type=float, default=30.0)
    p.add_argument("--warmup", type=float, default=3.0)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    try:
        if a.duration <= 0 or a.warmup < 0:
            raise BadInput("--duration phải > 0 và --warmup phải >= 0")
        tuning = load_contract()["tuning"]
        result = run_benchmark(a.seed, a.duration, a.warmup, tuning)
        _write_json_atomic(a.out, result)
    except BadInput as e:
        sys.stderr.write(f"lỗi tham số bench: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"lỗi ghi file bench: {e}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
