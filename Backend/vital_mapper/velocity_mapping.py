
from midi_analysis import compute_midi_stats

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
