"""Two-body lumped voice-coil thermal model and the copper resistance drift it produces.

Klippel's circuit: the coil dissipates P_Re = i_rms^2 Re into a coil body (Rtv, Ctv) which is
thermally coupled to the magnet and frame (Rtm, Ctm). The model neglects convection cooling,
eddy-current heating of the pole pieces and any distribution of heat within each body, and the
four parameters are almost never published, so everything here is a scenario over declared priors
rather than a prediction.
"""
import math

import numpy as np

from .cli import InputError

COPPER_COEFFICIENT_PER_C = 0.0039  # copper's temperature coefficient, quoted 0.39 to 0.395 percent per degree C
ABORT_RESISTANCE_RATIO = 1.30     # the standard power test aborts here, about +80 K for a copper coil
WORKING_RISE_RANGE_K = (50.0, 100.0)

# Priors for a parameter set no datasheet publishes. They are starting points to be replaced by a
# measurement, and every result computed from them says so. They came from the ACCELERATED protocol
# below - Klippel's two-body extraction - and a model calibrated against that protocol must not be
# reported as validated against the AES2 endurance test, which answers a different question.
PRIOR_PROTOCOL = "accelerated"
PRIOR_SOURCE = ("Klippel application note AN18: the two-body circuit and its extraction from a short accelerated power "
                "test. Nothing here is calibrated against an endurance test.")

PRIORS = {
    "dome_tweeter": {"rtv_k_per_w": 3.0, "rtm_k_per_w": 4.0, "ctv_ws_per_k": 0.5, "ctm_ws_per_k": 60.0},
    "midrange": {"rtv_k_per_w": 1.6, "rtm_k_per_w": 2.2, "ctv_ws_per_k": 2.5, "ctm_ws_per_k": 400.0},
    "woofer": {"rtv_k_per_w": 1.0, "rtm_k_per_w": 1.4, "ctv_ws_per_k": 6.0, "ctm_ws_per_k": 900.0},
    "compression_driver": {"rtv_k_per_w": 2.0, "rtm_k_per_w": 2.5, "ctv_ws_per_k": 1.5, "ctm_ws_per_k": 250.0},
}


def resistance_at(re_cold_ohm, temperature_c, reference_c=20.0, coefficient=COPPER_COEFFICIENT_PER_C):
    """Re(T) = Re * (1 + alpha (T - T0)); the same law that moves every filter corner with it.

    Accepts a scalar temperature or an array of them, so a trajectory converts in one call.
    """
    return float(re_cold_ohm) * (1 + float(coefficient) * (np.asarray(temperature_c, float) - float(reference_c)))


def rise_at_resistance_ratio(ratio, coefficient=COPPER_COEFFICIENT_PER_C):
    """The coil rise in kelvin that a given Re(T) / Re ratio corresponds to."""
    return (float(ratio) - 1) / float(coefficient)


def compression_db(re_cold_ohm, re_hot_ohm):
    """Level lost to coil heating at constant drive voltage, 20 log10(Re_cold / Re_hot).

    A resistance-dominated branch draws current in inverse proportion to Re, so this is the
    first-order thermal compression figure: 130 percent of cold Re is 2.3 dB.
    """
    return 20 * np.log10(float(re_cold_ohm) / np.asarray(re_hot_ohm, float))


def parameters(spec):
    """Validate a thermal parameter set and add the mass-equivalent sanity checks."""
    keys = ("rtv_k_per_w", "rtm_k_per_w", "ctv_ws_per_k", "ctm_ws_per_k")
    prior = spec.get("prior")
    values = dict(PRIORS[prior]) if prior in PRIORS else {}
    if prior and prior not in PRIORS:
        raise InputError(f"unknown thermal prior '{prior}'; known priors are {sorted(PRIORS)}")
    values.update({k: float(spec[k]) for k in keys if spec.get(k) is not None})
    missing = [k for k in keys if k not in values]
    if missing:
        raise InputError(f"thermal parameters are missing {missing}; supply them or name a prior from {sorted(PRIORS)}")
    rtv, rtm, ctv, ctm = (values[k] for k in keys)
    return dict(values, source="prior: " + prior if prior else "stated",
                calibration_protocol=PRIOR_PROTOCOL if prior else "stated by the caller",
                protocol_source=PRIOR_SOURCE if prior else "supplied values; state which protocol measured them",
                tau_v_s=rtv * ctv, tau_m_s=rtm * ctm,
                steady_state_k_per_w=dict(coil=rtv + rtm, magnet=rtm),
                equivalent_mass_check=dict(copper_g=2.7 * ctv, steel_g=2.0 * ctm,
                                           note="m_copper [g] = 2.7 Ctv and m_steel [g] = 2 Ctm, both for C in Ws/K; "
                                                "a capacitance that implies an impossible mass is an extraction error"))


