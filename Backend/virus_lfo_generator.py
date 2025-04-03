# virus_lfo_generator.py

import numpy as np
from typing import Dict, Any
from config import DEFAULT_LFO_FRAME_SIZE
  # Ensure this constant is defined


def virus_lfo_shape_number_to_name(value: int) -> str:
    if value < 16:
        return "sine"
    elif value < 32:
        return "square"
    elif value < 48:
        return "saw"
    elif value < 64:
        return "triangle"
    elif value < 80:
        return "ramp"
    elif value < 96:
        return "inv_ramp"
    else:
        return "noise"


def generate_lfo_shape_from_sysex(virus_params: Dict[str, Any], lfo_number: int = 1, frame_size: int = DEFAULT_LFO_FRAME_SIZE) -> Dict[str, Any]:
    """
    Generates a simple LFO shape for Vital based on Virus parameter value.
    """
    param_key = f"Lfo{lfo_number}_Shape"
    shape_value = virus_params.get(param_key, 0)
    shape_name = virus_lfo_shape_number_to_name(shape_value)

    x = np.linspace(0, 1, frame_size)

    if shape_name == "sine":
        y = np.sin(2 * np.pi * x)
    elif shape_name == "square":
        y = np.sign(np.sin(2 * np.pi * x))
    elif shape_name == "saw":
        y = 2 * (x % 1) - 1
    elif shape_name == "triangle":
        y = 2 * np.abs(2 * (x % 1) - 1) - 1
    elif shape_name == "ramp":
        y = x ** 2
    elif shape_name == "inv_ramp":
        y = 1 - np.sqrt(x)
    elif shape_name == "noise":
        y = np.random.rand(frame_size) * 2 - 1
    else:
        y = np.zeros(frame_size)

    # Normalize to [0, 1] for Vital
    y = (y + 1) / 2
    points = [val for pair in zip(x, y) for val in pair]
    powers = [0.0] * frame_size

    return {
        "name": f"Virus_LFO_{shape_name}",
        "num_points": frame_size,
        "points": points,
        "powers": powers,
        "smooth": True
    }


def inject_lfo1_shape_from_sysex(virus_value: int, preset: Dict[str, Any]) -> None:
    """
    Handler to inject LFO1 shape based on Lfo1_Shape virus parameter.
    """
    virus_params = {"Lfo1_Shape": virus_value}
    shape_dict = generate_lfo_shape_from_sysex(virus_params, lfo_number=1)

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    # Ensure LFO1 slot exists
    while len(preset["settings"]["lfos"]) < 1:
        preset["settings"]["lfos"].append({})

    preset["settings"]["lfos"][0] = shape_dict
    print(f"🎛️ Injected LFO1 shape → {shape_dict['name']}")


def inject_lfo2_shape_from_sysex(virus_value: int, preset: Dict[str, Any]) -> None:
    """
    Handler to inject LFO2 shape based on Lfo2_Shape virus parameter.
    """
    virus_params = {"Lfo2_Shape": virus_value}
    shape_dict = generate_lfo_shape_from_sysex(virus_params, lfo_number=2)

    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    # Ensure lfos[1] (second slot) exists
    while len(preset["settings"]["lfos"]) < 2:
        preset["settings"]["lfos"].append({})

    preset["settings"]["lfos"][1] = shape_dict
    print(f"🎛️ Injected LFO2 shape → {shape_dict['name']}")
