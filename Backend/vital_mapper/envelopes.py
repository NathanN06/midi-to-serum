from typing import Any, Dict, List, Optional

# MIDI analysis
from midi_analysis import compute_midi_stats

# Envelope config constants
from config import (
    DEFAULT_ADSR,
    ENVELOPE_ATTACK_MULTIPLIER,
    ENVELOPE_ATTACK_MAX,
    ENVELOPE_DECAY_MULTIPLIER,
    ENVELOPE_DECAY_MAX,
    ENVELOPE_RELEASE_MULTIPLIER,
    ENVELOPE_RELEASE_MAX,
    ENV2_ATTACK_SCALE,
    ENV2_DECAY_SCALE,
    ENV2_SUSTAIN_SCALE,
    ENV2_RELEASE_SCALE,
    ENV_ATTACK_MIN,
    ENV_ATTACK_MAX,
    ENV_DECAY_MIN,
    ENV_DECAY_MAX,
    ENV_RELEASE_MIN,
    ENV_RELEASE_MAX,
    ENV_DELAY_MAX,
    ENV_HOLD_MIN,
    ENV_HOLD_MAX,
)


def add_envelopes_to_preset(preset: Dict[str, Any], notes: List[Dict[str, Any]]) -> None:
    """
    Adds ADSR envelope settings to the Vital preset based on MIDI note characteristics.
    If no notes are provided, uses the default ADSR settings from config.

    Args:
        preset (Dict[str, Any]): The Vital preset dictionary to update.
        notes (List[Dict[str, Any]]): List of MIDI note dictionaries.
    """
    if not notes:
        print("⚠️ No notes found. Using default envelope settings.")
        preset.update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Compute average note length (used to approximate attack, decay, and release times)
    avg_note_length: float = sum(n["end"] - n["start"] for n in notes) / len(notes)

    # Compute average velocity and derive sustain level (normalize velocity from 0-127 to 0-1)
    avg_velocity: float = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level: float = (avg_velocity / 127.0) if avg_velocity > 0 else 0.5

    # Calculate envelope parameters using centralized multipliers and caps.
    attack_time: float = min(avg_note_length * ENVELOPE_ATTACK_MULTIPLIER, ENVELOPE_ATTACK_MAX)
    decay_time: float = min(avg_note_length * ENVELOPE_DECAY_MULTIPLIER, ENVELOPE_DECAY_MAX)
    release_time: float = min(avg_note_length * ENVELOPE_RELEASE_MULTIPLIER, ENVELOPE_RELEASE_MAX)

    # Update ENV1 settings
    preset.update({
        "env_1_attack":  attack_time,
        "env_1_decay":   decay_time,
        "env_1_sustain": sustain_level,
        "env_1_release": release_time
    })
    print(f"✅ ENV1: A={attack_time:.2f}, D={decay_time:.2f}, S={sustain_level:.2f}, R={release_time:.2f}")

    # Apply similar scaling for ENV2 with different multipliers
    preset.update({
        "env_2_attack":  attack_time * ENV2_ATTACK_SCALE,
        "env_2_decay":   decay_time * ENV2_DECAY_SCALE,
        "env_2_sustain": sustain_level * ENV2_SUSTAIN_SCALE,
        "env_2_release": release_time * ENV2_RELEASE_SCALE
    })
    print("✅ ENV2 applied with slightly different scaling.")


