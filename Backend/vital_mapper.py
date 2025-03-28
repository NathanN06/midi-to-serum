# vital_mapper.py

import json

import zlib
import base64
import copy
import re
import numpy as np
import os
import logging
from midi_analysis import compute_midi_stats
from midi_parser import parse_midi
import random
import math  


# Local imports

from config import (
    # MIDI Mappings & Defaults
    MIDI_TO_VITAL_MAP,
    MIDI_PITCH_REFERENCE,
    DEFAULT_PITCH_REFERENCE,
    DEFAULT_OSC_1_TRANSPOSE,
    DEFAULT_OSC_1_LEVEL,

    # ADSR & Envelope Settings
    DEFAULT_ADSR,
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
    ENV_ATTACK_MIN,
    ENV_ATTACK_MAX,
    ENV_DECAY_MIN,
    ENV_DECAY_MAX,
    ENV_RELEASE_MIN,
    ENV_RELEASE_MAX,
    ENV_DELAY_MAX,
    ENV_HOLD_MIN,
    ENV_HOLD_MAX,

    # Wavetable & Harmonics
    DEFAULT_NUM_WAVETABLE_FRAMES,
    DEFAULT_FRAME_SIZE,
    DEFAULT_WAVEFORM,
    DEFAULT_WAVEFORM_TYPE,
    HARMONIC_SCALING,
    DEFAULT_MIN_HARMONICS,
    DEFAULT_MAX_HARMONICS,
    DEFAULT_PHASE_DISTORTION,
    DEFAULT_PHASE_DISTORTION_AMOUNT,
    TRIANGLE_BLEND_RATIO,
    SAW_BLEND_RATIO,

    # FM Synthesis
    FM_MOD_INDEX,
    FM_MOD_FREQ_BASE,
    FM_MOD_FREQ_RANGE,

    # Unison, Stereo & Oscillator Defaults
    DEFAULT_DETUNE_POWER,
    DEFAULT_UNISON_BLEND,
    DEFAULT_RANDOM_PHASE,
    DEFAULT_STACK_STYLE,
    DEFAULT_STEREO_SPREAD,
    DEFAULT_SPECTRAL_MORPH_AMOUNT,
    MAX_UNISON_VOICES,
    DEFAULT_KEYFRAMES,
    DEFAULT_WAVE_DATA,

    # LFO Settings
    DEFAULT_LFO_POINTS,
    LFO_RATE_MULTIPLIER,
    LFO_DEPTH_MIN,
    LFO_DEPTH_MULTIPLIER,
    DEFAULT_LFO_TEMPO_OPTIONS,
    DEFAULT_LFO_SYNC,

    # Effect Thresholds & Parameter Mapping
    EFFECT_ENABLE_THRESHOLD, 
    EFFECTS_CC_MAP, 
    EFFECTS_PARAM_MAP,

    # File Paths & Extensions
    OUTPUT_DIR,
    PRESET_FILE_EXTENSION,

    FILTER_2_CUTOFF_CC,
    FILTER_2_RESONANCE_CC,
    FILTER_1_RESONANCE_CC,
    MIN_FILTER_FREQ,
    MAX_FILTER_FREQ,
    FILTER_1_CUTOFF_CC,
    FILTER_1_CC_NUMBERS,
    FILTER_2_CC_NUMBERS,

    DEFAULT_STACK_MODE, 
    STACK_MODE_RULES,
    MIN_FILTER_FREQ,
    MAX_FILTER_FREQ,
    EFFECT_ENABLE_THRESHOLD,
    DEFAULT_FILTER_DRIVE,
    DEFAULT_FILTER_KEYTRACK,
    DEFAULT_FILTER_MIX,
    FILTER_1_CC_NUMBERS,
    FILTER_1_CUTOFF_CC,
    FILTER_1_RESONANCE_CC,
    FILTER_1_DRIVE_CC,
    FILTER_1_KEYTRACK_CC,
    FILTER_1_MIX_CC,
    FILTER_2_CC_NUMBERS,
    FILTER_2_CUTOFF_CC,
    FILTER_2_RESONANCE_CC,
    FILTER_2_DRIVE_CC,
    FILTER_2_KEYTRACK_CC,
    FILTER_2_MIX_CC,
    OSC_SHAPE_POOLS,

)





from typing import Any, Dict, List, Optional, Tuple


