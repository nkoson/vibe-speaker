"""Loaded ladder networks shared by crossover_network and crossover_fit."""
import copy

import numpy as np

from . import acoustics, cli

# A compensated driver should look essentially resistive across at least one octave either side of
# its crossover: variation under about 1 ohm, roughly 10 percent. These are the targets the audit
# reports against; they are not enforced.
COMPENSATION_TARGET_OHM = 1.0
COMPENSATION_TARGET_FRACTION = 0.10


def section_load(section, f, base_dir):
    """Load impedance and free-field pressure per volt of a section from its source file or inline model."""
    pressure = None
    z = None
    if section.get("source"):
        ref = dict(section["source"])
        ref.setdefault("frequency_path", "results.f_hz")
        z = cli.curve_from_reference(dict(ref, path=ref.get("impedance_path", "results.z_ohm")), base_dir, f)
        try:
            pressure = cli.curve_from_reference(dict(ref, path=ref.get("pressure_path", "results.pressure_per_volt_pa")), base_dir, f)
        except cli.InputError:
            pressure = None
    if section.get("load"):
        load = section["load"]
        if "file" in load:
            ref = dict(load)
            ref.setdefault("frequency_path", "results.f_hz")
            z = cli.curve_from_reference(ref, base_dir, f)
        else:
            z = acoustics.impedance_model(load, f)
    if z is None:
        raise cli.InputError(f"section '{section.get('name')}' needs a source file or a load impedance")
    return z, pressure


def with_wire(section):
    """Elements of a section with its wiring resistance prepended as a series resistor."""
    elements = list(section.get("elements", []))
    for e in elements:
        if e.get("position") not in ("series", "shunt"):
            raise cli.InputError(f"section '{section.get('name')}': every element needs position series or shunt")
    wire = float(section.get("wire_loop_ohm", 0.0))
    if wire > 0:
        elements = [dict(id=f"{section.get('name')}_wire", position="series", type="R", value_ohm=wire, parasitic=True)] + elements
    return elements


def without_parasitics(elements):
    """The same ladder with every unintended resistance removed: coil DCR, capacitor ESR and the wire loop.

    The difference between this network and the real one is what the real parts cost in level, which
    is the only defensible reading of "insertion loss" separate from the attenuation the design asked for.
    """
    out = []
    for element in copy.deepcopy(elements):
        if element.get("parasitic"):
            continue
        for leaf in acoustics.iter_elements(element):
            if leaf.get("type") == "L":
                leaf["dcr_ohm"] = 0.0
            elif leaf.get("type") == "C":
                leaf["esr_ohm"] = 0.0
        out.append(element)
    return out


def compensated_load(f, load, elements, scale=None):
    """The driver seen through its declared compensation: the equalised resistance the filter works into.

    Only elements carrying "role": "compensation" are applied, because a shunt capacitor in a
    low-pass ladder and a Zobel across the driver are both shunt elements and only one of them is
    compensation. Where nothing is declared, the raw load comes back and the audit says so, which is
    itself the finding: an uncompensated driver at second order and above is the thing the audit exists
    to catch.
    """
    declared = [e for e in elements if str(e.get("role", "")).lower() == "compensation"]
    z = np.asarray(load, complex).copy()
    for element in declared:
        zi = acoustics.element_impedance(element, f, scale)
        z = z + zi if element["position"] == "series" else 1 / (1 / z + 1 / zi)
    return z, bool(declared)


