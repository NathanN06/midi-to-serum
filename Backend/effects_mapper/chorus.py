from typing import Dict, Any

def virus_chorus_mode_to_name(value: int) -> str:
    """Map Virus chorus mode numbers to readable names (for logging)."""
    modes = {
        0: "Off",
        1: "Classic",
        2: "Vintage",
        3: "Hyper",
        4: "Air",
        5: "Vibrato",
        6: "Rotary"
    }
    return modes.get(value, f"Unknown_{value}")

def inject_chorus_settings(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    """Injects chorus parameters from Virus into a Vital preset dictionary."""
    mode = virus_params.get("Chorus_Mode", 0)
    settings = preset.setdefault("settings", {})

    # Turn chorus ON only if Chorus_Mode is greater than 0
    if mode > 0:
        settings["chorus_on"] = 1

    # Logging/debug only
    mode_name = virus_chorus_mode_to_name(mode)
    print(f"🎧 Chorus Mode = {mode_name} ({mode}) → {'ON' if mode > 0 else 'OFF'}")
