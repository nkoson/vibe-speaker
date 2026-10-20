# board_nodal: physical board in every connection mode

Solves the realized crossover board as a netlist: every component between two named nodes, every wire with its resistance, the input terminal pairs, and the driver loads. Each connection mode says which terminals are linked and which inputs are driven, so a single-amplifier linked board and passive bi-amplification are solved from the same netlist. Reports the driver terminal transfers, input impedance and current per source, and the voltage, current and power of every component and wire, with optional tolerance draws.

Use it after the ladder design is settled in `crossover_network`, to check that the drawn board (including shared returns, links and wiring) does what the ladder intended, and to read component stress at the drive voltage you choose.

## Run

```
python framework/simulations/board_nodal/run.py --input board.json --out results/ [--name board_c01]
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 10 to 40000 Hz, 600 log points |
| `components[]` | `id`, `type` (`R`, `L`, `C`), value (`value_ohm`, `value_mh`, `value_uf`), optional `dcr_ohm` / `esr_ohm`, `nodes: [a, b]`, optional `tolerance_fraction`, optional `rating {voltage_rms, current_rms_a, power_w}` echoed next to the computed maxima |
| `wires[]` | `id`, `from`, `to`, `resistance_ohm` (0 merges the nodes) |
| `sources[]` | `id`, `plus`, `minus`, `voltage_rms`, optional `phase_deg` |
| `loads[]` | `id`, `plus`, `minus`, `impedance` as an inline model (see `source_response`) or `{file, path}` to a `results.z_ohm` curve |
| `modes[]` | `id`, `links [[nodeA, nodeB], ...]` closed for this mode, `active_sources [ids]`; inactive sources are open |
| `tolerances` | `draws`, `seed`, `C`, `L`, `R` spreads |

## Output (`results`)

Per mode: `sources[]` (active flag, `current_rms_a`, `input_z_ohm` complex record, minimum in 20 to 20000 Hz), `loads[]` (`transfer` = load voltage per active-source volt, complex record; `voltage_rms`, `current_rms_a`, `power_w`), `components[]` (curves and maxima with the frequency of maximum power, `rating` echoed), `wires[]` maxima, `kcl_relative_residual` and `power_relative_residual` (numerical health of the solve), and `tolerance` percentiles of each load transfer when draws were requested.

Compare `modes[].loads[].transfer` with `crossover_network` `results.sections[].transfer` (sign included: note the polarity is realized by wiring here) to confirm the board matches the intended ladder in every mode. Feed a load transfer into `whole_speaker` as a section `transfer` to hear the board rather than the ideal ladder.

## Mutual inductance and finite transformers

An inductor can declare `mutual_with: {other_coil_id: coupling}` with signed `-1 < coupling < 1`. The branch impedance matrix includes `j omega k sqrt(L1 L2)` and is checked for positive-definite inductance. Coupling values are explicit inputs, not inferred from board coordinates.

`transformers[]` supplies `id`, `primary_nodes`, `secondary_nodes`, `primary_inductance_mh`, `turns_ratio` (Np/Ns), `coupling`, `primary_dcr_ohm` and `secondary_dcr_ohm`. It expands to two coupled winding records and retains finite magnetizing/leakage behavior. An ideal transformer is approached as an explicit parameter limit; no silent perfect-coupling substitution is made. Current and power conservation are evaluated from the coupled solution.

Alternatively `transformers[].kind: ideal` uses exact constraints
`Vp = turns_ratio * Vs` and `Is = -turns_ratio * Ip`; only id, winding nodes
and turns ratio are needed. It has no magnetic loss or finite magnetizing current.
The solver returns winding voltages/currents and constraint residuals. This is an
explicit idealization, independent of the finite coupled-winding implementation.

Uncoupled inductors support `parallel_r_ohm` and `parallel_c_pf` across the entire
series DCR+L branch. For coupled windings represent shunts as separate R/C components.
Component dissipation includes the real part of the resulting branch impedance.
See [passive network diagnostics](../../references/passive-network-diagnostics.md).
