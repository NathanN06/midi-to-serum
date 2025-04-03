import base64
import numpy as np
from typing import Dict, Any
from config import DEFAULT_FRAME_SIZE  # Make sure this is defined
import re
from typing import List, Dict, Any


def virus_shape_number_to_name(value: int) -> str:
    if value < 32:
        return "sine"
    elif value < 64:
        return "triangle"
    elif value < 96:
        return "saw"
    else:
        return "folded"
    
def virus_shape_number_to_name_osc2(value: int) -> str:
    if value < 26:
        return "sine"
    elif value < 52:
        return "triangle"
    elif value < 78:
        return "saw"
    elif value < 102:
        return "folded"
    elif value < 114:
        return "harmonic_buzz"
    else:
        return "chaotic"

def virus_shape_number_to_name_osc3(value: int) -> str:
    if value < 32:
        return "sine"
    elif value < 64:
        return "triangle"
    elif value < 96:
        return "folded"
    else:
        return "dark_buzz"  # optional, or fallback to triangle


def generate_osc1_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Osc1_Shape", 0)
    shape = virus_shape_number_to_name(shape_value)

    velocity = 0.8  # Fixed gain multiplier
    pitch_range = 24  # Assumed complexity
    note_density = 4.0  # Static, no MIDI
    modwheel = virus_params.get("Modulation_Wheel", 64) / 127.0  # Default to halfway

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase + modwheel * np.sin(phase * 2))
    elif shape == "saw":
        max_h = int(6 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase)
            for h in range(1, max_h)
        ], axis=0)
    elif shape == "triangle":
        base = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        harmonic = 0.3 * np.sin(phase * 3 + modwheel * 2)
        waveform = base + harmonic
    elif shape == "folded":
        folded = np.tanh(2.5 * np.sin(phase + modwheel * np.pi))
        noise = 0.1 * np.sin(phase * 3)
        waveform = folded + noise
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")

def generate_osc2_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Osc2_Shape", 0)
    shape = virus_shape_number_to_name_osc2(shape_value)  # Use the OSC2-specific mapping

    velocity = 0.8  # Fixed gain multiplier
    pitch_range = 24  # Assume moderate harmonic complexity
    note_density = 4.0  # Placeholder since we're not using MIDI data
    modwheel = virus_params.get("Modulation_Wheel", 64) / 127.0

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "saw":
        max_h = int(8 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase)
            for h in range(1, max_h)
        ], axis=0)
    elif shape == "harmonic_buzz":
        waveform = np.sum([
            np.sin(h * phase) * (1.0 / (h ** 0.9))
            for h in range(1, 20)
        ], axis=0)
        waveform += 0.1 * np.sin(phase * 5)
    elif shape == "chaotic":
        fm = np.sin(phase * (2 + note_density)) * 0.6
        waveform = np.tanh(np.sin(phase * 2 + fm) + np.cos(phase * 3))
    elif shape == "triangle":
        waveform = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
    elif shape == "sine":
        waveform = np.sin(phase + modwheel * np.sin(phase * 2))
    elif shape == "folded":
        folded = np.tanh(2.5 * np.sin(phase + modwheel * np.pi))
        noise = 0.1 * np.sin(phase * 3)
        waveform = folded + noise
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")

def generate_osc3_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Suboscillator_Shape", 0)
    shape = virus_shape_number_to_name_osc3(shape_value)

    velocity = 0.8  # Fixed gain multiplier
    modwheel = virus_params.get("Modulation_Wheel", 64) / 127.0

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        vibrato = 0.05 * np.sin(phase * 6)
        waveform = np.sin(phase + vibrato)
    elif shape == "triangle":
        base = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        shimmer = 0.2 * np.sin(phase * 4)
        waveform = base + shimmer
    elif shape == "folded":
        base = np.tanh(3.0 * np.sin(phase + np.sin(phase * 3)))
        motion = 0.2 * np.sin(phase * 3 + modwheel * 2)
        waveform = base + motion
    elif shape == "dark_buzz":
        waveform = np.sum([
            np.sin(h * phase) * (1.0 / (h ** 1.2))
            for h in range(1, 15)
        ], axis=0)
        waveform *= np.exp(-phase / (2 * np.pi))  # mellow decay feel
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")

def replace_three_wavetables(json_data: str, frame_data_list: List[str], virus_params: Dict[str, Any]) -> str:
    """
    Replaces the first 3 "wave_data" entries in a Vital preset JSON with provided base64-encoded wavetable frames,
    and activates oscillator 2 and 3 conditionally based on Virus parameters.

    Args:
        json_data (str): The raw JSON string from the .vital preset.
        frame_data_list (List[str]): List of 3 base64-encoded wavetable frames.
        virus_params (dict): Parsed Virus parameter dictionary.

    Returns:
        str: Updated JSON string with modified wave_data fields and oscillator enable flags.
    """
    import re
    import json

    # Load the preset into a dict
    preset = json.loads(json_data)

    if "settings" in preset:
        # Always enable OSC2
        preset["settings"]["osc_2_on"] = 1.0

        # Conditionally enable OSC3 if it has meaningful shape or volume
        sub_shape = virus_params.get("Suboscillator_Shape", 0)
        sub_volume = virus_params.get("Suboscillator_Volume", 0)
        preset["settings"]["osc_3_on"] = 1.0 if sub_shape != 0 or sub_volume > 0 else 0.0

    # Convert back to JSON string before regex replacement
    updated_json = json.dumps(preset)

    # Find and replace wave_data blocks
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, updated_json))

    if len(matches) < 3:
        print(f"⚠️ Only found {len(matches)} 'wave_data' entries — expected at least 3.")
        return updated_json

    for i in reversed(range(3)):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        updated_json = updated_json[:start] + replacement + updated_json[end:]

    print("✅ Replaced 3 wave_data entries. OSC2 is ON. OSC3 =", preset["settings"]["osc_3_on"])
    return updated_json
