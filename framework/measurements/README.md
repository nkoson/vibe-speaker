# Offline loudspeaker measurement analysis

`tools/analyze_measurements.py` reads measurement files without REW running, a Java runtime, mouse control or screenshots. Missing Python dependencies are installed automatically through `bootstrap.py --install-only`, then the command re-enters `.speaker-venv`. Normal bootstrap also installs the pinned `javaobj-py3` parser. No audio is played and no measurement is acquired by these commands.

The analysis skill is [speaker-measurements](../skills/speaker-measurements/SKILL.md); its emphasis is measured speaker/crossover behaviour and improvement. [Engineering reference and sources](../references/measurement-analysis.md).

## Inputs and preserved information

| Input | Support |
|---|---|
| REW `.mdat` Java serialization | Multiple acoustic measurements; saved SPL/phase; raw impulse, calibration, window, acquisition and timing metadata. Structural reader exercised with REW V5.31.3 files. |
| `.frd`, `.txt`, `.csv` | One response per file, Hz / dB [/ degrees]. `*`, `#`, `;` comment lines; whitespace/comma/tab/semicolon separators. Decimal comma supported with tab/semicolon separators. |
| `.zma` or `--quantity impedance` text | Hz / ohms [/ degrees], preserving linear impedance units. |
| Analysis `.json` | Lossless numerical re-import, including impulse and calibration data. |

REW text may contain a zero phase placeholder for a magnitude-only measurement. Text phase is therefore not promoted to measured phase without `--phase-known`. Imported/RTA MDAT records without an IR require explicit `--quantity`; native impedance MDAT storage is not decoded as SPL or guessed as ohms: use its ZMA/text export. Unsupported MDAT headers or missing structures produce an explicit error, never an invented response.

Distortion, RT60, stepped-level and multi-trace text exports have different schemas and units. Do not pass them as ordinary FRD: use their named REW exports/official API and the interpretation reference. WAV impulse conversion is available through [response_prepare](../simulations/response_prepare/README.md), with explicit calibration and time origin. This reader does not deconvolve arbitrary audio recordings or claim every proprietary REW record type is supported.

## Inspect and analyse

```sh
.speaker-venv/bin/python framework/tools/analyze_measurements.py inspect "run.mdat"
.speaker-venv/bin/python framework/tools/analyze_measurements.py analyze "run.mdat" "second.mdat" --out framework/projects/PROJECT/measurements/RUN --band 1500 4500
.speaker-venv/bin/python framework/tools/analyze_measurements.py analyze "run.mdat" --select 1 3 --out framework/projects/PROJECT/measurements/GATED --mode ir --left-ms 1 --right-ms 5 --reference-ms 0 --window tukey --smoothing 12 --band 500 10000
```

Saved mode is the default. It copies REW's stored `splValues` and `phaseValues` without reapplying calibration or SPL offsets; it retains the existing smoothing and FDW in those curves. `--smoothing 12` adds a precisely defined 1/12-octave uniform log-frequency mean of power to the magnitude display and statistics only. It does **not** remove earlier smoothing or implement REW's proprietary smoothing kernel. CSV/JSON retain the pre-display-smoothing data. Use IR mode for new smoothing from raw data. Zero padding changes FFT sampling density, not resolution.

IR mode uses the raw stored sample interval (including decimation), original start time and an explicit common window reference. Rectangular, Hann and Tukey half-windows are supported; Tukey tapers the outer `--taper` fraction of each side (default .25). It retains the saved time axis and applies microphone/soundcard gain and phase once. The REW peak-to-RMS convention uses `20e-6 * 10^(irData.splOffset/20) / sqrt(2)` for pressure scaling. Calibration is interpolated linearly in Hz with endpoint hold, and any recorded 20 dB boost limit applies to combined calibration. The result records these processing choices. Custom IR mode does not apply FDW. C-weighting compensation, derived minimum-phase IRs and unresolved inversion flags require a saved response or REW export instead of guessed reprocessing.

`--context acquisition.json` preserves confirmed conditions verbatim, for example:

```json
{
  "distance_m": 1,
  "axis": "tweeter",
  "speaker": "right",
  "output_levels_identical": true,
  "reference_speaker_unchanged": true,
  "supersedes": ["earlier woofer and tweeter captures"],
  "notes": "Same mic/speaker positions and amplifier/output settings for this series"
}
```

Every measurement produces JSON, CSV and an index entry. Overview plots show magnitude, available phase and impulse envelope. Envelope peaks are numerical observations, not automatic declarations of reflections. Statistics cover the requested data overlap and, for custom gates, exclude frequencies below the reported right-window scale. Input hashes, calibration identity, saved SPL alignment, timing/clock metadata and custom processing settings remain in JSON. Existing analysis folders require `--overwrite`.

## Crossover evidence and arithmetic

```sh
.speaker-venv/bin/python framework/tools/analyze_measurements.py crossover --woofer W.json --tweeter T.json --combined WT.json --band 1500 6000 --out framework/projects/PROJECT/evaluations/crossover
.speaker-venv/bin/python framework/tools/analyze_measurements.py compare BEFORE.json AFTER.json --operation difference --out delta.json
.speaker-venv/bin/python framework/tools/analyze_measurements.py compare W.json T.json --operation sum --common-timing "same fixed left acoustic reference; mic unchanged; no individual time shifts" --out sum.json
```

`crossover` plots acoustic branches, a supplied measured sum and the triangle-inequality maximum possible sum. It reports equal-level crossings and the measured sum's shortfall below the bound. This separates inadequate branch output from possible phase cancellation without manufacturing a phase relationship. With `--common-timing` and unsmoothed phase data it also calculates the coherent sum and relative phase. A timing-reference flag alone cannot prove identical reference geometry across two files.

`difference` is B minus A in dB (ohms for impedance); `ratio` is complex B/A and requires common timing; `sum` is complex A+B; `bounds` needs only magnitudes. All operations use the common measured band, without extrapolation, independent level normalization or peak alignment. Complex arithmetic rejects already-smoothed saved MDAT curves; process unsmoothed impulses or use suitable exports, then smooth the sum. The files supply observed values; the agent selects a diagnosis and component changes.

For simulation interchange the result stores `response.complex` and `response.frequency_hz`. SPL complex values are **Pa RMS at the captured drive and geometry**, not pressure per volt or automatically at 1 m. Normalize only with a known voltage/distance basis; retain the saved timing or remove one declared common propagation delay. Source references can use explicit `frequency_path` and `path` fields. Do not double-count the original crossover or baffle.

## Validation

```sh
.speaker-venv/bin/python -m pytest framework/tests/test_measurements.py -q
```

Tests cover multi-record Java serialization, linear/log grids, calibration ownership, absolute impulse scale and phase, known delays, gated reflections, unchanged relative levels, complex sums/cancellation, smoothing, text units and missing phase, malformed inputs and CLI round trips. Set `REW_TEST_FILES` to an OS-path-separator-delimited list of private `.mdat` files to run the additional real-file test. Private captures are not committed. Saved-value extraction and custom IR processing are distinct validation targets.

REW's [official HTTP API](https://www.roomeqwizard.com/help/help/html/api.html) can independently provide numerical exports on builds that support it. Do not depend on it for basic offline import; the installed V5.31.3 build used in development reports `API not supported in this build`. REW documents its public exports and API, not a stable MDAT field schema. The adapter is structurally validated and its supported cases are explicit above.
