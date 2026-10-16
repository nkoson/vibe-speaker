"""Analytic limiting cases for the rectangular-room reflection model."""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

SIMS = Path(__file__).resolve().parents[1] / "simulations"
sys.path.insert(0, str(SIMS))
from _common import acoustics, cli, radiation

spec = importlib.util.spec_from_file_location("room_response_run", SIMS / "room_response/run.py")
room = importlib.util.module_from_spec(spec)
spec.loader.exec_module(room)


def setup(tmp_path, order=1):
    f = np.array([30., 120., 500.])
    cli.write_document(tmp_path / "source.json", dict(status="computed", results=dict(
        f_hz=f, pressure_per_volt_pa=np.ones(len(f), complex), acoustic_depth_mm=0., directivity={"kind": "omni"})))
    params = dict(frequencies={"values_hz": f.tolist()}, room=dict(dimensions_m=[7., 9., 4.],
                  pressure_reflection=dict.fromkeys(room.WALLS, 0.)), max_order=order,
                  speakers=[dict(name="test", origin_m=[2., 2., 0.], input_voltage_rms=1., speaker=dict(
                      sections=[dict(name="full", source={"file": "source.json"}, position={"z_mm": 1000.})]))],
                  receivers=[dict(name="seat", position_m=[2., 4., 1.])])
    return params, f


def free(f, distance):
    return np.exp(-2j * np.pi * f * distance / acoustics.C) / distance


def test_absorbing_room_is_absolute_free_field_and_doubles_distance(tmp_path):
    p, f = setup(tmp_path, 3)
    p["receivers"].append(dict(position_m=[2., 6., 1.]))
    result = room.compute(p, tmp_path)
    for row, distance in zip(result["receivers"], [2., 4.]):
        np.testing.assert_allclose(row["pressure_pa"], free(f, distance), atol=1e-14)
        np.testing.assert_allclose(row["reflected_pressure_pa"], 0.)
    np.testing.assert_allclose(result["receivers"][0]["spl_db"] - result["receivers"][1]["spl_db"], 20 * np.log10(2))


def test_single_floor_reflection_complex_sum_and_existing_floor_model(tmp_path):
    p, f = setup(tmp_path)
    p["room"]["pressure_reflection"]["z_min"] = .7
    row = room.compute(p, tmp_path)["receivers"][0]
    expected = free(f, 2.) + .7 * free(f, np.sqrt(8.))
    np.testing.assert_allclose(row["pressure_pa"], expected, atol=1e-14)
    source = dict(name="test", pressure=np.ones(len(f), complex), baffle=np.ones(len(f)),
                  transfer=np.ones(len(f)), centre=np.array([0., 0., 1.]), directivity={"kind": "omni"}, tilt_rad=0., outlets=[])
    existing, _ = radiation.pressure([source], f, [[0., 2., 1.]], 2., floor_reflection=.7)
    np.testing.assert_allclose(row["pressure_pa"], existing[0] / 2 * np.exp(-2j * np.pi * f * 2 / acoustics.C))
    arrivals = row["direct_and_first_arrivals"]
    assert len(arrivals) == 2
    assert arrivals[1]["arrival_ms"] == pytest.approx(np.sqrt(8.) / acoustics.C * 1000)


def test_each_wall_uses_its_own_coefficient_and_image_distance(tmp_path):
    p, f = setup(tmp_path)
    values = [.1, .2, .3, .4, .5, .6]
    p["room"]["pressure_reflection"] = dict(zip(room.WALLS, values))
    result = room.compute(p, tmp_path)
    expected = free(f, 2.)
    distances = [np.sqrt(20.), np.sqrt(104.), 6., 12., np.sqrt(8.), np.sqrt(40.)]
    for coefficient, distance in zip(values, distances):
        expected += coefficient * free(f, distance)
    np.testing.assert_allclose(result["receivers"][0]["pressure_pa"], expected, atol=1e-14)
    assert result["image_count"] == 7


def test_second_order_parallel_wall_paths_have_product_not_square(tmp_path):
    p, f = setup(tmp_path, 2)
    p["room"]["pressure_reflection"].update(y_min=.2, y_max=.7)
    row = room.compute(p, tmp_path)["receivers"][0]
    first = free(f, 2.) + .2 * free(f, 6.) + .7 * free(f, 12.)
    second = .2 * .7 * (free(f, 16.) + free(f, 20.))
    np.testing.assert_allclose(row["pressure_pa"], first + second, atol=1e-14)
    np.testing.assert_allclose(row["last_order_pressure_pa"], second, atol=1e-14)


def test_omni_reciprocity_with_unequal_walls(tmp_path):
    p, _ = setup(tmp_path, 4)
    p["room"]["pressure_reflection"] = dict(zip(room.WALLS, [.1, .3, .5, .7, -.2, .8]))
    p["receivers"][0]["position_m"] = [4., 6., 2.]
    a = room.compute(p, tmp_path)["receivers"][0]["pressure_pa"]
    p["speakers"][0]["origin_m"] = [4., 6., 1.]
    p["receivers"][0]["position_m"] = [2., 2., 1.]
    b = room.compute(p, tmp_path)["receivers"][0]["pressure_pa"]
    np.testing.assert_allclose(a, b, atol=2e-14)


