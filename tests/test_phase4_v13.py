"""Kiểm thử Phase 4 (contract v1.3): bench_cmd, soak_cmd, mở rộng leaderboard và HUD/cảnh báo."""

import json
import os
import subprocess
import unittest

from chonoi.contract import load_contract
from helpers import ROOT, Workdir, frames, run_headless, write_json


def _run_module(mod: str, *args: str):
    cmd_base = load_contract()[mod].split()
    p = subprocess.run([*cmd_base, *args], cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


class Phase4V13Tests(unittest.TestCase):
    def test_contract_v13_declares_bench_soak_and_extensions(self):
        c = load_contract()
        self.assertEqual(c["contract_version"], "1.3")
        self.assertIn("burn", c["extensions"])
        self.assertIn("leaderboard", c["extensions"])
        self.assertTrue(c["bench_cmd"])
        self.assertTrue(c["soak_cmd"])

    def test_bench_cmd_renders_1280x720_and_meets_fps_targets(self):
        with Workdir() as w:
            out = w.path("bench.json")
            code, _, err = _run_module("bench_cmd", "--seed", "42", "--duration", "1", "--warmup", "0.2", "--out", out)
            self.assertEqual(code, 0, err)
            with open(out, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(set(data), {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"})
            self.assertGreaterEqual(data["avg_fps"], 60.0)
            self.assertGreaterEqual(data["p1_low_fps"], 30.0)
            self.assertLessEqual(data["load_ms"], 10_000.0)
            self.assertGreater(data["frames"], 0)

    def test_soak_cmd_10_days_deterministic_zero_crashes_no_leaderboard(self):
        with Workdir() as w:
            s1 = w.path("s1.json")
            s2 = w.path("s2.json")
            c1, _, e1 = _run_module("soak_cmd", "--seed", "7", "--days", "10", "--out", s1)
            c2, _, e2 = _run_module("soak_cmd", "--seed", "7", "--days", "10", "--out", s2)
            self.assertEqual(c1, 0, e1)
            self.assertEqual(c2, 0, e2)
            with open(s1, encoding="utf-8") as f1, open(s2, encoding="utf-8") as f2:
                d1 = json.load(f1)
                d2 = json.load(f2)
            self.assertEqual(set(d1), {"days", "days_completed", "crashes", "results", "duration_s"})
            self.assertEqual(d1["days"], 10)
            self.assertEqual(d1["days_completed"], 10)
            self.assertEqual(d1["crashes"], 0)
            self.assertEqual(len(d1["results"]), 10)
            self.assertEqual(d1["results"], d2["results"])

    def test_leaderboard_recording_top10_tie_preservation_and_export(self):
        inp = frames(
            {"tick": 22200, "shop_done": False},
        )
        # Complete 5 full days via large ticks; compare JSONL bytes with vs without leaderboard!
        with Workdir() as w:
            store = w.path("lb.json")
            o_no = w.path("no_lb.jsonl")
            o_lb = w.path("with_lb.jsonl")
            c1, e1 = run_headless("--mode", "day", "--days", "5", "--seed", "42", "--ticks", "120000", "--out", o_no)
            c2, e2 = run_headless(
                "--mode", "day", "--days", "5", "--seed", "42", "--ticks", "120000",
                "--leaderboard", store, "--player-name", "Út Sen", "--out", o_lb,
            )
            self.assertEqual(c1, 0, e1)
            self.assertEqual(c2, 0, e2)
            with open(o_no, "rb") as f1, open(o_lb, "rb") as f2:
                self.assertEqual(f1.read(), f2.read())

            # Second tie entry preserves insertion order across reload, non-5-day/scenario does NOT record
            run_headless(
                "--mode", "day", "--days", "5", "--seed", "7", "--ticks", "120000",
                "--leaderboard", store, "--player-name", "Má Tư", "--out", w.path("t2.jsonl"),
            )
            run_headless(
                "--mode", "day", "--days", "1", "--seed", "9", "--ticks", "25000",
                "--leaderboard", store, "--player-name", "Bỏ qua", "--out", w.path("d1.jsonl"),
            )
            sc = write_json(w.path("sc.json"), {"gather": {"random_fish": False}})
            run_headless(
                "--mode", "day", "--days", "5", "--seed", "9", "--ticks", "120000",
                "--scenario", sc, "--leaderboard", store, "--player-name", "Có Scenario", "--out", w.path("sc_out.jsonl"),
            )

            # Export via run_cmd --export-leaderboard
            exp = w.path("exported.json")
            rc, _, err = _run_module("run_cmd", "--export-leaderboard", exp, "--leaderboard", store)
            self.assertEqual(rc, 0, err)
            with open(exp, encoding="utf-8") as f:
                entries = json.load(f)["entries"]
            self.assertEqual([(e["name"], e["days_completed"], e["seed"]) for e in entries], [
                ("Út Sen", 5, 42),
                ("Má Tư", 5, 7),
            ])
            self.assertEqual(entries[0]["score"], 300)

            # Top-10 cap + tie preservation directly via store API
            from chonoi.leaderboard import record_entry, load_leaderboard
            for i in range(1, 13):
                record_entry(store, f"Thí sinh {i}", score=500 if i <= 2 else i * 10, days_completed=5, seed=i)
            top = load_leaderboard(store)
            self.assertEqual(len(top), 10)
            self.assertEqual([e["name"] for e in top[:2]], ["Thí sinh 1", "Thí sinh 2"])

    def test_leaderboard_cli_errors_return_exit_2(self):
        with Workdir() as w:
            out = w.path("o.jsonl")
            store = w.path("lb.json")
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "0", "--leaderboard", store, "--out", out)[0], 2)
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "0", "--player-name", "A", "--out", out)[0], 2)
            self.assertEqual(run_headless("--mode", "day", "--seed", "1", "--ticks", "0", "--leaderboard", store, "--player-name", "   ", "--out", out)[0], 2)
            self.assertEqual(run_headless("--mode", "gather", "--seed", "1", "--ticks", "0", "--leaderboard", store, "--player-name", "A", "--out", out)[0], 2)

    def test_web_ui_has_three_warnings_and_high_contrast(self):
        html_path = os.path.join(ROOT, "chonoi", "web", "index.html")
        with open(html_path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("Thủy quái!", text)
        self.assertIn("Hết hơi!", text)
        self.assertIn("Khách sắp giận!", text)
        self.assertIn("Tương phản cao", text)
        self.assertIn("Chơi", text)

    def test_all_six_member_reflections_under_200_words(self):
        handles = ["hieunhangia", "Ducbaynao", "Besoi2004", "hnib1908", "letuandat131", "Laurent2526"]
        for h in handles:
            p = os.path.join(ROOT, "docs", "members", f"{h}.md")
            self.assertTrue(os.path.exists(p), f"missing {p}")
            with open(p, encoding="utf-8") as f:
                words = len(f.read().split())
            self.assertLessEqual(words, 200, f"{h}.md has {words} > 200 words")


if __name__ == "__main__":
    unittest.main()