def compensation_audit(f, raw_z, compensated_z, spec, declared=True):
    """Residual impedance variation of the compensated driver around each crossover it works at."""
    spec = spec or {}
    centres = spec.get("crossover_hz")
    if centres is None:
        return None
    centres = centres if isinstance(centres, (list, tuple)) else [centres]
    octaves = float(spec.get("octaves", 1.0))
    rows = []
    for centre in centres:
        centre = float(centre)
        band = (centre / 2 ** octaves, centre * 2 ** octaves)
        inside = (f >= band[0]) & (f <= band[1])
        if not np.any(inside):
            rows.append(dict(crossover_hz=centre, band_hz=list(band), covered=False))
            continue
        z = np.abs(compensated_z)[inside]
        raw = np.abs(raw_z)[inside]
        effective = float(np.mean(z))
        rows.append(dict(
            crossover_hz=centre, band_hz=list(band), octaves=octaves, covered=True,
            effective_resistance_ohm=effective,
            variation_ohm=float(np.ptp(z)), variation_fraction=float(np.ptp(z) / effective),
            min_ohm=float(z.min()), min_hz=float(f[inside][np.argmin(z)]),
            max_ohm=float(z.max()), max_hz=float(f[inside][np.argmax(z)]),
            max_reactance_fraction=float(np.max(np.abs(np.imag(compensated_z)[inside]) / np.abs(compensated_z)[inside])),
            uncompensated_variation_ohm=float(np.ptp(raw)), uncompensated_mean_ohm=float(np.mean(raw)),
            variation_removed_ohm=float(np.ptp(raw) - np.ptp(z)),
            effective_resistance_change_fraction=float(effective / np.mean(raw) - 1),
            target_ohm=COMPENSATION_TARGET_OHM, target_fraction=COMPENSATION_TARGET_FRACTION))
    return dict(crossovers=rows, compensation_declared=bool(declared),
                target="variation under about 1 ohm, roughly 10 percent, across at least one octave either side of the "
                       "crossover, preferably one and a half to two. Sensitivity to the load grows with filter order.",
                note="a driver whose impedance rise is semi-inductive rather than a clean single Le cannot be tracked by "
                     "one R-C at all; a residual that stays large after compensation is that case, not a value error. "
                     "The effective resistance reported here, not the nominal rating, is what belongs in a component formula. "
                     "Compensation typically lowers a driver's effective impedance by 20 percent or so, which is what "
                     "effective_resistance_change_fraction measures." if declared else
                     "no element of this section carries \"role\": \"compensation\", so these figures describe the bare driver. "
                     "Textbook filter alignments are derived for a resistive termination, and sensitivity to the load grows "
                     "with filter order. Compare compensation with fitting directly into the complex load; filter order "
                     "alone does not require a compensation branch.")


def insertion_loss(f, load, elements, transfer, band_hz=None):
    """What the network takes off this section: the real parts' cost, and the total passband loss.

    resistive_loss_db is against the same ladder with coil DCR, capacitor ESR and the wire loop
    removed, so it isolates the parasitics from the attenuation the topology was asked for.
    """
    ideal, _ = ladder_transfer(f, load, without_parasitics(elements))
    actual = np.asarray(transfer, complex)
    resistive = acoustics.db(ideal) - acoustics.db(actual)
    passband = acoustics.db(actual)
    band = band_hz or [float(f[0]), float(f[-1])]
    inside = (f >= band[0]) & (f <= band[1])
    peak = float(passband[inside].max()) if np.any(inside) else float(passband.max())
    near_peak = inside & (passband >= peak - 1.0)
    return dict(band_hz=list(band), resistive_loss_db=resistive, total_loss_db=-passband,
                passband_peak_transfer_db=peak, passband_loss_db=-peak,
                mean_resistive_loss_in_passband_db=float(np.mean(resistive[near_peak])) if np.any(near_peak) else None,
                passband_definition="the frequencies inside band_hz within 1 dB of the section's own maximum transfer",
                note="a heavily padded network with high-DCR coils has been quoted as losing as much as 3 dB overall, which is "
                     "an upper bound from an author arguing for bi-amping rather than a typical value. Each series element's "
                     "contribution is 20 log10(R / Z + 1) against the impedance it works into.")


OCTAVE_BAND_EDGES_HZ = [(22.1, 44.2), (44.2, 88.4), (88.4, 176.8), (176.8, 353.6), (353.6, 707.1),
                        (707.1, 1414.2), (1414.2, 2828.4), (2828.4, 5656.9), (5656.9, 11313.7), (11313.7, 22627.4)]


def _weighted_share(f, numerator, denominator, inside):
    """Share of denominator taken by numerator, weighted for equal energy per octave (1/f)."""
    if not np.any(inside):
        return None
    weight = 1.0 / f[inside]
    bottom = float(np.trapezoid(denominator[inside] * weight, f[inside]))
    if bottom <= 0:
        return None
    return float(np.trapezoid(numerator[inside] * weight, f[inside]) / bottom)


