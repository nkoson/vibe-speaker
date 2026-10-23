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

The present paper arrangement fits a 220 x 390 mm carrier. A3 sheets are 1:1.
Each carrier's four A4 tiles cover the full rectangle with overlapping square
registration marks; these marks are not holes. Horizontal and vertical 100 mm
rulers allow checking printer scale. Print Actual Size / 100%, never Fit/Shrink.
Use only the component-face pages as drill templates; the wiring view is mirrored.

Keep substrate thickness, mounting stack, hole schedules, wire lengths and the
cabinet's displaced volume synchronized with the final construction records.
