import numpy as np
import random
from typing import Any, Dict, List, Optional

# MIDI stats
from midi_analysis import compute_midi_stats

# Config constants
from config import (
    DEFAULT_LFO_POINTS,
    LFO_RATE_MULTIPLIER,
    LFO_DEPTH_MIN,
    LFO_DEPTH_MULTIPLIER,
    DEFAULT_LFO_SYNC,
    DEFAULT_LFO_TEMPO_OPTIONS,
)


def select_lfo_shape(midi_data: Dict[str, Any], lfo_idx: int) -> int:
    """
    Dynamically selects the best LFO shape index (1-8) based on MIDI data.
    """
    stats = compute_midi_stats(midi_data)
    density = stats.get("note_density", 4.0)
    pitch_range = stats.get("pitch_range", 12)
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    if lfo_idx == 1:
        return 2 if density > 6 else 1  # Square if fast, Sine if slow
    elif lfo_idx == 2:
        return 6 if pitch_range > 24 else 4  # Inverted Ramp or Triangle
    elif lfo_idx == 3:
        return 3 if cc_map.get(11, 0.0) > 0.5 else 7  # Saw or Noise
    elif lfo_idx == 4:
        return 8 if cc_map.get(1, 0.0) > 0.3 else 5  # Sin-Square mix or Curved Ramp

    return 1  # Default fallback


def build_lfo_from_cc(preset: Dict[str, Any],
                      midi_data: Dict[str, Any],
                      lfo_idx: int = 1,
                      destination: str = "filter_1_cutoff",
                      one_shot: bool = False) -> None:
    """
    Builds an LFO shape from MIDI data with dynamic waveform selection.
    """
    num_points: int = DEFAULT_LFO_POINTS
    times_interp = np.linspace(0, 1, num_points)

    # Extended set of 8 LFO shapes
    lfo_shapes: Dict[int, Any] = {
        1: ("Sine LFO", np.sin(times_interp * 2 * np.pi)),
        2: ("Square LFO", np.sign(np.sin(times_interp * 2 * np.pi))),
        3: ("Saw LFO", 2 * (times_interp % 1) - 1),
        4: ("Triangle LFO", 2 * np.abs(2 * (times_interp % 1) - 1) - 1),
        5: ("Curved Ramp", times_interp ** 2),
        6: ("Inverted Ramp", 1 - np.sqrt(times_interp)),
        7: ("Noise Pulse", np.random.rand(num_points)),
        8: ("Sin-Square Mix", 0.5 * (np.sin(times_interp * 2 * np.pi) + np.sign(np.sin(times_interp * 2 * np.pi))))
    }

    selected_shape_idx = select_lfo_shape(midi_data, lfo_idx)
    lfo_name, values_interp = lfo_shapes.get(selected_shape_idx, lfo_shapes[1])

    values_interp = (values_interp + 1) / 2
    values_interp = np.clip(values_interp, 0, 1)

    points: List[float] = [val for pair in zip(times_interp, values_interp) for val in pair]
    powers: List[float] = [0.0] * num_points

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    while len(preset["settings"]["lfos"]) < lfo_idx:
        preset["settings"]["lfos"].append({
            "name": f"LFO {len(preset['settings']['lfos']) + 1}",
            "num_points": DEFAULT_LFO_POINTS,
            "points": [0.0, 1.0, 1.0, 0.0],
            "powers": [0.0, 0.0],
            "smooth": False
        })

    cc_map: Dict[int, float] = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}
    lfo_rate_cc_map = {
        1: cc_map.get(1, 0.5),
        2: cc_map.get(2, 0.5),
        3: cc_map.get(3, 0.5),
        4: cc_map.get(4, 0.5)
    }
    lfo_depth_cc: float = cc_map.get(11, 0.8)

    lfo_rate_scaled: float = 1.0 + (lfo_rate_cc_map.get(lfo_idx, 0.5) * LFO_RATE_MULTIPLIER)
    lfo_depth_scaled: float = LFO_DEPTH_MIN + (lfo_depth_cc * LFO_DEPTH_MULTIPLIER)

    preset["settings"]["lfos"][lfo_idx - 1] = {
        "name": lfo_name,
        "num_points": num_points,
        "points": points,
        "powers": powers,
        "smooth": True
    }

    preset["settings"][f"lfo_{lfo_idx}_frequency"] = lfo_rate_scaled
    preset["settings"][f"lfo_{lfo_idx}_sync"] = DEFAULT_LFO_SYNC
    preset["settings"][f"lfo_{lfo_idx}_tempo"] = random.choice(DEFAULT_LFO_TEMPO_OPTIONS)

    if one_shot:
        preset["settings"][f"lfo_{lfo_idx}_one_shot"] = 1.0

    preset["settings"].setdefault("modulations", [])
    preset["settings"]["modulations"].append({
        "source": f"lfo_{lfo_idx}",
        "destination": destination,
        "amount": lfo_depth_scaled
    })

    print(f"✅ {lfo_name} → {destination} (LFO{lfo_idx}, one_shot={one_shot}) | Rate={lfo_rate_scaled:.2f} | Depth={lfo_depth_scaled:.2f}")


