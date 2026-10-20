# enclosure_network

Arbitrary lumped chambers, vents, passive diaphragms and individually driven motors.
All quantities are simulated observables; no alignment is selected.

`chambers[]`: `{id,volume_l}`, optional `qa`, `ql`, `loss_reference_hz` or explicit
`leak_resistance_pa_s_m3`. Qa is a series absorption resistance and Ql is a shunt
leak; their reference frequency is mandatory when used.

`vents[]`: `{id,nodes:[a,b],area_m2,effective_length_m}`, optional
`resistance_pa_s_m3`, `count`, `position_m`. `null` denotes ambient. Length already
includes end corrections.

`radiators[]`: `{id,nodes,sd_cm2,mmp_g,cmp_m_per_n,rmp_ns_m}`, optional
`added_mass_g`, `count`, `position_m`.

`drivers[]`: `{id,ts,front_node,rear_node}`, optional `voltage_rms`, `phase_deg`,
`series_resistance_ohm`, `extra_mass_g`, `position_m`. Use individual terminal
voltages for separately wired motors. Multiple motors in a chamber remain coupled
through the solved pressure. Constant, lossy and creep T/S extensions are supported.

Alternatively `preset` expands `driver`, `rear`, `front`, `port`, `outer_port`,
`radiator`, optional `rear_port`/`coupling_port` into a network. Presets:
`infinite_baffle`, `sealed`, `vented`, `passive_radiator`, `double_tuned_reflex`,
`bandpass`, `bandpass_pr`. Chamber records need volume; branch records use the same
fields as above without id/nodes. `voltage_rms` defaults to 2.83.

`frequencies`, `space: half|full`, `observers_m` control evaluation. Outputs:
expanded network, complex chamber pressures, motor impedance/current, excursion,
acceleration, reaction force, copper loss, outlet flows/velocities/excursions,
separate emission pressures, total observer pressure and equation residual.
Zero-drive impedance is unresolved (null), not inferred from zero/zero.

A single nonzero-drive motor also exports `pressure_per_volt_pa`, `z_ohm` and a
source contract for `source_response` simulation imports. This is the explicitly
colocated emission sum. Use individual emissions and their positions for distributed
outlet effects. External series resistance, if supplied, remains in the acoustic
source-voltage normalization and must not be applied twice downstream.

See [passive enclosure networks](../../references/passive-enclosure-networks.md).
