# virus_lfo_generator.py

import numpy as np
from typing import Dict, Any
from config import DEFAULT_LFO_FRAME_SIZE
  # Ensure this constant is defined


def virus_lfo_shape_number_to_name(value: int) -> str:
    if value == 0:
        return "sine"
    elif value == 1:
        return "triangle"
    elif value == 2:
        return "saw"
    elif value == 3:
        return "square"
    elif value == 4:
        return "sample_and_hold"
    elif value == 5:
        return "sample_and_glide"
    elif 6 <= value <= 63:
        return f"wave_{value}"  # because wave_3 starts at value=6
    else:
        return "unknown"


def generate_lfo_shape_from_sysex(virus_params: Dict[str, Any], lfo_number: int = 1, frame_size: int = DEFAULT_LFO_FRAME_SIZE) -> Dict[str, Any]:
    """
    Generates an LFO shape for Vital from Virus LFO shape parameter, in Vital-compatible format.
    """
    param_key = f"Lfo{lfo_number}_Shape"
    shape_value = virus_params.get(param_key, 0)
    shape_name = virus_lfo_shape_number_to_name(shape_value)

    x = np.linspace(0, 1, frame_size)

    if shape_name == "sine":
        y = np.sin(2 * np.pi * x)
    elif shape_name == "triangle":
        y = 2 * np.abs(2 * (x % 1) - 1) - 1
    elif shape_name == "saw":
        y = 2 * (x % 1) - 1
    elif shape_name == "square":
        y = np.sign(np.sin(2 * np.pi * x))
    elif shape_name == "sample_and_hold":
        block_size = frame_size // 8
        y = np.repeat(np.random.uniform(-1, 1, 8), block_size)
    elif shape_name == "sample_and_glide":
        points = np.random.uniform(-1, 1, 8)
        y = np.interp(x, np.linspace(0, 1, 8), points)
    elif shape_name.startswith("wave_"):
        y = 2 * np.abs(2 * (x % 1) - 1) - 1
    else:
        y = np.zeros(frame_size)

    # Normalize y to [0, 1] for Vital
    y = (y + 1) / 2
    points = [val for pair in zip(x, y) for val in pair]  # [x0, y0, x1, y1, ...]
    powers = [0.0] * frame_size

    return {
        "name": f"Virus_LFO_{shape_name}",
        "num_points": frame_size,
        "points": points,
        "powers": powers,
        "smooth": True
    }


def inject_lfo1_shape_from_sysex(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    shape_dict = generate_lfo_shape_from_sysex(virus_params, lfo_number=1)

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    while len(preset["settings"]["lfos"]) < 1:
        preset["settings"]["lfos"].append({})

    preset["settings"]["lfos"][0] = shape_dict
    print(f"🎛️ Injected LFO1 shape → {shape_dict['name']}")



def inject_lfo2_shape_from_sysex(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    shape_dict = generate_lfo_shape_from_sysex(virus_params, lfo_number=2)

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    while len(preset["settings"]["lfos"]) < 2:
        preset["settings"]["lfos"].append({})

    preset["settings"]["lfos"][1] = shape_dict
    print(f"🎛️ Injected LFO2 shape → {shape_dict['name']}")



def inject_lfo3_shape_from_sysex(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    shape_dict = generate_lfo_shape_from_sysex(virus_params, lfo_number=3)

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    while len(preset["settings"]["lfos"]) < 3:
        preset["settings"]["lfos"].append({})

    preset["settings"]["lfos"][2] = shape_dict
    print(f"🎛️ Injected LFO3 shape → {shape_dict['name']}")
