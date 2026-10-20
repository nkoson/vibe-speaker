---
id: driver-impedance-identification
applies_when: Modeling lossy inductance or suspension creep and identifying parameters from impedance
updated: 2026-10-20
---

# Driver impedance and identification

For `s=j omega`, use `Zin=Ze+Bl²/Zm`. Mechanical loading adds to Zm; external wire
resistance adds to Ze for excitation but is excluded from the reported driver load.
The classical blocked impedance is `Re+sLe`.

Leach's fractional law is `Ze=Re+K s^n`, with K in ohm·second^n and `0<=n<=1`.
Its phase above the resistive term is n*pi/2. A rational alternative is
`Re+sLe+(sL2 || R2)`. The extended semi-inductive circuit used here is
`Re+sLeb+(Rss || sLe || Ke sqrt(s))`; omitted parallel branches are open.
These models represent small-signal eddy-current loss, not nonlinear inductance.

The viscoelastic law is `C(s)=C0[1+beta log(1+omega0/s)]` and
`Zm=R0+sMms+1/(sC(s))`. Beta is nonnegative and omega0 is explicit. C0/R0 are
model parameters, not necessarily conventional compliance/damping measured at
resonance. Import fitted values explicitly. Setting beta to zero recovers the
constant-compliance limit. Changing Re at fixed motor mechanics requires changing
Qes proportionally when deriving Bl from T/S data.

Parameter identification minimizes complex impedance residuals across free-air and
known added-mass or sealed-volume observations. A known Mms or Bl can fix the
scale with a single curve. With no known mechanical scale, free-air impedance alone
cannot identify absolute Mms, Cms and Bl separately. Return residuals, Jacobian rank,
singular values and parameter bounds; do not label a fit good or infer measurement
uncertainty from its residual alone. Added mass is assumed rigidly attached; sealed
volume and effective piston area are independently supplied inputs.

## Sources

- W. M. Leach Jr., “Loudspeaker Voice-Coil Inductance Losses: Circuit Models,
  Parameter Estimation, and Effect on Frequency Response,” *JAES* 50(6), 442–449,
  2002. [Author's paper](https://leachlegacy.ece.gatech.edu/papers/vcinduc.pdf).
- J. Candy and C. Futtrup, [Advanced Model Fit](https://speakerbench.com/doc/fit.html)
  and [Box Theory](https://speakerbench.com/doc/box_theory.html), equations 1–2 and 15.
  Author-published electrical and viscoelastic circuit equations. The local
  least-squares implementation is independent and does not reproduce proprietary fitting.
- M. H. Knudsen and J. Grue Jensen, “Low-Frequency Loudspeaker Models That Include
  Suspension Creep,” *JAES* 41, 3–18, 1993; and A. Ritter and F. T. Agerkvist,
  “Modeling Viscoelasticity of Loudspeaker Suspensions Using Retardation Spectra,”
  AES Convention 128, 2010, [publisher record](https://aes.org/publications/elibrary/elibrary-page/?id=15639).
  The implemented extended logarithmic expression is also derived in the authors'
  [time-domain notes](https://speakerbench.com/doc/time_theory.html), equation 44.
- Klippel GmbH, [SIM-AUR reference](https://docs.klippel.de/db-lab/latest/simulation-auralisation/simaur/simaur.html):
  LR-2 equivalent circuit and separation of small-signal and nonlinear parameters.
