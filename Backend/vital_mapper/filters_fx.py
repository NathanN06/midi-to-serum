import math
from typing import Any, Dict, List

# MIDI stats
from midi_analysis import compute_midi_stats

# Config constants
from config import (
    MIN_FILTER_FREQ,
    MAX_FILTER_FREQ,

    FILTER_1_CC_NUMBERS,
    FILTER_2_CC_NUMBERS,
    FILTER_1_CUTOFF_CC,
    FILTER_1_RESONANCE_CC,
    FILTER_1_DRIVE_CC,
    FILTER_1_KEYTRACK_CC,
    FILTER_1_MIX_CC,
    FILTER_2_CUTOFF_CC,
    FILTER_2_RESONANCE_CC,
    FILTER_2_DRIVE_CC,
    FILTER_2_KEYTRACK_CC,
    FILTER_2_MIX_CC,

    EFFECT_ENABLE_THRESHOLD,
    EFFECTS_CC_MAP,
    EFFECTS_PARAM_MAP,
)


def apply_filters_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float], midi_data: Dict[str, Any]) -> None:
    """
    Sets filter parameters directly at the top level of the Vital preset JSON file,
    based on incoming MIDI CC data or fallback MIDI stats.
    """
    from midi_analysis import compute_midi_stats  # Avoid circular import
    import math

    # Remove nested "filters" if it exists
    if "settings" in preset and "filters" in preset["settings"]:
        preset["settings"].pop("filters", None)

    preset.setdefault("settings", {})

    def scale_cutoff(cc_value: float) -> float:
        freq = MIN_FILTER_FREQ * (MAX_FILTER_FREQ / MIN_FILTER_FREQ) ** cc_value
        return (math.log(freq) - math.log(MIN_FILTER_FREQ)) / (math.log(MAX_FILTER_FREQ) - math.log(MIN_FILTER_FREQ))

    def configure_filter(filter_id: int, detected_ccs: List[int],
                         cutoff_cc, resonance_cc, drive_cc, keytrack_cc, mix_cc):
        prefix = f"filter_{filter_id}_"
        if detected_ccs:
            preset["settings"][f"{prefix}on"] = 1.0
            for cc in detected_ccs:
                value = cc_map[cc]
                if cc in cutoff_cc:
                    preset["settings"][f"{prefix}cutoff"] = scale_cutoff(value)
                elif cc in resonance_cc:
                    preset["settings"][f"{prefix}resonance"] = value
                elif cc in drive_cc:
                    preset["settings"][f"{prefix}drive"] = value * 20.0  # Scaled for Vital's drive range
                elif cc in keytrack_cc:
                    preset["settings"][f"{prefix}keytrack"] = value
                elif cc in mix_cc:
                    preset["settings"][f"{prefix}mix"] = value
        else:
            preset["settings"][f"{prefix}on"] = 0.0

    # Detect CCs
    filter_1_detected = [cc for cc in FILTER_1_CC_NUMBERS if cc in cc_map and cc_map[cc] >= EFFECT_ENABLE_THRESHOLD]
    filter_2_detected = [cc for cc in FILTER_2_CC_NUMBERS if cc in cc_map and cc_map[cc] >= EFFECT_ENABLE_THRESHOLD]

    # Apply filters based on CCs
    configure_filter(1, filter_1_detected, FILTER_1_CUTOFF_CC, FILTER_1_RESONANCE_CC,
                     FILTER_1_DRIVE_CC, FILTER_1_KEYTRACK_CC, FILTER_1_MIX_CC)

    configure_filter(2, filter_2_detected, FILTER_2_CUTOFF_CC, FILTER_2_RESONANCE_CC,
                     FILTER_2_DRIVE_CC, FILTER_2_KEYTRACK_CC, FILTER_2_MIX_CC)

    # Fallback logic with dynamic values
    if not filter_1_detected and not filter_2_detected:
        stats = compute_midi_stats(midi_data)
        avg_pitch = stats.get("avg_pitch", 60)
        pitch_range = stats.get("pitch_range", 12)
        velocity = stats.get("avg_velocity", 80) / 127.0

        # Dynamically scale additional filter parameters
        fallback_cutoff = scale_cutoff((avg_pitch - 20) / 80)  # Maps avg_pitch from 20–100 range
        fallback_resonance = min(1.0, pitch_range / 24.0 + velocity * 0.3)
        fallback_drive = min(20.0, velocity * 15.0 + 1.0)       # Drive increases with velocity
        fallback_keytrack = min(1.0, pitch_range / 36.0)
        fallback_mix = 1.0  # You can make this dynamic if needed

        preset["settings"].update({
            "filter_1_on": 1.0,
            "filter_1_cutoff": fallback_cutoff,
            "filter_1_resonance": fallback_resonance,
            "filter_1_drive": fallback_drive,
            "filter_1_keytrack": fallback_keytrack,
            "filter_1_mix": fallback_mix
        })

        print("Fallback: Enabled Filter 1 based on pitch/velocity stats")

    print(f"Filter 1 CCs detected: {filter_1_detected}")
    print(f"Filter 2 CCs detected: {filter_2_detected}")


def apply_effects_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float], midi_data: Dict[str, Any]) -> None:
    preset.setdefault("settings", {})
    effects_applied = False

    for effect, cc in EFFECTS_CC_MAP.items():
        if cc in cc_map and cc_map[cc] >= EFFECT_ENABLE_THRESHOLD:
            effects_applied = True
            preset["settings"][f"{effect}_on"] = 1.0

            # Multi-param support
            effect_params = EFFECTS_PARAM_MAP.get(effect, {})
            if isinstance(effect_params, dict):
                for subparam, vital_param in effect_params.items():
                    preset["settings"][vital_param] = cc_map[cc]
            else:
                # Fallback if it's still a string (legacy support)
                preset["settings"][effect_params] = cc_map[cc]
        else:
            preset["settings"][f"{effect}_on"] = 0.0

    # Fallback if no FX CCs were used
    if not effects_applied:
        stats = compute_midi_stats(midi_data)
        velocity = stats.get("avg_velocity", 80) / 127.0
        note_density = stats.get("note_density", 4.0)

        if velocity > 0.5 or note_density > 4.0:
            preset["settings"].update({
                "reverb_on": 1.0,
                "reverb_dry_wet": velocity,
                "delay_on": 1.0,
                "delay_dry_wet": 0.3 + (note_density / 10.0)
            })
            print("Fallback: Enabled default effects based on velocity and note density")
