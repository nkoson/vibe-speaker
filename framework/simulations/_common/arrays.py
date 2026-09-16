"""Criteria for several sources reproducing the SAME band, and the near/far-field border.

`baffle-and-driver-placement.md` governs the spacing between drivers that cross over to each other,
which is what the pair geometry in whole_speaker reports. This module governs the other case - the
woofers of an MTM, a stacked pair, a column - where the controlling physics is Urban, Heil and
Bauman's Fresnel analysis. Two sources reproducing the same band do not become one source because
they are close together; they become one source when the criteria below are met, and they comb when
they are not.
"""
import math

import numpy as np

from .cli import InputError, C

# The Active Radiating Factor a set of touching circular sources cannot exceed, before any flange,
# gap or cabinet wall is allowed for. It is below the 80 % criterion by construction, which is the
# actual argument for a waveguide.
TOUCHING_CIRCLES_ARF = math.pi / 4
ARF_CRITERION = 0.8

WST_CRITERIA = [
    "1. The sum of the individual flat radiating areas covers more than 80 % of the vertical frame of the array, OR",
    "2. the spacing between acoustic centres is smaller than lambda/2 at the highest operating frequency,",
    "3. AND the deviation from a flat wavefront is less than lambda/4 at the highest operating frequency - 5 mm at 16 kHz.",
    "Curved arrays add: 4. the product of enclosure tilt angle and throw distance is constant, and 5. the vertical "
    "cabinet size is bounded by STEP <= 2 d_min / (3 F_max ARF).",
    "Criterion 2 is unsatisfiable at high frequency - lambda/2 at 16 kHz is about 10.7 mm - and criterion 1 is "
    "unsatisfiable with circular sources, because touching circles give ARF = pi/4 = 78.5 %. That is what a waveguide "
    "is for: it converts a small circular driver into a tall, nearly rectangular aperture that can fill the frame.",
]


def spacing_criterion(spacing_m, upper_hz=None):
    """The lambda/2 criterion for one same-band group, and the frequency at which it fails.

    f_max = c / (2 d). For an MTM with 180 mm between woofer acoustic centres that is 953 Hz, and
    that number should be setting the crossover frequency before any fitting happens.
    """
    spacing_m = float(spacing_m)
    if spacing_m <= 0:
        raise InputError("a same-band group needs a positive spacing_mm between acoustic centres")
    f_max = C / (2 * spacing_m)
    out = dict(spacing_mm=spacing_m * 1000, half_wavelength_limit_hz=f_max,
               derivation="f_max = c / (2 d): above it the spacing exceeds lambda/2, the sources are no longer one "
                          "source, and the pattern develops the nulls the c/(2d) formula predicts.",
               use="this is the frequency that should set the crossover of a same-band group, and it is available "
                   "before any filter is fitted.")
    if upper_hz:
        out.update(highest_operating_hz=float(upper_hz), passes=bool(float(upper_hz) <= f_max),
                   spacing_over_half_wavelength=float(upper_hz) / f_max,
                   spacing_for_stated_upper_hz_mm=C / (2 * float(upper_hz)) * 1000)
    return out


def active_radiating_factor(radiating_area_m2, frame_area_m2):
    """ARF against the 80 % criterion, with the reason circular sources cannot meet it."""
    radiating_area_m2 = float(radiating_area_m2)
    frame_area_m2 = float(frame_area_m2)
    if radiating_area_m2 <= 0 or frame_area_m2 <= 0:
        raise InputError("the Active Radiating Factor needs positive radiating and frame areas")
    arf = radiating_area_m2 / frame_area_m2
    return dict(radiating_area_m2=radiating_area_m2, frame_area_m2=frame_area_m2, arf=arf, criterion=ARF_CRITERION,
                passes=bool(arf >= ARF_CRITERION), touching_circles_ceiling=TOUCHING_CIRCLES_ARF,
                note="ARF is the fraction of the array's frame that actually radiates. Touching circular sources average "
                     "pi/4 = 78.5 %, which is below the 80 % criterion before any gap, mounting flange or cabinet wall is "
                     "allowed for, so the criterion is impossible to satisfy with cones and domes. The paper's own "
                     "conclusion is that this is precisely what the waveguide is for.")


