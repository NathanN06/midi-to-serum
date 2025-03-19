# vital_mapper.py

import json

import zlib
import base64

import re
import numpy as np
import os
import logging
from midi_analysis import compute_midi_stats

# Local imports

from config import (
    MIDI_TO_VITAL_MAP,
    DEFAULT_ADSR,
    DEFAULT_WAVEFORM,
    HARMONIC_SCALING,
    OUTPUT_DIR,
    PRESETS_DIR,
    DEFAULT_VITAL_PRESET_FILENAME,
    DEFAULT_DETUNE_POWER,
    DEFAULT_UNISON_BLEND,
    DEFAULT_RANDOM_PHASE,
    DEFAULT_STACK_STYLE,
    DEFAULT_STEREO_SPREAD,
    DEFAULT_SPECTRAL_MORPH_AMOUNT,
    MAX_UNISON_VOICES,
    DEFAULT_KEYFRAMES,
    DEFAULT_WAVE_DATA,
    DEFAULT_LFO_POINTS,
    LFO_RATE_MULTIPLIER,
    LFO_DEPTH_MIN,
    LFO_DEPTH_MULTIPLIER,
    DEFAULT_LFO_TEMPO_OPTIONS,
    DEFAULT_LFO_SYNC,
    ENVELOPE_ATTACK_MULTIPLIER, 
    ENVELOPE_ATTACK_MAX,
    ENVELOPE_DECAY_MULTIPLIER, 
    ENVELOPE_DECAY_MAX, 
    ENVELOPE_RELEASE_MULTIPLIER, 
    ENVELOPE_RELEASE_MAX, 
    ENV2_ATTACK_SCALE, 
    ENV2_DECAY_SCALE, 
    ENV2_SUSTAIN_SCALE, 
    ENV2_RELEASE_SCALE,
    DEFAULT_ADSR,
    ENV_ATTACK_MIN,
    ENV_ATTACK_MAX,
    ENV_DECAY_MIN,
    ENV_DECAY_MAX,
    ENV_RELEASE_MIN,
    ENV_RELEASE_MAX,
    ENV_DELAY_MAX,
    ENV_HOLD_MIN,
    ENV_HOLD_MAX
)


from typing import Dict, List, Optional, Any


def load_default_vital_preset(default_preset_path: str) -> Optional[Dict[str, Any]]:
    """
    Loads a default Vital preset, handling both compressed and uncompressed JSON,
    and ensures a structure with at least 3 keyframes for Oscillator 1.
    
    Args:
        default_preset_path (str): Path to the default Vital preset file.
    
    Returns:
        Optional[Dict[str, Any]]: The parsed preset data if successful, None otherwise.
    """
    try:
        with open(default_preset_path, "rb") as f:
            file_data = f.read()

        # Attempt to decompress; if not compressed, decode as plain text.
        try:
            json_data = zlib.decompress(file_data).decode()
        except zlib.error:
            json_data = file_data.decode()

        # Parse JSON data.
        try:
            preset: Dict[str, Any] = json.loads(json_data)
        except json.JSONDecodeError as e:
            logging.error(f"❌ Error decoding Vital preset JSON: {e}")
            return None

        # Ensure that the first oscillator has at least DEFAULT_KEYFRAMES keyframes.
        if "groups" in preset and preset["groups"]:
            group = preset["groups"][0]
            if "components" in group and group["components"]:
                component = group["components"][0]
                if "keyframes" in component:
                    keyframes: List[Any] = component["keyframes"]
                    if len(keyframes) < DEFAULT_KEYFRAMES:
                        logging.warning("⚠️ Adjusting preset to ensure 3 keyframes for Oscillator 1.")
                        # Replace with DEFAULT_KEYFRAMES keyframes using default wave data.
                        component["keyframes"] = [
                            {"position": i / 2.0, "wave_data": DEFAULT_WAVE_DATA} 
                            for i in range(DEFAULT_KEYFRAMES)
                        ]
        return preset

    except (OSError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading default Vital preset: {e}")
        return None


def build_lfo_from_cc(preset: Dict[str, Any],
                      midi_data: Dict[str, Any],
                      lfo_idx: int = 1,
                      destination: str = "filter_1_cutoff",
                      one_shot: bool = False) -> None:
    """
    Builds an LFO shape from a MIDI CC source or generates a fallback LFO if no CC is provided.

    - Uses different MIDI CCs to control LFO **Rate (Speed)**
    - Uses MIDI CC11 (Expression) to control **Depth (Modulation Strength)**
    - Supports free-running and one-shot LFOs.

    Args:
        preset (Dict[str, Any]): The Vital preset to update.
        midi_data (Dict[str, Any]): Parsed MIDI data.
        lfo_idx (int, optional): Which LFO (1-4). Defaults to 1.
        destination (str, optional): The parameter to modulate. Defaults to "filter_1_cutoff".
        one_shot (bool, optional): If True, sets one-shot mode. Defaults to False.
    """
    # Generate time points for the LFO shape
    num_points: int = DEFAULT_LFO_POINTS
    times_interp = np.linspace(0, 1, num_points)

    # Define default LFO shapes
    lfo_shapes: Dict[int, Any] = {
        1: ("Sine LFO", np.sin(times_interp * 2 * np.pi)),
        2: ("Square LFO", np.sign(np.sin(times_interp * 2 * np.pi))),
        3: ("Saw LFO", 2 * (times_interp % 1) - 1),
        4: ("Triangle LFO", 2 * np.abs(2 * (times_interp % 1) - 1) - 1)
    }

    # Select LFO shape (fallback to Sine if index not found)
    lfo_name, values_interp = lfo_shapes.get(lfo_idx, lfo_shapes[1])
    
    # Normalize values between 0 and 1
    values_interp = (values_interp + 1) / 2  
    values_interp = np.clip(values_interp, 0, 1)

    # Create a list of time/value pairs for Vital's LFO format
    points: List[float] = [val for pair in zip(times_interp, values_interp) for val in pair]
    powers: List[float] = [0.0] * num_points  

    # Ensure "settings" and "lfos" exist
    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])
    while len(preset["settings"]["lfos"]) < lfo_idx:
        preset["settings"]["lfos"].append({
            "name": f"LFO {len(preset['settings']['lfos']) + 1}",
            "num_points": 2,
            "points": [0.0, 1.0, 1.0, 0.0],
            "powers": [0.0, 0.0],
            "smooth": False
        })

    # Map MIDI CC values for LFO rate and depth
    cc_map: Dict[int, float] = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}
    lfo_rate_cc_map = {
        1: cc_map.get(1, 0.5),  # CC1 for LFO1 Rate
        2: cc_map.get(2, 0.5),  # CC2 for LFO2 Rate
        3: cc_map.get(3, 0.5),  # CC3 for LFO3 Rate
        4: cc_map.get(4, 0.5)   # CC4 for LFO4 Rate
    }
    lfo_depth_cc: float = cc_map.get(11, 0.8)  # CC11 for depth (Expression)

    # Apply scaling to determine the final LFO parameters
    lfo_rate_scaled: float = 1.0 + (lfo_rate_cc_map[lfo_idx] * LFO_RATE_MULTIPLIER)
    lfo_depth_scaled: float = LFO_DEPTH_MIN + (lfo_depth_cc * LFO_DEPTH_MULTIPLIER)

    # Update the LFO shape in preset settings
    preset["settings"]["lfos"][lfo_idx - 1] = {
        "name": lfo_name,
        "num_points": num_points,
        "points": points,
        "powers": powers,
        "smooth": True
    }

    # Set dynamic speed and synchronization settings
    preset["settings"][f"lfo_{lfo_idx}_frequency"] = lfo_rate_scaled
    preset["settings"][f"lfo_{lfo_idx}_sync"] = DEFAULT_LFO_SYNC
    preset["settings"][f"lfo_{lfo_idx}_tempo"] = np.random.choice(DEFAULT_LFO_TEMPO_OPTIONS)

    # Apply one-shot mode if requested
    if one_shot:
        preset["settings"][f"lfo_{lfo_idx}_one_shot"] = 1.0

    # Add a modulation mapping for the LFO depth
    preset.setdefault("modulations", [])
    preset["modulations"].append({
        "source": f"lfo_{lfo_idx}",
        "destination": destination,
        "amount": lfo_depth_scaled  
    })

    print(f"✅ {lfo_name} -> {destination} applied (one_shot={one_shot}). Rate={lfo_rate_scaled:.2f}, Depth={lfo_depth_scaled:.2f}")


