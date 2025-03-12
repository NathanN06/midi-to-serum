# midi_analysis.py
from midi_parser import parse_midi  # ✅ Import the function instead of redefining it

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
