"""Kiểm thử luồng sáng → kho → tối qua lệnh headless trong Test Contract."""

import json
import math
from pathlib import Path
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.scenario import load_scenario
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


DISH = "lau_ca_linh_dien_dien"


def gather_fixture(tuning):
    g = tuning["gather"]
    hz = tuning["tick_hz"]
    x = g["dock_pos"][0] + g["dock_radius"] + g["interact_radius"]
    fish_depth = g["surface_depth"] + g["catch_radius"] / 2
    catch = math.ceil(fish_depth * hz / g["swim_speed"]) + g["ramp_max_ticks"]
    scenario = {
        "player": {"pos": [x, 0]},
        "nodes": [{"id": "N1", "kind": "bong_dien_dien", "pos": [x, 0]}],
        "fish": [{"id": "F1", "kind": "ca_linh", "pos": [x, fish_depth]}],
        "time_left_ticks": catch + 2,
    }
    inputs = frames(
        {"tick": 0, "interact": True},
        {"tick": 1, "interact": False, "move": [0, 1]},
        {"tick": catch, "move": [0, 0], "catch": True},
    )
    return scenario, inputs


def quan_fixture(tuning):
    q = tuning["quan"]
    hz = tuning["tick_hz"]
    stove = q["stoves"][0]["pos"]
    table = q["tables"][0]["pos"]
    distance = math.dist(stove, table)
    move = [(end - start) / distance for start, end in zip(stove, table)]
    cook = q["first_customer_tick"] + 1
    pick = cook + round(tuning["menu"][DISH]["cook_s"] * hz) + 1
    serve = pick + 1 + round(distance * hz / q["walk_speed"])
    end = serve + round(q["eat_s"] * hz) + 2
    scenario = {"player": {"pos": stove}, "time_left_ticks": end}
    inputs = frames(
        {"tick": cook, "interact": True},
        {"tick": cook + 1, "interact": False},
        {"tick": pick, "interact": True},
        {"tick": pick + 1, "interact": False, "move": move},
        {"tick": serve, "interact": True, "move": [0, 0]},
    )
    return scenario, inputs


class Pipeline(unittest.TestCase):
    def run_mode(self, work, mode, fixture, *extra):
        scenario, inputs = fixture(self.tuning)
        out = work.path(f"{mode}_run.jsonl")
        code, err = run_headless(
            "--mode", mode, "--seed", "1", "--ticks", str(scenario["time_left_ticks"]),
            "--scenario", write_json(work.path(f"{mode}.scenario.json"), {mode: scenario}),
            "--inputs", write_json(work.path(f"{mode}.inputs.json"), inputs),
            "--snapshot-every", "120", "--out", out, *extra,
        )
        self.assertEqual(code, 0, err)
        return read_jsonl(out)

    def setUp(self):
        self.tuning = load_contract()["tuning"]

    def test_harvest_to_paid_order(self):
        with Workdir() as work:
            inventory = work.path("inventory.json")
            gather = self.run_mode(work, "gather", gather_fixture, "--inventory-out", inventory)
            self.assertEqual(snapshots(gather)[0]["hold"], [])
            self.assertEqual(len(events(gather, "gather")), 1)
            self.assertEqual(len(events(gather, "fish_caught")), 1)
            items = self.tuning["menu"][DISH]["recipe"]
            exported = json.loads(Path(inventory).read_text(encoding="utf-8"))
            self.assertEqual(exported, {"items": items})
            self.assertEqual(events(gather, "gather_end")[0]["data"]["inventory"], exported)

            quan = self.run_mode(work, "quan", quan_fixture, "--inventory", inventory)
            self.assertEqual(snapshots(quan)[0]["stock"], items)
            required = ["customer_arrived", "cook_started", "dish_ready", "dish_picked", "served", "paid", "quan_end"]
            actual = [e["name"] for e in events(quan) if e["name"] in required]
            self.assertEqual(actual, required)
            arrived, = events(quan, "customer_arrived")
            self.assertEqual(arrived["tick"], self.tuning["quan"]["first_customer_tick"])
            self.assertEqual(arrived["data"]["dish"], DISH)
            self.assertEqual(events(quan, "cook_started")[0]["data"]["dish"], DISH)
            self.assertEqual(events(quan, "served")[0]["data"]["dish"], DISH)
            paid, = events(quan, "paid")
            self.assertEqual(paid["data"]["customer_id"], arrived["data"]["customer_id"])
            price = self.tuning["menu"][DISH]["price"]
            q = self.tuning["quan"]
            tip = round(price * q["tip_rate"])
            self.assertEqual(paid["data"]["tip"], tip)
            final = quan[-1]
            self.assertEqual(final["reason"], "time")
            self.assertEqual(final["money"], price + tip)
            self.assertEqual(final["earned"], price + tip)
            reputation = min(q["reputation_max"], q["reputation_initial"] + q["tip_reputation"])
            self.assertAlmostEqual(final["reputation"], reputation)
            self.assertEqual(final["score"], price + tip + self.tuning["score"]["reputation_multiplier"] * math.floor(reputation))
            self.assertEqual(snapshots(quan)[-1]["stock"], {})