def add_lfos_to_preset(preset: Dict[str, Any],
                       midi_data: Dict[str, Any],
                       notes: List[Dict[str, Any]]) -> None:
    """
    Adds 4 different LFOs to the preset, each with its own waveform.
    The LFO shapes will be influenced by MIDI CC data contained in midi_data.
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary to update.
        midi_data (Dict[str, Any]): Parsed MIDI data (should include a "control_changes" key).
        notes (List[Dict[str, Any]]): A list of MIDI note dictionaries (currently not used).
    """
    # Ensure required keys exist
    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    print("🔹 Adding LFOs to preset...")

    # Build and add four LFOs with unique waveforms.
    # Using the complete MIDI data for CC mapping inside build_lfo_from_cc.
    build_lfo_from_cc(preset, midi_data=midi_data, lfo_idx=1, destination="filter_1_cutoff")
    build_lfo_from_cc(preset, midi_data=midi_data, lfo_idx=2, destination="osc_1_pitch", one_shot=True)
    build_lfo_from_cc(preset, midi_data=midi_data, lfo_idx=3, destination="volume")
    build_lfo_from_cc(preset, midi_data=midi_data, lfo_idx=4, destination="filter_2_resonance")

    print("✅ 4 LFOs added with unique waveforms!")


def generate_lfo_shape_from_cc(cc_data: List[Dict[str, Any]], 
                               num_points: int = 16, 
                               lfo_type: str = "sine") -> Optional[Dict[str, Any]]:
    """
    Generates an LFO shape based on MIDI CC automation.
    Converts CC values into a set of time/value points in Vital's LFO JSON format.
    
    Args:
        cc_data (List[Dict[str, Any]]): A list of CC event dictionaries, each with "time" and "value" keys.
        num_points (int): The number of points for the generated LFO shape. Defaults to 16.
        lfo_type (str): The waveform type to use ('sine', 'square', 'saw', 'triangle'). Defaults to "sine".
        
    Returns:
        Optional[Dict[str, Any]]: A dictionary representing the LFO shape in Vital's JSON format,
                                  or None if no CC data is provided.
    """
    if not cc_data:
        print("⚠️ No MIDI CC data found. Skipping LFO generation.")
        return None

    # Sort the CC data by time.
    cc_data = sorted(cc_data, key=lambda x: x["time"])
    times = np.array([cc["time"] for cc in cc_data])
    values = np.array([cc["value"] / 127.0 for cc in cc_data])

    # Resample time and values to a fixed number of points.
    resampled_times = np.linspace(times[0], times[-1], num_points)
    resampled_values = np.interp(resampled_times, times, values)

    # Generate waveform based on the specified type.
    if lfo_type == "sine":
        waveform = np.sin(resampled_times * 2 * np.pi)
    elif lfo_type == "square":
        waveform = np.sign(np.sin(resampled_times * 2 * np.pi))
    elif lfo_type == "saw":
        waveform = 2 * (resampled_times % 1) - 1
    elif lfo_type == "triangle":
        waveform = 2 * np.abs(2 * (resampled_times % 1) - 1) - 1
    else:
        waveform = np.sin(resampled_times * 2 * np.pi)

    lfo_shape: Dict[str, Any] = {
        "name": "MIDI_CC_LFO",
        "num_points": num_points,
        "points": list(resampled_times) + list(resampled_values),
        "powers": list(waveform),
        "smooth": True
    }

    print(f"✅ Created LFO with type {lfo_type} from MIDI CC data.")
    return lfo_shape


