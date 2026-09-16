"""What the network keeps, what it passes on, and how many bodies it asks for."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "simulations"))
from _common import networks


def _split(f, load, elements, voltage):
    """Input, driver and component power of one section, the way the apps compute them."""
    state = networks.ladder_state(f, load, elements, voltage=voltage)
    driver = np.abs(state["load_current"]) ** 2 * load.real
    components = sum(leaf["dissipation_w"] for leaf in state["states"])
    return voltage ** 2 * np.real(1 / state["input_z"]), driver, components, state


def test_power_into_the_drivers_and_the_parts_sums_to_what_the_amplifier_delivers():
    f = np.array([100., 500., 2000.])
    load = np.full(3, 8.0 + 0j)
    elements = [dict(id="ser", type="R", position="series", value_ohm=4.),
                dict(id="sh", type="R", position="shunt", value_ohm=8.),
                dict(id="coil", type="L", position="series", value_mh=1., dcr_ohm=.3, core="air")]
    total, driver, components, _ = _split(f, load, elements, 10.0)
    np.testing.assert_allclose(driver + components, total, rtol=1e-9)


def test_a_lossless_ladder_passes_everything_and_a_pad_passes_its_own_fraction():
    f = np.geomspace(20., 20000., 200)
    load = np.full(len(f), 8.0 + 0j)
    lossless = [dict(id="c", type="C", position="series", value_uf=1000., esr_ohm=0.0)]
    total, driver, components, _ = _split(f, load, lossless, 2.83)
    clean = networks.power_efficiency(f, total, driver, components)
    assert clean["to_drivers_fraction"] > 0.999
    assert clean["loss_db"] < 0.01

    # A 6 dB L-pad into 8 ohm: series 4, shunt 8, which is a quarter of the power to the driver.
    pad = [dict(id="rs", type="R", position="series", value_ohm=4.),
           dict(id="rp", type="R", position="shunt", value_ohm=8.)]
    total, driver, components, _ = _split(f, load, pad, 2.83)
    padded = networks.power_efficiency(f, total, driver, components)
    assert abs(padded["to_drivers_fraction"] - 0.25) < 1e-6
    assert abs(padded["loss_db"] - 6.0) < 0.05
    assert all(abs(band["to_drivers_fraction"] - 0.25) < 1e-6 for band in padded["octave_bands"])


def test_a_zobel_diverts_current_in_proportion_to_the_impedance_it_flattens():
    """The reference's arithmetic: a shunt R across a driver takes |Z| / R times the driver's current."""
    f = np.array([1000.])
    load = np.full(1, 24.0 + 0j)
    bare = [dict(id="ser", type="R", position="series", value_ohm=0.001)]
    total_bare, driver_bare, components_bare, _ = _split(f, load, bare, 10.0)
    with_zobel = bare + [dict(id="z", type="R", position="shunt", value_ohm=8., role="compensation")]
    total, driver, components, _ = _split(f, load, with_zobel, 10.0)
    assert abs(components[0] / driver[0] - 3.0) < 1e-3          # 24 ohm flattened to 8 costs three parts in one
    assert driver[0] < driver_bare[0] * 1.001                   # the driver itself gains nothing
    assert total[0] > total_bare[0] * 3                         # the amplifier pays for all of it


def test_part_count_is_bodies_and_leaves_the_wiring_out():
    f = np.array([1000.])
    section = dict(name="lf", wire_loop_ohm=0.03, elements=[
        dict(id="bank", type="parallel", position="shunt",
             parts=[dict(id="r1", type="R", value_ohm=6.6), dict(id="r2", type="R", value_ohm=6.6)]),
        dict(id="coil", type="L", position="series", value_mh=1., core="air")])
    elements = networks.with_wire(section)
    state = networks.ladder_state(f, np.full(1, 8.0 + 0j), elements, voltage=2.83)
    rows = [dict(name="lf", components=networks.leaf_summary(elements, state["states"], f))]
    counts = networks.part_counts(rows)
    assert counts["total"] == 3
    assert counts["by_type"] == {"R": 2, "L": 1}
    assert any(row.get("parasitic") for row in rows[0]["components"])


def test_section_shares_are_read_over_each_passband():
    f = np.geomspace(20., 20000., 400)
    load = np.full(len(f), 8.0 + 0j)
    pad = [dict(id="rs", type="R", position="series", value_ohm=4.),
           dict(id="rp", type="R", position="shunt", value_ohm=8.)]
    total, driver, components, _ = _split(f, load, pad, 2.83)
    report = networks.power_efficiency(f, total, driver, components,
                                       sections=[(dict(name="mf", passband_hz=[500., 5000.]), driver)])
    row = report["sections"][0]
    assert row["name"] == "mf"
    assert abs(row["to_driver_fraction"] - 0.25) < 1e-6
    assert abs(row["loss_db"] - 6.0) < 0.05