def test_yaw_turns_directional_source_and_its_reflected_rays(tmp_path):
    p, f = setup(tmp_path)
    section = p["speakers"][0]["speaker"]["sections"][0]
    section.update(directivity={"kind": "gaussian", "horizontal_deg": 60., "vertical_deg": 40.},
                   rear_radiation={"kind": "shadowed_monopole", "corner_hz": 200., "floor_db": -20.})
    # Rotate the entire square room configuration by 90 degrees about its centre.
    p["room"]["dimensions_m"] = [8., 8., 4.]
    p["room"]["pressure_reflection"].update(y_min=.6)
    a = room.compute(p, tmp_path)["receivers"][0]["pressure_pa"]
    p["speakers"][0].update(origin_m=[2., 6., 0.], yaw_deg=90.)
    p["receivers"][0]["position_m"] = [4., 6., 1.]
    p["room"]["pressure_reflection"].update(y_min=0., x_min=.6)
    b = room.compute(p, tmp_path)["receivers"][0]["pressure_pa"]
    np.testing.assert_allclose(a, b, atol=1e-14)


def test_frequency_dependent_pressure_coefficients_and_spatial_energy_mean(tmp_path):
    p, f = setup(tmp_path)
    p["room"]["pressure_reflection"]["z_min"] = {"points": [[30., .8], [500., .2]]}
    p["receivers"].append(dict(position_m=[3., 5., 1.2]))
    r = room.compute(p, tmp_path)
    coefficients = np.interp(np.log(f), np.log([30., 500.]), [.8, .2])
    np.testing.assert_allclose(r["receivers"][0]["pressure_pa"], free(f, 2.) + coefficients * free(f, np.sqrt(8.)))
    pressures = np.array([row["pressure_pa"] for row in r["receivers"]])
    expected = 10 * np.log10(np.mean(np.abs(pressures) ** 2, axis=0) / acoustics.P0 ** 2)
    np.testing.assert_allclose(r["spatial_summary"]["energy_mean_spl_db"], expected)


def test_import_relative_paths_transfer_polarity_and_outlet_no_second_floor(tmp_path):
    p, f = setup(tmp_path)
    folder = tmp_path / "candidate"
    folder.mkdir()
    speaker = p["speakers"][0].pop("speaker")
    speaker["floor"] = {"reflection": 1., "cases": [{"distance_m": 2.}]}
    speaker["cabinet"] = {"depth_mm": 400.}
    section = speaker["sections"][0]
    section["source"]["file"] = "../source.json"
    section["transfer"] = {"ideal": {"gain_db": -6.020599913279624, "polarity": -1}}
    section["rear_outlets"] = [dict(face="rear", voltage_rms=1., positions=[{"z_mm": 1000.}],
                                    pressure={"file": "../source.json", "path": "results.pressure_per_volt_pa"})]
    (folder / "speaker.json").write_text(json.dumps(speaker))
    p["speakers"][0]["speaker_file"] = "candidate/speaker.json"
    row = room.compute(p, tmp_path)["receivers"][0]
    # Rear outlet inherits half-space-to-full-space factor .5, applied once.
    np.testing.assert_allclose(row["pressure_pa"], -.5 * (free(f, 2.) + .5 * free(f, 2.4)), atol=1e-14)
    np.testing.assert_allclose(row["reflected_pressure_pa"], 0.)


@pytest.mark.parametrize("mutation", [
    lambda p: p["room"]["pressure_reflection"].update(z_min=1.01),
    lambda p: p["room"]["pressure_reflection"].update(z_min={"points": [[40., .5], [500., .5]]}),
    lambda p: p.update(max_order=-1),
    lambda p: p["receivers"][0].update(position_m=[0., 4., 1.]),
    lambda p: p["speakers"][0]["speaker"]["sections"][0].update(directivity={"kind": "piston", "sd_cm2": 100.}),
])
def test_invalid_geometry_boundaries_and_missing_rear_prior(tmp_path, mutation):
    p, _ = setup(tmp_path)
    mutation(p)
    with pytest.raises(cli.InputError):
        room.compute(p, tmp_path)


def test_source_band_cannot_be_silently_extended(tmp_path):
    p, _ = setup(tmp_path)
    p["frequencies"]["values_hz"] = [20., 500.]
    with pytest.raises(cli.InputError, match="cover the requested band"):
        room.compute(p, tmp_path)


def test_adding_coherent_identical_speaker_gives_six_db(tmp_path):
    p, _ = setup(tmp_path)
    a = room.compute(p, tmp_path)["receivers"][0]["spl_db"]
    p["speakers"].append(dict(p["speakers"][0], name="second"))
    b = room.compute(p, tmp_path)["receivers"][0]["spl_db"]
    np.testing.assert_allclose(b - a, 20 * np.log10(2))
