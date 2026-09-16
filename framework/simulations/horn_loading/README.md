# horn_loading: throat impedance, mouth termination and constant-directivity sizing

Webster one-parameter throat impedance of an infinite exponential, hyperbolic-exponential or conical horn, the `k rm` mouth criterion at cutoff with both of its competing optima, and Keele's constant-directivity mouth relation applied to each plane with the pattern-flip check. It fills the largest capability gap for horn and PA work: `directivity` can describe a horn's pattern but nothing derived it from geometry, and nothing modelled loading at all.

**Bass-horn design from driver parameters is not here — it is in `horn_design`.** Keele's Thiele/Small equations for throat area, rear cavity volume, bandwidth, the HF corners and maximum acoustic output are now in hand and implemented there. Run that application for the design arithmetic and this one for the impedance of a contour already chosen.

**And read the contour curves against one finding before choosing a flare on them.** Geddes, at first hand: virtually any shape connecting a given throat and mouth area yields approximately the same impedance — within a dB or so — in the long-wavelength region where Webster's equation is valid, and outside that region the equation cannot predict the wavefront at all. The difference this application computes between exponential, hypex and conical is about 1 dB, produced by an equation that has stopped being valid where the distinction would matter.

## Run

```
python framework/simulations/horn_loading/run.py --input params.json --out results/
```

## Input

| Key | Meaning |
|---|---|
| `frequencies` | Grid, default 20 to 20000 Hz, 600 log points |
| `horn.flare` | `exponential`, `hypex` or `conical` |
| `horn.t` | The hypex family parameter: 1 is the exponential, 0 the catenoidal, and growing `T` approaches the conical. `0.5 < T < 1` is the useful range when loading is the goal |
| `horn.throat_area_cm2`, `horn.mouth_area_cm2`, `horn.length_mm` | The flare geometry |
| `horn.cutoff_hz` | Optional. When given it is used and the geometry's own cutoff is reported beside it, with their ratio |
| `horn.throat_intensity_w_m2` | Optional, for the air-nonlinearity estimate |
| `horn.coverage` | `horizontal_deg`, `vertical_deg`, `mouth_width_mm`, `mouth_height_mm` for the constant-directivity block |

## Output (`results`)

- `geometry`: flare rate from the geometry and from the stated cutoff, the length each implies, the reference length `x0 = c / (2 pi fc)`, and for a conical horn the apex-to-throat distance.
- `loading`: the normalised throat impedance (1 is full plane-wave loading of the throat), the absolute acoustic impedance, and the frequency at which the throat resistance first reaches 80 percent of its asymptote. Below cutoff the resistance of the infinite exponential and hypex horn is zero: the horn stops loading the diaphragm.
- `mouth`: `k rm` at cutoff and, for each of the two published criteria — 0.93 under a plane-wave assumption and 1.4 under a spherical-wave one — the mouth radius and area it asks for and the ratio the design actually has. **The sources disagree by a factor of 1.5 in radius and 2.3 in area; this application does not choose.**
- `constant_directivity`: per plane, the pattern-control limit `f = K / (theta d)` and the mouth dimension that would hold control down to cutoff; `planes_let_go_together` with the mouth aspect ratio the coverage pair actually requires; and `pattern_flip`, the band in which one plane still controls and the other has already let go, so the nominal coverage pair does not describe the horn there.
- `air_nonlinearity`: Beranek's `D2 [%] = 1.73e-2 (f / fc) It`, when a throat intensity was given.
- `mid_band_narrowing`: the 40 to 50 percent narrowing of spherical-segment horns, reported at second hand and not modelled.

## Limits worth repeating

Infinite-horn, plane-wave theory in one dimension. A real finite horn softens the cutoff and adds mouth-reflection ripple whose depth grows as the mouth shrinks below the `k rm` criterion — which is the practical reason the criterion exists. No driver, no phase plug, no throat-cavity rolloff, no mouth roundover, no diffraction slot and no higher-order modes. Geddes-lineage oblate-spheroidal waveguide theory is not represented at all. `K` is an empirical constant, not physics.
