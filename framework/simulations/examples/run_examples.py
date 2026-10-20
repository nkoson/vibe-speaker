#!/usr/bin/env python3
"""Run every simulation example in dependency order into examples/out and print one line per result."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIMS = HERE.parent
OUT = HERE / "out"
sys.path.insert(0, str(SIMS.parent / "tools"))
from run_simulation import run_simulation  # noqa: E402

# (simulation folder, parameter file, result name)
CHAIN = [
    ("polar_import", SIMS / "polar_import" / "example.json", "polar_import"),
    ("response_prepare", SIMS / "response_prepare" / "example.json", "response_prepare"),
    ("enclosure_network", SIMS / "enclosure_network" / "example.json", "enclosure_network"),
    ("parameter_identification", SIMS / "parameter_identification" / "example.json", "parameter_identification"),
    ("network_diagnostics", SIMS / "network_diagnostics" / "example.json", "network_diagnostics"),
    ("response_diagnostics", SIMS / "response_diagnostics" / "example.json", "response_diagnostics"),
    ("source_response", HERE / "section_polar.json", "section_polar"),
    ("baffle_diffraction", HERE / "baffle_angular.json", "baffle_angular"),
    ("lf_box", SIMS / "lf_box" / "example.json", "lf_box"),
    # the same woofer in the three loadings added with the second source round: a fourth-order
    # bandpass, an isobaric pair in half the box, and the aperiodic resistance sweep
    ("lf_box", HERE / "lf_box_bandpass.json", "lf_box_bandpass"),
    ("lf_box", HERE / "lf_box_isobaric.json", "lf_box_isobaric"),
    ("lf_box", HERE / "lf_box_aperiodic.json", "lf_box_aperiodic"),
    ("lf_uncertainty", SIMS / "lf_uncertainty" / "example.json", "lf_uncertainty"),
    ("source_response", HERE / "section_lf.json", "section_lf"),
    # the same woofer section and the same datasheet curve with published_shape mode "replace", so the
    # two result documents can be read side by side to see what the option does
    ("source_response", HERE / "section_lf_replace.json", "section_lf_replace"),
    ("source_response", HERE / "section_lf_terminal.json", "section_lf_terminal"),
    ("source_response", SIMS / "source_response" / "example.json", "section_mf"),
    ("source_response", HERE / "section_uhf.json", "section_uhf"),
    ("directivity", SIMS / "directivity" / "example.json", "directivity"),
    ("baffle_diffraction", SIMS / "baffle_diffraction" / "example.json", "baffle_diffraction"),
    ("crossover_network", SIMS / "crossover_network" / "example.json", "crossover_network"),
    ("crossover_fit", SIMS / "crossover_fit" / "example.json", "crossover_fit"),
    ("board_nodal", SIMS / "board_nodal" / "example.json", "board_nodal"),
    ("whole_speaker", SIMS / "whole_speaker" / "example.json", "whole_speaker"),
    ("room_response", SIMS / "room_response" / "example.json", "room_response"),
    # the full orbit has to exist before response_metrics can take an LFX from its sound power curve
    ("spinorama", SIMS / "spinorama" / "example.json", "spinorama"),
    ("cavity_modes", SIMS / "cavity_modes" / "example.json", "cavity_modes"),
    ("plate_structure", SIMS / "plate_structure" / "example.json", "plate_structure"),
    ("response_metrics", SIMS / "response_metrics" / "example.json", "response_metrics"),
    ("thermal_power", SIMS / "thermal_power" / "example.json", "thermal_power"),
    ("horn_loading", SIMS / "horn_loading" / "example.json", "horn_loading"),
    ("horn_design", SIMS / "horn_design" / "example.json", "horn_design"),
    ("open_baffle", SIMS / "open_baffle" / "example.json", "open_baffle"),
    ("transmission_line", SIMS / "transmission_line" / "example.json", "transmission_line"),
    ("assembly_geometry", SIMS / "assembly_geometry" / "example.json", "assembly_geometry"),
    ("exterior_bem", SIMS / "exterior_bem" / "example.json", "exterior_bem"),
    ("room_modal", SIMS / "room_modal" / "example.json", "room_modal"),
    ("room_rays", SIMS / "room_rays" / "example.json", "room_rays"),
    ("coupled_cabinet", SIMS / "coupled_cabinet" / "example.json", "coupled_cabinet"),
    ("distributed_loading", SIMS / "distributed_loading" / "example.json", "distributed_loading"),
    ("nonlinear_driver", SIMS / "nonlinear_driver" / "example.json", "nonlinear_driver"),
    ("electrothermal_network", SIMS / "electrothermal_network" / "example.json", "electrothermal_network"),
    ("network_fit", SIMS / "network_fit" / "example.json", "network_fit"),
    ("system_scenarios", SIMS / "system_scenarios" / "example.json", "system_scenarios"),
]


def main(selection=None):
    OUT.mkdir(parents=True, exist_ok=True)
    failures = 0
    for folder, params, name in CHAIN:
        if selection and folder not in selection and name not in selection:
            continue
        script = SIMS / folder / "run.py"
        if not script.exists() or not params.exists():
            print(f"FAIL {folder}: missing script or example")
            failures += 1
            continue
        path = OUT / f"{name}.json"
        try:
            run_simulation(folder, params, OUT, name)
        except (ValueError, RuntimeError, OSError) as exc:
            failures += 1
            print(f"FAIL {folder:20s} -> {path.name}: {exc}")
        else:
            print(f"ok   {folder:20s} -> {path.name} (computed)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(set(sys.argv[1:])))
