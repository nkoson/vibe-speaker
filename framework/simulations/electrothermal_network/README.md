# electrothermal_network: Programme-weighted hot passive network

```sh
.speaker-venv/bin/python framework/tools/run_simulation.py electrothermal_network --input framework/simulations/electrothermal_network/example.json --out results --name electrothermal_network
```

`network` uses the crossover-network ladder/section input contract; each section also supplies its cold `re_ohm`. `thermal.<section name>.steady_resistance_k_w` defines a thermal scenario. `programme.voltage_rms` is total programme RMS voltage; optional `relative_psd` has one nonnegative value per frequency. Its default is 1/f, normalized by frequency integration.

The app iterates cold impedance plus copper resistance rise, loaded network current and `I² Re` heating. Thermal resistance maps heating to a target coil temperature; `iterations` and `relaxation` control the fixed-point calculation. `ambient_c` and `copper_alpha_per_k` set the resistance reference.

Output sections contain hot impedance, transfer, temperature and power; when a cold source exists, the exported per-terminal-volt pressure is scaled by the cold/hot impedance ratio for the unchanged mechanical model. Network dissipation is integrated at coincident frequencies under the programme PSD. Each iteration reports its heat-balance temperature residual.

Compare iteration/relaxation sensitivity and plausible thermal resistances. The model changes voice-coil resistance while holding mechanical and motor parameters fixed. It does not automatically heat the crossover coils or predict thermal endurance. Use `nonlinear_driver` for time-domain state changes and separately sourced nonlinear curves.

See [simulation methods](../../references/simulation-methods.md) for equations, sources and verification scope, and [advanced workflow guidance](../../skills/speaker-designer/references/advanced-simulation.md) for connecting the result to a design.