def add_envelopes_to_preset(preset: Dict[str, Any], notes: List[Dict[str, Any]]) -> None:
    """
    Adds ADSR envelope settings to the Vital preset based on MIDI note characteristics.
    If no notes are provided, uses the default ADSR settings from config.

    Args:
        preset (Dict[str, Any]): The Vital preset dictionary to update.
        notes (List[Dict[str, Any]]): List of MIDI note dictionaries.
    """
    if not notes:
        print("⚠️ No notes found. Using default envelope settings.")
        preset.update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Compute average note length (used to approximate attack, decay, and release times)
    avg_note_length: float = sum(n["end"] - n["start"] for n in notes) / len(notes)

    # Compute average velocity and derive sustain level (normalize velocity from 0-127 to 0-1)
    avg_velocity: float = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level: float = (avg_velocity / 127.0) if avg_velocity > 0 else 0.5

    # Calculate envelope parameters using centralized multipliers and caps.
    attack_time: float = min(avg_note_length * ENVELOPE_ATTACK_MULTIPLIER, ENVELOPE_ATTACK_MAX)
    decay_time: float = min(avg_note_length * ENVELOPE_DECAY_MULTIPLIER, ENVELOPE_DECAY_MAX)
    release_time: float = min(avg_note_length * ENVELOPE_RELEASE_MULTIPLIER, ENVELOPE_RELEASE_MAX)

    # Update ENV1 settings
    preset.update({
        "env_1_attack":  attack_time,
        "env_1_decay":   decay_time,
        "env_1_sustain": sustain_level,
        "env_1_release": release_time
    })
    print(f"✅ ENV1: A={attack_time:.2f}, D={decay_time:.2f}, S={sustain_level:.2f}, R={release_time:.2f}")

    # Apply similar scaling for ENV2 with different multipliers
    preset.update({
        "env_2_attack":  attack_time * ENV2_ATTACK_SCALE,
        "env_2_decay":   decay_time * ENV2_DECAY_SCALE,
        "env_2_sustain": sustain_level * ENV2_SUSTAIN_SCALE,
        "env_2_release": release_time * ENV2_RELEASE_SCALE
    })
    print("✅ ENV2 applied with slightly different scaling.")


