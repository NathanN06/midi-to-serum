# midi_analysis.py
from midi_parser import parse_midi  # ✅ Import the function instead of redefining it
from typing import Dict, List, Optional, Any


def estimate_frame_count(midi_data, frame_size=2048):
    """
    Estimate the number of frames required for a MIDI file
    based on note durations and divisions.
    """
    notes = midi_data.get("notes", [])
    if not notes:
        return 3  # Default to 3 frames if no notes exist

    total_duration = max(note["end"] for note in notes) if notes else 1
    num_frames = max(3, int(total_duration * 10))  # Adjust scaling factor as needed
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
        return {
            "avg_pitch": 60.0,
            "avg_velocity": 0.7,
            "pitch_range": 0.0,
            "note_density": 1.0
        }
    
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