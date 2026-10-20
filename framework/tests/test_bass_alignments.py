"""The bass arithmetic against the figures its sources publish.

Every expected value here is quoted in framework/references/, so a failure means the code drifted
from the reference, not that a tolerance was tuned.
"""
import json
import math
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]
OUT = HARNESS / "simulations" / "examples" / "out"
sys.path.insert(0, str(HARNESS / "simulations"))
from _common import acoustics, bass, thermal  # noqa: E402


def test_small_lossy_quartic_roots_at_ql_7():
    # enclosure-alignments.md section 1: at QL = 7 the B4 roots are 0.0548, 1.0000 and 18.237,
    # and only the one near unity is physical.
    solution = bass.solve_alignment("B4", 7.0)
    roots = solution["quartic"]["positive_real_roots"]
    assert roots == pytest.approx([0.0548, 1.0000, 18.237], abs=5e-3)
    assert solution["quartic"]["selected_root"] == pytest.approx(1.0, abs=1e-9)
    assert solution["quartic"]["rejected_roots"] == pytest.approx([0.0548, 18.237], abs=5e-3)


def test_b4_at_ql_7_matches_smalls_alignment_table():
    solution = bass.solve_alignment("B4", 7.0)
    assert solution["h_fb_over_fs"] == pytest.approx(1.0, abs=1e-9)
    assert solution["alpha_vas_over_vb"] == pytest.approx(1.061, abs=2e-3)
    assert solution["required_qt"] == pytest.approx(0.4048, abs=1e-3)
    assert solution["f3_over_fs"] == pytest.approx(1.0, abs=1e-3)


def test_lossless_limit_reduces_to_thieles_forms():
    a1, a2, a3 = bass.PROTOTYPES["B4"]
    solution = bass.solve_alignment("B4", 1e7)
    assert solution["h_fb_over_fs"] == pytest.approx(a3 / a1, rel=1e-5)
    assert solution["alpha_vas_over_vb"] == pytest.approx(a2 * (a3 / a1) - (a3 / a1) ** 2 - 1, rel=1e-4)
    assert solution["required_qt"] == pytest.approx(1 / (a1 * a3) ** 0.5, rel=1e-4)


def test_prototype_half_power_ratios():
    # B4 is -3 dB at f0 by definition; the Bessel prototype is at 1.5143 f0.
    assert bass.f3_over_f0(*bass.PROTOTYPES["B4"]) == pytest.approx(1.0, abs=1e-4)
    assert bass.f3_over_f0(*bass.PROTOTYPES["BL4"]) == pytest.approx(1.5143, abs=1e-3)


def test_chebyshev_alignment_prototype_has_declared_ripple():
    import numpy as np
    a1,a2,a3=bass.prototype("C4",ripple_db=.5)
    s=1j*np.geomspace(1,1000,20000)
    h=s**4/(s**4+a1*s**3+a2*s**2+a3*s+1)
    assert np.max(20*np.log10(abs(h)))==pytest.approx(.5,abs=.002)


def test_qb3_needs_its_free_coefficient_and_rejects_an_impossible_one():
    with pytest.raises(acoustics.InputError):
        bass.prototype("QB3")
    with pytest.raises(acoustics.InputError):
        bass.prototype("QB3", 3.0)
    a1, a2, a3 = bass.prototype("QB3", 4.0)
    assert a1 == pytest.approx((2 * 4.0) ** 0.5)
    assert a3 == pytest.approx((4.0 ** 2 + 2) / (2 * a1))


def test_sealed_q_peaking_table():
    # driver-selection.md section 2, peak and f3/fc against Qt.
    published = {0.5: (0.0, 1.554), 0.707: (0.0, 1.000), 1.0: (1.25, 0.786), 1.4: (3.5, 0.709), 2.0: (6.3, 0.674)}
    for qt, (peak, ratio) in published.items():
        row = bass.sealed_alignment(qt)
        assert row["peak_db"] == pytest.approx(peak, abs=0.03)
        assert row["f3_over_fc"] == pytest.approx(ratio, abs=1e-3)


def test_efficiency_ceiling_matches_smalls_worked_example():
    # 50 litres at f3 = 40 Hz gives 1.25 percent, about a 93 dB/2.83 V/m ceiling.
    ceiling = bass.efficiency_ceiling(40.0, 50.0)
    assert ceiling["eta_0_max_percent"] == pytest.approx(1.25, abs=0.01)
    assert ceiling["sensitivity_ceiling_1w_1m_db"] == pytest.approx(93.0, abs=0.1)


def test_reynolds_thresholds_are_diameter_dependent():
    # 10 m/s is Re ~ 67,000 in a 100 mm port but only ~33,000 in a 50 mm one, where Re = 50,000
    # needs about 15 m/s. The two thresholds coincide only near 100 mm.
    assert bass.reynolds(10.0, 0.100) == pytest.approx(67000, rel=0.02)
    assert bass.reynolds(10.0, 0.050) == pytest.approx(33000, rel=0.02)
    assert bass.velocity_at_reynolds(50000, 0.050) == pytest.approx(15.0, rel=0.03)


def test_small_minimum_vent_forms_agree_with_each_other():
    # SV >= 0.8 fB VD and dV >= sqrt(fB VD) are the same rule: pi/4 = 0.785, within Small's 10 percent.
    vent = dict(diameter_mm=100.0, count=1, area_m2=3.141592653589793 * 0.05 ** 2, physical_length_mm=200.0)
    out = bass.vent_physics(vent, 34.0, 150.0, 5.0, 5e-4)
    d = out["small_minimum_vent"]["required_single_diameter_m"]
    assert 3.141592653589793 / 4 * d ** 2 == pytest.approx(out["small_minimum_vent"]["required_area_m2"], rel=0.02)