class QuanScenario(unittest.TestCase):
    def setUp(self):
        self.tuning = load_contract()["tuning"]
        self.recipe = self.tuning["menu"][DISH]["recipe"]
        self.table = self.tuning["quan"]["tables"][0]
        self.customer = {"id": "C1", "table_id": self.table["id"], "state": "assigned", "dish": DISH}

    def test_invalid_orders_exit_2(self):
        cases = (
            ({"hand": "unknown"}, "hand"),
            ({"stoves": [{"id": self.tuning["quan"]["stoves"][0]["id"], "dish": []}]}, "stoves."),
            ({"customers": [dict(self.customer, dish="unknown")]}, "menu"),
            ({"customers": [dict(self.customer, dish=None)]}, "assigned"),
            ({"customers": [dict(self.customer, dish_id="ca_loc_nuong_trui")]}, "mâu thuẫn"),
            ({"customers": [dict(self.customer, dish=None, dish_id=DISH)]}, "mâu thuẫn"),
            ({"customers": [{"id": "C1", "table_id": self.table["id"], "reserved": self.recipe}]}, "công thức"),
            ({"customers": [dict(self.customer, state="eating", eat_ticks_left=1)]}, "price/tip"),
            ({"customers": [dict(self.customer, state="eating", eat_ticks_left=1, price=1)]}, "tip"),
            ({"customers": [dict(self.customer, state="eating", eat_ticks_left=0, price=1, tip=0)]}, "eat_ticks_left"),
            ({"customers": [dict(self.customer, reserved={"ca_linh": 1})]}, "công thức"),
        )
        with Workdir() as work:
            for block, diagnostic in cases:
                with self.subTest(block=block):
                    scenario = write_json(work.path("quan.json"), {"quan": block})
                    out = work.path("out.jsonl")
                    code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", scenario, "--out", out)
                    self.assertEqual(code, 2, err)
                    self.assertIn(diagnostic, err)
                    self.assertFalse(Path(out).exists())

    def test_reservations_use_actual_inventory(self):
        with Workdir() as work:
            customer = dict(self.customer, reserved=self.recipe)
            scenario = write_json(work.path("quan.json"), {"quan": {"customers": [customer]}})
            inv = work.path("inventory.json")
            args = ("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", scenario,
                    "--out", work.path("out.jsonl"), "--inventory", inv)
            write_json(inv, {"items": {}})
            code, err = run_headless(*args)
            self.assertEqual(code, 2, err)
            self.assertIn("vượt kho", err)
            write_json(inv, {"items": self.recipe})
            code, err = run_headless(*args)
            self.assertEqual(code, 0, err)

    def test_reservations_sum_across_tables(self):
        other = dict(self.table, id="T99")
        self.tuning["quan"]["tables"].append(other)
        customers = [dict(self.customer, reserved=self.recipe),
                     dict(self.customer, id="C2", table_id=other["id"], reserved=self.recipe)]
        with Workdir() as work:
            scenario = work.path("quan.json")
            write_json(scenario, {"quan": {"customers": customers, "stock": self.recipe}})
            with self.assertRaisesRegex(BadInput, "vượt kho"):
                load_scenario(scenario, "quan", self.tuning)
            stock = {kind: 2 * quantity for kind, quantity in self.recipe.items()}
            write_json(scenario, {"quan": {"customers": customers, "stock": stock}})
            self.assertEqual(load_scenario(scenario, "quan", self.tuning)["stock"], stock)

    def test_waiting_customer_reserves_recipe_by_default(self):
        with Workdir() as work:
            waiting = dict(self.customer, state="waiting")
            scenario = write_json(work.path("quan.json"), {"quan": {"customers": [waiting]}})
            with self.assertRaisesRegex(BadInput, "vượt kho"):
                load_scenario(scenario, "quan", self.tuning)
            self.assertEqual(load_scenario(scenario, "quan", self.tuning, inventory=self.recipe)["customers"], [waiting])
