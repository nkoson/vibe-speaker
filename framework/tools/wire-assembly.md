# Shared-wire crossover layout

`wire_assembly.py` describes component placement and ordinary shared-node wiring on an insulating carrier. It exports the electrical realization, conductor schedules, component-side wiring/drilling sheets and millimetre carrier DXFs. The agent authors and selects the placement using [crossover assembly](../references/crossover-assembly.md); the tool reports routing and geometry quantities.

```
.speaker-venv/bin/python framework/tools/wire_assembly.py \
  --input PROJECT/final/wire-layout.json \
  --circuit PROJECT/release/sim/board.params.json \
  --out PROJECT/final --compare PROJECT/evidence/previous-layout.json \
  --pdf PROJECT/final/wire-sheets.pdf
```

The shared layout schema uses `boards`, physical `parts` and `rails` (the historical field name for shared-node paths). For this tool, each rail is ordinary wire: `id`, logical `net`, centreline `points`, actual `cut_length_mm`, conductive `section_mm2` and insulated `width_mm`. A path with `kind: direct_joint`, coincident endpoints and zero cut length represents a direct component-lead or harness joint. Parts supply body position/envelope, axis, height, stand-off, restraint holes and two lead paths ending on their target node wires. `terminals` identifies external wire attachment points. `harness` supplies each external conductor and cut length. `wire_anchors` specifies each tie position and its two holes; `overpasses` identifies intentional insulated lead/wire crossings and the agent's construction instruction. Installation/interpretation notes are authored project data.

The electrical compiler splits wires at their bends and taps. It distributes each specified cut length over those segments in proportion to drawn length, preserving the complete resistance of the cut conductor, including fitting allowance. Component leads and contact resistances are separate. Feed `assembly-board.params.json` to `board_nodal` and replay changed dependencies before using the results in the package.

For through-carrier leads, supply each lead's complete `length_mm`, including the
vertical route and solder allowance. This replaces the legacy planar length plus
component stand-off in the electrical compiler. Routing reports retain both the
planar projection and complete routed length. Use [blank-carrier templates](carrier-templates.md)
for component-face drilling and mirrored underside wiring exports.

Outputs include:

- `assembly-routing.json`: internal conductor path length, cut wire length, straight runs, bends, direct-joint count and connected-component route lengths. Optional `routing-comparison.json` retains both layouts' quantities.
- `assembly-geometry.json`: body bounding-box gaps, hole ligaments and lead/wire crossings. An intended insulated overpass remains visible in this report.
- `assembly-audit.json`: node identity/connectivity, segment quantities and geometry from the shared compiler.
- `assembly-conductors.csv` and `shared-wire-cut-list.csv`: electrical segments and the physical whole-wire cut schedule respectively.
- `assembly-cad/`: carrier outline, mounting/restraint/tie holes, routing guides and dimensions. WIRE_GUIDE is a placement annotation layer; CARRIER/MOUNT/RESTRAINT/WIRE_TIES define the mechanical work.

Routing quantities describe the drawn arrangement, rather than certifying a global optimum. Compare complete alternatives with the same circuit and conditions, account for native lead reach and practical joints, then state the engineering reason for selection. The current A2 template accommodates carriers approximately220 by390 mm; change sheet layout for larger assemblies.