def apply_dynamic_env_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Dynamically adjusts Envelope 1, 2, and 3 based on MIDI note data.

    - ENV1: Amplitude (volume envelope)
    - ENV2: Filter cutoff envelope
    - ENV3: Oscillator shape/pitch envelope
    
    Each envelope's parameters are calculated based on note length, note density,
    and MIDI CC data (e.g., Expression/Mod Wheel influence).
    """
    preset.setdefault("settings", {})
    notes: List[Dict[str, Any]] = midi_data.get("notes", [])
    ccs: List[Dict[str, Any]] = midi_data.get("control_changes", [])

    if not notes:
        print("⚠️ No MIDI notes detected. Using default envelopes.")
        preset["settings"].update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Compute average note length and average velocity.
    avg_note_length: float = sum(n["end"] - n["start"] for n in notes) / len(notes)
    avg_velocity: float = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level: float = min(1.0, avg_velocity / 127.0)

    # Determine note density (using average gap between notes).
    if len(notes) > 1:
        time_gaps: List[float] = [notes[i+1]["start"] - notes[i]["end"] for i in range(len(notes) - 1)]
        avg_gap: float = sum(time_gaps) / len(time_gaps)
    else:
        avg_gap = avg_note_length

    note_density_factor: float = max(0.2, min(1.0, 1.0 - (avg_gap / 2.0)))

    # Check for CC influence (Expression = CC11, Mod Wheel = CC1)
    expression_value: Optional[float] = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 11), None)
    mod_wheel_value: Optional[float] = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 1), None)

    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Ensures value stays within the specified range."""
        return max(min_val, min(value, max_val))

    # ENV1: Amplitude Envelope (Volume)
    env1_attack: float = clamp(avg_note_length ** 1.2 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env1_decay: float = clamp(avg_note_length * 0.5 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env1_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.5), 0, 1)
    env1_release: float = clamp(avg_note_length * 0.8 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env1_delay: float = clamp(avg_gap * 0.5, 0, ENV_DELAY_MAX)
    env1_hold: float = clamp(avg_note_length * 1.5 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    preset["settings"].update({
        "env_1_attack": env1_attack,
        "env_1_decay": env1_decay,
        "env_1_sustain": env1_sustain,
        "env_1_release": env1_release,
        "env_1_delay": env1_delay,
        "env_1_hold": env1_hold,
    })
    print(f"✅ ENV1 → A={env1_attack:.2f}s, D={env1_decay:.2f}s, S={env1_sustain:.2f}, R={env1_release:.2f}s, H={env1_hold:.2f}, Delay={env1_delay:.2f}")

    # ENV2: Filter Envelope
    env2_attack: float = clamp(avg_note_length ** 1.1 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env2_decay: float = clamp(avg_note_length * 0.7 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env2_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.4), 0, 1)
    env2_release: float = clamp(avg_note_length * 1.2 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env2_delay: float = clamp(avg_gap * 0.4, 0, ENV_DELAY_MAX)
    env2_hold: float = clamp(avg_note_length * 1.2 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    if mod_wheel_value is not None:
        env2_sustain = clamp(env2_sustain * (0.7 + mod_wheel_value * 0.3), 0, 1)

    preset["settings"].update({
        "env_2_attack": env2_attack,
        "env_2_decay": env2_decay,
        "env_2_sustain": env2_sustain,
        "env_2_release": env2_release,
        "env_2_delay": env2_delay,
        "env_2_hold": env2_hold,
    })
    print(f"✅ ENV2 → A={env2_attack:.2f}s, D={env2_decay:.2f}s, S={env2_sustain:.2f}, R={env2_release:.2f}s, H={env2_hold:.2f}, Delay={env2_delay:.2f}")

    # ENV3: Oscillator Morphing/Pitch Envelope
    env3_attack: float = clamp(avg_note_length ** 1.15 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env3_decay: float = clamp(avg_note_length * 0.6 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env3_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.3), 0, 1)
    env3_release: float = clamp(avg_note_length * 1.5 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env3_delay: float = clamp(avg_gap * 0.3, 0, ENV_DELAY_MAX)
    env3_hold: float = clamp(avg_note_length * 1.8 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    preset["settings"].update({
        "env_3_attack": env3_attack,
        "env_3_decay": env3_decay,
        "env_3_sustain": env3_sustain,
        "env_3_release": env3_release,
        "env_3_delay": env3_delay,
        "env_3_hold": env3_hold,
    })
    print(f"✅ ENV3 → A={env3_attack:.2f}s, D={env3_decay:.2f}s, S={env3_sustain:.2f}, R={env3_release:.2f}s, H={env3_hold:.2f}, Delay={env3_delay:.2f}")

    print("✅ Envelope modulations added: ENV2 → Filter, ENV3 → Warp")



def apply_filters_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float]) -> None:
    """
    Enables and configures Filter 1 & 2 based on MIDI CC data.
    Maps cutoff and resonance values from CCs using a logarithmic scale mapping
    from 20 Hz to 20 kHz, and writes parameters under preset["filters"].
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary.
        cc_map (Dict[int, float]): Mapping of MIDI CC numbers to normalized values (0.0–1.0).
    """
    preset.setdefault("filters", {})
    preset["filters"].setdefault("filter_1", {})
    preset["filters"].setdefault("filter_2", {})

    def scale_cutoff(cc_value: float) -> float:
        """
        Maps a normalized CC value (0.0–1.0) to a normalized frequency value using an exponential mapping.
        
        Args:
            cc_value (float): The normalized CC value.
            
        Returns:
            float: The normalized frequency value (0.0–1.0).
        """
        min_freq: float = 20.0
        max_freq: float = 20000.0
        freq: float = min_freq * (max_freq / min_freq) ** cc_value
        normalized: float = (math.log(freq) - math.log(min_freq)) / (math.log(max_freq) - math.log(min_freq))
        return max(0.0, min(1.0, normalized))

    # Filter 1 (CC 74 & 102 for cutoff, 71 for resonance)
    filter_1_ccs: set[int] = {74, 71, 102}
    filter_1_detected: List[int] = [cc for cc in filter_1_ccs if cc in cc_map and cc_map[cc] >= 0.01]
    if filter_1_detected:
        preset["filters"]["filter_1"]["enabled"] = True
        for cc in filter_1_detected:
            if cc in {74, 102}:
                preset["filters"]["filter_1"]["cutoff"] = scale_cutoff(cc_map[cc])
            elif cc == 71:
                preset["filters"]["filter_1"]["resonance"] = cc_map[cc]
    else:
        preset["filters"]["filter_1"]["enabled"] = False

    # Filter 2 (CC 85 & 103 for cutoff; 86 & 104 for resonance)
    filter_2_ccs: set[int] = {85, 86, 103, 104}
    filter_2_detected: List[int] = [cc for cc in filter_2_ccs if cc in cc_map and cc_map[cc] >= 0.01]
    if filter_2_detected:
        preset["filters"]["filter_2"]["enabled"] = True
        for cc in filter_2_detected:
            if cc in {85, 103}:
                preset["filters"]["filter_2"]["cutoff"] = scale_cutoff(cc_map[cc])
            elif cc in {86, 104}:
                preset["filters"]["filter_2"]["resonance"] = cc_map[cc]
    else:
        preset["filters"]["filter_2"]["enabled"] = False

    print(f"Filter 1 CCs detected: {filter_1_detected}")
    print(f"Filter 2 CCs detected: {filter_2_detected}")


def apply_effects_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float]) -> None:
    """
    Applies MIDI CC-based effect settings to the preset by updating entries under preset["fx"].
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary.
        cc_map (Dict[int, float]): Mapping of MIDI CC numbers to normalized values.
    """
    preset.setdefault("fx", {})

    # Reverb (CC 91)
    if 91 in cc_map and cc_map[91] > 0.1:
        preset["fx"].setdefault("reverb", {})
        preset["fx"]["reverb"]["enabled"] = True
        preset["fx"]["reverb"]["dry_wet"] = cc_map[91]
    else:
        if "reverb" in preset["fx"]:
            preset["fx"]["reverb"]["enabled"] = False

    # Chorus (CC 93)
    if 93 in cc_map and cc_map[93] > 0.1:
        preset["fx"].setdefault("chorus", {})
        preset["fx"]["chorus"]["enabled"] = True
        preset["fx"]["chorus"]["dry_wet"] = cc_map[93]
    else:
        if "chorus" in preset["fx"]:
            preset["fx"]["chorus"]["enabled"] = False

    # Delay (CC 94)
    if 94 in cc_map and cc_map[94] > 0.1:
        preset["fx"].setdefault("delay", {})
        preset["fx"]["delay"]["enabled"] = True
        preset["fx"]["delay"]["dry_wet"] = cc_map[94]
    else:
        if "delay" in preset["fx"]:
            preset["fx"]["delay"]["enabled"] = False

    # Phaser (CC 95)
    if 95 in cc_map and cc_map[95] > 0.1:
        preset["fx"].setdefault("phaser", {})
        preset["fx"]["phaser"]["enabled"] = True
        preset["fx"]["phaser"]["dry_wet"] = cc_map[95]
    else:
        if "phaser" in preset["fx"]:
            preset["fx"]["phaser"]["enabled"] = False

    # Distortion (CC 116)
    if 116 in cc_map and cc_map[116] > 0.1:
        preset["fx"].setdefault("distortion", {})
        preset["fx"]["distortion"]["enabled"] = True
        preset["fx"]["distortion"]["drive"] = cc_map[116]
    else:
        if "distortion" in preset["fx"]:
            preset["fx"]["distortion"]["enabled"] = False

    # Compressor (CC 117)
    if 117 in cc_map and cc_map[117] > 0.1:
        preset["fx"].setdefault("compressor", {})
        preset["fx"]["compressor"]["enabled"] = True
        preset["fx"]["compressor"]["amount"] = cc_map[117]
    else:
        if "compressor" in preset["fx"]:
            preset["fx"]["compressor"]["enabled"] = False

    # Flanger (CC 119)
    if 119 in cc_map and cc_map[119] > 0.1:
        preset["fx"].setdefault("flanger", {})
        preset["fx"]["flanger"]["enabled"] = True
        preset["fx"]["flanger"]["dry_wet"] = cc_map[119]
    else:
        if "flanger" in preset["fx"]:
            preset["fx"]["flanger"]["enabled"] = False


def set_vital_parameter(preset: Dict[str, Any], param_name: str, value: Any) -> None:
    """
    Safely sets a Vital parameter, placing it in the top-level or in 'settings' as needed.
    Handles macro parameters specially.
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary.
        param_name (str): The name of the parameter to set.
        value (Any): The value to assign.
    """
    preset.setdefault("settings", {})

    if param_name.startswith("macro"):
        try:
            macro_number = int(param_name.replace("macro", ""))
            control_key = f"macro_control_{macro_number}"
            preset["settings"][control_key] = value
        except ValueError:
            logging.error(f"Invalid macro parameter: {param_name}")
    else:
        preset[param_name] = value


def enable_sample_in_preset(preset: Dict[str, Any], sample_path: str = "assets/sample.wav") -> None:
    """
    Reads a WAV file from sample_path, base64-encodes its bytes, and embeds the data in the preset's "sample" key.
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary to update.
        sample_path (str, optional): Path to the sample WAV file. Defaults to "assets/sample.wav".
    """
    try:
        with open(sample_path, "rb") as f:
            raw = f.read()
        encoded = base64.b64encode(raw).decode("utf-8")
        preset["sample"] = {
            "enabled": True,
            "playback_mode": "one_shot",
            "sample_bytes": encoded
        }
        print("Sample oscillator enabled with sample from:", sample_path)
    except Exception as e:
        print(f"Error loading sample from {sample_path}: {e}")


def update_settings(modified_preset: Dict[str, Any], notes: List[Dict[str, Any]], snapshot_method: str) -> None:
    """
    Sets Oscillator 1 transpose/level based on the chosen snapshot method:
      1 = first note, 2 = average note, 3 = single user-specified time.
    
    Args:
        modified_preset (Dict[str, Any]): The preset dictionary to update.
        notes (List[Dict[str, Any]]): List of MIDI note dictionaries.
        snapshot_method (str): The snapshot method ("1", "2", or "3").
    """
    if snapshot_method == "1":
        if notes:
            note = notes[0]
            modified_preset["osc_1_transpose"] = note["pitch"] - 69
            modified_preset["osc_1_level"] = note["velocity"] / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "2":
        if notes:
            avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
            avg_vel = sum(n["velocity"] for n in notes) / len(notes)
            modified_preset["osc_1_transpose"] = avg_pitch - 69
            modified_preset["osc_1_level"] = avg_vel / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "3":
        try:
            snap_time = float(input("Enter snapshot time (sec): ").strip())
        except ValueError:
            print("Invalid time input, defaulting to method 1.")
            snap_time = None

        chosen_note: Optional[Dict[str, Any]] = None
        if snap_time is not None:
            for n in notes:
                if n["start"] <= snap_time < n["end"]:
                    chosen_note = n
                    break
        if chosen_note:
            modified_preset["osc_1_transpose"] = chosen_note["pitch"] - 69
            modified_preset["osc_1_level"] = chosen_note["velocity"] / 127.0
        else:
            print("No note active at that time. Using default.")
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5


def add_modulations(modified_preset: Dict[str, Any], ccs: List[Dict[str, Any]]) -> None:
    """
    Maps MIDI CC values to Vital parameters using a mapping from config and
    stores the modulations in the preset.
    
    Args:
        modified_preset (Dict[str, Any]): The preset dictionary to update.
        ccs (List[Dict[str, Any]]): A list of MIDI CC event dictionaries.
    """
    print("\n🔍 Debug: Processing MIDI CCs...")
    cc_map: Dict[int, float] = {}
    for cc_event in ccs:
        val_normalized = cc_event["value"] / 127.0
        cc_map[cc_event["controller"]] = val_normalized

    from config import MIDI_TO_VITAL_MAP  # Assuming this mapping is defined in config.py
    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            set_vital_parameter(modified_preset, param, cc_val)
            print(f"✅ CC{cc_num} -> {param} = {cc_val}")

    print("\n🔍 Debug: Final modulations:")
    if "modulations" not in modified_preset:
        modified_preset["modulations"] = []
    print(json.dumps(modified_preset["modulations"], indent=2))


def generate_frame_waveform(midi_data, frame_idx, num_frames, frame_size, waveform_type="saw"):
    """
    Generate a single float32 waveform frame for Vital.
    Dynamically scales harmonics based on velocity/CC, plus a morph factor.
    """
    notes = midi_data.get("notes", [])
    ccs = {
        cc["controller"]: cc["value"] / 127.0
        for cc in midi_data.get("control_changes", [])
    }

    if not notes:
        # fallback => single A4 note
        notes = [{"pitch": 69, "velocity": 100}]

    note = notes[frame_idx % len(notes)]
    pitch = note["pitch"]
    velocity = note["velocity"] / 127.0

    # CC1 => mod wheel => harmonic boost
    harmonic_boost = HARMONIC_SCALING.get(waveform_type, 1) * ccs.get(1, 0.5)

    # Build a phase array
    phase = np.linspace(0, 2*np.pi, frame_size, endpoint=False)

    # Morph factor => 0..1 across frames
    if num_frames > 1:
        morph = frame_idx / (num_frames - 1)
    else:
        morph = 0
    harmonic_intensity = (velocity * harmonic_boost) * (0.5 + 0.5 * morph)

    # Construct the wave
    if waveform_type == "sine":
        waveform = np.sin(phase)
    elif waveform_type == "saw":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / h) * np.sin(h * phase)
             for h in range(1, max_harm)],
            axis=0
        )
    elif waveform_type == "square":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / h) * np.sin(h * phase)
             for h in range(1, max_harm, 2)],
            axis=0
        )
    elif waveform_type == "triangle":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / (h**2)) * (-1)**((h-1)//2) * np.sin(h * phase)
             for h in range(1, max_harm, 2)],
            axis=0
        )
    elif waveform_type == "pulse":
        pulse_width = ccs.get(2, 0.5)  # CC2 => width
        waveform = np.where(
            phase < (2*np.pi*pulse_width),
            1.0,
            -1.0
        )
    else:
        waveform = np.sin(phase)  # fallback

    waveform *= harmonic_intensity
    # Normalize to avoid clipping
    max_val = np.max(np.abs(waveform)) or 1.0
    waveform /= max_val

    return waveform.astype(np.float32)


def generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048):
    """
    Generate 3 structured wavetable frames for Vital:
    - Frame 1: Blended sine & saw (attack phase)
    - Frame 2: Complex harmonics + **stronger FM synthesis** (sustain phase)
    - Frame 3: Pulsating saw-triangle blend with **deeper phase distortion** (release phase)
    """

    notes = midi_data.get("notes", [])
    ccs = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    if not notes:
        # Fallback to a single A4 note
        notes = [{"pitch": 69, "velocity": 100}]

    # Extract first, average, and last note characteristics
    first_note = notes[0]
    last_note = notes[-1]
    avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)

    # Generate waveforms for each frame
    frames = []
    for i, note in enumerate([first_note, {"pitch": avg_pitch, "velocity": avg_velocity}, last_note]):
        pitch = note["pitch"]
        velocity = note["velocity"] / 127.0

        # Use CC1 (mod wheel) to affect harmonics
        harmonic_boost = HARMONIC_SCALING.get(DEFAULT_WAVEFORM, 1) * (ccs.get(1, 0.5) + 0.5)  # Boosted

        # Generate phase array
        phase = np.linspace(0, 2*np.pi, frame_size, endpoint=False)

        if i == 0:  # 🔹 Frame 1 (Attack) - Sine + Bright Saw
            sine_wave = np.sin(phase) * velocity
            saw_wave = np.sum([(1.0 / h) * np.sin(h * phase) for h in range(1, 8)], axis=0) * (velocity * 0.4)
            waveform = sine_wave + saw_wave  # Stronger saw harmonics

        elif i == 1:  # 🔹 Frame 2 (Sustain) - **Stronger FM Synthesis**
            mod_freq = 3.0 + 5.0 * velocity  # Higher modulation frequency
            mod_index = 0.7  # **Increased FM depth**
            fm_mod = np.sin(phase * mod_freq) * mod_index
            harmonics = np.sum([(1.0 / h) * np.sin(h * phase + fm_mod) for h in range(1, int(15 * harmonic_boost))], axis=0)
            waveform = harmonics * velocity

        else:  # 🔹 Frame 3 (Release) - **Deeper Phase Distortion**
            triangle_wave = np.abs(np.mod(phase / np.pi, 2) - 1) * 2 - 1  # Triangle wave
            saw_wave = np.sign(np.sin(phase * (pitch / 64.0))) * velocity  # Faster saw modulation
            phase_distortion = np.sin(phase * 3.5) * 0.4  # **Stronger phase warping**
            waveform = (triangle_wave * 0.6 + saw_wave * 0.4) + phase_distortion  # **More distortion applied**

        # Normalize the waveform
        max_val = np.max(np.abs(waveform)) or 1.0
        waveform /= max_val

        # Convert to Base64
        raw_bytes = waveform.astype(np.float32).tobytes()
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        frames.append(encoded)

    return frames