def apply_dynamic_env_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Dynamically adjusts Envelope 1, 2, and 3 based on MIDI note data.

    - ENV1: Amplitude (volume envelope)
    - ENV2: Filter cutoff envelope
    - ENV3: Oscillator shape/pitch envelope
    
    Each envelope's parameters are calculated based on note length, note density,
    and MIDI CC data (e.g., Expression/Mod Wheel influence).
    """
    preset.setdefault("settings", {})
    notes: List[Dict[str, Any]] = midi_data.get("notes", [])
    ccs: List[Dict[str, Any]] = midi_data.get("control_changes", [])

    if not notes:
        print("⚠️ No MIDI notes detected. Using default envelopes.")
        preset["settings"].update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Compute average note length and average velocity.
    avg_note_length: float = sum(n["end"] - n["start"] for n in notes) / len(notes)
    avg_velocity: float = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level: float = min(1.0, avg_velocity / 127.0)

    # Determine note density (using average gap between notes).
    if len(notes) > 1:
        time_gaps: List[float] = [notes[i+1]["start"] - notes[i]["end"] for i in range(len(notes) - 1)]
        avg_gap: float = sum(time_gaps) / len(time_gaps)
    else:
        avg_gap = avg_note_length

    note_density_factor: float = max(0.2, min(1.0, 1.0 - (avg_gap / 2.0)))

    # Check for CC influence (Expression = CC11, Mod Wheel = CC1)
    expression_value: Optional[float] = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 11), None)
    mod_wheel_value: Optional[float] = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 1), None)

    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Ensures value stays within the specified range."""
        return max(min_val, min(value, max_val))

    # ENV1: Amplitude Envelope (Volume)
    env1_attack: float = clamp(avg_note_length ** 1.2 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env1_decay: float = clamp(avg_note_length * 0.5 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env1_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.5), 0, 1)
    env1_release: float = clamp(avg_note_length * 0.8 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env1_delay: float = clamp(avg_gap * 0.5, 0, ENV_DELAY_MAX)
    env1_hold: float = clamp(avg_note_length * 1.5 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    preset["settings"].update({
        "env_1_attack": env1_attack,
        "env_1_decay": env1_decay,
        "env_1_sustain": env1_sustain,
        "env_1_release": env1_release,
        "env_1_delay": env1_delay,
        "env_1_hold": env1_hold,
    })
    print(f"✅ ENV1 → A={env1_attack:.2f}s, D={env1_decay:.2f}s, S={env1_sustain:.2f}, R={env1_release:.2f}s, H={env1_hold:.2f}, Delay={env1_delay:.2f}")

    # ENV2: Filter Envelope
    env2_attack: float = clamp(avg_note_length ** 1.1 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env2_decay: float = clamp(avg_note_length * 0.7 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env2_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.4), 0, 1)
    env2_release: float = clamp(avg_note_length * 1.2 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env2_delay: float = clamp(avg_gap * 0.4, 0, ENV_DELAY_MAX)
    env2_hold: float = clamp(avg_note_length * 1.2 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    if mod_wheel_value is not None:
        env2_sustain = clamp(env2_sustain * (0.7 + mod_wheel_value * 0.3), 0, 1)

    preset["settings"].update({
        "env_2_attack": env2_attack,
        "env_2_decay": env2_decay,
        "env_2_sustain": env2_sustain,
        "env_2_release": env2_release,
        "env_2_delay": env2_delay,
        "env_2_hold": env2_hold,
    })
    print(f"✅ ENV2 → A={env2_attack:.2f}s, D={env2_decay:.2f}s, S={env2_sustain:.2f}, R={env2_release:.2f}s, H={env2_hold:.2f}, Delay={env2_delay:.2f}")

    # ENV3: Oscillator Morphing/Pitch Envelope
    env3_attack: float = clamp(avg_note_length ** 1.15 * note_density_factor, ENV_ATTACK_MIN, ENV_ATTACK_MAX)
    env3_decay: float = clamp(avg_note_length * 0.6 * note_density_factor, ENV_DECAY_MIN, ENV_DECAY_MAX)
    env3_sustain: float = clamp(sustain_level * (1.0 - note_density_factor * 0.3), 0, 1)
    env3_release: float = clamp(avg_note_length * 1.5 * note_density_factor, ENV_RELEASE_MIN, ENV_RELEASE_MAX)
    env3_delay: float = clamp(avg_gap * 0.3, 0, ENV_DELAY_MAX)
    env3_hold: float = clamp(avg_note_length * 1.8 * note_density_factor, ENV_HOLD_MIN, ENV_HOLD_MAX)

    preset["settings"].update({
        "env_3_attack": env3_attack,
        "env_3_decay": env3_decay,
        "env_3_sustain": env3_sustain,
        "env_3_release": env3_release,
        "env_3_delay": env3_delay,
        "env_3_hold": env3_hold,
    })
    print(f"✅ ENV3 → A={env3_attack:.2f}s, D={env3_decay:.2f}s, S={env3_sustain:.2f}, R={env3_release:.2f}s, H={env3_hold:.2f}, Delay={env3_delay:.2f}")

    print("✅ Envelope modulations added: ENV2 → Filter, ENV3 → Warp")
