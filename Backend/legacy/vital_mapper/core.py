


import os
import re
import json
import copy
import logging
from typing import Any, Dict, List, Optional, Tuple
import zlib
import base64
import numpy as np
import random


# Local utility functions (make sure to import based on the new structure)
from midi_parser import parse_midi
from midi_analysis import compute_midi_stats
from .velocity_mapping import map_velocity_to_macros_and_volume
from .modulations import apply_modulations_to_preset, apply_macro_controls_to_preset
from .envelopes import apply_dynamic_env_to_preset
from .oscillators import apply_full_oscillator_params_to_preset, determine_oscillator_stack
from .wavetables import (
    get_shape_for_osc1,
    get_shape_for_osc2,
    get_shape_for_osc3,
    generate_osc1_frame,
    generate_osc2_frame,
    generate_osc3_frame,
)
from .filters_fx import apply_filters_to_preset, apply_effects_to_preset
from .lfos import (
    build_lfo_from_cc,
    get_best_lfo_targets,
)
from config import (
    DEFAULT_FRAME_SIZE,
    PRESET_FILE_EXTENSION,
    DEFAULT_KEYFRAMES,
    DEFAULT_WAVE_DATA
)

# Optional, depending on file location
from .sample_loader import enable_sample_in_preset  # If you isolate this function

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

    except Exception as e:
        logging.error(f"❌ Failed to load default Vital preset: {e}")
        return None


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