def test_binding_displacement_limit_is_the_smallest_one():
    # driver-selection.md section 4: Klippel's example has xL = 2.28 mm against xC = 4.28 and
    # xD = 15.9, so inductance binds and a suspension-derived figure would be nearly twice too large.
    limit = bass.binding_displacement_limit(
        {"displacement_limits": {"xbl_mm": 2.63, "xc_mm": 4.28, "xl_mm": 2.28, "xd_mm": 15.9}})
    assert limit["binding_limit"] == "xl_mm"
    assert limit["xmax_mm"] == pytest.approx(2.28)
    # the IEC 62458 limits are one comparability group, so a set of them is not a mixed comparison
    assert limit["definition_groups_present"] == ["two_tone_10_percent"]
    assert limit["definitions_mixed"] is False
    # a single published Xmax is used, and the definition it came from travels with it
    single = bass.binding_displacement_limit({"xmax_mm": 5.75, "xmax_standard": "aes2_1984"})
    assert single["binding_limit"] == "published_xmax"
    assert single["standard"] == "AES2-1984"
    assert single["definition"]["comparable_group"] == "aes2_1984"
    # a blank field is recorded as not_stated rather than quietly assumed to mean anything
    assert bass.binding_displacement_limit({"xmax_mm": 5.75})["definition"]["name"] == "not_stated"
    # and free text is an error at the part record, not a figure that means nothing later
    with pytest.raises(bass.InputError):
        bass.binding_displacement_limit({"xmax_mm": 5.75, "xmax_standard": "AES2-1984"})


def test_displacement_limited_output_carries_the_kp_span():
    output = bass.displacement_limited_output(857.0, 5.2, 53.0, 0.03)
    assert output["kp"] == 3.0
    low, high = output["range_over_kp"]
    assert low["kp"] == 0.3 and high["kp"] == 5.0
    # the kP span Small's own figures cover is 0.3 to 5, which is 10 log10(5 / 0.3) = 12.2 dB of
    # spread on the rating: the honest band around the headline SPL figure.
    spread = high["spl_db_at_1m_half_space"] - low["spl_db_at_1m_half_space"]
    assert spread == pytest.approx(10 * math.log10(5.0 / 0.3), abs=0.01)


def test_thermal_calibration_points():
    # 130 percent of cold Re is about +80 K, and a 6.6 ohm coil at 150 C is about 10 ohms.
    assert thermal.rise_at_resistance_ratio(1.30) == pytest.approx(80, abs=4)
    assert thermal.resistance_at(6.6, 150.0) == pytest.approx(10.0, abs=0.1)
    assert thermal.compression_db(6.0, 6.0 * 1.30) == pytest.approx(-2.28, abs=0.02)


def test_baffle_step_is_shallower_near_the_baffle():
    # measurement-and-model-limits.md section 2: a 250 mm baffle shows about 5 dB of step at
    # 0.25 m against 6 dB in the far field.
    far = acoustics.baffle_step_db(250, 250, 125, 125)
    near = acoustics.baffle_step_db(250, 250, 125, 125, 0.25)
    assert far == pytest.approx(6.02, abs=0.05)
    assert near == pytest.approx(5.0, abs=0.2)
    assert acoustics.baffle_step_db(250, 250, 125, 125, 3.0) == pytest.approx(far, abs=0.05)


def test_roundover_does_nothing_below_its_lambda_eighth_frequency():
    corner = acoustics.roundover_corner_hz(0.020)
    assert corner == pytest.approx(343.0 / 0.160)
    assert abs(acoustics.roundover_factor(corner / 100, 0.020)) == pytest.approx(1.0, abs=1e-3)
    assert abs(acoustics.roundover_factor(corner * 100, 0.020)) < 0.02


def test_lf_box_example_reports_the_new_blocks():
    r = json.loads((OUT / "lf_box.json").read_text())["results"]
    assert r["displacement_limit"]["binding_limit"] == "xl_mm"
    assert r["efficiency"]["ceiling"]["margin_below_ceiling_db"] > 0
    # the solved alignments cover every requested QL and name the QT the driver would need
    targets = {(a["target"], a["ql"]) for a in r["solved_alignments"]}
    assert ("B4", 5.0) in targets and ("BL4", 7.0) in targets and ("QB3", 7.0) in targets
    # the flared duct in the example is designed to land on its requested tuning
    flare = r["vent_physics"]["flare"]
    assert flare["tuning_hz"] == pytest.approx(flare["requested_tuning_hz"], rel=0.02)
    assert flare["effective_length_m"] * 1000 > r["vent"]["physical_length_mm"]
    assert r["vent_physics"]["edge_radius"]["radius_minus_reference_mm"] >= 0


def test_every_document_carries_a_validity_block_and_constants():
    for path in sorted(OUT.glob("*.json")):
        doc = json.loads(path.read_text())
        if doc.get("status") != "computed":
            continue
        assert doc["validity"]["app_version"] == doc["version"], path.name
        assert doc["validity"]["statements"], path.name
        assert doc["constants"]["speed_of_sound_m_s"] == acoustics.C, path.name
        assert doc["constants"]["air_density_kg_m3"] == acoustics.RHO, path.name
