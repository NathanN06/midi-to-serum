from midi_parser import parse_midi  # ✅ Import the function instead of redefining it
from typing import Dict, List, Optional, Any
from config import (
    DEFAULT_MIDI_STATS,
    DEFAULT_FRAME_COUNT,
    FRAME_SCALING_FACTOR,
    DEFAULT_FRAME_SIZE
)


def estimate_frame_count(midi_data, frame_size=DEFAULT_FRAME_SIZE):
    """
    Estimate the number of frames required for a MIDI file
    based on note durations and divisions.
    """
    notes = midi_data.get("notes", [])
    if not notes:
        return DEFAULT_FRAME_COUNT  # Use config default

    total_duration = max(note["end"] for note in notes) if notes else 1
    num_frames = max(DEFAULT_FRAME_COUNT, int(total_duration * FRAME_SCALING_FACTOR))  # Use config scaling factor
    return num_frames


def compute_midi_stats(midi_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Compute MIDI statistics (average pitch, average velocity, pitch range, note density)
    from the MIDI data.
    
    Args:
        midi_data (Dict[str, Any]): Parsed MIDI data.
        
    Returns:
        Dict[str, float]: A dictionary containing 'avg_pitch', 'avg_velocity',
                          'pitch_range', and 'note_density'.
    """
    notes = midi_data.get("notes", [])
    if not notes:
        return DEFAULT_MIDI_STATS  # Use fallback values from config

    pitches = [float(n["pitch"]) for n in notes]
    velocities = [float(n["velocity"]) / 127.0 for n in notes]
    total_time = max(n["end"] for n in notes)

    avg_pitch = sum(pitches) / len(pitches)
    avg_velocity = sum(velocities) / len(velocities)
    pitch_range = max(pitches) - min(pitches)
    note_density = len(notes) / total_time if total_time > 0 else 1.0

    return {
        "avg_pitch": avg_pitch,
        "avg_velocity": avg_velocity,
        "pitch_range": pitch_range,
        "note_density": note_density
    }
