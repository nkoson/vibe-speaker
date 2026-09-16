"""Physical leaves must conserve power and carry their own branch current."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import networks


def test_nested_bank_reports_every_leaf_and_conserves_power():
    f = np.array([100., 1000., 10000.])
    bank = dict(id="bank", type="parallel", position="series", parts=[
        dict(id="path", type="series", parts=[
            dict(id="r", type="R", value_ohm=4.),
            dict(id="c", type="C", value_uf=100., esr_ohm=.02)]),
        dict(id="l", type="L", value_mh=1., dcr_ohm=.1, core="air")])
    solved = networks.ladder_state(f, np.full(3, 8.), [bank], voltage=18.)
    leaves = list(networks.leaf_states(bank, solved["states"][0], f))
    np.testing.assert_allclose(sum(s["dissipation_w"] for _, s in leaves),
                               solved["states"][0]["dissipation_w"])
    rows = networks.leaf_summary([bank], solved["states"], f)
    assert all("max_dissipation_w" in row for row in rows)
    r, c, l = rows
    assert np.isclose(r["max_dissipation_w"] / c["max_dissipation_w"], 200.)
    np.testing.assert_allclose(leaves[0][1]["current"], leaves[1][1]["current"])
    np.testing.assert_allclose(leaves[0][1]["voltage"] + leaves[1][1]["voltage"], leaves[2][1]["voltage"])
    rating = networks.part_ratings([bank], solved["states"], f)[0]
    assert np.isclose(rating["max_current_rms_a"], l["max_current_rms_a"])
    assert not np.isclose(rating["max_current_rms_a"], abs(solved["states"][0]["current"]).max())


def test_plain_resistor_stress_matches_ohms_law():
    f = np.array([100., 1000.])
    element = dict(id="r", type="R", position="series", value_ohm=4.)
    state = networks.ladder_state(f, np.full(2, 8.), [element], voltage=12.)
    row = networks.leaf_summary([element], state["states"], f)[0]
    assert row["max_current_rms_a"] == 1.
    assert row["max_voltage_rms"] == 4.
    assert row["max_dissipation_w"] == 4.