def power_efficiency(f, input_power_w, driver_power_w, component_power_w, sections=None, band_hz=(20.0, 20000.0)):
    """How the amplifier's power divides between the drivers and the network that feeds them.

    Every figure is a share of the real power the amplifier delivers, at the flat drive voltage the
    run was given. The weighting is pink - equal energy per octave - because a share integrated
    against a flat voltage over-counts the top of the band relative to any programme material. The
    result is a reading of the network that was designed, not a target: what share is acceptable is
    the level budget's answer and the designer's, and the figure means nothing without the pad
    depths and the compensation audit beside it.
    """
    f = np.asarray(f, float)
    inside = (f >= band_hz[0]) & (f <= band_hz[1])
    to_drivers = np.asarray(driver_power_w, float)
    to_components = np.asarray(component_power_w, float)
    total = np.asarray(input_power_w, float)
    share = _weighted_share(f, to_drivers, total, inside)
    bands = []
    for lo, hi in OCTAVE_BAND_EDGES_HZ:
        sel = (f >= lo) & (f <= hi) & inside
        value = _weighted_share(f, to_drivers, total, sel)
        if value is not None:
            bands.append(dict(band_hz=[lo, hi], to_drivers_fraction=value, to_components_fraction=1 - value,
                              loss_db=float(-10 * np.log10(max(value, 1e-12)))))
    rows = []
    for section, power in (sections or []):
        passband = section.get("passband_hz") or list(band_hz)
        sel = (f >= passband[0]) & (f <= passband[1])
        value = _weighted_share(f, np.asarray(power, float), total, sel)
        rows.append(dict(name=section.get("name"), band_hz=list(passband), to_driver_fraction=value,
                         loss_db=None if value is None else float(-10 * np.log10(max(value, 1e-12)))))
    with np.errstate(divide="ignore", invalid="ignore"):
        curve = np.where(total > 0, to_drivers / total, np.nan)
    return dict(band_hz=list(band_hz), weighting="pink, equal energy per octave",
                to_drivers_fraction=share, to_components_fraction=None if share is None else 1 - share,
                loss_db=None if share is None else float(-10 * np.log10(max(share, 1e-12))),
                octave_bands=bands, sections=rows, fraction_to_drivers=curve,
                note="a reading, not a target. Power reaching a driver is not sound: a direct radiator turns about one "
                     "percent of it into acoustic output and the rest into voice-coil heat, so this figure compares the "
                     "network against the drivers it feeds and nothing else. Read it with the pad depths of the level "
                     "budget, the compensation audit and insertion_loss: attenuation a sensitivity mismatch forces is not "
                     "the same finding as current diverted around a driver to flatten its impedance, and only the level "
                     "budget says which one this is.")


def part_counts(sections):
    """Physical bodies per section and per type, wiring and other parasitics excluded."""
    totals = {}
    rows = []
    for row in sections:
        counts = {}
        for part in row.get("components", []):
            if part.get("parasitic"):
                continue
            counts[part["type"]] = counts.get(part["type"], 0) + 1
            totals[part["type"]] = totals.get(part["type"], 0) + 1
        rows.append(dict(name=row.get("name"), total=int(sum(counts.values())), by_type=counts))
    return dict(total=int(sum(totals.values())), by_type=totals, sections=rows,
                note="one count per physical part that has to be bought, held and wired, which is what a bank of four "
                     "resistors costs and a single body does not. Wiring resistance is excluded.")


# The manufacturer's own answer about cored-coil saturation, which is that the measurement has not
# been taken: "We have not done any measurements for power handling and saturation points for our
# induction coils." That is a settled finding, not a search still to be done, so the field is
# "not published" rather than a blank - a blank invites a later assumption.
SATURATION_NOT_PUBLISHED = "not published"
CORE_BEHAVIOUR = {
    "air": "an air core does not saturate at all; its inductance is essentially constant over the full operating "
           "current range. Every saturation question is a cored-coil question.",
    "ferrite": "a ferrite core saturates EARLIER than a powder core, and when it does the inductance loss is instant, "
               "with a much more aggressive loss curve.",
    "powder": "a non-ferrite powder core handles higher power, saturates later, and falls off more softly than ferrite.",
    "cored_unspecified": "a ferromagnetic core whose type is not stated. The failure mode depends on which it is - ferrite "
                         "saturates earlier and its inductance collapses abruptly, a powder core saturates later and more "
                         "softly - so the core type belongs in the part record even though the saturation current does not "
                         "exist to be recorded.",
}
# The only published threshold anyone gives is a frequency, not a current: ferromagnetic cores below
# about 1.2 kHz, air cores above. A vendor rule of thumb with no derivation attached, recorded as one.
CORED_COIL_FREQUENCY_LIMIT_HZ = 1200.0
AIR_CORE_HIERARCHY = ["foil", "litz wire", "single wire"]