def near_field_border_m(frequency_hz, height_m):
    """The near/far-field border of a line source of height H, from the WST paper.

        d_B = (3 F H^2 / 2) sqrt(1 - (1 / (3 F H))^2)      F in kHz, H in metres

    Inside d_B level falls 3 dB per doubling of distance rather than 6, and polar data is not a
    far-field property at all. There is no near field below F = 1/(3H): the root goes imaginary, so
    an array does not control its own bass however tall it is.
    """
    f_khz = np.asarray(frequency_hz, float) / 1000
    h = float(height_m)
    if h <= 0:
        raise InputError("the near-field border needs a positive coherent radiating height")
    inner = 3 * f_khz * h
    with np.errstate(invalid="ignore"):
        border = np.where(inner > 1, 3 * f_khz * h * h / 2 * np.sqrt(1 - (1 / inner) ** 2), np.nan)
    return border


def no_near_field_below_hz(height_m):
    """F = 1/(3H) in hertz: below this an array of that height is already radiating into the far field."""
    return 1000.0 / (3 * float(height_m))


def near_field_table(frequencies_hz, height_m, observer_m=None):
    """The border at each frequency against the distance a result was actually computed at."""
    f = np.asarray(frequencies_hz, float)
    border = near_field_border_m(f, height_m)
    rows = []
    for frequency, distance in zip(f, border):
        row = dict(frequency_hz=float(frequency), border_m=None if np.isnan(distance) else float(distance))
        if observer_m and row["border_m"] is not None:
            row["observer_inside_near_field"] = bool(float(observer_m) < row["border_m"])
            row["observer_over_border"] = float(observer_m) / row["border_m"]
        elif observer_m:
            row["observer_inside_near_field"] = False
            row["observer_over_border"] = None
        rows.append(row)
    return dict(coherent_radiating_height_m=float(height_m), observer_distance_m=observer_m, rows=rows,
                no_near_field_below_hz=no_near_field_below_hz(height_m),
                laws="near field: 3 dB per doubling of distance (cylindrical). Far field: 6 dB per doubling "
                     "(spherical). Near-field extent is linear in frequency and QUADRATIC in height, so doubling the "
                     "height quadruples the near field.",
                consequence="polar plots and directivity figures are meaningless inside the near field - they describe "
                            "a far-field property. For a 1 m tall coherent radiating section the border is about 1.4 m "
                            "at 1 kHz and about 15 m at 10 kHz, so a 1 m response of a tall speaker is a near-field "
                            "response over most of its range.",
                caveat="THE FORMULA IS DERIVED FOR A LINE SOURCE OF HEIGHT H RADIATING AN ISOPHASIC WAVEFRONT, and a "
                       "conventional multiway is not that. The height used here is the coherent radiating section, not "
                       "the cabinet height, and the result is an indication of where far-field assumptions become safe "
                       "rather than a computed border for this geometry.")


def same_band_group(spec):
    """One group of sources reproducing the same band: the spacing criterion and, where the geometry
    is declared, the Active Radiating Factor."""
    spec = dict(spec or {})
    count = int(spec.get("count", 2))
    if count < 2:
        raise InputError("a same-band group has at least two sources; one source is not an array")
    spacing_mm = spec.get("spacing_mm")
    if not spacing_mm:
        raise InputError(f"same-band group '{spec.get('name')}' needs spacing_mm between acoustic centres; "
                         "it is what the lambda/2 criterion is computed from")
    row = dict(name=spec.get("name"), count=count, band_hz=spec.get("band_hz"),
               spacing=spacing_criterion(float(spacing_mm) / 1000, spec.get("upper_hz")))
    source = spec.get("source") or {}
    diameter_mm = source.get("radiating_diameter_mm")
    if diameter_mm:
        diameter = float(diameter_mm) / 1000
        radiating = count * math.pi * (diameter / 2) ** 2
        frame_height = float(spec.get("frame_height_mm") or count * float(spacing_mm)) / 1000
        frame_width = float(spec.get("frame_width_mm") or diameter_mm) / 1000
        row["active_radiating_factor"] = dict(
            active_radiating_factor(radiating, frame_width * frame_height),
            shape="circular", radiating_diameter_mm=float(diameter_mm),
            frame_mm=[frame_width * 1000, frame_height * 1000],
            frame_note="the frame defaults to the sources' own diameter by count times their spacing, which is the "
                       "touching-circles case; give frame_height_mm and frame_width_mm for the real array frame.")
    return row
