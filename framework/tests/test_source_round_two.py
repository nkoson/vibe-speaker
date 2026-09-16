"""The second source round's arithmetic against the figures its sources publish.

Every expected value here is quoted in framework/references/, so a failure means the code drifted
from the reference, not that a tolerance was tuned.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]
OUT = HARNESS / "simulations" / "examples" / "out"
sys.path.insert(0, str(HARNESS / "simulations"))
from _common import acoustics, arrays, bass, cli, horn, panels, preference  # noqa: E402


def load(name):
    return json.loads((OUT / f"{name}.json").read_text())["results"]


def document(name):
    return json.loads((OUT / f"{name}.json").read_text())


# --- A3: the Xmax definition field ------------------------------------------

def test_the_four_xmax_definitions_fall_into_three_comparability_groups():
    # measurement-and-model-limits.md section 4b and driver-selection.md section 4: geometric,
    # AES2-1984 and the two-tone 10 percent procedure are three different quantities, and only
    # IEC 62458 and AES2-2012 measure the same one.
    groups = {name: row["comparable_group"] for name, row in bass.XMAX_DEFINITIONS.items()
              if name != "not_stated"}
    assert groups["iec_62458"] == groups["aes2_2012"]
    assert len(set(groups.values())) == 3
    # AES2-2012's second tone is IEC 62458's xL frequency: the two probe the same mechanism
    assert "8.5 fs" in bass.XMAX_DEFINITIONS["aes2_2012"]["definition"]
    assert "8.5 fs" in bass.XMAX_DEFINITIONS["iec_62458"]["definition"]


def test_an_aes2_figure_beside_iec_limits_is_flagged_as_a_mixed_comparison():
    limit = bass.binding_displacement_limit(
        {"displacement_limits": {"xl_mm": 5.2, "xc_mm": 7.1, "x_aes2_2012_mm": 4.4}})
    assert limit["binding_limit"] == "x_aes2_2012_mm"
    assert limit["definitions_mixed"] is True
    assert limit["definition_kinds_present"] == ["parameter_based", "performance_based"]
    assert limit["definition"]["standard"] == "AES2-2012 clause 5.5"
    # the IEC limits on their own are one kind and one group, so nothing is flagged
    assert bass.binding_displacement_limit(
        {"displacement_limits": {"xl_mm": 5.2, "xc_mm": 7.1}})["definitions_mixed"] is False


def test_lf_box_prints_the_definition_beside_the_displacement_figure():
    r = load("lf_box")
    limit = r["displacement_limit"]
    assert limit["binding_limit"] == "xl_mm"
    assert limit["definition"]["name"] == "iec_62458"
    # the example's own published Xmax is geometric and larger than the binding limit
    assert limit["published_xmax"]["definition"]["name"] == "geometric"
    assert limit["published_xmax"]["xmax_mm"] > limit["xmax_mm"]
    basis = next(row for row in r["linear_scaling_to_limits"] if row["limit"] == "cone_excursion")
    assert "62458" in basis["limit_basis"]


# --- N5: the isobaric transform ---------------------------------------------

def test_isobaric_transform_is_rederived_from_the_definitions():
    # alternative-loadings.md section 2: Mms doubles, Cms halves, so fs and Qts are unchanged and
    # Vas halves; efficiency falls 3 dB for both wirings. This test re-derives it rather than
    # trusting the table, because the derivation is this repository's own and not a citation.
    ts = dict(fs_hz=35, vas_l=248.9, qms=6.0, qes=0.34, re_ohm=5.1, le_mh=0.72, sd_cm2=857,
              mms_g=85.2, bl_tm=16.7)
    single = acoustics.driver_elements(ts)
    for wiring, re_factor, bl_factor in (("series", 2.0, 2.0), ("parallel", 0.5, 1.0)):
        pair_ts, report = bass.isobaric_pair(ts, wiring)
        pair = acoustics.driver_elements(pair_ts)
        assert pair["mms"] == pytest.approx(2 * single["mms"])
        assert pair["cms"] == pytest.approx(single["cms"] / 2)
        assert pair_ts["vas_l"] == pytest.approx(ts["vas_l"] / 2)
        assert pair_ts["re_ohm"] == pytest.approx(ts["re_ohm"] * re_factor)
        assert pair["bl"] == pytest.approx(single["bl"] * bl_factor)
        assert pair["qts"] == pytest.approx(single["qts"])
        # fs comes out of Mms and Cms, so it has to be unchanged
        assert 1 / (2 * math.pi * math.sqrt(pair["mms"] * pair["cms"])) == pytest.approx(ts["fs_hz"])
        assert report["reference_efficiency"]["ratio"] == pytest.approx(0.5)
        assert report["reference_efficiency"]["sensitivity_change_db"] == pytest.approx(-3.01, abs=0.01)


def test_isobaric_example_halves_the_box_at_the_same_alignment():
    plain = load("lf_box")
    iso = load("lf_box_isobaric")
    single_vas = document("lf_box_isobaric")["inputs"]["driver"]["ts"]["vas_l"]
    assert iso["isobaric"]["pair"]["vas_l"] == pytest.approx(single_vas / 2)
    assert iso["isobaric"]["pair"]["fs_hz"] == iso["isobaric"]["single_driver"]["fs_hz"]
    # half the box (75 against 150 litres) at the same tuning, and the same f3 within a hertz or two
    assert iso["enclosure_used"]["net_volume_l"] == pytest.approx(plain["enclosure_used"]["net_volume_l"] / 2)
    assert iso["curves"][0]["statistics"]["cutoffs"]["f3"]["value_hz"] == pytest.approx(
        plain["curves"][0]["statistics"]["cutoffs"]["f3"]["value_hz"], rel=0.06)
    # and 3 dB less efficiency for it
    assert iso["efficiency"]["eta_0"] == pytest.approx(plain["efficiency"]["eta_0"] / 2, rel=1e-6)
    assert "same as one driver" in iso["isobaric"]["exchange"]["conclusion"]


# --- N4: bandpass topologies -------------------------------------------------

def test_bandpass_component_values_match_the_published_worked_example():
    # alternative-loadings.md section 1: VBF = 40 l, fBF = 30 Hz, QLF = 10 gives CABF = 2.822e-7,
    # LMAPF = 99.730 and RALF = 1.87993e5. The published figures use c = 343.68 and rho = 1.20
    # against this repository's 343.0 and 1.204, which is where the 0.1 percent comes from.
    node = acoustics.chamber_network(
        {"volume_l": 40, "ql": 10, "vent": {"tuning_hz": 30, "diameter_mm": 100}}, np.array([30.0]), 30.0, "front")
    assert node["cab"] == pytest.approx(2.8220e-7, rel=0.002)
    assert node["branch"]["lmap_kg_per_m4"] == pytest.approx(99.730, rel=0.002)
    assert node["record"]["ral_pa_s_per_m3"] == pytest.approx(1.87993e5, rel=0.002)


def test_bandpass_order_is_counted_from_the_topology():
    ts = dict(fs_hz=35, vas_l=248.9, qms=6.0, qes=0.34, re_ohm=5.1, sd_cm2=857)
    f = np.geomspace(15, 400, 200)
    sealed_rear = {"volume_l": 120, "ql": 10}
    front_vent = {"tuning_hz": 55, "diameter_mm": 150, "count": 2}
    fourth = acoustics.box_response(ts, {"type": "bandpass", "rear": sealed_rear,
                                         "front": {"volume_l": 80, "ql": 10, "vent": dict(front_vent)}}, f)
    sixth = acoustics.box_response(ts, {"type": "bandpass",
                                        "rear": dict(sealed_rear, vent={"tuning_hz": 30, "diameter_mm": 100}),
                                        "front": {"volume_l": 80, "ql": 10, "vent": dict(front_vent)}}, f)
    eighth = acoustics.box_response(ts, {"type": "bandpass",
                                         "rear": dict(sealed_rear, vent={"tuning_hz": 30, "diameter_mm": 100}),
                                         "front": {"volume_l": 80, "ql": 10,
                                                   "vent": dict(front_vent,
                                                                into={"volume_l": 40, "ql": 10,
                                                                      "vent": {"tuning_hz": 90, "diameter_mm": 150}})}}, f)
    assert [r["bandpass"]["order"] for r in (fourth, sixth, eighth)] == [4, 6, 8]
    # the driver radiates into its chambers only: every reported decibel leaves through a port
    assert fourth["bandpass"]["cone_radiates_directly"] is False
    assert np.allclose(np.abs(fourth["cone_pressure_pa"]), 0.0)
    # an eighth-order box has one internal vent that does not reach the room
    assert [p["radiates_to_room"] for p in eighth["bandpass"]["ports"]] == [False, True, True]
    # and no alignment table is claimed anywhere
    assert "no bandpass alignment tables" in fourth["bandpass"]["alignment_note"]


def test_bandpass_skirts_have_the_order_the_topology_implies():
    # a fourth-order box is a second-order high-pass from the sealed rear chamber and a second-order
    # low-pass from the front Helmholtz resonator, so both skirts asymptote to 12 dB/octave; venting
    # the rear makes its side fourth order.
    ts = dict(fs_hz=35, vas_l=248.9, qms=6.0, qes=0.34, re_ohm=5.1, sd_cm2=857)
    f = np.geomspace(5, 2000, 2000)
    front = {"volume_l": 80, "ql": 10, "vent": {"tuning_hz": 55, "diameter_mm": 150, "count": 2}}

    def slope(spl, low_hz, high_hz):
        a = np.interp(math.log(low_hz), np.log(f), spl)
        b = np.interp(math.log(high_hz), np.log(f), spl)
        return (b - a) / math.log2(high_hz / low_hz)

    fourth = acoustics.box_response(ts, {"type": "bandpass", "rear": {"volume_l": 120, "ql": 10},
                                         "front": dict(front)}, f)["spl_db"]
    assert slope(fourth, 10, 20) == pytest.approx(12, abs=1)
    assert slope(fourth, 400, 800) == pytest.approx(-12, abs=1)
    sixth = acoustics.box_response(ts, {"type": "bandpass",
                                        "rear": {"volume_l": 120, "ql": 10,
                                                 "vent": {"tuning_hz": 30, "diameter_mm": 100}},
                                        "front": dict(front)}, f)["spl_db"]
    assert slope(sixth, 8, 16) > 20


def test_bandpass_reports_the_port_pipe_resonance_and_demands_an_electrical_low_pass():
    r = load("lf_box_bandpass")
    resonances = r["bandpass"]["port_resonances"]
    port = resonances["ports"][0]
    # f = c / (4 L) on the port's physical length
    assert port["pipe_resonance_hz"] == pytest.approx(343.0 / (4 * port["physical_length_mm"] / 1000), rel=1e-6)
    assert "MANDATORY" in resonances["consequence"]
    # the bandwidth-for-gain exchange is reported, not implied
    exchange = r["bandpass"]["exchange"]
    assert exchange["passband_3_db"]["width_octaves"] > 0
    assert "given up" in exchange["exchange"]


def test_bandpass_narrower_passband_raises_the_midband_level():
    # the defining property, and the only reason to build one: bandwidth and gain are exchangeable,
    # because the same displacement-limited volume velocity is concentrated into fewer octaves.
    ts = dict(fs_hz=35, vas_l=248.9, qms=6.0, qes=0.34, re_ohm=5.1, sd_cm2=857)
    f = np.geomspace(10, 600, 900)
    def peak_and_width(front_volume_l, tuning_hz=45.0):
        r = acoustics.box_response(ts, {"type": "bandpass", "rear": {"volume_l": 120, "ql": 10},
                                        "front": {"volume_l": front_volume_l, "ql": 10,
                                                  "vent": {"tuning_hz": tuning_hz, "diameter_mm": 150, "count": 2}}}, f)
        spl = r["spl_db"]
        peak = float(spl.max())
        inside = np.flatnonzero(spl >= peak - 3)
        return peak, math.log2(f[inside[-1]] / f[inside[0]])
    rows = [peak_and_width(volume) for volume in (20, 40, 80, 160, 320)]
    peaks = [row[0] for row in rows]
    octaves = [row[1] for row in rows]
    assert peaks == sorted(peaks)
    assert octaves == sorted(octaves, reverse=True)
    # four octaves of front-chamber volume buys about 18 dB and costs a factor of seven in bandwidth
    assert peaks[-1] - peaks[0] > 15
    assert octaves[0] / octaves[-1] > 5


# --- N8: the aperiodic sweep -------------------------------------------------

def test_aperiodic_vent_spans_sealed_and_vented_at_its_limits():
    ts = dict(fs_hz=35, vas_l=248.9, qms=6.0, qes=0.34, re_ohm=5.1, sd_cm2=857)
    f = np.geomspace(15, 300, 300)
    base = dict(net_volume_l=120, tuning_hz=38, ql=10, qp=20, port={"diameter_mm": 100, "count": 2})
    vented = acoustics.box_response(ts, dict(base, type="vented"), f)["spl_db"]
    sealed = acoustics.box_response(ts, dict(net_volume_l=120, ql=10, type="sealed"), f)["spl_db"]
    zero = acoustics.box_response(ts, dict(base, type="aperiodic", rav_pa_s_per_m3=0.0), f)["spl_db"]
    huge = acoustics.box_response(ts, dict(base, type="aperiodic", rav_pa_s_per_m3=1e9), f)["spl_db"]
    assert np.allclose(zero, vented)
    # the sealed limit is approached rather than reached, because the two models refer their leakage
    # loss to different frequencies; 0.3 dB is the whole difference
    assert np.max(np.abs(huge - sealed)) < 0.3


def test_aperiodic_refuses_a_single_resistance():
    example = HARNESS / "simulations" / "examples" / "lf_box_aperiodic.json"
    params = json.loads(example.read_text())
    params["enclosure"]["rav_sweep_pa_s_per_m3"] = [600]
    with pytest.raises(cli.InputError) as excinfo:
        sys.path.insert(0, str(HARNESS / "simulations" / "lf_box"))
        import run as lf_box  # noqa: PLC0415
        lf_box.compute(params, example.parent)
    assert "at least two values" in str(excinfo.value)


def test_aperiodic_sweep_is_labelled_exploratory():
    r = load("lf_box_aperiodic")
    sweep = r["aperiodic"]["sweep"]
    assert sweep["status"].startswith("EXPLORATORY")
    assert "no source" in r["aperiodic"]["note"]
    # rising resistance moves the alignment from vented toward sealed, so f3 rises monotonically
    f3 = [row["cutoffs"]["f3"]["value_hz"] for row in sweep["cutoffs"]]
    assert f3 == sorted(f3)


# --- N1, N2, N3: panels ------------------------------------------------------

def test_leissa_pinned_column_reproduces_its_closed_form():
    # cabinet-materials-and-panels.md section 2: the simply supported column is exactly
    # lambda = pi^2 (1 + (a/b)^2), which is what fixes the normalisation with a the shorter side.
    published = {1.0: 19.74, 0.9: 17.86, 0.8: 16.19, 0.6: 13.42, 0.4: 11.45, 0.2: 10.26}
    for aspect, value in published.items():
        assert panels.lambda_pinned(aspect) == pytest.approx(value, abs=0.01)
    # and the clamped square is Leissa's 35.99, where Galin's closed form gives exactly 36
    assert panels.lambda_clamped(1.0)[0] == pytest.approx(35.99)


def test_edge_condition_moves_the_fundamental_by_about_an_octave():
    for aspect, ratio in ((1.0, 1.82), (0.8, 1.80), (0.6, 1.93), (0.4, 2.07), (0.2, 2.21)):
        computed = panels.lambda_clamped(aspect)[0] / panels.lambda_pinned(aspect)
        assert computed == pytest.approx(ratio, abs=0.02)


def test_ls3_6_side_panel_bracket_matches_the_worked_example():
    # 63 x 30 cm in 9 mm birch ply, E the geometric mean 8.0 GPa, rho 720: 196 to 393 Hz.
    band = panels.mode_band(0.30, 0.63, 0.009, 8.0e9, 720)
    assert band["pinned_hz"] == pytest.approx(196, abs=3)
    assert band["clamped_hz"] == pytest.approx(393, abs=3)
    assert band["band_octaves"] == pytest.approx(1.0, abs=0.05)
    # the BBC measured that cabinet's dominant side-panel output near 150 Hz, below even the pinned
    # bound, which is why the app refuses to nominate one number
    assert "150 Hz" in band["optimistic_at_the_bottom"]
    assert "false precision" in band["single_value_refused"]


def test_material_figure_of_merit_reproduces_the_bbc_ranking():
    # sqrt(E rho) / Q: GRP best, carbon-fibre honeycomb worst despite the highest stiffness-to-weight
    values = {name: panels.material({"name": name})["figure_of_merit_si"]["bbc_tabulated_equivalent"]
              for name in ("grp_random_50", "birch_ply_9mm", "oak_across_grain", "carbon_honeycomb")}
    assert values["grp_random_50"] == pytest.approx(0.085, abs=0.003)
    assert values["birch_ply_9mm"] == pytest.approx(0.044, abs=0.002)
    assert values["oak_across_grain"] == pytest.approx(0.015, abs=0.002)
    assert values["carbon_honeycomb"] == pytest.approx(0.009, abs=0.002)
    assert min(values, key=values.get) == "carbon_honeycomb"
    assert max(values, key=values.get) == "grp_random_50"


def test_damping_treatments_carry_the_measured_loss_factors_and_rank_per_millimetre():
    bare = panels.treatment("none")
    best = panels.treatment("roofing_felt_2_steel")
    assert bare["loss_factor"] == pytest.approx(0.0142, abs=0.0002)
    assert best["loss_factor"] == pytest.approx(0.1428, abs=0.0002)
    # a constrained layer beats a free layer: twice what the same felt gives unconstrained
    assert best["loss_factor"] > 2 * panels.treatment("roofing_felt_1")["loss_factor"]
    assert best["gain_over_bare_panel"] == pytest.approx(10.0, abs=0.2)
    # thickness is the cost, so the ranking is by loss factor per millimetre: Aquaplas at 2.9 mm
    # beats Celotex at 12 mm even though Celotex is the thicker treatment
    ranking = panels.treatment_ranking()
    assert ranking[0]["name"] == "aquaplas_1"
    assert [row["name"] for row in ranking].index("aquaplas_1") < [row["name"] for row in ranking].index("celotex_1")
    assert "RANK ORDER ALWAYS TRANSFERS" in bare["caveat"]


def test_audibility_criterion_shape_and_its_seventeen_decibel_span():
    criterion = panels.audibility_criterion_db([100.0, 400.0, 1000.0, 10000.0])
    assert criterion[0] == pytest.approx(-13.0)
    assert criterion[1] == pytest.approx(-30.0)
    assert criterion[2] == pytest.approx(-30.0)
    assert criterion[3] == pytest.approx(-30.0)
    # a 150 Hz resonance needs 13 dB of margin and a 1 kHz one needs 30: that 17 dB is the point
    assert criterion[2] - criterion[0] == pytest.approx(-17.0)
    # and the curve travels with its own limits
    record = panels.criterion_record([100.0, 1000.0])
    assert record["scatter_db"] == 1.0
    assert any("NO THEORETICAL BACKING" in line for line in record["limits"])


def test_plate_structure_reports_a_band_and_the_damping_it_was_given():
    r = load("plate_structure")
    panel = next(row for row in r["panels"] if row["name"] == "side_bay_1")
    assert panel["mode_band"]["clamped_hz"] > panel["mode_band"]["pinned_hz"]
    # the Navier solve is pinned, so its first mode is the lower edge of the band
    assert panel["first_mode_hz"] == pytest.approx(panel["mode_band"]["pinned_hz"], rel=0.02)
    treatments = {t["name"] for t in r["damping"]["treatments"]}
    assert {"none", "roofing_felt_2_steel"} <= treatments
    # every loss variant is a measured treatment, and damping lowers the panel's output
    variants = {v["treatment"]: v["audibility"]["worst_margin_db"] for v in panel["loss_variants"]}
    assert variants["roofing_felt_2_steel"] > variants["none"]
    assert "not a measured panel-to-direct pressure ratio" in panel["loss_variants"][0]["audibility"]["basis"]


# --- N6: same-band groups, ARF and the near-field border ---------------------

def test_mtm_woofer_spacing_sets_the_crossover_before_any_fitting():
    # arrays-and-directivity-control.md section 1: 180 mm between acoustic centres is 953 Hz.
    row = arrays.spacing_criterion(0.180, 800.0)
    assert row["half_wavelength_limit_hz"] == pytest.approx(953, abs=2)
    assert row["passes"] is True
    assert arrays.spacing_criterion(0.180, 1500.0)["passes"] is False


def test_touching_circles_cannot_meet_the_eighty_percent_criterion():
    group = arrays.same_band_group({"name": "pair", "count": 2, "spacing_mm": 180, "upper_hz": 800,
                                    "source": {"radiating_diameter_mm": 180}})
    arf = group["active_radiating_factor"]
    assert arf["arf"] == pytest.approx(math.pi / 4, rel=1e-9)
    assert arf["arf"] == pytest.approx(0.785, abs=0.001)
    assert arf["passes"] is False
    assert "waveguide" in arf["note"]


def test_near_field_border_reproduces_the_published_example():
    # the WST paper's own worked case: H = 5.4 m at 2 kHz gives 87.4 m against a published 88 m.
    assert arrays.near_field_border_m(2000.0, 5.4) == pytest.approx(87.4, rel=0.01)
    # and for a 1 m coherent radiating section, about 1.4 m at 1 kHz and about 15 m at 10 kHz
    assert arrays.near_field_border_m(1000.0, 1.0) == pytest.approx(1.41, abs=0.02)
    assert arrays.near_field_border_m(10000.0, 1.0) == pytest.approx(15.0, abs=0.1)
    # there is no near field below F = 1/(3H): a 4 m array does not control its own bass
    assert arrays.no_near_field_below_hz(4.0) == pytest.approx(83.3, abs=0.1)
    assert math.isnan(arrays.near_field_border_m(50.0, 4.0))


def test_whole_speaker_reports_the_border_against_its_own_observation_distance():
    r = load("whole_speaker")
    near = r["arrays"]["near_field"]
    assert near["observer_distance_m"] == 3.0
    assert near["observer_inside_near_field_above_hz"] == 8000.0
    assert "ISOPHASIC" in near["caveat"]
    group = r["arrays"]["groups"][0]
    assert group["spacing"]["half_wavelength_limit_hz"] == pytest.approx(953, abs=2)


# --- B3 rescoped and N7: horn design ----------------------------------------

def test_keele_worked_example_reproduces_line_by_line():
    # horn-and-waveguide-design.md section 1: the verification bar for the whole application.
    ts = dict(fs_hz=45, qts=0.210, vas_l=140, sd_cm2=500, re_ohm=5.6, le_mh=3.2, vd_m3=1.66e-4, bl_tm=15.0)
    d = horn.keele_design(ts, 50.0, front_cavity_l=1.1)
    assert d["throat"]["area_cm2"] == pytest.approx(242, abs=1)
    assert d["rear_cavity"]["volume_l"] == pytest.approx(32.6, abs=0.1)
    assert d["band"]["resistance_controlled_high_hz"] == pytest.approx(214, abs=1)
    assert d["hf_corners"]["moving_mass_fhm_hz"] == pytest.approx(430, abs=2)
    assert d["hf_corners"]["voice_coil_fhvc_hz"] == pytest.approx(560, abs=4)
    assert d["hf_corners"]["front_cavity_fhc_hz"] == pytest.approx(2400, abs=10)
    assert d["rear_cavity"]["annulling_check_hz"] == pytest.approx(50.0, abs=0.1)
    assert d["max_acoustic_output"]["par_w_acoustic"] == pytest.approx(35, abs=1)
    # the band ratio is 1/Qts^2, which is the single most useful number in horn driver selection
    assert d["band"]["ratio"] == pytest.approx(1 / 0.210 ** 2, rel=1e-9)


def test_horn_suitability_test_rejects_a_driver_before_any_modelling():
    # VB is finite and positive only when fs Qts < fc
    unsuitable = dict(fs_hz=45, qts=1.5, vas_l=140, sd_cm2=500, re_ohm=5.6)
    d = horn.keele_design(unsuitable, 50.0)
    assert d["suitability"]["suitable"] is False
    assert d["rear_cavity"]["volume_l"] is None
    assert "does not suit a horn" in d["rear_cavity"]["reason"]


def test_horn_efficiency_peaks_at_fifty_percent_when_ret_equals_re():
    ts = dict(fs_hz=45, qts=0.210, vas_l=140, sd_cm2=500, re_ohm=5.6, bl_tm=15.0)
    d = horn.keele_design(ts, 50.0)
    st = d["throat"]["area_m2"]
    # solve Bl for RET = RE and check the efficiency lands on the 50 percent ceiling
    bl = math.sqrt(5.6 * acoustics.RHO * acoustics.C * (500e-4) ** 2 / st)
    tuned = horn.keele_design(dict(ts, bl_tm=bl), 50.0)
    assert tuned["efficiency"]["ret_ohm"] == pytest.approx(5.6, rel=1e-6)
    assert tuned["efficiency"]["eta_percent"] == pytest.approx(50.0, rel=1e-6)
    assert tuned["efficiency"]["eta_percent"] >= d["efficiency"]["eta_percent"]


def test_mouth_criterion_reports_both_optima_and_says_they_disagree():
    mouth = horn.mouth_criteria(500.0, 0.05)
    plane = mouth["criteria"]["plane_wave_0p93"]
    spherical = mouth["criteria"]["spherical_wave_1p4"]
    assert spherical["required_radius_m"] / plane["required_radius_m"] == pytest.approx(1.4 / 0.93, rel=1e-9)
    assert spherical["required_area_m2"] / plane["required_area_m2"] == pytest.approx((1.4 / 0.93) ** 2, rel=1e-9)
    assert "disagree" in mouth["disagreement"]


def test_os_waveguide_cutoff_matches_the_published_figure():
    # horn-and-waveguide-design.md section 3: rt = 12.7 mm, theta0 = 30 degrees gives 862 Hz.
    w = horn.os_waveguide(12.7, 30.0, [0, 50, 100])
    assert w["cutoff_hz"] == pytest.approx(862, rel=0.01)
    assert w["included_angle_deg"] == 60.0
    # the contour starts at the throat radius and grows as tan(theta0) x
    assert w["contour"]["radius_mm"][0] == pytest.approx(12.7)
    assert w["contour"]["radius_mm"][-1] == pytest.approx(
        math.hypot(12.7, math.tan(math.radians(30.0)) * 100), rel=1e-9)
    assert "NO sharp cutoff" in w["cutoff_convention"]
    assert "NOT COMPUTED" in w["throat_impedance"]


def test_horn_design_example_and_directivity_agree_on_the_waveguide():
    design = load("horn_design")
    assert design["design"]["throat"]["area_cm2"] == pytest.approx(242, abs=3)
    assert design["os_waveguide"]["cutoff_hz"] == pytest.approx(862, rel=0.01)
    assert document("horn_design")["validity"]["throat_impedance_computed"] is False
    source = next(row for row in load("directivity")["sources"] if "os_waveguide" in row)
    assert source["os_waveguide"]["cutoff_hz"] == pytest.approx(862, rel=0.01)
    assert source["os_waveguide"]["included_angle_matches_declared_coverage"] is True


def test_horn_loading_states_that_contour_barely_moves_impedance():
    notes = document("horn_loading")["model_notes"]
    assert any("BARELY MOVES THE IMPEDANCE" in note for note in notes)
    assert document("horn_loading")["validity"]["contour_distinguishes_impedance_by_about_db"] == 1.0


# --- N9: the cardioid gradient pair -----------------------------------------

def test_cardioid_pattern_and_its_two_limits():
    c = load("open_baffle")["cardioid"]
    pattern = dict(zip(c["pattern"]["angles_deg"], c["pattern"]["relative_db"]))
    assert pattern[0.0] == pytest.approx(0.0)
    assert pattern[90.0] == pytest.approx(-6.02, abs=0.02)
    assert pattern[180.0] < -100
    # the upper limit is the same lambda/2 spacing criterion as any two-source array
    assert c["upper_limit"]["half_wavelength_limit_hz"] == pytest.approx(343.0 / (2 * 0.300), rel=1e-6)
    assert c["lower_limit"]["rolloff_db_per_octave"] == 6.0
    assert c["reported_practical_passband_octaves"] == [2.0, 2.5]
    assert "patent specification" in c["passband_source"]
    assert "resistive" in c["not_modelled"]


# --- A9: metrics named with their curve -------------------------------------

def test_every_metric_is_named_with_the_curve_it_came_from():
    metrics = load("spinorama")["predictors"]
    assert "NBD_ON" in metrics["named"] and "SM_PIR" in metrics["named"] and "NBD_PIR" in metrics["named"]
    assert not any(name in ("NBD", "SM", "AAD") for name in metrics["named"])
    assert metrics["on_axis"]["nbd"]["name"] == "NBD_ON"
    assert metrics["predicted_in_room"]["smoothness"]["name"] == "SM_PIR"
    assert metrics["lfx"]["defined_on"] == "sound_power"


def test_preference_reports_the_published_term_contributions():
    score = preference.preference_score(0.3, 0.3, math.log10(50.0), 0.9)
    assert score["contributions_percent"] == {"nbd_on": 31.5, "lfx": 30.5, "nbd_pir": 20.5, "sm_pir": 17.5}
    assert sum(score["contributions_percent"].values()) == pytest.approx(100.0)
    terms = load("spinorama")["preference"]["terms_used"]
    assert terms["nbd_on"] == "NBD_ON" and terms["sm_pir"] == "SM_PIR"


def test_a_curve_that_is_not_one_of_the_seven_says_so():
    f = np.geomspace(20, 20000, 400)
    metrics = preference.curve_metrics(f, np.zeros_like(f), "modelled", curve="woofer_near_field")
    assert metrics["curve_is_a_cta_curve"] is False
    assert metrics["nbd"]["name"] == "NBD_WOOFERNEARFIELD"
    assert "not comparable" in metrics["curve_note"]


def test_aad_and_lfq_are_computed_and_carry_zero_weight():
    f = np.geomspace(20, 20000, 600)
    tilted = 90 - 2.0 * np.log2(f / 1000)
    row = preference.aad(f, tilted)
    assert row["weight_in_generalized_model"] == 0.0
    assert "must not be reported as NBD" in row["note"]
    flat = np.full_like(f, 90.0)
    assert preference.lfq(f, flat, 40.0)["value"] == pytest.approx(0.0, abs=1e-9)


# --- B2: two thermal protocols, kept apart ----------------------------------

def test_the_two_thermal_protocols_are_reported_separately():
    r = load("thermal_power")
    protocols = r["test_protocols"]
    assert protocols["priors_came_from"] == "accelerated"
    assert protocols["accelerated"]["cycle_s"] == 30.0
    assert protocols["aes2_endurance"]["step_duration_s"] == 7200.0
    assert protocols["aes2_endurance"]["crest_factor_db"] == 12.0
    assert "NOT be reported as validated against" in protocols["do_not_merge"]
    # AES2's cheapest diagnostic is fs before and after, which no model here contains
    assert any("BEFORE AND AFTER" in line for line in protocols["aes2_endurance"]["reported_alongside"])
    assert document("thermal_power")["validity"]["calibration_protocol"] == "accelerated"


# --- A10: the meshing rule and the two universal statements -----------------

def test_element_size_rule_and_its_pollution_warning():
    # measurement-and-model-limits.md section 5: quadratic elements at f_max = 100 Hz allow 0.686 m.
    rule = acoustics.mesh_rule(100.0, order=2)
    assert rule["max_element_size_m"] == pytest.approx(0.686, abs=0.001)
    assert "LOSES VALIDITY AS FREQUENCY RISES" in rule["error_bound"]
    assert "NOT AGREEMENT WITH MEASUREMENT" in rule["what_it_does_not_buy"]
    # a first-order cell gets half the allowance of a quadratic element
    assert acoustics.mesh_rule(100.0, order=1)["max_element_size_m"] == pytest.approx(0.343, abs=0.001)


def test_cavity_modes_states_the_mesh_rule_for_its_wave_basis():
    validity = document("cavity_modes")["validity"]
    assert validity["method"] == "fvm"
    rule = validity["mesh_rule"]
    assert rule["shape_function_order"] == 1
    assert rule["max_element_size_mm"] == pytest.approx(343.0 / (10 * validity["max_mode_hz"]) * 1000, rel=1e-9)
    assert isinstance(rule["finest_mesh_inside_rule"], bool)


def test_every_result_document_carries_the_two_universal_statements():
    names = ["lf_box", "whole_speaker", "spinorama", "plate_structure", "horn_design", "cavity_modes",
             "crossover_network", "thermal_power", "open_baffle", "directivity"]
    for name in names:
        universal = document(name)["validity"]["universal"]
        assert len(universal) == 2, name
        assert "no error bar from the literature" in universal[0], name
        assert "NEVER QUOTE NUMERICAL ACCURACY" in universal[1], name


# --- A11: the saturation figure that does not exist -------------------------

def test_cored_coil_saturation_is_reported_as_not_published_with_the_frequency_rule():
    r = load("crossover_network")
    lf = next(row for row in r["sections"] if row["name"] == "lf")
    cored = next(row for row in lf["inductor_ratings"] if row["cored"])
    assert cored["saturation_current_a"] == "not published"
    assert cored["saturation_current_published"] is False
    assert "has not been measured" in cored["missing_rating_note"]
    rule = cored["frequency_rule"]
    assert rule["threshold_hz"] == 1200.0
    assert rule["passband_below_threshold"] is True
    assert rule["air_core_hierarchy"] == ["foil", "litz wire", "single wire"]
    # a coil in a midrange branch above the threshold is flagged instead
    mf = next(row for row in r["sections"] if row["name"] == "mf")
    assert mf["inductor_ratings"][0]["frequency_rule"]["passband_below_threshold"] is False
    # an air core needs no saturation question at all
    air = next(row for row in lf["inductor_ratings"] if row["core_kind"] == "air")
    assert air["saturation_current_published"] is True
    assert "does not saturate" in air["core_failure_mode"]
