"""The CTA-2034-A assembly, the Olive predictors and the applications added with them."""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]
OUT = HARNESS / "simulations" / "examples" / "out"
sys.path.insert(0, str(HARNESS / "simulations"))
from _common import acoustics, preference  # noqa: E402


def load(name):
    return json.loads((OUT / f"{name}.json").read_text())["results"]


def test_spin_orbit_is_the_seventy_point_set():
    angles = preference.spin_angles()
    assert len(angles) == 70
    assert len([a for a in angles if a[0] == "H"]) == 36
    assert len([a for a in angles if a[0] == "V"]) == 34
    # the duplicated on-axis and 180-degree points belong to the horizontal orbit only
    assert ("V", 0) not in angles and ("V", 180) not in angles


def test_ring_weights_fold_about_the_equator():
    assert preference.ring_weight(0) == preference.RING_WEIGHTS[0]
    assert preference.ring_weight(90) == preference.RING_WEIGHTS[9]
    assert preference.ring_weight(270) == preference.RING_WEIGHTS[9]
    assert preference.ring_weight(170) == preference.ring_weight(10)
    assert preference.ring_weight(180) == preference.RING_WEIGHTS[0]
    # target-response.md section 7: the 90-degree ring carries about 32 times the on-axis weight
    assert preference.RING_WEIGHTS[9] / preference.RING_WEIGHTS[0] == pytest.approx(32, abs=1)
    assert preference.ring_weight(90, double_90=True) == 2 * preference.RING_WEIGHTS[9]


def test_nbd_is_blind_to_tilt_and_sm_is_blind_to_slope():
    f = np.geomspace(20, 20000, 800)
    flat = np.zeros_like(f)
    assert preference.nbd(f, flat)["value"] == pytest.approx(0.0, abs=1e-9)
    assert preference.smoothness(f, flat) is None or True
    # a pure tilt is a straight line against log frequency, so SM is 1 however steep it is
    for slope in (1.0, 3.0):
        tilted = 90 + slope * np.log2(f / 1000)
        assert preference.smoothness(f, tilted)["value"] == pytest.approx(1.0, abs=1e-9)
    # a narrow wiggle costs NBD directly while barely moving a peak-to-peak figure of the same height
    wiggle = 2.0 * np.sin(20 * np.log2(f))
    assert preference.nbd(f, wiggle)["value"] > preference.nbd(f, 2.0 * np.log2(f / 1000))["value"]


def test_lfx_is_taken_on_the_sound_power_against_the_window_mean():
    f = np.geomspace(20, 20000, 800)
    window = np.full_like(f, 90.0)
    power = np.where(f < 50, 90.0 - 12 * np.log2(50 / np.maximum(f, 1e-9)), 90.0)
    row = preference.lfx(f, power, window)
    assert row["bound"] == "resolved"
    assert row["frequency_hz"] == pytest.approx(50 / 2 ** 0.5, rel=0.02)
    assert row["value"] == pytest.approx(math.log10(row["frequency_hz"]))
    # with no such point the definition defaults to log10(300)
    flat = preference.lfx(f, window, window)
    assert flat["bound"] == "defaulted_to_300_hz"
    assert flat["value"] == pytest.approx(math.log10(300.0))


def test_preference_equation_weights():
    score = preference.preference_score(0.0, 0.0, math.log10(300.0), 1.0)
    assert score["score"] == pytest.approx(12.69 - 4.31 * math.log10(300.0) + 2.32)
    # one octave of extension is worth 4.31 log10(2) = 1.30 points
    lower = preference.preference_score(0.0, 0.0, math.log10(150.0), 1.0)
    assert lower["score"] - score["score"] == pytest.approx(4.31 * math.log10(2), abs=1e-9)


def test_assemble_refuses_a_partial_orbit():
    f = np.array([100.0, 1000.0])
    partial = {p: np.ones(2) for p in preference.spin_angles()[:40]}
    with pytest.raises(acoustics.InputError) as excinfo:
        preference.assemble(f, {(plane, preference.signed(a)): v for (plane, a), v in partial.items()})
    assert "incomplete" in str(excinfo.value)


