from typing import Dict, Any

def set_filter_balance_mix(value: int, vital_preset: dict) -> None:
    """
    Adjusts filter_1_mix and filter_2_mix in Vital based on Virus Filter_Balance.
    - value: 0–127 → maps to -1 to +1
    """
    balance = (value - 64) / 64.0  # Normalize to -1 to +1
    f1_mix = max(0.0, 1.0 - balance)
    f2_mix = max(0.0, 1.0 + balance)

    vital_preset["settings"]["filter_1_mix"] = round(min(f1_mix, 1.0), 4)
    vital_preset["settings"]["filter_2_mix"] = round(min(f2_mix, 1.0), 4)


def set_pitch_bend_range_from_up_down(_, preset: Dict[str, Any], virus_params: Dict[str, int]):
    up = virus_params.get("Bender_Range_Up", 64)
    down = virus_params.get("Bender_Range_Down", 64)
    max_range = max(abs(up - 64), abs(down - 64))

    preset.setdefault("settings", {})
    preset["settings"]["pitch_bend_range"] = max_range
    print(f"🎯 Set pitch_bend_range = ±{max_range} semitones from up={up} down={down}")

def enable_filter_1(_, settings):
    settings["filter_1_on"] = 1.0

def enable_filter_2(_, settings):
    settings["filter_2_on"] = 1.0