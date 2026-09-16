# horn_design: closed-form horn design from Thiele/Small parameters

Keele's recasting of the classical horn equations into the parameters a driver's datasheet actually carries. Every figure is closed form and each one settles a decision: whether the driver suits a horn at that cutoff at all, how big the throat and the rear cavity have to be, how wide a band the driver can work over, where the top rolls off, how much acoustic output its displacement allows, and how big the mouth has to be for the pattern.

**No throat impedance is computed here, and that is the design decision behind this application.** Geddes, at first hand: virtually any shape connecting a given throat and mouth area yields approximately the same impedance — within a dB or so — in the long-wavelength region where Webster's equation is valid, and outside that region the equation cannot predict the wavefront at all. `horn_loading` still computes the Webster impedance of a chosen contour; read its curves against that 1 dB caveat. The pattern comes from the mouth, not from the flare.

## Run

```
python framework/simulations/horn_design/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `driver.ts` | `fs_hz`, `vas_l`, `sd_cm2`, `re_ohm` and either `qts` or `qes` and `qms`; optional `le_mh` for the voice-coil corner, `bl_tm` for the efficiency, and `xmax_mm` or `vd_m3` for the output rating |
| `cutoff_hz` | The horn cutoff the design is sized for |
| `front_cavity_l` | Volume trapped between the cone and the throat, for the `fHC` corner |
| `mouth` | `area_cm2`, or `width_mm` and `height_mm`, for the `k rm` criterion |
| `coverage` | `horizontal_deg`, `vertical_deg`, `mouth_width_mm`, `mouth_height_mm` for the constant-directivity block |
| `os_waveguide` | `throat_radius_mm`, `half_angle_deg` (HALF the included angle), optional `axial_positions_mm` |

## Output (`results`)

- `design.suitability`: `fs Qts` against the cutoff. **`VB` is finite and positive only when `fs Qts < fc`**; a driver that fails this is not suited to a horn at that cutoff and no cavity volume will annul the reactance. One line of arithmetic, and it rejects unsuitable drivers before any modelling.
- `design.throat`: `ST = 2 pi fs Qts Vas / c`, the **efficiency-optimal** throat. Keele's own conclusion, credited to Small, is that fixing the throat to maximise efficiency removes one valuable degree of design freedom, so treat it as a reference point.
- `design.rear_cavity`: `VB = Vas / (fc/(fs Qts) - 1)` from Klipsch reactance annulling, with the annulling check `fLS (1 + Vas/VB) = fc` recomputed beside it. This is the equation that sets a bass horn's size, and the number is usually the reason the design is abandoned.
- `design.band`: `fHS = fs/Qts`, `fLS = Qts fs` and the ratio `1/Qts^2` in octaves. The width of the usable band goes as `1/Qts^2`, so a low `Qts` is what buys bandwidth.
- `design.hf_corners`: `fHM = 2 fs/Qts` (6 dB/octave), `fHVC = RE/(pi LE)` (12), `fHC = 2 Qts fs (Vas/VFC)` (18). The front cavity is the one the designer controls.
- `design.max_acoustic_output`: `PAR = 6.7e5 fc^2 VD^2 / (fs Qts Vas)` with the SPL it implies, valid down to `1.26 fc` for a well-designed finite horn with an optimum mouth. Thermal limits are a separate ceiling and are not in the equation.
- `design.efficiency`: `eta = 2 RE RET/(RE+RET)^2` with `RET = ST Bl^2/(rho0 c SD^2)`, peaking at 50 % when `RET = RE`.
- `mouth`: `k rm` at cutoff against **both** published optima, 0.93 under a plane-wave assumption and 1.4 under a spherical-wave one — a factor of 1.5 in radius and 2.3 in area. The sources disagree and this application does not choose.
- `constant_directivity`: per plane the pattern-control limit `f = K / (theta d)`, the mouth dimension that would hold control to cutoff, the mouth aspect ratio the coverage pair actually requires, and the **pattern flip** band in which one plane still controls and the other has already let go.
- `os_waveguide`: the contour `r(x) = sqrt(rt^2 + tan^2(theta0) x^2)` and the cutoff `fc = 0.2 c sin(theta0) / (pi rt)`. Verification bar: `rt = 12.7 mm` at `theta0 = 30 deg` gives 862 Hz.
- `webster_limits`: the four statements that bound everything above, including why no throat impedance is computed.

## Limits worth repeating

An OS waveguide has **no sharp cutoff**; the figure reported is the 0.2-of-asymptotic-resistance convention, so it means roughly what exponential-horn cutoff means and nothing more. Throat impedance for that contour has no closed form. Higher-order modes exist above a frequency set by throat radius and horn angle, and **no source consulted gives that frequency as a formula**, so none is invented. Keele's directivity constant is empirical, not physics. And a horn model cannot state its own accuracy above the first break-up of the driver, which for a compression driver is a measured frequency and not a simulated one.