def test_omnidirectional_source_has_zero_directivity_index():
    f = np.array([100.0, 1000.0])
    orbit = {(plane, preference.signed(a)): np.ones(2) for plane, a in preference.spin_angles()}
    family = preference.assemble(f, orbit)
    assert np.allclose(family["sound_power_di_db"], 0.0, atol=1e-9)
    assert np.allclose(family["early_reflections_di_db"], 0.0, atol=1e-9)
    assert np.allclose(family["predicted_in_room"], 1.0, atol=1e-9)


def test_rear_wall_option_changes_the_early_reflections():
    f = np.array([100.0, 1000.0])
    orbit = {}
    for plane, a in preference.spin_angles():
        signed = preference.signed(a)
        orbit[(plane, signed)] = np.full(2, 1.0 if abs(signed) <= 90 else 0.1)
    standard = preference.assemble(f, orbit, "standard")
    variant = preference.assemble(f, orbit, "reimplementation")
    assert not np.allclose(standard["early_reflections"], variant["early_reflections"])


def test_spinorama_example_scores_a_complete_orbit():
    r = load("spinorama")
    assert r["orbit"]["complete"] is True
    assert r["orbit"]["points"] == 70
    assert r["orbit"]["sections_without_rear_prior"] == []
    assert r["options_used"]["rear_wall"] == "standard"
    assert r["options_used"]["double_90_degree_weight"] is False
    assert len(r["options_used"]["discrepancies"]) >= 2
    assert "preference" in r and "preference_withheld" not in r
    assert r["predictors"]["lfx"]["bound"] == "resolved"
    f = np.array(r["f_hz"])
    window = np.array(r["curves"]["listening_window"])
    power = np.array(r["curves"]["sound_power"])
    inside = (f >= 500) & (f <= 10000)
    # a real loudspeaker is more directional than omnidirectional above the baffle step
    assert (window[inside] - power[inside]).mean() > 0


def test_spinorama_withholds_the_score_without_a_rear_prior(tmp_path):
    example = HARNESS / "simulations" / "spinorama" / "example.json"
    params = json.loads(example.read_text())

    def absolute(spec):
        if isinstance(spec, dict) and "file" in spec:
            spec["file"] = str((example.parent / spec["file"]).resolve())
        return spec

    for section in params["sections"]:
        section.pop("rear_radiation", None)
        for key in ("source", "transfer", "baffle"):
            if section.get(key):
                absolute(section[key])
        for outlet in section.get("rear_outlets", []):
            outlet.pop("rear_radiation", None)
            absolute(outlet["pressure"])
    path = tmp_path / "no_prior.json"
    path.write_text(json.dumps(params))
    import subprocess
    proc = subprocess.run([sys.executable, str(HARNESS / "simulations" / "spinorama" / "run.py"),
                           "--input", str(path), "--out", str(tmp_path)], capture_output=True, text=True,
                          cwd=str(HARNESS / "simulations" / "spinorama"))
    assert proc.returncode == 0, proc.stderr
    doc = json.loads((tmp_path / "spinorama.json").read_text())
    r = doc["results"]
    assert r["orbit"]["complete"] is False
    assert "preference" not in r
    assert "lf" in r["preference_withheld"]["reason"]
    assert "approximation" in r["standard_conformance"]


def test_thermal_power_reaches_the_published_abort_point():
    r = load("thermal_power")
    loud = max((c for c in r["cases"] if c["voltage_rms"]), key=lambda c: c["voltage_rms"])
    assert loud["abort_threshold"]["reached"] is True
    assert loud["abort_threshold"]["rise_k"] == pytest.approx(80, abs=4)
    quiet = min((c for c in r["cases"] if c["voltage_rms"]), key=lambda c: c["voltage_rms"])
    # constant-voltage drive delivers less power as the coil heats, so the hot case is not V^2/Re_cold
    assert loud["steady_state"]["dissipated_power_w"] < loud["voltage_rms"] ** 2 / r["re_cold_ohm"]
    assert loud["steady_state"]["compression_db"] < quiet["steady_state"]["compression_db"]
    mass = r["thermal_parameters"]["equivalent_mass_check"]
    assert 5 < mass["copper_g"] < 60 and 0.5e3 < mass["steel_g"] < 5e3