def apply_cc_modulations(preset, cc_map):
    """
    Apply MIDI CC-based modulations with extra logic, e.g. mod wheel -> filter cutoff.
    """
    if "modulations" not in preset:
        preset["modulations"] = []

    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            set_vital_parameter(preset, param, cc_val)
            print(f"✅ CC{cc_num} -> {param} = {cc_val}")

    # Example special handling
    if 1 in cc_map:  # mod wheel => filter_1_cutoff
        mod_val = cc_map[1]
        if mod_val > 0.1:
            preset["modulations"].append({
                "source": "mod_wheel",
                "destination": "filter_1_cutoff",
                "amount": mod_val * 0.8
            })

    if 11 in cc_map:  # expression => volume
        exp_val = cc_map[11]
        preset["modulations"].append({
            "source": "cc_expression",
            "destination": "volume",
            "amount": exp_val
        })

    # If any pitch bend is > 0.1, we might set pitch bend range
    if any(pb["pitch"] > 0.1 for pb in preset.get("pitch_bends", [])):
        preset["settings"]["pitch_bend_range"] = 12


def replace_three_wavetables(json_data, frame_data_list):
    """
    Find the first 3 "wave_data" fields in the JSON, replace them with the
    provided base64-encoded frames, and return the modified JSON string.
    """
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, json_data))

    if len(matches) < 3:
        print(f"⚠️ Warning: Only {len(matches)} 'wave_data' entries found. Need 3+.")
        replace_count = min(len(matches), 3)
    else:
        replace_count = 3

    result = json_data
    for i in range(replace_count):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        result = result[:start] + replacement + result[end:]

    print(f"✅ Replaced wave_data in {replace_count} place(s).")
    return result