def core_kind(core):
    """Classify a declared core into the three behaviours the manufacturer distinguishes."""
    text = str(core or "").lower()
    if not text or text in ("not stated", "unknown"):
        return None
    if any(word in text for word in ("air", "aircore")):
        return "air"
    if "ferrite" in text:
        return "ferrite"
    if any(word in text for word in ("powder", "sendust", "kool", "p-core", "pcore")):
        return "powder"
    return "cored_unspecified"


def part_ratings(elements, states, f, passband_hz=None, scale=None):
    """What each part is asked to do, what its datasheet published, and what nobody has measured.

    The saturation current of a cored coil is not a figure that is hard to find: the supplier states
    in its own technical FAQ that it has not measured power handling or saturation points at all, and
    considers the measurement inconclusive for deciding crossover suitability. So this reports "not
    published" as a value, names the core's failure mode where the core is known, and falls back on
    the only threshold anyone published - a frequency, 1.2 kHz, below which a ferromagnetic core is
    the vendor's own recommendation and above which it is a choice to argue for.

    The current reported is the coil's own branch current, not its group's: a coil inside a parallel
    notch carries a fraction of what the notch carries.
    """
    rows = []
    for element, state in zip(elements, states):
        for leaf, leaf_state in leaf_states(element, state, f, scale):
            if leaf.get("type") != "L":
                continue
            core = leaf.get("core")
            kind = core_kind(core)
            saturation = leaf.get("saturation_current_a")
            peak = float(np.abs(leaf_state["current"]).max())
            peak_hz = float(f[np.argmax(np.abs(leaf_state["current"]))])
            row = dict(id=leaf.get("id") or element.get("id"), value_mh=leaf.get("value_mh"),
                       core=core or "not stated", core_kind=kind or "not stated",
                       cored=bool(kind and kind != "air"),
                       max_current_rms_a=peak, max_current_hz=peak_hz,
                       saturation_current_a=float(saturation) if saturation else SATURATION_NOT_PUBLISHED,
                       saturation_current_published=bool(saturation))
            if kind in CORE_BEHAVIOUR:
                row["core_failure_mode"] = CORE_BEHAVIOUR[kind]
            if saturation:
                row["current_fraction_of_saturation"] = peak / float(saturation)
            else:
                row["missing_rating_note"] = (
                    "SATURATION CURRENT NOT PUBLISHED, and the supplier states it has not been measured: 'We have not "
                    "done any measurements for power handling and saturation points for our induction coils.' The model "
                    "therefore treats this coil as linear at every level. That is a stated assumption, not a rating, and "
                    "for a non-air core it has not been characterised by anyone. Chasing the per-part datasheet does not "
                    "help; measure it or avoid the question.")
            if row["cored"] or kind is None:
                band = passband_hz or [peak_hz, peak_hz]
                row["frequency_rule"] = dict(
                    threshold_hz=CORED_COIL_FREQUENCY_LIMIT_HZ,
                    passband_hz=list(band),
                    current_peak_below_threshold=bool(peak_hz <= CORED_COIL_FREQUENCY_LIMIT_HZ),
                    passband_below_threshold=bool(float(band[1]) <= CORED_COIL_FREQUENCY_LIMIT_HZ),
                    rule="the supplier's own practice threshold: ferromagnetic-cored inductors for the bass and lower "
                         "midrange, 'as rule of thumb for positions below 1.2 kHz', and air cores above it. A vendor "
                         "rule of thumb with no derivation attached - but it is the only threshold anyone published, so "
                         "a cored coil above 1.2 kHz is a choice the candidate notes have to argue for.",
                    air_core_hierarchy=list(AIR_CORE_HIERARCHY))
            rows.append(row)
    return rows


def ladder_state(f, load, elements, scale=None, voltage=1.0):
    """Solve a loaded ladder: terminal voltage, input impedance and every element's voltage, current and dissipation."""
    z = np.asarray(load, complex).copy()
    impedances = [acoustics.element_impedance(e, f, scale) for e in elements]
    downstream = []
    for e, zi in zip(reversed(elements), reversed(impedances)):
        downstream.append(z.copy())
        z = z + zi if e["position"] == "series" else 1 / (1 / z + 1 / zi)
    vin = np.full(len(f), voltage, complex)
    states = []
    for (e, zi), after in zip(zip(elements, impedances), reversed(downstream)):
        if e["position"] == "series":
            current = vin / (zi + after)
            drop = current * zi
            vin = current * after
        else:
            current = vin / zi
            drop = vin.copy()
        states.append(dict(id=e.get("id"), impedance=zi, voltage=drop, current=current, dissipation_w=abs(current) ** 2 * zi.real))
    return dict(terminal=vin, input_z=z, states=states, load_current=vin / np.asarray(load, complex))


