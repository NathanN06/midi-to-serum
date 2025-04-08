import base64
import numpy as np
from typing import Dict, Any
from config import DEFAULT_FRAME_SIZE  # Make sure this is defined
import re
from typing import List, Dict, Any


def virus_shape_number_to_name(value: int) -> str:
    if value == 0:
        return "sine"
    elif value == 1:
        return "triangle"
    elif 2 <= value <= 63:
        return f"custom_{value - 1}"  # simpler: 2 → custom_1
    else:
        return "custom_undefined"
    
def virus_shape_number_to_name_osc2(value: int) -> str:
    if value == 0:
        return "sine"
    elif value == 1:
        return "triangle"
    elif 2 <= value <= 63:
        return f"custom_{value - 1}"  # simpler: 2 → custom_1
    else:
        return "custom_undefined"

def virus_shape_number_to_name_osc3(value: int) -> str:
    if value == 0:
        return "off"
    elif value == 1:
        return "slave"
    elif value == 2:
        return "saw"
    elif value == 3:
        return "pulse"
    elif value == 4:
        return "sine"
    elif value == 5:
        return "triangle"
    elif 6 <= value <= 67:
        return f"custom_{value - 5}"  # Wave 3 starts at index 6
    else:
        return "custom_undefined"

def generate_osc1_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Osc1_Wave_Select", 0)
    shape = virus_shape_number_to_name(shape_value)

    velocity = 0.8
    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase)
    elif shape == "triangle":
    # Triangle wave derived from sine
        waveform = (2/np.pi) * np.arcsin(np.sin(phase))
    else:
        waveform = np.sin(phase)  # fallback

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")

def generate_osc2_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Osc2_Wave_Select", 0)
    shape = virus_shape_number_to_name(shape_value)

    velocity = 0.8
    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase)
    elif shape == "triangle":
    # Triangle wave derived from sine
        waveform = (2/np.pi) * np.arcsin(np.sin(phase))
    else:
        waveform = np.sin(phase)  # fallback to sine

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")

def generate_osc3_frame_from_sysex(virus_params: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE) -> str:
    shape_value = virus_params.get("Osc3_Wave_Select", 0)
    shape = virus_shape_number_to_name_osc3(shape_value)

    # Treat 'off' and 'slave' as no waveform (OSC3 disabled or sync mode)
    if shape in ("off", "slave"):
        return ""

    velocity = 0.8
    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase)
    elif shape == "triangle":
        waveform = (2 / np.pi) * np.arcsin(np.sin(phase))  # Symmetrical triangle wave
    elif shape == "saw":
        waveform = 2 * (phase / (2 * np.pi)) - 1  # Linear ramp from -1 to 1
    elif shape == "pulse":
        waveform = np.where(np.sin(phase) >= 0, 1.0, -1.0)  # Hard pulse wave
    elif shape.startswith("custom_"):
        waveform = np.sin(phase) * np.cos(phase * 2)  # Placeholder for Virus wavetables
    else:
        waveform = np.sin(phase)  # Fallback to sine

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

        # OSC3 is OFF if Wave_Select is 0 ("Off") or 1 ("Slave")
        osc3_wave_select = virus_params.get("Osc3_Wave_Select", 0)
        preset["settings"]["osc_3_on"] = 0.0 if osc3_wave_select in (0, 1) else 1.0

    # Convert back to JSON string before regex replacement
    updated_json = json.dumps(preset)

    # Find and replace wave_data blocks
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, updated_json))

    if len(matches) < 3:
        print(f"⚠️ Only found {len(matches)} 'wave_data' entries — expected at least 3.")
        return updated_json

    # Replace OSC1 and OSC2 wave_data
    for i in reversed(range(2)):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        updated_json = updated_json[:start] + replacement + updated_json[end:]

    # Only replace OSC3 wavetable if it's on
    if preset["settings"]["osc_3_on"] == 1.0:
        start, end = matches[2].span()
        replacement = f'"wave_data": "{frame_data_list[2]}"'
        updated_json = updated_json[:start] + replacement + updated_json[end:]

    print("✅ Replaced wave_data. OSC2 = ON, OSC3 =", preset["settings"]["osc_3_on"])
    return updated_json