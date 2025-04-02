import logging
from typing import Any, Dict, List

from midi_analysis import compute_midi_stats
from config import (
    DEFAULT_STACK_MODE,
    STACK_MODE_RULES,
    DEFAULT_DETUNE_POWER,
    DEFAULT_RANDOM_PHASE,
    DEFAULT_STACK_STYLE,
    MAX_UNISON_VOICES
)



def determine_oscillator_stack(midi_data):
    """Determine the best oscillator stack setting based on MIDI note intervals."""
    notes = sorted(set(note["pitch"] for note in midi_data.get("notes", [])))  # Get unique sorted pitches

    if len(notes) == 0:
        return DEFAULT_STACK_MODE  # Use default from config

    intervals = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]

    if len(notes) == 1:
        return STACK_MODE_RULES["single_note"]
    elif len(notes) == 2:
        if 12 in intervals:
            return STACK_MODE_RULES["octave"]
        elif 24 in intervals:
            return STACK_MODE_RULES["double_octave"]
        elif 7 in intervals:
            return STACK_MODE_RULES["power_chord"]
        elif 5 in intervals:
            return STACK_MODE_RULES["minor_chord"]
    elif len(notes) == 3:
        if 12 in intervals and 7 in intervals:
            return STACK_MODE_RULES["double_power_chord"]
        elif {4, 3, 7}.issubset(set(intervals)):
            return STACK_MODE_RULES["major_chord"]
        elif {3, 4, 7}.issubset(set(intervals)):
            return STACK_MODE_RULES["minor_chord"]
    elif len(notes) > 3:
        if max(intervals) > 24:
            return STACK_MODE_RULES["wide_interval_24"]
        elif max(intervals) > 12:
            return STACK_MODE_RULES["wide_interval_12"]
        elif all(i % 2 == 0 for i in intervals):
            return STACK_MODE_RULES["odd_harmonics"]
        else:
            return STACK_MODE_RULES["harmonics"]

    return DEFAULT_STACK_MODE  # Fallback case


def derive_full_oscillator_params(stats: Dict[str, float], osc_index: int) -> Dict[str, Any]:
    """
    Derive a full set of oscillator parameters for a given oscillator based on MIDI stats.

    Args:
        stats (Dict[str, float]): Dictionary with keys 'avg_pitch', 'avg_velocity',
                                  'pitch_range', and 'note_density'.
        osc_index (int): Oscillator index (1, 2, or 3).

    Returns:
        Dict[str, Any]: A dictionary mapping Vital oscillator parameter names to computed values.
    """
    avg_velocity = stats["avg_velocity"]
    pitch_range = stats["pitch_range"]
    note_density = stats["note_density"]
    avg_pitch = stats["avg_pitch"]

    # Dynamically derived values
    unison_voices = float(min(MAX_UNISON_VOICES, int(1 + note_density / 5)))
    unison_detune = min(20.0, pitch_range * 0.8)
    phase = (avg_pitch % 12) / 12.0
    tune = (avg_pitch - 60) % 12
    frame_spread = min(1.0, pitch_range / 12.0)
    spectral_spread = min(1.0, pitch_range / 24.0)
    distortion_spread = min(1.0, avg_velocity)
    morph_amount = min(1.0, pitch_range / 32.0 + 0.3)
    stereo_spread = min(1.0, 0.5 + note_density / 10.0)
    blend = min(1.0, 0.6 + avg_velocity * 0.4)

    return {
        f"osc_{osc_index}_destination": 0.0,
        f"osc_{osc_index}_detune_power": DEFAULT_DETUNE_POWER,
        f"osc_{osc_index}_detune_range": min(4.0, pitch_range / 10.0 + 1.0),
        f"osc_{osc_index}_distortion_amount": 0.5,
        f"osc_{osc_index}_distortion_phase": 0.5,
        f"osc_{osc_index}_distortion_spread": distortion_spread,
        f"osc_{osc_index}_distortion_type": 0.0,
        f"osc_{osc_index}_frame_spread": frame_spread,
        f"osc_{osc_index}_level": min(1.0, avg_velocity + 0.1 * osc_index),
        f"osc_{osc_index}_midi_track": 1.0,
        f"osc_{osc_index}_on": 1.0,
        f"osc_{osc_index}_pan": -0.5 + osc_index * 0.5,
        f"osc_{osc_index}_phase": phase,
        f"osc_{osc_index}_random_phase": DEFAULT_RANDOM_PHASE,
        f"osc_{osc_index}_smooth_interpolation": 0.0,
        f"osc_{osc_index}_spectral_morph_amount": morph_amount,
        f"osc_{osc_index}_spectral_morph_spread": spectral_spread,
        f"osc_{osc_index}_spectral_morph_type": 0.0,
        f"osc_{osc_index}_spectral_unison": 0.0,
        f"osc_{osc_index}_stack_style": DEFAULT_STACK_STYLE,
        f"osc_{osc_index}_stereo_spread": stereo_spread,
        f"osc_{osc_index}_transpose": 0.0,
        f"osc_{osc_index}_transpose_quantize": 0.0,
        f"osc_{osc_index}_tune": tune,
        f"osc_{osc_index}_unison_blend": blend,
        f"osc_{osc_index}_unison_detune": unison_detune,
        f"osc_{osc_index}_unison_voices": unison_voices,
        f"osc_{osc_index}_view_2d": 1.0,
        f"osc_{osc_index}_wave_frame": 0.0,
    }


def apply_full_oscillator_params_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Compute MIDI stats and update the preset's oscillator settings dynamically for
    oscillators 1, 2, and 3.
    
    Args:
        preset (Dict[str, Any]): The Vital preset.
        midi_data (Dict[str, Any]): Parsed MIDI data.
    """
    stats = compute_midi_stats(midi_data)
    for osc_index in range(1, 4):
        params = derive_full_oscillator_params(stats, osc_index)
        preset["settings"].update(params)
    logging.info("✅ Full dynamic oscillator parameters applied based on MIDI data.")