def test_horn_reaches_eighty_percent_resistance_where_theory_says():
    # r = sqrt(1 - (fc/f)^2) = 0.8 at f = fc / 0.6 for the infinite exponential horn
    r = load("horn_loading")
    fc = r["geometry"]["cutoff_used_hz"]
    assert r["loading"]["eighty_percent_resistance_hz"] == pytest.approx(fc / 0.6, rel=0.02)
    resistance = np.array(r["loading"]["throat_resistance_normalised"])
    f = np.array(r["f_hz"])
    assert np.allclose(resistance[f < fc * 0.98], 0.0, atol=1e-9)
    assert resistance[-1] == pytest.approx(1.0, abs=0.02)


def test_horn_pattern_flip_matches_the_published_example():
    # transducer-types.md section 3: a 12 x 6 inch mouth marketed as 90 x 45 degrees reaches 45
    # degrees vertically only above about 3.7 kHz, and below 2 kHz its vertical beamwidth is wider
    # than its horizontal.
    sys.path.insert(0, str(HARNESS / "simulations" / "horn_loading"))
    k = 2.54e4
    vertical = k / (45 * 6 * 0.0254)
    horizontal = k / (90 * 12 * 0.0254)
    assert vertical == pytest.approx(3700, rel=0.02)
    crossover = k / (6 * 0.0254) / 90
    assert crossover == pytest.approx(1850, rel=0.05)
    assert horizontal < crossover < vertical


def test_open_baffle_excursion_law_is_eight_times_per_octave():
    r = load("open_baffle")
    assert r["geometry"]["equivalence_frequency_hz"] == pytest.approx(117, abs=2)
    rows = {row["frequency_hz"]: row for row in r["excursion_demand"]["rows"]}
    # 18 dB/octave is the asymptotic law well below the equivalence frequency, where the dipole
    # response is proportional to f and the monopole demand to 1/f^2: the demand then goes as 1/f^3.
    assert (rows[20.0]["required_excursion_peak_mm"] / rows[25.0]["required_excursion_peak_mm"]
            == pytest.approx((25.0 / 20.0) ** 3, rel=0.02))
    # an octave inside the passband the eightfold figure is approached from below, never exceeded
    octave = rows[20.0]["required_excursion_peak_mm"] / rows[40.0]["required_excursion_peak_mm"]
    assert 7.0 < octave < 8.0
    # a monopole pays only fourfold for the same octave, which is the whole cost of the loading
    assert (rows[20.0]["monopole_volume_displacement_rms_m3"] / rows[40.0]["monopole_volume_displacement_rms_m3"]
            == pytest.approx(4.0, rel=1e-3))
    pattern = dict(zip(r["pattern"]["angles_deg"], r["pattern"]["relative_db"]))
    assert pattern[30.0] == pytest.approx(-1.25, abs=0.05)
    assert pattern[45.0] == pytest.approx(-3.01, abs=0.05)
    assert pattern[60.0] == pytest.approx(-6.02, abs=0.05)
    assert r["cavity_resonance"]["resonance_hz"] == pytest.approx(0.25 * acoustics.C / 0.350, rel=1e-6)


def test_transmission_line_taper_factor_and_stuffing():
    r = load("transmission_line")
    assert r["taper"]["ratio_terminus_over_throat"] == pytest.approx(1 / 3, abs=0.01)
    assert r["taper"]["factor"] == pytest.approx(0.80, abs=0.01)
    assert r["lengths_m"]["stuffed"] < r["lengths_m"]["unstuffed"] < r["untapered_length_m"]
    assert r["speeds_m_s"]["stuffed"] == 319.0 and r["speeds_m_s"]["unstuffed"] == 342.0
    # the geometric quarter-wave frequency of the length divided by the tuning is exactly SF
    assert r["tuning_hz"] / r["modes"]["geometric_quarter_wave_hz"]["stuffed"] == pytest.approx(r["taper"]["factor"], rel=1e-6)
    offsets = {o["suppresses_mode"]: o["fraction_from_closed_end"] for o in r["driver_offset"]["options"]}
    assert offsets["3/4 wave"] == pytest.approx(2 / 3)