def map_velocity_to_macros_and_volume(preset: dict, midi_data: dict) -> None:
    """
    Maps velocity statistics from the MIDI file to musical parameters in the Vital preset.
    Routes dynamic velocity to volume and macro modulation depths for expressive control.
    
    Args:
        preset (dict): The Vital preset dictionary.
        midi_data (dict): Parsed MIDI data including notes and CCs.
    """
    preset.setdefault("settings", {})
    preset["settings"].setdefault("modulations", [])

    stats = compute_midi_stats(midi_data)

    avg_velocity = stats.get("avg_velocity", 80)
    velocity_range = stats.get("velocity_range", 20)
    velocity_std = stats.get("velocity_std", 10)
    max_velocity = stats.get("max_velocity", 100)
    min_velocity = stats.get("min_velocity", 40)

    # Normalize values (0.0 - 1.0)
    avg_vel_norm = avg_velocity / 127.0
    range_norm = velocity_range / 127.0
    std_norm = velocity_std / 127.0

    # Route average velocity directly to volume level
    preset["settings"]["volume"] = avg_vel_norm

    # Route macro depths based on expressive velocity stats
    preset["settings"].update({
        "macro_control_1": 0.4 + range_norm * 0.6,  # Wide range = more modulation
        "macro_control_2": 0.3 + std_norm * 0.7,    # High std = more dynamic
        "macro_control_3": 0.2 + avg_vel_norm * 0.8,
        "macro_control_4": 0.1 + (max_velocity - min_velocity) / 127.0 * 0.9
    })

    # Modulate expressive destinations
    preset["settings"]["modulations"].extend([
        {"source": "macro_control_1", "destination": "filter_1_cutoff", "amount": 0.8},
        {"source": "macro_control_2", "destination": "distortion_drive", "amount": 0.7},
        {"source": "macro_control_3", "destination": "reverb_dry_wet", "amount": 0.6},
        {"source": "macro_control_4", "destination": "volume", "amount": 0.5}
    ])


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
    
    # Expand the list to include at least `lfo_idx` LFOs, setting default values
    while len(preset["settings"]["lfos"]) < lfo_idx:
        preset["settings"]["lfos"].append({
            "name": f"LFO {len(preset['settings']['lfos']) + 1}",
            "num_points": DEFAULT_LFO_POINTS,  # Updated from hardcoded 2
            "points": [0.0, 1.0, 1.0, 0.0],  # Still basic, could be configurable
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
    preset["settings"][f"lfo_{lfo_idx}_tempo"] = random.choice(DEFAULT_LFO_TEMPO_OPTIONS)  # Replaced `numpy` random choice

    # Apply one-shot mode if requested
    if one_shot:
        preset["settings"][f"lfo_{lfo_idx}_one_shot"] = 1.0

    # Add a modulation mapping for the LFO depth
    preset.setdefault("settings", {})  # Ensure "settings" exists
    preset["settings"].setdefault("modulations", [])  # Ensure "modulations" exists inside "settings"

    preset["settings"]["modulations"].append({

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


def get_best_lfo_targets(midi_data: Dict[str, Any]) -> List[str]:
    """
    Suggests LFO modulation targets based on MIDI features.
    Returns a list of 4 ideal LFO destinations.
    """
    stats = compute_midi_stats(midi_data)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    avg_velocity = stats.get("avg_velocity", 80) / 127.0

    # CC map for dynamic logic
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    # Start with essential LFO targets
    targets = []

    # If there's a lot of movement, modulate pitch or filter cutoff
    if pitch_range > 12:
        targets.append("osc_1_pitch")
        targets.append("filter_1_cutoff")
    else:
        targets.append("osc_1_level")

    # If CC1 is used, modulate something expressive
    if 1 in cc_map and cc_map[1] > 0.2:
        targets.append("osc_1_warp")
    else:
        targets.append("osc_2_pitch")

    # Use note density to choose rhythmic vs static modulation
    if note_density > 4.0:
        targets.append("filter_2_resonance")
    else:
        targets.append("reverb_dry_wet")

    # Fallback filler to ensure 4 targets
    while len(targets) < 4:
        fallback_pool = ["volume", "osc_2_warp", "distortion_drive", "delay_feedback"]
        for param in fallback_pool:
            if param not in targets:
                targets.append(param)
                break

    return targets[:4]  # Just in case it overflows


def set_vital_parameter(preset: Dict[str, Any], param_name: str, value: Any) -> None:
    """
    Safely sets a Vital parameter, ensuring it is placed inside 'settings'.
    Handles macro parameters separately.

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
        # 🔥 Ensure ALL parameters go inside "settings"
        preset["settings"][param_name] = value


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
    modified_preset.setdefault("settings", {})  # Ensure "settings" exists

    if snapshot_method == "1":
        if notes:
            note = notes[0]
            modified_preset["settings"]["osc_1_transpose"] = note["pitch"] - MIDI_PITCH_REFERENCE
            modified_preset["settings"]["osc_1_level"] = note["velocity"] / 127.0
        else:
            modified_preset["settings"]["osc_1_transpose"] = DEFAULT_OSC_1_TRANSPOSE
            modified_preset["settings"]["osc_1_level"] = DEFAULT_OSC_1_LEVEL

    elif snapshot_method == "2":
        if notes:
            avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
            avg_vel = sum(n["velocity"] for n in notes) / len(notes)
            modified_preset["settings"]["osc_1_transpose"] = avg_pitch - MIDI_PITCH_REFERENCE
            modified_preset["settings"]["osc_1_level"] = avg_vel / 127.0
        else:
            modified_preset["settings"]["osc_1_transpose"] = DEFAULT_OSC_1_TRANSPOSE
            modified_preset["settings"]["osc_1_level"] = DEFAULT_OSC_1_LEVEL

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
            modified_preset["settings"]["osc_1_transpose"] = chosen_note["pitch"] - MIDI_PITCH_REFERENCE
            modified_preset["settings"]["osc_1_level"] = chosen_note["velocity"] / 127.0
        else:
            print("No note active at that time. Using default.")
            modified_preset["settings"]["osc_1_transpose"] = DEFAULT_OSC_1_TRANSPOSE
            modified_preset["settings"]["osc_1_level"] = DEFAULT_OSC_1_LEVEL


def get_shape_for_osc1(stats):
    """
    OSC1 → Attack Phase: Sharper = more aggression, smoother = more mellow.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_range = stats.get("velocity_range", 0)
    velocity_std = stats.get("velocity_std", 0)
    avg_pitch = stats.get("avg_pitch", 60)
    note_density = stats.get("note_density", 0.02)

    # High aggression
    if avg_velocity > 90 and velocity_range > 60:
        return "folded"

    # Fast-moving passages
    if note_density > 0.07:
        return "saw"

    # Dynamic expressiveness
    if velocity_std > 25:
        return "triangle"

    # Sparse or mellow
    if note_density < 0.015:
        return "sine"

    # Fallback based on pitch
    if avg_pitch > 75:
        return "saw"
    elif avg_pitch < 50:
        return "triangle"
    else:
        return "folded"


def get_shape_for_osc2(stats):
    """
    OSC2 → Harmonic Blend: richer or fuzzier based on pitch and note complexity.
    """
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    avg_pitch = stats.get("avg_pitch", 60)

    # Wild pitch motion = chaotic
    if pitch_range > 65:
        return "chaotic"

    # Busy textures = rich buzz
    if note_density > 0.05:
        return "harmonic_buzz"

    # Melodic and clear
    if avg_pitch > 68:
        return "triangle"

    # Simple, minimal range
    if pitch_range < 15:
        return "sine"

    # Mid-complexity fallback
    if pitch_range > 40:
        return "saw"
    else:
        return "triangle"


def get_shape_for_osc3(stats):
    """
    OSC3 → Final Release: smoother or noisier based on decay needs.
    No randomness — purely MIDI-driven.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_std = stats.get("velocity_std", 0)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    velocity_range = stats.get("velocity_range", 0)

    # Highly expressive: big swings in dynamics or sparse notes
    if velocity_std > 30 or (velocity_std > 25 and note_density < 0.02):
        return "triangle"

    # Rich, bright release needed for dense, varied pitch movement
    if note_density > 0.065 and pitch_range > 25:
        return "folded"

    # Low energy, soft touch
    if avg_velocity < 35 or velocity_range < 10:
        return "sine" if pitch_range < 50 else "triangle"

    # No dynamics at all, use shape based on pitch context
    if velocity_range == 0:
        if pitch_range > 60:
            return "folded"
        elif pitch_range < 10:
            return "triangle"
        else:
            return "saw"

    # Default deterministic fallback — based on pitch shape only
    if pitch_range > 40:
        return "folded"
    elif pitch_range > 20:
        return "triangle"
    else:
        return "sine"



def generate_osc1_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "sine") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    ccs = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}
    modwheel = ccs.get(1, 0.5)
    rng = random.Random(int(stats["avg_pitch"] * 1234))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase + modwheel * np.sin(phase * 2))
    elif shape == "saw":
        max_h = int(6 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase + rng.uniform(0, 0.2))
            for h in range(1, max_h)
        ], axis=0)
    elif shape == "triangle":
        base = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        harmonic = 0.3 * np.sin(phase * 3 + modwheel * 2)
        waveform = base + harmonic
    elif shape == "folded":
        folded = np.tanh(2.5 * np.sin(phase + modwheel * np.pi))
        noise = 0.1 * rng.uniform(-1, 1) * np.sin(phase * rng.randint(2, 5))
        waveform = folded + noise
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")


def generate_osc2_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "saw") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    rng = random.Random(int(stats["avg_pitch"] * 4321))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "saw":
        max_harm = int(8 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase + rng.uniform(0, 0.3))
            for h in range(1, max_harm)
        ], axis=0)
    elif shape == "harmonic_buzz":
        base = np.sum([
            np.sin(h * phase + rng.uniform(0, 0.1)) * (1.0 / (h ** 0.9))
            for h in range(1, 20)
        ], axis=0)
        detune = 0.1 * np.sin(phase * rng.randint(2, 6))
        waveform = base + detune
    elif shape == "chaotic":
        fm = np.sin(phase * (2 + note_density)) * 0.6
        waveform = np.tanh(np.sin(phase * 2 + fm) + np.cos(phase * 3))
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")


def generate_osc3_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "triangle") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    avg_pitch = stats.get("avg_pitch", 60.0)
    rng = random.Random(int(avg_pitch * 5678))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "triangle":
        tri = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        shimmer = 0.2 * np.sin(phase * 4 + pitch_range * 0.1)
        waveform = tri + shimmer
    elif shape == "folded":
        base = np.tanh(3.0 * np.sin(phase + np.sin(phase * 3)))
        motion = 0.2 * np.sin(phase * rng.randint(2, 5) + avg_pitch * 0.05)
        waveform = base + motion
    elif shape == "sine":
        vibrato = 0.05 * np.sin(phase * 6)
        waveform = np.sin(phase + vibrato)
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")


def replace_three_wavetables(json_data: str, frame_data_list: List[str]) -> str:
    """
    Replaces the first 3 "wave_data" entries in a Vital preset JSON with provided base64-encoded wavetable frames.
    
    Args:
        json_data (str): The raw JSON string from the .vital preset.
        frame_data_list (List[str]): List of 3 base64-encoded wavetable frames.

    Returns:
        str: Updated JSON string with modified wave_data fields.
    """
    import re

    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, json_data))

    if len(matches) < 3:
        print(f"⚠️ Warning: Only {len(matches)} 'wave_data' entries found. Need at least 3.")
        replace_count = len(matches)
    else:
        replace_count = 3

    result = json_data
    for i in range(replace_count):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        result = result[:start] + replacement + result[end:]

    print(f"✅ Replaced wave_data in {replace_count} place(s).")
    return result


def determine_oscillator_stack(midi_data):
    """Determine the best oscillator stack setting based on MIDI note intervals."""
    notes = sorted(set(note["pitch"] for note in midi_data.get("notes", [])))  # Get unique sorted pitches

    if len(notes) == 0:
        return DEFAULT_STACK_MODE  # Use default from config

    intervals = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]

    if len(notes) == 1:
        return STACK_MODE_RULES["single_note"]
    elif len(notes) == 2:
        if 12 in intervals:
            return STACK_MODE_RULES["octave"]
        elif 24 in intervals:
            return STACK_MODE_RULES["double_octave"]
        elif 7 in intervals:
            return STACK_MODE_RULES["power_chord"]
        elif 5 in intervals:
            return STACK_MODE_RULES["minor_chord"]
    elif len(notes) == 3:
        if 12 in intervals and 7 in intervals:
            return STACK_MODE_RULES["double_power_chord"]
        elif {4, 3, 7}.issubset(set(intervals)):
            return STACK_MODE_RULES["major_chord"]
        elif {3, 4, 7}.issubset(set(intervals)):
            return STACK_MODE_RULES["minor_chord"]
    elif len(notes) > 3:
        if max(intervals) > 24:
            return STACK_MODE_RULES["wide_interval_24"]
        elif max(intervals) > 12:
            return STACK_MODE_RULES["wide_interval_12"]
        elif all(i % 2 == 0 for i in intervals):
            return STACK_MODE_RULES["odd_harmonics"]
        else:
            return STACK_MODE_RULES["harmonics"]

    return DEFAULT_STACK_MODE  # Fallback case


def apply_modulations_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Applies advanced modulation logic to the Vital preset, based on MIDI CCs, note features, and expressive controls.
    Dynamically adapts macro targets, routes mod wheel/expression, and enhances musicality.
    """

    preset.setdefault("settings", {})
    preset["settings"].setdefault("modulations", [])
    modulations = []

    # === Extract MIDI data ===
    ccs = midi_data.get("control_changes", [])
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    stats = compute_midi_stats(midi_data)

    avg_vel = stats.get("avg_velocity", 80) / 127.0
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    expressive = any(cc in cc_map for cc in [1, 11])

    # === 1. Map CCs directly to parameters ===
    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            preset["settings"][param] = cc_val
            print(f"✅ CC{cc_num} -> {param} = {cc_val:.2f}")

    # === 2. Mod Wheel / Expression ===
    if 1 in cc_map and cc_map[1] > 0.05:
        modulations.append({
            "source": "mod_wheel",
            "destination": "filter_1_cutoff",
            "amount": cc_map[1] * 0.8
        })
    if 11 in cc_map:
        modulations.append({
            "source": "cc_expression",
            "destination": "volume",
            "amount": cc_map[11]
        })

    # === 3. Dynamic Macro Routing ===
    # Detect active filters and dominant FX
    filter_dest = "filter_1_cutoff" if preset["settings"].get("filter_1_on", 0.0) else "filter_2_cutoff"
    fx_strengths = {
        fx: cc_map.get(cc, 0.0) for fx, cc in EFFECTS_CC_MAP.items()
    }
    main_fx = max(fx_strengths.items(), key=lambda x: x[1])[0] if fx_strengths else "reverb"
    main_fx_param = f"{main_fx}_dry_wet" if main_fx in ["reverb", "delay", "chorus"] else f"{main_fx}_drive"

    # Macro sources
    macros = {
        "macro_control_1": cc_map.get(20, 0.5),
        "macro_control_2": cc_map.get(21, 0.5),
        "macro_control_3": cc_map.get(22, 0.5),
        "macro_control_4": cc_map.get(23, 0.5),
    }
    preset["settings"].update(macros)

    modulations.extend([
        {"source": "macro_control_1", "destination": filter_dest, "amount": 0.8},
        {"source": "macro_control_2", "destination": "osc_1_warp", "amount": 0.7},
        {"source": "macro_control_3", "destination": main_fx_param, "amount": 0.6},
        {"source": "macro_control_4", "destination": "lfo_1_frequency", "amount": 0.5},
    ])

    # === 4. Envelope modulations ===
    modulations.extend([
        {"source": "env_2", "destination": filter_dest, "amount": 0.8},
        {"source": "env_3", "destination": "osc_1_frame", "amount": 0.6},
    ])

    # === 5. Adaptive pitch modulation ===
    if pitch_range > 12:
        modulations.append({
            "source": "lfo_2",
            "destination": "osc_1_pitch",
            "amount": 0.4 + (pitch_range / 48.0)
        })
    if note_density > 5.0:
        modulations.append({
            "source": "lfo_3",
            "destination": "filter_2_resonance",
            "amount": 0.3 + (note_density / 20.0)
        })

    # === 6. Pitch bend detection ===
    if any(pb["pitch"] > 0.1 for pb in midi_data.get("pitch_bends", [])):
        preset["settings"]["pitch_bend_range"] = 12

    # === Finalize ===
    preset["settings"]["modulations"] = modulations
    print(f"✅ {len(modulations)} modulations applied dynamically.")



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

    # Dynamically derived values
    unison_voices = float(min(MAX_UNISON_VOICES, int(1 + note_density / 5)))
    unison_detune = min(20.0, pitch_range * 0.8)
    phase = (avg_pitch % 12) / 12.0
    tune = (avg_pitch - 60) % 12
    frame_spread = min(1.0, pitch_range / 12.0)
    spectral_spread = min(1.0, pitch_range / 24.0)
    distortion_spread = min(1.0, avg_velocity)
    morph_amount = min(1.0, pitch_range / 32.0 + 0.3)
    stereo_spread = min(1.0, 0.5 + note_density / 10.0)
    blend = min(1.0, 0.6 + avg_velocity * 0.4)

    return {
        f"osc_{osc_index}_destination": 0.0,
        f"osc_{osc_index}_detune_power": DEFAULT_DETUNE_POWER,
        f"osc_{osc_index}_detune_range": min(4.0, pitch_range / 10.0 + 1.0),
        f"osc_{osc_index}_distortion_amount": 0.5,
        f"osc_{osc_index}_distortion_phase": 0.5,
        f"osc_{osc_index}_distortion_spread": distortion_spread,
        f"osc_{osc_index}_distortion_type": 0.0,
        f"osc_{osc_index}_frame_spread": frame_spread,
        f"osc_{osc_index}_level": min(1.0, avg_velocity + 0.1 * osc_index),
        f"osc_{osc_index}_midi_track": 1.0,
        f"osc_{osc_index}_on": 1.0,
        f"osc_{osc_index}_pan": -0.5 + osc_index * 0.5,
        f"osc_{osc_index}_phase": phase,
        f"osc_{osc_index}_random_phase": DEFAULT_RANDOM_PHASE,
        f"osc_{osc_index}_smooth_interpolation": 0.0,
        f"osc_{osc_index}_spectral_morph_amount": morph_amount,
        f"osc_{osc_index}_spectral_morph_spread": spectral_spread,
        f"osc_{osc_index}_spectral_morph_type": 0.0,
        f"osc_{osc_index}_spectral_unison": 0.0,
        f"osc_{osc_index}_stack_style": DEFAULT_STACK_STYLE,
        f"osc_{osc_index}_stereo_spread": stereo_spread,
        f"osc_{osc_index}_transpose": 0.0,
        f"osc_{osc_index}_transpose_quantize": 0.0,
        f"osc_{osc_index}_tune": tune,
        f"osc_{osc_index}_unison_blend": blend,
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


def apply_macro_controls_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float]) -> None:
    """
    Apply macros to dynamic modulation targets based on active filters and FX.
    Velocity-based macro values should already be set. This only overrides with CCs if provided.
    """
    preset.setdefault("settings", {})
    preset["settings"].setdefault("modulations", [])
    settings = preset["settings"]

    # Step 1: Allow CCs to override macro values if present
    for i in range(1, 5):
        cc_num = 19 + i  # CC20-23
        macro_key = f"macro_control_{i}"
        if cc_num in cc_map:
            settings[macro_key] = cc_map[cc_num]

    # Step 2: Detect active filters and effects
    filter_1_active = settings.get("filter_1_on", 0.0) >= 1.0
    filter_2_active = settings.get("filter_2_on", 0.0) >= 1.0
    reverb_active = settings.get("reverb_on", 0.0) >= 1.0
    delay_active = settings.get("delay_on", 0.0) >= 1.0
    distortion_active = settings.get("distortion_on", 0.0) >= 1.0
    chorus_active = settings.get("chorus_on", 0.0) >= 1.0
    phaser_active = settings.get("phaser_on", 0.0) >= 1.0

    # Step 3: Dynamically assign macro modulations
    macro_mods = []

    # 🟣 Macro 1 → Main filter (whichever is on)
    existing_macro1_routes = [mod for mod in settings["modulations"] if mod.get("source") == "macro1"]
    if existing_macro1_routes:
        logging.info("🛡️ Skipping Macro 1 routing – already dynamically handled.")
    else:
        if filter_1_active:
            macro_mods.extend([
                {"source": "macro_control_1", "destination": "filter_1_cutoff", "amount": 0.8},
                {"source": "macro_control_1", "destination": "osc_1_frame", "amount": 0.4},
            ])
        elif filter_2_active:
            macro_mods.extend([
                {"source": "macro_control_1", "destination": "filter_2_cutoff", "amount": 0.8},
                {"source": "macro_control_1", "destination": "osc_2_frame", "amount": 0.4},
            ])

    # 🔥 Macro 2 → Distortion + filter2 resonance if used
    if distortion_active:
        macro_mods.append({"source": "macro_control_2", "destination": "distortion_drive", "amount": 0.7})
    if filter_2_active:
        macro_mods.append({"source": "macro_control_2", "destination": "filter_2_resonance", "amount": 0.5})

    # 🌊 Macro 3 → Reverb or Delay
    if reverb_active:
        macro_mods.extend([
            {"source": "macro_control_3", "destination": "reverb_dry_wet", "amount": 0.6},
            {"source": "macro_control_3", "destination": "reverb_feedback", "amount": 0.3},
        ])
    elif delay_active:
        macro_mods.extend([
            {"source": "macro_control_3", "destination": "delay_dry_wet", "amount": 0.6},
            {"source": "macro_control_3", "destination": "delay_feedback", "amount": 0.4},
        ])

    # 🎛️ Macro 4 → Chorus, Phaser, or fallback
    if chorus_active:
        macro_mods.append({"source": "macro_control_4", "destination": "chorus_dry_wet", "amount": 0.5})
    if phaser_active:
        macro_mods.append({"source": "macro_control_4", "destination": "phaser_feedback", "amount": 0.3})
    if not (chorus_active or phaser_active):
        macro_mods.append({"source": "macro_control_4", "destination": "delay_feedback", "amount": 0.3})

    # Add to preset
    settings["modulations"].extend(macro_mods)

    logging.info(f"✅ Macro routing complete. {len(macro_mods)} dynamic modulations applied.")


def modify_vital_preset(vital_preset: Dict[str, Any],
                        midi_file: Any) -> Tuple[Dict[str, Any], List[str]]:
    """
    Modifies a Vital preset with MIDI data (notes, CCs, pitch bends, etc.)
    and returns the updated preset along with generated wavetable frame data.
    """
    logging.info(f"🔍 Debug: Received midi_file of type {type(midi_file)}")

    
    # 1) Parse MIDI data
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

    # 1.5) Compute MIDI stats
    stats = compute_midi_stats(midi_data)
    logging.info(f"📊 MIDI Stats: {stats}")

    # 2) Deep-copy the preset
    modified: Dict[str, Any] = copy.deepcopy(vital_preset)

    # Ensure modulations list exists
    modified.setdefault("modulations", [])

    # 🎯 STEP 2: Route macro1 based on pitch range
    if stats.get("pitch_range", 0) > 12:
        # Wide pitch range = more aggressive macro target
        modified["modulations"].append({
            "source": "macro1",
            "target": "osc_1_warp",
            "amount": 0.5
        })
        logging.info("🎚️ Routed macro1 to osc_1_warp due to wide pitch range.")
    else:
        # Narrow pitch range = gentler modulation
        modified["modulations"].append({
            "source": "macro1",
            "target": "filter_1_cutoff",
            "amount": -0.3
        })
        logging.info("🎚️ Routed macro1 to filter_1_cutoff due to narrow pitch range.")


    # 2) Deep-copy the preset
    modified: Dict[str, Any] = copy.deepcopy(vital_preset)

    # Extract MIDI components
    notes: List[Dict[str, Any]] = midi_data.get("notes", [])
    ccs: List[Dict[str, Any]] = midi_data.get("control_changes", [])
    pitch_bends: List[Dict[str, Any]] = midi_data.get("pitch_bends", [])

    # ⚠️ Rebuild cc_map (needed for filters, FX, macros, etc.)
    cc_map: Dict[int, float] = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}

    modified.setdefault("settings", {})

    # 3.5) Dynamically route velocity to volume & macros
    map_velocity_to_macros_and_volume(modified, midi_data)


    # 4) Apply all modulations: CCs, macros, mod wheel, envelopes, expression, etc.
    apply_modulations_to_preset(modified, midi_data)

    # 5) Set pitch bend
    modified["pitch_wheel"] = pitch_bends[-1]["pitch"] / 8192.0 if pitch_bends else 0.0

    # 6) Envelopes
    apply_dynamic_env_to_preset(modified, midi_data)

    # 7) Oscillators
    apply_full_oscillator_params_to_preset(modified, midi_data)

    # 8) Wavetables: Generate dynamic shapes per oscillator based on MIDI stats
    shape1 = get_shape_for_osc1(stats)
    shape2 = get_shape_for_osc2(stats)
    shape3 = get_shape_for_osc3(stats)

    frames_osc1 = generate_osc1_frame(midi_data, frame_size=DEFAULT_FRAME_SIZE, shape=shape1)
    frames_osc2 = generate_osc2_frame(midi_data, frame_size=DEFAULT_FRAME_SIZE, shape=shape2)
    frames_osc3 = generate_osc3_frame(midi_data, frame_size=DEFAULT_FRAME_SIZE, shape=shape3)
    frame_data = [frames_osc1, frames_osc2, frames_osc3]


    # 9) Enable oscillators
    num_notes: int = len(notes)
    modified["settings"]["osc_1_on"] = 1.0 if num_notes > 0 else 0.0
    modified["settings"]["osc_2_on"] = 1.0 if num_notes > 1 else 0.0
    modified["settings"]["osc_3_on"] = 1.0 if num_notes > 2 else 0.0

    # 10) Enable Sample Oscillator if any SMP-related CC is present
    SMP_CCS: set[int] = {31, 39, 40, 74, 85, 86}
    smp_detected = [cc for cc in SMP_CCS if cc in cc_map and cc_map[cc] > 0.01]
    if smp_detected:
        modified["settings"]["sample_on"] = 1.0
        logging.info(f"✅ Enabling SMP (Sample Oscillator) due to MIDI CCs: {smp_detected}")
        enable_sample_in_preset(modified, sample_path="assets/sample.wav")
    else:
        modified["settings"]["sample_on"] = 0.0
        logging.info("❌ SMP NOT Enabled.")

    # 11) Filters
    apply_filters_to_preset(modified, cc_map, midi_data)

    # 12) Effects
    apply_effects_to_preset(modified, cc_map, midi_data)

    # 13) LFOs
    lfo_targets = get_best_lfo_targets(midi_data)
    build_lfo_from_cc(modified, midi_data, lfo_idx=1, destination=lfo_targets[0])
    build_lfo_from_cc(modified, midi_data, lfo_idx=2, destination=lfo_targets[1], one_shot=True)
    build_lfo_from_cc(modified, midi_data, lfo_idx=3, destination=lfo_targets[2])
    build_lfo_from_cc(modified, midi_data, lfo_idx=4, destination=lfo_targets[3])

    # 14) Wavetable frames into keyframes
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

    # 15) Preset name from MIDI file
    if "preset_name" in modified:
        midi_base_name = os.path.splitext(os.path.basename(midi_file))[0] if isinstance(midi_file, str) else "Custom_Preset"
        modified["preset_name"] = f"Generated from {midi_base_name}"

    # 16) Rename Init names
    def replace_init_names(obj: Any, replacement_names: List[str], count: List[int] = [0]) -> None:
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

    # 17) Oscillator stack setting
    stack_setting = determine_oscillator_stack(midi_data)
    modified["settings"]["osc_1_stack"] = stack_setting
    modified["settings"]["osc_2_stack"] = stack_setting
    modified["settings"]["osc_3_stack"] = stack_setting
    logging.info(f"🎛️ Oscillator stack: {stack_setting}")

    # 18) Macro control routing
    apply_macro_controls_to_preset(modified, cc_map)

    logging.info("✅ Vital preset fully modified based on MIDI.")
    return modified, frame_data


def get_preset_filename(midi_path: str) -> str:
    """
    Extracts the base name from the MIDI file and ensures it has the correct preset extension.

    Args:
        midi_path (str): The MIDI file path.

    Returns:
        str: The generated preset filename with the correct extension.
    """
    base_name: str = os.path.splitext(os.path.basename(midi_path))[0]
    return f"{base_name}{PRESET_FILE_EXTENSION}"


def save_vital_preset(vital_preset: Dict[str, Any],
                      output_path: str,
                      frame_data_list: Optional[List[str]] = None) -> Optional[str]:
    """
    Saves the modified Vital preset as an uncompressed JSON file to the given output_path.

    Args:
        vital_preset (Dict[str, Any]): The modified Vital preset data.
        output_path (str): Full path where the preset should be saved (.vital extension).
        frame_data_list (Optional[List[str]]): Optional list of 3 wavetable frames (base64 strings).

    Returns:
        Optional[str]: The output file path if successful, None otherwise.
    """
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 🔥 Move top-level parameters inside "settings"
        vital_preset.setdefault("settings", {})
        params_to_move = ["osc_1_level", "osc_1_pan", "reverb_dry_wet", "chorus_dry_wet", "pitch_wheel"]
        for param in params_to_move:
            if param in vital_preset:
                vital_preset["settings"][param] = vital_preset.pop(param)

        vital_preset["settings"].setdefault("modulations", [])

        json_data: str = json.dumps(vital_preset, indent=2)

        if isinstance(frame_data_list, list) and len(frame_data_list) == 3:
            json_data = replace_three_wavetables(json_data, frame_data_list)
            logging.info("✅ Replaced wavetables in the preset.")
        else:
            logging.warning("⚠️ No valid wave_data provided or not exactly 3 frames.")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        logging.info(f"✅ Successfully saved Vital preset to: {output_path}")
        return output_path

    except OSError as e:
        logging.error(f"❌ File error when saving Vital preset: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON encoding error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error in save_vital_preset: {e}")

    return None