def derive_full_oscillator_params(stats: Dict[str, float], osc_index: int) -> Dict[str, Any]:
    """
    Derive a full set of oscillator parameters for a given oscillator based on MIDI stats.
    
    Args:
        stats (Dict[str, float]): Dictionary with keys 'avg_pitch', 'avg_velocity', 
                                  'pitch_range', and 'note_density'.
        osc_index (int): Oscillator index (1, 2, or 3).
    
    Returns:
        Dict[str, Any]: A dictionary mapping Vital oscillator parameter names to computed values.
    """
    avg_velocity = stats["avg_velocity"]
    pitch_range = stats["pitch_range"]
    note_density = stats["note_density"]
    avg_pitch = stats["avg_pitch"]

    unison_voices = float(min(MAX_UNISON_VOICES, int(1 + note_density / 5)))
    unison_detune = min(20, pitch_range / 2.0)
    phase = (avg_pitch % 12) / 12.0  # Maps average pitch mod 12 to 0..1
    tune = (avg_pitch - 60) % 12
    frame_spread = 1.0 if pitch_range >= 12 else pitch_range / 12.0

    return {
        f"osc_{osc_index}_destination": 0.0,
        f"osc_{osc_index}_detune_power": DEFAULT_DETUNE_POWER,
        f"osc_{osc_index}_detune_range": min(4.0, pitch_range / 10.0 + 1.0),
        f"osc_{osc_index}_distortion_amount": 0.5,
        f"osc_{osc_index}_distortion_phase": 0.5,
        f"osc_{osc_index}_distortion_spread": 0.0,
        f"osc_{osc_index}_distortion_type": 0.0,
        f"osc_{osc_index}_frame_spread": frame_spread,
        f"osc_{osc_index}_level": min(1.0, avg_velocity + 0.1 * osc_index),
        f"osc_{osc_index}_midi_track": 1.0,
        f"osc_{osc_index}_on": 1.0,
        f"osc_{osc_index}_pan": -0.5 + osc_index * 0.5,
        f"osc_{osc_index}_phase": phase,
        f"osc_{osc_index}_random_phase": DEFAULT_RANDOM_PHASE,
        f"osc_{osc_index}_smooth_interpolation": 0.0,
        f"osc_{osc_index}_spectral_morph_amount": DEFAULT_SPECTRAL_MORPH_AMOUNT,
        f"osc_{osc_index}_spectral_morph_spread": 0.0,
        f"osc_{osc_index}_spectral_morph_type": 0.0,
        f"osc_{osc_index}_spectral_unison": 0.0,
        f"osc_{osc_index}_stack_style": DEFAULT_STACK_STYLE,
        f"osc_{osc_index}_stereo_spread": DEFAULT_STEREO_SPREAD,
        f"osc_{osc_index}_transpose": 0.0,
        f"osc_{osc_index}_transpose_quantize": 0.0,
        f"osc_{osc_index}_tune": tune,
        f"osc_{osc_index}_unison_blend": DEFAULT_UNISON_BLEND,
        f"osc_{osc_index}_unison_detune": unison_detune,
        f"osc_{osc_index}_unison_voices": unison_voices,
        f"osc_{osc_index}_view_2d": 1.0,
        f"osc_{osc_index}_wave_frame": 0.0,
    }


