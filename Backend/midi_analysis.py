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


import statistics

def compute_midi_stats(data):
    notes = data.get("notes", [])
    velocities = [n["velocity"] for n in notes]
    pitches = [n["pitch"] for n in notes]

    avg_pitch = sum(pitches) / len(pitches) if pitches else 60
    pitch_range = max(pitches) - min(pitches) if pitches else 0
    avg_velocity = sum(velocities) / len(velocities) if velocities else 80
    velocity_range = max(velocities) - min(velocities) if velocities else 0
    velocity_std = statistics.stdev(velocities) if len(velocities) > 1 else 0
    note_density = len(notes) / (max(n["end"] for n in notes) - min(n["start"] for n in notes)) if notes else 0
    max_velocity = max(velocities) if velocities else 127
    min_velocity = min(velocities) if velocities else 0

    return {
        "avg_pitch": avg_pitch,
        "pitch_range": pitch_range,
        "avg_velocity": avg_velocity,
        "velocity_range": velocity_range,
        "velocity_std": velocity_std,
        "note_density": note_density,
        "max_velocity": max_velocity,
        "min_velocity": min_velocity
    }
