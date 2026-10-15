# thermal_power: what the speaker does after ten minutes

Two-body lumped voice-coil thermal model. It answers the question every sensitivity claim dodges: what is the output once the coil is hot. The coil dissipates `P_Re = i_rms^2 Re` into a coil body `(Rtv, Ctv)` coupled to the magnet and frame `(Rtm, Ctm)`, and the rising `Re` feeds back into the drive.

**Report a predicted thermal scenario with its parameter basis.** Datasheets rarely publish `Rtv`, `Rtm`, `Ctv` or `Ctm`. Use sourced driver-class priors, check equivalent masses and time constants, and compare plausible parameter ranges when heat affects selection. Choose the design and margins from those scenarios; no new user measurement is required.

**Two power-test protocols exist and they answer different questions.** This model's priors and its 130 %-of-cold-`RE` abort point come from the accelerated protocol — short steps, target coil rise — which measures how fast the coil heats. AES2-2012 clause 6 specifies an endurance test instead: pink noise a decade above the stated low-frequency limit, 12 dB crest factor, **two hours per step to thermal equilibrium**, with rated power being what survives two hours without permanent change. Both are reported in `results.test_protocols`, and nothing here is calibrated against the second, so no figure from this application is a rated power in the AES2 sense.

AES2 also requires `fs` to be reported **before and after** the power test. That is the cheapest available evidence of suspension change, it costs one extra impedance sweep, and no model here contains it — which is also the reminder that the framework's cold Thiele/Small parameters describe a driver that has not been played.

## Run

```
python framework/simulations/thermal_power/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `driver.re_ohm` | Cold DC resistance of the voice coil |
| `thermal.prior` | `dome_tweeter`, `midrange`, `woofer` or `compression_driver` — a starting parameter set to be overridden |
| `thermal.rtv_k_per_w`, `rtm_k_per_w`, `ctv_ws_per_k`, `ctm_ws_per_k` | The four parameters; any given here override the prior |
| `drive.voltages_rms` | Constant-voltage cases. The power falls as the coil heats, which the integration carries |
| `drive.powers_w` | Constant-power cases, for comparison with a published power test |
| `time.duration_s`, `time.points` or `time.values_s` | Integration window. Four long time constants is roughly steady state |
| `ambient_c`, `reference_c` | Ambient, and the temperature `driver.re_ohm` was measured at |

## Output (`results`)

- `thermal_parameters`: the set used, `tau_v_s = Rtv Ctv`, `tau_m_s = Rtm Ctm`, the steady-state K/W of each body, and `equivalent_mass_check` (`m_copper [g] = 2.7 Ctv`, `m_steel [g] = 2 Ctm`). A capacitance that implies an impossible mass is an extraction error, and this is where it shows.
- `cases[]`: per drive case, the time series of `coil_rise_k`, `magnet_rise_k`, `dissipated_power_w`, `re_ohm` and `compression_db`, the `steady_state` block with `settled` against four long time constants, the `abort_threshold` (130 percent of cold `Re`, about +80 K) with when it was reached, and the 50 to 100 K working window.
- `compression_over_drive_range`: the compression across the requested voltage span, beside the published calibration point of about 3 dB over a 12 dB range for a 51 mm-coil compression driver. A model that cannot reproduce the order of magnitude of that figure has wrong priors, not a device that does not compress.
- `test_protocol`: the IEC 60268 noise procedure, 2 dB steps on a 30 s cycle, the resistance abort, and the pilot-tone method for reading `Re` through a passive crossover.
- `feeds_into`: the keys that carry the steady-state coil temperature into `lf_box` (`thermal.coil_temperature_c`) and `crossover_network` (`thermal.coil_temperatures_c`).

## Reading it with the other applications

`compression_db` here is the level lost at constant drive voltage from the resistance change alone. `crossover_network`'s hot case reports the opposite sign on the electrical transfer, because a hot driver takes a larger share of the terminal voltage. Read the two together: the network gives the driver more volts and the driver turns fewer of them into sound. Nonlinear compression, which is instantaneous rather than thermal, is in neither.
