# Shared-rail prototype PCB exporter

`pcb_rails.py` turns a physical prototype-board layout into a segmented resistive wiring network, conductor schedule, geometry/connectivity report and vector construction sheets. Layout choices and interpretation belong to the agent; the tool does not approve a crossover or choose parts.

```
.speaker-venv/bin/python framework/tools/pcb_rails.py \
  --input PROJECT/final/pcb-layout.json \
  --circuit PROJECT/release/sim/board.params.json \
  --out PROJECT/final --pdf PROJECT/final/pcb-sheets.pdf
```

The input circuit supplies component values, physical endpoint IDs, sources, loads and modes. Its old wires are replaced; components remain unchanged. The layout supplies:

- `boards`: ID, `size_mm`, mounting `holes`, `rails`, `parts`, named `terminals` and optional `jumpers`. Coordinates are millimetres viewed from the copper/component side. The current PDF template is A2 and suits modules up to about 220 by 368 mm; larger modules require a larger sheet template.
- A rail has an ID, logical `net`, polyline `points`, `width_mm` and `section_mm2`. Each distinct rail remains separate even if its logical name is repeated: explicitly connect separate islands using jumpers or harnesses.
- Each physical part has its canonical `id`, body centre/width/height, `type`, coil `axis`, `restraint_holes_mm`, `stand_off_mm`, and two `leads`. Each lead has a path starting at its body exit and ending on its target `rail`. Source catalogue data can accompany these fields.
- `terminals` maps a label to `[rail_id, [x,y]]`. `harness` entries name `BOARD:terminal` or an external circuit endpoint, with ID and actual cut length. Jumpers specify two rail taps, a drawing path and cut length.
- `logical_components` maps every component ID to its intended pair of circuit nodes. `installation_notes`, `harness_notes`, `title`, `drawing_label` and `revision` are authored project content, not calculated advice.
- Copper resistivity, native-lead section, contact resistance and link section are explicit construction assumptions. A rail is split at every tap and bend; segment resistance is `rho * length / area`. Lead lengths include the specified stand-off height. Contact resistance is added at lead terminals and both ends of insulated links. Mitred rail joints require a properly soldered common land; this model does not infer a defective-joint resistance.

Outputs are `pcb-board.params.json` for `board_nodal`, `pcb-conductors.csv`, `pcb-audit.json` optional PDF, millimetre DXFs and 1:1 copper-artwork SVGs. The audit reports conductor counts and lengths, board/rail volume, logical endpoint mismatches, disconnected or shorted logical node groups, pairwise rail clearances, hole-to-copper distances, hole-pair ligaments, mounting-hole/lead projection clearances and body bounding-box clearances. These are quantities for review. Invalid taps raise an input error. A positive clearance does not establish temperature suitability, stock lead reach, magnetic isolation or mechanical strength. Review body shape, tie paths, mounting access, copper stock and rendered drawings independently using [crossover assembly](../references/crossover-assembly.md).

The drawing convention uses 1 by 5 mm copper strips over prototype-board lands or etched/milled tracks, with unused copper removed. The centreline schedule controls the finished width; butt joints are soldered over a retained copper land or track. Verify the selected stock before machining. All copper and connections appear from the same side; if routing on the reverse side, provide a mirrored copper view and its through-board interfaces as well.