def response(params, power_w, seconds):
    """Coil and magnet temperature rise against time for a step of dissipated power.

    dT_v(ss) = (Rtv + Rtm) P, dT_m(ss) = Rtm P, with tau_v = Rtv Ctv and tau_m = Rtm Ctm. The two
    bodies are treated as separable exponentials, which is exact for tau_m >> tau_v and an
    approximation otherwise; the time constants are reported so the reader can see which case it is.
    """
    t = np.asarray(seconds, float)
    p = float(power_w)
    coil_ss = params["steady_state_k_per_w"]["coil"] * p
    magnet_ss = params["steady_state_k_per_w"]["magnet"] * p
    magnet = magnet_ss * (1 - np.exp(-t / params["tau_m_s"]))
    coil = magnet + (coil_ss - magnet_ss) * (1 - np.exp(-t / params["tau_v_s"]))
    return dict(seconds=t, coil_rise_k=coil, magnet_rise_k=magnet,
                coil_steady_state_k=coil_ss, magnet_steady_state_k=magnet_ss)


NOTES = [
    "Two-body lumped thermal model (Klippel AN18): the coil dissipates i_rms^2 Re into a coil body coupled to the magnet and frame.",
    "The priors and the 130-percent abort point come from the ACCELERATED protocol - short steps, target coil rise - not from AES2-2012's two-hour-per-step endurance test. The two answer different questions and a model calibrated against one is not validated against the other; both are reported so the distinction stays visible.",
    "AES2-2012 also requires fs to be reported before and after a power test. That is the cheapest available evidence of suspension change, it is not in any model here, and a datasheet that omits it has not shown that its parameters survive being played.",
    "The model neglects convection cooling, eddy-current heating of the pole pieces and heat distribution within each body.",
    "Rtv, Rtm, Ctv and Ctm are almost never published. Every figure computed from a prior is a scenario, not a prediction, and the equivalent-mass check is the only sanity test available without a measurement.",
    "Compression is computed at constant drive voltage from the resistance change alone; nonlinear compression, which is instantaneous rather than thermal, is a separate mechanism this model does not contain.",
]

# Two protocols, two different questions. The accelerated one measures how fast the coil heats; the
# endurance one measures what the driver survives. DO NOT MERGE THEM, and do not report a model
# calibrated against one as validated against the other.
PROTOCOLS = {
    "accelerated": {
        "answers": "how hot does the coil get, and how fast",
        "source": "Klippel application note AN18",
        "stimulus": "IEC 60268 noise",
        "level_steps_db": 2.0,
        "cycle_s": 30.0,
        "target_coil_rise_k": list(WORKING_RISE_RANGE_K),
        "abort_at_resistance_ratio": ABORT_RESISTANCE_RATIO,
        "abort_rise_k": rise_at_resistance_ratio(ABORT_RESISTANCE_RATIO),
        "pilot_tone": "about 2 Hz behind a low-pass, about 3 kHz behind a high-pass, 20 to 40 dB below programme, chosen "
                      "from a measured impedance sweep of the actual network, so Re can be read through the crossover",
        "calibration": "about 3 dB of thermal compression over a 12 dB drive range for a 51 mm-coil compression driver",
    },
    "aes2_endurance": {
        "answers": "what power does this driver survive",
        "source": "AES2-2012 clause 6, read at first hand",
        "stimulus": "pink noise spanning one decade upward from the manufacturer's stated low-frequency limit, bandpass "
                    "filtered at 24 dB/octave with Butterworth response",
        "crest_factor_db": 12.0,
        "amplifier_headroom_db": "peaks at least 9 dB and preferably 12 dB above the rms voltage, which means an "
                                 "amplifier rated at 4 to 8 times the test power",
        "step_duration_s": 7200.0,
        "procedure": "successively higher powers with thermal equilibrium at each step, about 2 hours. Power is the "
                     "square of the applied rms voltage divided by the RATED impedance.",
        "rated_power_definition": "the power the device withstands for 2 hours without significant permanent change in "
                                  "acoustical, mechanical or electrical characteristics",
        "reported_alongside": [
            "the temperature rise of BOTH the voice coil and the magnet assembly at the end of the test, with the "
            "measurement method stated",
            "the maximum excursion beyond which permanent mechanical damage occurs, with the cause named",
            "the low resonance frequency fs measured BEFORE AND AFTER the power test",
        ],
        "cheapest_diagnostic": "fs shifting across a power test is direct evidence of suspension change and costs one "
                               "extra impedance sweep. It is also the reminder that the framework's cold Thiele/Small "
                               "parameters describe a driver that has not been played.",
    },
}

PROTOCOLS_NOTE = ("the accelerated protocol measures how fast the coil heats; the AES2 endurance test measures what the "
                  "driver survives. A thermal model calibrated against one must NOT be reported as validated against "
                  "the other.")

# The protocol this module's priors and abort point come from, kept under its old name so a result
# document that quotes one protocol still quotes the right one.
PROTOCOL = PROTOCOLS["accelerated"]