def ladder_transfer(f, load, elements, scale=None):
    """Terminal transfer and input impedance only, for repeated evaluation inside a fit."""
    z = np.asarray(load, complex).copy()
    impedances = [acoustics.element_impedance(e, f, scale) for e in elements]
    downstream = []
    for e, zi in zip(reversed(elements), reversed(impedances)):
        downstream.append(z.copy())
        z = z + zi if e["position"] == "series" else 1 / (1 / z + 1 / zi)
    transfer = np.ones(len(f), complex)
    for (e, zi), after in zip(zip(elements, impedances), reversed(downstream)):
        if e["position"] == "series":
            transfer = transfer * after / (after + zi)
    return transfer, z


def leaf_states(element, state, f, scale=None):
    """Distribute a composite element's voltage and current to its physical leaves.

    A series group shares its current and divides its voltage; a parallel group shares its voltage
    and divides its current. Applied recursively this gives every physical part its own stress, and
    the leaf powers sum to the group's power exactly.

    `scale` must be the same tolerance draw the state was solved with: the child impedances are
    recomputed here, and pairing a scaled state with nominal children would report stress the
    network never saw.
    """
    kind = element.get("type")
    if kind not in ("series", "parallel"):
        yield element, state
        return
    for child in element.get("parts", []):
        z = acoustics.element_impedance(child, f, scale)
        if kind == "series":
            current = state["current"]
            voltage = current * z
        else:
            if np.any(np.abs(z) == 0):
                raise cli.InputError(
                    f"element '{child.get('id') or child.get('type')}' has zero impedance inside the parallel group "
                    f"'{element.get('id')}', which shorts the group: its own stress and every sibling's is undefined")
            voltage = state["voltage"]
            current = voltage / z
        child_state = dict(voltage=voltage, current=current,
                           dissipation_w=np.abs(current) ** 2 * z.real)
        yield from leaf_states(child, child_state, f, scale)


def leaf_summary(elements, states, f, scale=None):
    """One row per physical part, with the stress that part alone carries."""
    rows = []
    for e, st in zip(elements, states):
        for leaf, leaf_state in leaf_states(e, st, f, scale):
            row = dict(id=leaf.get("id") or e.get("id"), type=leaf["type"], position=e["position"])
            if e.get("parasitic") or leaf.get("parasitic"):
                row["parasitic"] = True
            for key in ("value_mh", "value_uf", "value_ohm", "dcr_ohm", "esr_ohm"):
                if key in leaf:
                    row[key] = leaf[key]
            if leaf["type"] == "L" and "dcr_ohm" not in leaf:
                row["dcr_ohm_assumed"] = acoustics.default_coil_dcr(float(leaf["value_mh"]))
            if leaf["type"] == "C" and "esr_ohm" not in leaf:
                row["esr_ohm_assumed"] = 0.01
            rows.append(row)
            i = int(np.argmax(leaf_state["dissipation_w"]))
            row.update(max_voltage_rms=float(np.abs(leaf_state["voltage"]).max()),
                       max_voltage_hz=float(f[np.argmax(np.abs(leaf_state["voltage"]))]),
                       max_current_rms_a=float(np.abs(leaf_state["current"]).max()),
                       max_dissipation_w=float(leaf_state["dissipation_w"][i]),
                       max_dissipation_hz=float(f[i]), element_group=e.get("id"))
    return rows


def draw_scale(elements, rng, tol):
    scale = {}
    for e in elements:
        for leaf in acoustics.iter_elements(e):
            key = leaf.get("id") or e.get("id")
            if key:
                spread = float(leaf.get("tolerance_fraction", tol.get(leaf["type"], 0.0)))
                scale[key] = 1 + rng.uniform(-spread, spread)
    return scale


def inventory_cost(records):
    """Known subtotal and missing prices; a missing quote is not a zero price."""
    subtotal=0.;missing=[];currencies=set()
    for index,record in enumerate(records):
        price=record.get("price")
        if isinstance(price,dict):
            if price.get("currency"):currencies.add(price["currency"])
            price=price.get("amount")
        if price is None:missing.append(record.get("sku",record.get("id",str(index))))
        else:subtotal+=float(price)
    return dict(known_subtotal=subtotal,unpriced_items=missing,currencies=sorted(currencies),
                basis="Only comparable currency/tax/quantity records should be interpreted as a total; no currency conversion is performed.")
