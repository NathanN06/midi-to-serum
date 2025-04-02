import base64
import numpy as np
from typing import Dict, Any
from config import DEFAULT_FRAME_SIZE  # Make sure this is defined

def virus_shape_number_to_name(value: int) -> str:
    if value < 32:
        return "sine"
    elif value < 64:
        return "triangle"
    elif value < 96:
        return "saw"
    else:
        return "folded"

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

import re

def replace_single_wavetable(json_data: str, frame_data: str) -> str:
    """
    Replaces the first "wave_data" entry in a Vital preset JSON with the provided base64-encoded wavetable frame.

    Args:
        json_data (str): The raw JSON string from the .vital preset.
        frame_data (str): Base64-encoded wavetable frame to insert.

    Returns:
        str: Updated JSON string with the modified wave_data field.
    """
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    match = re.search(pattern, json_data)

    if not match:
        print("⚠️ No 'wave_data' entry found in the preset.")
        return json_data

    start, end = match.span()
    replacement = f'"wave_data": "{frame_data}"'
    updated = json_data[:start] + replacement + json_data[end:]

    print("✅ Replaced the first wave_data entry.")
    return updated
