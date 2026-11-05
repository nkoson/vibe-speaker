# Existing-strip crossover layout

`stripboard_layout.py` compiles the agent's layout on a purchased board with continuous factory strips. It exports pad-to-pad copper segments, native-lead losses, full component/copper-face drawings, lead schedules and geometric quantities. It does not place components or select a layout.

```sh
.speaker-venv/bin/python framework/tools/stripboard_layout.py \
  --input PROJECT/layout.json --circuit PROJECT/board.params.json \
  --out PROJECT/layout-results --draw --cad
```

The JSON supplies `size_mm`, `grid {origin_mm,pitch_mm}`, logical `rows`, `copper_ohm_per_mm`, and `parts`. Each part has an electrical `id`, two logical `nodes`, a `center_mm`, `reserve_mm`, `footprint_mm`, an exact `body` (box or finite circular cylinder), and two `leads`. Each lead identifies its `[row,column]` pad and its complete `points_mm` route in three dimensions, `solder_tail_mm`, conductor `section_mm2`, and `sleeve_od_mm`. Coordinates are u right, v rear, z above the component face. Routes end at negative substrate thickness on the copper face. `under_body` marks a hidden routing projection in the drawing.

`holes` gives centres, diameter, role, part and optional copper-only clearance diameter. `harness` gives each external electrical node, pad and label, plus either `resistance_ohm` or `length_mm`/`section_mm2` (copper resistance plus two joints); optional `points_mm` draws its local insulated approach on the copper face. Preserve the source/load terminal names from the input circuit. Body centres and supplied lead exits are receiving-fit inputs: establish their physical meaning from the selected parts before authoring the routes. This first contract represents native leads only; layouts requiring extensions must describe those with the shared-wire compiler instead of hiding them inside a native route.

The compiler replaces existing interconnects, retains every component/source/load/mode, and splits each used strip at every tap. Two output cases retain nominal and doubled strip resistance. Native lead resistance uses routed 3D length plus the solder tail and a separately stated joint resistance. The agent feeds these inputs to `board_nodal` and replays affected acoustics.

The audit reports free-lead requirements, hole-to-strip margins, reserve-box gaps, sampled sleeve-to-body and sleeve-to-sleeve separations. Lead-pair separation is sampled at at most 0.25 mm intervals; resolve tight cases with finer geometry. `--cad` adds exact solid body-pair distances/intersection volumes and a STEP body assembly. Negative reserve-box gaps can occur at the empty corners of circular bodies; inspect the exact solids and restraints before interpreting them. Body models omit hidden winding detail and restraint geometry. The agent reviews routing, purchased lead exit/length, complete strap/lacing paths, heat spacing and tool access together. A list of positive clearances does not select a design.

Keep fabrication CAD and builder instructions synchronized with the final layout using [cad-drawing](../skills/cad-drawing/SKILL.md) and [speaker-documentation](../skills/speaker-documentation/SKILL.md). Compare complete alternatives with the same stock and circuit; state which lengths are routed geometry and which are receiving allowances.
