"""Tests for the calculators, the renderer and the build. Run from the plugin root:

    python3 -m unittest discover -s tests
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


portfolio = load(ROOT / "skills/portfolio-checkup/scripts/portfolio.py", "portfolio")
dcf = load(ROOT / "skills/fair-value/scripts/dcf.py", "dcf")
dca = load(ROOT / "skills/dca-plan/scripts/dca.py", "dca")
bars_io = load(ROOT / "shared/bars_io.py", "bars_io")
rotation = load(ROOT / "skills/sector-rotation/scripts/rotation.py", "rotation")
event_study = load(ROOT / "skills/event-study/scripts/event_study.py", "event_study")
render = load(ROOT / "shared/render_report.py", "render_report")

PARTNER = json.loads((ROOT / "partner.json").read_text(encoding="utf-8"))


def weeks(count: int) -> list[str]:
    return [f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}" for i in range(count)]


class PortfolioTest(unittest.TestCase):
    def test_weights_and_concentration(self):
        out = portfolio.analyse({"cash": 100, "positions": [
            {"symbol": "aapl", "market_value": 500, "cost_basis": 400, "sector": "Tech"},
            {"symbol": "MSFT", "market_value": 300, "sector": "Tech"},
            {"symbol": "KO", "market_value": 100, "sector": "Staples"}]})
        s = out["summary"]
        self.assertAlmostEqual(s["total_value"], 1000)
        self.assertAlmostEqual(s["largest_weight"], 0.5)
        self.assertAlmostEqual(s["top_three_weight"], 0.9)
        self.assertAlmostEqual(s["cash_weight"], 0.1)
        self.assertAlmostEqual(s["hhi_invested"], (5 / 9) ** 2 + (3 / 9) ** 2 + (1 / 9) ** 2)
        self.assertAlmostEqual(s["largest_sector_weight"], 0.8)
        self.assertAlmostEqual(s["unrealised_pct"], 0.25)
        crossed = {f["check"] for f in out["flags"] if f["crossed"]}
        self.assertEqual(crossed, {"single_position", "top_three", "single_sector", "effective_holdings_min"})

    def test_duplicate_symbols_merge_and_bad_input_fails(self):
        out = portfolio.analyse({"positions": [{"symbol": "KO", "market_value": 1}, {"symbol": "ko", "market_value": 3}]})
        self.assertEqual(out["summary"]["holdings"], 1)
        with self.assertRaises(portfolio.InputError):
            portfolio.analyse({"positions": [{"symbol": "KO", "market_value": "n/a"}]})
        with self.assertRaises(portfolio.InputError):
            portfolio.analyse({"positions": [{"symbol": "KO", "market_value": 1}], "thresholds": {"nope": 1}})


class DcfTest(unittest.TestCase):
    CASE = {"growth_1_5": 0.0, "growth_6_10": 0.0, "terminal_growth": 0.0, "discount_rate": 0.10}

    def inputs(self, **extra):
        data = {"price": 50, "shares_outstanding": 10, "net_debt": 100, "base_fcf": 100, "years": 10,
                "cases": {"bear": dict(self.CASE), "base": dict(self.CASE), "bull": dict(self.CASE)}}
        data.update(extra)
        return data

    def test_no_growth_equals_a_perpetuity(self):
        out = dcf.run(self.inputs())
        base = out["cases"]["base"]
        self.assertAlmostEqual(base["enterprise_value"], 1000.0, places=6)  # 100 / 0.10
        self.assertAlmostEqual(base["per_share"], 90.0, places=6)
        self.assertAlmostEqual(base["gap_to_price"], 0.8, places=6)

    def test_reverse_growth_reproduces_the_price(self):
        out = dcf.run(self.inputs(price=120))
        g = out["reverse"]["implied_constant_growth"]
        again = dcf.value_per_share(100, g, g, 0.0, 0.10, 10, 100, 10)["per_share"]
        self.assertAlmostEqual(again, 120, places=4)

    def test_rejects_impossible_inputs(self):
        bad = self.inputs()
        bad["cases"]["base"]["terminal_growth"] = 0.10
        with self.assertRaises(dcf.InputError):
            dcf.run(bad)
        with self.assertRaises(dcf.InputError):
            dcf.run(self.inputs(base_fcf=-5))

    def test_sensitivity_grid_shape_and_direction(self):
        grid = dcf.run(self.inputs())["sensitivity"]
        self.assertEqual(len(grid["per_share"]), len(grid["discount_rates"]))
        self.assertGreater(grid["per_share"][0][1], grid["per_share"][-1][1])  # lower rate, higher value


class DcaTest(unittest.TestCase):
    def test_zero_return_is_plain_addition(self):
        value, paid = dca.future_value(1000, 100, 2, 0.0, 0.0)
        self.assertAlmostEqual(value, 3400)
        self.assertAlmostEqual(paid, 3400)

    def test_step_up_raises_the_second_year(self):
        value, _ = dca.future_value(0, 100, 2, 0.0, 0.10)
        self.assertAlmostEqual(value, 1200 + 1320)

    def test_required_monthly_inverts_future_value(self):
        need = dca.required_monthly(1_000_000, 50_000, 15, 0.06, 0.05)
        self.assertAlmostEqual(dca.future_value(50_000, need, 15, 0.06, 0.05)[0], 1_000_000, delta=1)

    def test_goal_in_todays_money_is_inflated(self):
        out = dca.plan({"years": 10, "goal_amount": 100, "inflation_pct": 2, "returns_pct": [5], "step_ups_pct": [0]})
        self.assertAlmostEqual(out["goal"]["target_at_end"], 100 * 1.02 ** 10)
        with self.assertRaises(dca.InputError):
            dca.plan({"years": 10})


class BarsTest(unittest.TestCase):
    def test_three_formats_agree(self):
        want = {"SPY": [("2026-11-13", 754.37), ("2026-11-20", 689.81)]}
        webull = {"result": [{"symbol": "SPY", "result": [
            {"time": "2026-11-20T05:00:00.000+0000", "close": "689.810000"},
            {"time": "2026-11-13T05:00:00.000+0000", "close": "754.37"}]}]}
        samples = ["# spy\n2026-11-20,689.81\n2026-11-13,754.37\n", json.dumps(webull),
                   json.dumps({"SPY": [["2026-11-13", 754.37], ["2026-11-20", 689.81]]})]
        with tempfile.TemporaryDirectory() as tmp:
            for n, text in enumerate(samples):
                path = Path(tmp) / f"bars{n}.txt"
                path.write_text(text, encoding="utf-8")
                self.assertEqual(bars_io.load_series(path), want)
            bad = Path(tmp) / "bad.txt"
            bad.write_text("2026-11-20,689.81\n", encoding="utf-8")
            with self.assertRaises(bars_io.BarsError):
                bars_io.load_series(bad)


class RotationTest(unittest.TestCase):
    def test_quadrants(self):
        days = weeks(30)
        bench = [(d, 100.0) for d in days]
        series = {"SPY": bench, "SAME": list(bench),
                  "UP": [(d, 100 * 1.01 ** i) for i, d in enumerate(days)],
                  "DOWN": [(d, 100 * 0.99 ** i) for i, d in enumerate(days)],
                  "SHORT": bench[:5]}
        out = rotation.rotate(series, "spy")
        got = {m["symbol"]: m for m in out["members"]}
        self.assertAlmostEqual(got["SAME"]["strength"], 100.0)
        self.assertAlmostEqual(got["SAME"]["momentum"], 100.0)
        self.assertEqual(got["UP"]["quadrant"], "Leading")
        self.assertEqual(got["DOWN"]["quadrant"], "Lagging")
        self.assertAlmostEqual(got["UP"]["relative_return_4w"], 1.01 ** 4 - 1)
        self.assertEqual([s["symbol"] for s in out["skipped"]], ["SHORT"])
        with self.assertRaises(bars_io.BarsError):
            rotation.rotate(series, "QQQ")


class EventStudyTest(unittest.TestCase):
    def rows(self):
        closes, price = [], 100.0
        for i in range(200):
            price *= 0.90 if i in (50, 52, 120) else 1.001
            closes.append(price)
        return [(f"2026-{1 + i // 28:02d}-{1 + i % 28:02d}", c) for i, c in enumerate(closes)]

    def test_move_events_respect_the_gap(self):
        out = event_study.study(self.rows(), "move", threshold=-5, horizons=(5, 20), gap=5)
        self.assertEqual(out["events_found"], 3)
        self.assertEqual(out["events_used"], 2)  # day 52 falls inside the gap after day 50
        five = out["results"][0]
        self.assertEqual(five["after_event"]["n"], 2)
        self.assertEqual(five["all_days"]["n"], 195)
        self.assertIn("too few", out["notes"][0])

    def test_streak_and_dates(self):
        rows = self.rows()
        up = event_study.study(rows, "streak", days=3, direction="up", horizons=(5,), gap=0)
        self.assertGreater(up["events_used"], 100)
        by_date = event_study.study(rows, "dates", dates=[rows[10][0], "2099-01-01"], horizons=(5,))
        self.assertEqual(by_date["event_dates"], [rows[10][0]])
        with self.assertRaises(bars_io.BarsError):
            event_study.study(rows[:10], "move")


class RenderTest(unittest.TestCase):
    SRC = {"source": "Webull get_stock_bars", "period": "26 weeks", "unit": "USD"}

    def report(self):
        return {"lang": "th", "kicker": "Test", "title_en": "A test page", "title_th": "หน้าทดสอบ",
                "answer": "คำตอบ", "as_of": "26 Nov 2026",
                "kpis": [{"label": "Price", "value": "1.00", "note": "USD"}],
                "sections": [
                    {"type": "bars", "heading": "Bars", "items": [{"label": "A", "value": 2}, {"label": "B", "value": -1}],
                     "highlight": "A", "source": self.SRC},
                    {"type": "line", "heading": "Line", "series": [{"name": "X", "points": [["a", 1], ["b", 2]]}],
                     "highlight": True, "source": self.SRC},
                    {"type": "scatter", "heading": "Map", "points": [{"label": "P", "x": 101, "y": 99}],
                     "centre": [100, 100], "highlight": "P", "source": self.SRC},
                    {"type": "table", "heading": "Table", "columns": ["a", "b"], "numeric": [1], "rows": [["x", "1"]],
                     "source": self.SRC, "limits": "one line"},
                    {"type": "columns", "heading": "Cols", "columns": [{"title": "One", "items": ["<b>x</b>"]}]}],
                "limits": ["ข้อจำกัด"], "sources": [{"label": "Webull", "detail": "today"}]}

    def test_structure_matches_the_design_rules(self):
        page = render.render(self.report(), PARTNER)
        self.assertEqual(page.count('data-qc="band"'), 1)
        self.assertLess(page.index('data-qc="headline-en"'), page.index('data-qc="headline-th"'))
        self.assertEqual(page.count('data-qc="figure"'), 4)
        self.assertEqual(page.count('data-qc="source-line"'), 4)
        self.assertEqual(page.count('data-qc="signal-point"'), 1)
        self.assertNotIn("<b>x</b>", page)
        colours = set(re.findall(r"#[0-9A-Fa-f]{6}\b", page))
        self.assertLessEqual(colours, {"#F4F2EB", "#1D1D1B", "#173C2C", "#1E8E63", "#8C8B84", "#5E5D57", "#AEB9B1"})

    def test_referral_link_never_appears_without_its_disclosure(self):
        page = render.render(self.report(), PARTNER)
        self.assertIn(PARTNER["referral_url"], page)
        self.assertIn(render.esc(PARTNER["disclosure_th"]), page)
        self.assertNotIn(PARTNER["referral_url"], render.render(self.report(), {}))
        hidden = dict(PARTNER, show_in_report_footer=False)
        self.assertNotIn(PARTNER["referral_url"], render.render(self.report(), hidden))

    def test_contract_errors(self):
        for change in ({"title_th": ""}, {"title_th": "English"}, {"title_en": "ไทย"}):
            with self.assertRaises(render.ReportError):
                render.render(dict(self.report(), **change), PARTNER)
        bad = self.report()
        del bad["sections"][0]["source"]
        with self.assertRaises(render.ReportError):
            render.render(bad, PARTNER)
        bad = self.report()
        bad["sections"][3]["rows"] = [["only one cell"]]
        with self.assertRaises(render.ReportError):
            render.render(bad, PARTNER)


class BuildTest(unittest.TestCase):
    def test_generated_copies_are_current_and_plugin_is_consistent(self):
        done = subprocess.run([sys.executable, str(ROOT / "tools/build.py"), "--check"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_referral_reaches_every_skill_with_its_disclosure(self):
        for rules in sorted((ROOT / "skills").glob("*/references/desk-rules.md")):
            text = rules.read_text(encoding="utf-8")
            self.assertIn(PARTNER["referral_url"], text, rules)
            self.assertIn(PARTNER["disclosure_th"], text, rules)
            self.assertIn(PARTNER["disclosure_en"], text, rules)
            self.assertNotIn("{{", text, rules)

    def test_scripts_run_from_the_command_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.json"
            plan.write_text(json.dumps({"years": 5, "monthly": 1000}), encoding="utf-8")
            done = subprocess.run([sys.executable, str(ROOT / "skills/dca-plan/scripts/dca.py"), str(plan)],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertIn("projection", json.loads(done.stdout))
            plan.write_text("{}", encoding="utf-8")
            done = subprocess.run([sys.executable, str(ROOT / "skills/dca-plan/scripts/dca.py"), str(plan)],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 1)
            self.assertIn("error:", done.stderr)


if __name__ == "__main__":
    unittest.main()