def apply_full_oscillator_params_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Compute MIDI stats and update the preset's oscillator settings dynamically for
    oscillators 1, 2, and 3.
    
    Args:
        preset (Dict[str, Any]): The Vital preset.
        midi_data (Dict[str, Any]): Parsed MIDI data.
    """
    stats = compute_midi_stats(midi_data)
    for osc_index in range(1, 4):
        params = derive_full_oscillator_params(stats, osc_index)
        preset["settings"].update(params)
    logging.info("✅ Full dynamic oscillator parameters applied based on MIDI data.")


def modify_vital_preset(vital_preset, midi_file, snapshot_method="1"):
    """
    High-level function that modifies a Vital preset with MIDI data
    (notes, CCs, pitch bends, etc.) and returns the updated preset plus
    the generated wavetable frame data.
    """
    import copy, os, logging
    from midi_parser import parse_midi
    # Ensure helper functions are available:
    # update_settings, apply_cc_modulations, apply_dynamic_env_to_preset,
    # generate_three_frame_wavetables, build_lfo_from_cc,
    # apply_filters_to_preset, apply_effects_to_preset, enable_sample_in_preset,
    # compute_midi_stats, derive_full_oscillator_params, apply_full_oscillator_params_to_preset

    logging.info(f"🔍 Debug: Received midi_file of type {type(midi_file)}")
    
    # 1) Parse MIDI data: either from an existing dict or a file path
    try:
        if isinstance(midi_file, dict):
            logging.warning("⚠️ Using existing parsed MIDI data instead of a file path.")
            midi_data = midi_file
        elif isinstance(midi_file, str):
            logging.info(f"📂 Parsing MIDI file: {midi_file}")
            midi_data = parse_midi(midi_file)
        else:
            raise ValueError(f"Invalid type for midi_file: {type(midi_file)}")
    except Exception as e:
        logging.error(f"❌ Error parsing MIDI: {e}")
        midi_data = {"notes": [], "control_changes": [], "pitch_bends": []}

    # 2) Deep-copy the preset so the original is not mutated
    modified = copy.deepcopy(vital_preset)

    # Extract MIDI components
    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])
    pitch_bends = midi_data.get("pitch_bends", [])

    # Ensure "settings" exists
    modified.setdefault("settings", {})

    # 3) Snapshot method: update osc1 pitch/level based on chosen method
    update_settings(modified, notes, snapshot_method)

    # 4) Apply CC-based direct parameter mappings
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    apply_cc_modulations(modified, cc_map)

    # 5) Set pitch bend (final pitch wheel value)
    modified["pitch_wheel"] = pitch_bends[-1]["pitch"] / 8192.0 if pitch_bends else 0.0

    # 6) Apply dynamic envelopes based on MIDI note data
    apply_dynamic_env_to_preset(modified, midi_data)

    # ✅ Debug: Log final envelope values
    logging.info("\n🔍 **Final Envelope Values in Modified Preset:**")
    for env in ["env_1", "env_2", "env_3"]:
        logging.info(f"  {env}_attack: {modified.get(f'{env}_attack', 'N/A')}")
        logging.info(f"  {env}_decay: {modified.get(f'{env}_decay', 'N/A')}")
        logging.info(f"  {env}_sustain: {modified.get(f'{env}_sustain', 'N/A')}")
        logging.info(f"  {env}_release: {modified.get(f'{env}_release', 'N/A')}")

    # 7) Apply dynamic oscillator settings based on MIDI data.
    # This uses compute_midi_stats and derive_full_oscillator_params to set parameters like unison voices, detune, phase, tune, etc.
    apply_full_oscillator_params_to_preset(modified, midi_data)

    # 8) Generate three wavetable frames
    frame_data = generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048)

    # 9) Enable oscillators based on note count
    num_notes = len(notes)
    modified["settings"]["osc_1_on"] = 1.0 if num_notes > 0 else 0.0
    modified["settings"]["osc_2_on"] = 1.0 if num_notes > 1 else 0.0
    modified["settings"]["osc_3_on"] = 1.0 if num_notes > 2 else 0.0

    # 10) Enable Sample Oscillator if specific MIDI CCs are present
    SMP_CCS = {31, 39, 40, 74, 85, 86}  # List of CCs that trigger the sample oscillator
    smp_detected = [cc for cc in SMP_CCS if cc in cc_map and cc_map[cc] > 0.01]
    if smp_detected:
        modified["settings"]["sample_on"] = 1.0
        logging.info(f"✅ Enabling SMP (Sample Oscillator) due to MIDI CCs: {smp_detected}.")
        enable_sample_in_preset(modified, sample_path="assets/sample.wav")
    else:
        modified["settings"]["sample_on"] = 0.0
        logging.info("❌ SMP NOT Enabled.")

    # 11) Apply filters using the updated, modular function
    apply_filters_to_preset(modified, cc_map)

    # 12) Apply effects using the modular function
    apply_effects_to_preset(modified, cc_map)

    # 13) Apply LFO modulations (each with unique rate/depth settings)
    build_lfo_from_cc(modified, midi_data, lfo_idx=1, destination="filter_1_cutoff")
    build_lfo_from_cc(modified, midi_data, lfo_idx=2, destination="osc_1_pitch", one_shot=True)
    build_lfo_from_cc(modified, midi_data, lfo_idx=3, destination="volume")
    build_lfo_from_cc(modified, midi_data, lfo_idx=4, destination="filter_2_resonance")

    # 14) Append envelope modulations
    modified.setdefault("modulations", [])
    modified["modulations"].append({
        "source": "env_2",
        "destination": "filter_1_cutoff",
        "amount": 0.8
    })
    modified["modulations"].append({
        "source": "env_3",
        "destination": "osc_1_warp",
        "amount": 0.6
    })

    # 15) Apply generated wavetable frames to the first oscillator keyframes
    if "groups" in modified and modified["groups"]:
        group0 = modified["groups"][0]
        if "components" in group0 and group0["components"]:
            component0 = group0["components"][0]
            if "keyframes" in component0:
                keyframes = component0["keyframes"]
                while len(keyframes) < 3:
                    keyframes.append({
                        "position": 0.0,
                        "wave_data": "",
                        "wave_source": {"type": "sample"}
                    })
                for i in range(3):
                    keyframes[i]["wave_data"] = frame_data[i]
                    keyframes[i]["wave_source"] = {"type": "sample"}
                component0["name"] = "Generated Wavetable"

    # 16) Update the preset name based on the MIDI file name
    if "preset_name" in modified:
        midi_base_name = os.path.splitext(os.path.basename(midi_file))[0] if isinstance(midi_file, str) else "Custom_Preset"
        modified["preset_name"] = f"Generated from {midi_base_name}"

    # 17) Rename the first three occurrences of "Init" to descriptive names
    def replace_init_names(obj, replacement_names, count=[0]):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "name" and value == "Init" and count[0] < 3:
                    obj[key] = replacement_names[count[0]]
                    count[0] += 1
                else:
                    replace_init_names(value, replacement_names, count)
        elif isinstance(obj, list):
            for item in obj:
                replace_init_names(item, replacement_names, count)
    replace_init_names(modified, ["Attack Phase", "Harmonic Blend", "Final Release"])

    logging.info("✅ Finished applying wavetables, envelopes, LFOs, filters, effects, sample oscillator, and custom oscillator settings.")
    return modified, frame_data


def get_preset_filename(midi_path):
    """
    Extracts the base name from the MIDI file and ensures it has a .vital extension.
    """
    base_name = os.path.splitext(os.path.basename(midi_path))[0]
    return f"{base_name}.vital"


def save_vital_preset(vital_preset, midi_path, frame_data_list=None):
    """
    Saves the modified Vital preset as an uncompressed JSON file
    named after the MIDI file (but with a .vital extension).
    
    Args:
        vital_preset (dict): The modified Vital preset data.
        midi_path (str): The path to the original MIDI file.
        frame_data_list (list): Optional list of three wavetables (base64 strings).
    
    Returns:
        str: The output file path if successful, None otherwise.
    """
    try:
        # Generate the output path based on MIDI file name
        output_path = os.path.join(OUTPUT_DIR, get_preset_filename(midi_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Ensure "modulations" key exists
        vital_preset.setdefault("modulations", [])

        # Convert the preset to JSON format
        json_data = json.dumps(vital_preset, indent=2)

        # If valid wavetables are provided, replace them
        if isinstance(frame_data_list, list) and len(frame_data_list) == 3:
            json_data = replace_three_wavetables(json_data, frame_data_list)
            logging.info("✅ Replaced wavetables in the preset.")
        else:
            logging.warning("⚠️ No valid wave_data provided or not exactly 3 frames.")

        # Write the preset to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        logging.info(f"✅ Successfully saved Vital preset as JSON: {output_path}")
        return output_path  # Return the path for reference

    except OSError as e:
        logging.error(f"❌ File error when saving Vital preset: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON encoding error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error in save_vital_preset: {e}")

    return None


def apply_macro_controls_to_preset(preset, cc_map):
    """
    Maps MIDI CCs (20-23) => Macro Controls (1-4), then assigns some example macro modulations.
    """
    print("🔹 Applying Macro Controls to preset...")

    for i in range(1, 5):  # Macro 1..4
        macro_key = f"macro_control_{i}"
        midi_cc = 19 + i  # e.g. CC20 => Macro1, CC21 => Macro2, ...
        preset[macro_key] = cc_map.get(midi_cc, 0.5)  # default 0.5

    macro_mods = [
        {"source": "macro_control_1", "destination": "filter_1_cutoff",   "amount": 0.8},
        {"source": "macro_control_2", "destination": "distortion_drive",  "amount": 0.6},
        {"source": "macro_control_3", "destination": "reverb_dry_wet",    "amount": 0.7},
        {"source": "macro_control_4", "destination": "chorus_dry_wet",    "amount": 0.5}
    ]

    if "modulations" not in preset:
        preset["modulations"] = []
    preset["modulations"].extend(macro_mods)

    print("✅ Macro Controls applied successfully!")
 