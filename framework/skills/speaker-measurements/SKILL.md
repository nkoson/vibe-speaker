---
name: speaker-measurements
description: Analyse measured loudspeaker and crossover performance from REW MDAT files, frequency-response exports and impedance data; diagnose branch overlap, phase, attenuation and load effects, propose component changes, and plan discriminating follow-up measurements. Reads files directly without mouse or screenshot control.
---

# Speaker measurements

Turn measurements into an explanation of the speaker's behaviour and a concrete improvement. The main work is acoustic and crossover analysis: identify what each branch contributes, why the sum has its shape, which circuit or physical mechanism controls the feature, and which change would improve it. Acquisition checks support that work; do not turn the task into an extended hunt for measurement errors.

Use [measurement analysis](../../references/measurement-analysis.md) for the engineering and primary sources, and [tool commands and formats](../../measurements/README.md) for execution. For component changes, also read [crossover design](../../references/crossover-design.md) and use `speaker-designer` to run the loaded circuit and complete acoustic sum. Keep source provenance in project records; builder explanations should describe the observed behaviour and action.

## Read the files first

Use the filesystem, not the REW UI. The launcher installs missing dependencies in `.speaker-venv` through the repository bootstrap. Run from the repository root:

```sh
.speaker-venv/bin/python framework/tools/analyze_measurements.py inspect "measurement.mdat"
.speaker-venv/bin/python framework/tools/analyze_measurements.py analyze "measurement.mdat" --out framework/projects/PROJECT/measurements/RUN --band 1500 4500
```

If the environment does not exist, `python3 framework/bootstrap.py --install-only` creates it. Thereafter use its Python. Inspect every record in a multi-measurement file, retain its name/index and original file hash, and identify which supplied files supersede earlier ones. Never select a fixed serialized object index or assume a single measurement. Saved mode preserves REW's saved curve and smoothing. IR mode explicitly creates a new windowed result; it is not a command to reproduce every REW display option.

Record confirmed microphone position/axis, speaker or branch, polarity, amplifier/output setting and reference arrangement in a JSON context file (`--context`). Consult existing conversation and project evidence before asking. The user's confirmation of identical output levels is evidence: preserve absolute levels and do not repeatedly request the same confirmation. Sweep dBFS does not alone establish terminal voltage. Keep the original files unchanged.

## Analyse the speaker and crossover

1. Read the overall measured response, then inspect the relevant frequency band at useful resolution. Identify the level/width of each hump or dip and its relationship to the woofer, tweeter and intended balance. Use mild display smoothing to reveal the trend while retaining unsmoothed data for numerical operations. Inspect the plots you create.
2. Where branch captures exist, run `crossover` with the woofer, tweeter and measured combined response. Compare absolute branch levels and their acoustic overlap. A maximum-possible-sum curve that remains low identifies insufficient branch output regardless of polarity. If branch output is sufficient but the measured sum is lower, inspect phase, acoustic delay and polarity. An upper bound is not the actual sum. Avoid blaming one branch solely from the combined SPL trace.
3. Relate the finding to the built circuit: excessive woofer roll-off, insufficient tweeter output through the handover, too much attenuation, resonance/notch behaviour, leakage above crossover, or phase disagreement. Compare direct versus filtered driver captures at the same drive to locate the electrical effect. Assess the load curve rather than substituting nominal impedance. Trace component values, DCR and parallel/series connections to the actual build.
4. Propose the smallest useful controlled change, and calculate its effect on both branches, their complex sum, input impedance and component/driver stress before recommending it. A resistor alters filter loading as well as level; a low-pass change affects phase as well as magnitude. When retargeting a measured filtered branch, remove the old electrical transfer and apply the new one to the full complex response **before** applying the common time gate. Do not divide an already short-gated response by the old filter. Never invent missing measured phase or measured impedance.
5. Explain the change's practical effect: flatter handover, corrected tonal balance, retained tweeter protection, or a specific remaining tradeoff. Compare old/new at unchanged drive. Use the user's stated target; do not equate lower narrow-band ripple with better overall balance if it creates a broad treble shelf.

## Focused acquisition checks

Check recorded calibration, available bandwidth, window and timing basis once. Follow up only on evidence that affects the conclusion. Individual impulses always contain a time axis; that does not establish a shared time origin across separate captures. Keep common-reference measurements on that origin. Do not independently align driver peaks, remove each branch's delay, or synthesize zero/minimum phase and call it measured phase.

For complete-speaker UMIK measurements, the same speaker can play reference and sweep (Output = Ref output). For separate branches, retain one unchanged high-frequency reference path; a second speaker is the simplest ordinary-wiring arrangement. Moving or modifying that path changes the reference. Acoustic clock correction and common timing solve different problems. Details and exact official controls are in the reference.

## Choose measurements that decide the next design step

Start with the unresolved circuit mechanism, not a generic checklist. Usually the useful set is each filtered branch plus the assembled speaker, all at the same microphone position and output setting; add a polarity-reversed sum when it distinguishes phase cancellation. Compare a direct woofer with its filtered capture to test electrical attenuation. Use a properly calibrated electrical impedance measurement when the load is the central unknown. Keep the tweeter's protective filter in place.

If a feature plausibly involves cabinet/room interaction, use a short/long window comparison or a controlled position change to distinguish it. If high-level compression or distortion is the issue, compare known drive steps and inspect absolute harmonics and noise, not just THD percentages. The reference provides these secondary branches without making them the default diagnosis.

Deliver an assessment with: observed feature and magnitude; most likely mechanism and evidence; specific change and expected response; the next discriminating measurement if needed. Cite result paths internally and primary technical sources for the causal explanation. Manufacturer manuals, REW help, standards and original engineering publications are appropriate. Forums, Reddit and unattributed shopping claims are not engineering sources.
