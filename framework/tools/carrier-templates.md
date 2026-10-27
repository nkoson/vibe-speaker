# Blank-carrier drilling templates

`carrier_templates.py` exports true-scale A3 drilling sheets, overlapping A4 tiles,
mirrored A2 underside wiring views, full-size millimetre DXFs and a hole CSV.

```
.speaker-venv/bin/python framework/tools/carrier_templates.py \
  --input PROJECT/layout.json --out PROJECT/templates
```

The input extends the shared-wire layout with `boards[].drill_holes`, each carrying
`id`, `kind` (`lead`, `restraint`, `wire_tie`, `mount`), `center` and `diameter`.
Coordinates are always from the component-face bottom-left datum. Each component
lead adds `hole`, `under_points` and `length_mm`; the last is the full routed
conductor length including vertical descent and the declared solder allowance.
`pcb_rails.compile_layout` uses this explicit length when supplied, preserving the
legacy planar-plus-stand-off convention for other layouts.

The exporter checks unique hole IDs, one passage per component end, edge and
inter-hole ligaments, DXF units and exported circle counts. It does not infer
lead exit geometry, decide component fit, or assess the carrier's mechanical
strength. Review body/fastener envelopes, native lead reach, sleeving, support
spacing and underside conductor clearances separately.

Carriers up to 277 x 180 mm receive one full-size landscape A4 sheet each.
Larger carriers use the existing four-tile arrangement for a 220 x 390 mm
outline. A3 sheets are also 1:1. The larger carrier's A4 tiles overlap with square
registration marks; these marks are not holes. Calibration rulers and the
dimensioned outline allow checking printer scale. Print Actual Size / 100%.
Use only the component-face pages as drill templates; the wiring view is mirrored.

Optional `underside_raise_mm` on a node wire marks a lower wiring plane in the
view and schedule. A lead's `under_z_mm` below -10 mm is dashed to distinguish
its lower route. Those fields describe authored geometry; provide the insulating
supports, clearance review and full conductor lengths in the construction data.

Keep substrate thickness, mounting stack, hole schedules, wire lengths and the
cabinet's displaced volume synchronized with the final construction records.