def add_lfos_to_preset(preset: Dict[str, Any],
                       midi_data: Dict[str, Any],
                       notes: List[Dict[str, Any]]) -> None:
    """
    Adds 4 LFOs to the preset with dynamically chosen waveforms based on MIDI data.
    """
    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    print("🔹 Adding LFOs to preset...")

    # Automatically choose meaningful destinations
    lfo_targets = get_best_lfo_targets(midi_data)

    for idx, target in enumerate(lfo_targets):
        one_shot = True if idx == 1 else False  # e.g., LFO2 could be one-shot
        build_lfo_from_cc(preset, midi_data, lfo_idx=idx + 1, destination=target, one_shot=one_shot)

    print("✅ LFOs added with adaptive waveforms!")


def generate_lfo_shape_from_cc(cc_data: List[Dict[str, Any]], 
                               num_points: int = 16, 
                               lfo_type: str = "sine") -> Optional[Dict[str, Any]]:
    """
    Generates an LFO shape based on MIDI CC automation.
    Converts CC values into a set of time/value points in Vital's LFO JSON format.
    """
    if not cc_data:
        print("⚠️ No MIDI CC data found. Skipping LFO generation.")
        return None

    cc_data = sorted(cc_data, key=lambda x: x["time"])
    times = np.array([cc["time"] for cc in cc_data])
    values = np.array([cc["value"] / 127.0 for cc in cc_data])

    resampled_times = np.linspace(times[0], times[-1], num_points)
    resampled_values = np.interp(resampled_times, times, values)

    lfo_waveforms = {
        "sine": np.sin,
        "square": lambda t: np.sign(np.sin(t)),
        "saw": lambda t: 2 * (t % 1) - 1,
        "triangle": lambda t: 2 * np.abs(2 * (t % 1) - 1) - 1,
        "ramp": lambda t: t ** 2,
        "inv_ramp": lambda t: 1 - np.sqrt(t),
        "noise": lambda t: np.random.rand(len(t)),
        "mixed": lambda t: 0.5 * (np.sin(t) + np.sign(np.sin(t)))
    }

    func = lfo_waveforms.get(lfo_type, np.sin)
    waveform = func(resampled_times * 2 * np.pi)

    lfo_shape: Dict[str, Any] = {
        "name": f"MIDI_CC_LFO_{lfo_type}",
        "num_points": num_points,
        "points": list(resampled_times) + list(resampled_values),
        "powers": list(waveform),
        "smooth": True
    }

    print(f"✅ Created LFO with type {lfo_type} from MIDI CC data.")
    return lfo_shape


def get_best_lfo_targets(midi_data: Dict[str, Any]) -> List[str]:
    """
    Suggests LFO modulation targets based on MIDI features.
    Returns a list of 4 ideal LFO destinations.
    """
    stats = compute_midi_stats(midi_data)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    avg_velocity = stats.get("avg_velocity", 80) / 127.0

    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}
    targets = []

    if pitch_range > 12:
        targets.extend(["osc_1_pitch", "filter_1_cutoff"])
    else:
        targets.append("osc_1_level")

    if cc_map.get(1, 0) > 0.2:
        targets.append("osc_1_warp")
    else:
        targets.append("osc_2_pitch")

    if note_density > 4.0:
        targets.append("filter_2_resonance")
    else:
        targets.append("reverb_dry_wet")

    fallback_pool = ["volume", "osc_2_warp", "distortion_drive", "delay_feedback"]
    for param in fallback_pool:
        if len(targets) >= 4:
            break
        if param not in targets:
            targets.append(param)

    return targets[:4]
