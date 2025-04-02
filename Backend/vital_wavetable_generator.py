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


def replace_two_wavetables(json_data: str, frame_data_list: List[str]) -> str:
    """
    Replaces the first two "wave_data" entries in a Vital preset JSON with the provided base64-encoded wavetable frames.

    Args:
        json_data (str): The raw JSON string from the .vital preset.
        frame_data_list (List[str]): List of two base64-encoded wavetable frames.

    Returns:
        str: Updated JSON string with modified wave_data fields.
    """
    import re

    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, json_data))

    if len(matches) < 2:
        print(f"⚠️ Only found {len(matches)} 'wave_data' entries — expected at least 2.")
        return json_data

    result = json_data
    # Process replacements in reverse to avoid shifting match positions
    for i in reversed(range(2)):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        result = result[:start] + replacement + result[end:]

    print("✅ Replaced the first two wave_data entries.")
    return result
