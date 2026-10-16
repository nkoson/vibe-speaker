"""Unresolved and censored cutoff draws stay visible, including when no draw resolves."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("uncertainty_outcomes", Path(__file__).resolve().parents[1] / "simulations/lf_uncertainty/run.py")
uncertainty = importlib.util.module_from_spec(spec)
spec.loader.exec_module(uncertainty)


def test_mixed_cutoff_outcomes_have_explicit_denominator():
    rows = [{"f6_hz": 30, "f6_bound": "resolved"}, {"f6_hz": 50, "f6_bound": "resolved"},
            {"f6_hz": None, "f6_bound": "no_sustained_pass"}, {"f6_hz": 10, "f6_bound": "left_censored"}]
    item = uncertainty.summarize_samples(rows, [50])["f6_hz"]
    assert item["p50"] == 40
    assert item["total_draws"] == 4
    assert item["resolved_draws"] == 2
    assert item["unresolved_draws"] == 2
    assert item["bound_counts"] == {"resolved": 2, "left_censored": 1, "no_sustained_pass": 1}
    assert "conditional" in item["percentile_basis"]


def test_all_unresolved_cutoffs_remain_in_summary():
    rows = [{"f3_hz": None, "f3_bound": "no_sustained_pass"}] * 3
    item = uncertainty.summarize_samples(rows, [5, 50, 95])["f3_hz"]
    assert item["total_draws"] == item["bound_counts"]["no_sustained_pass"] == 3
    assert item["resolved_draws"] == 0
    assert item["p5"] is item["p50"] is item["p95"] is None
