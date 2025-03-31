import os
import json
import statistics
import mido
import random

def parse_midi(file_path):
    midi = mido.MidiFile(file_path)
    notes, control_changes, pitch_bends = [], [], []
    current_time = 0
    note_dict = {}

    for track in midi.tracks:
        current_time = 0
        for msg in track:
            current_time += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                note_dict[msg.note] = current_time
            elif msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):
                start = note_dict.pop(msg.note, None)
                if start is not None:
                    notes.append({
                        "pitch": msg.note,
                        "velocity": msg.velocity,
                        "start": start,
                        "end": current_time
                    })
            elif msg.type == "control_change":
                control_changes.append({
                    "controller": msg.control,
                    "value": msg.value,
                    "time": current_time
                })
            elif msg.type == "pitchwheel":
                pitch_bends.append({
                    "pitch": msg.pitch / 8192.0,
                    "time": current_time
                })

    return {"notes": notes, "control_changes": control_changes, "pitch_bends": pitch_bends}

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

    return {
        "avg_pitch": avg_pitch,
        "pitch_range": pitch_range,
        "avg_velocity": avg_velocity,
        "velocity_range": velocity_range,
        "velocity_std": velocity_std,
        "note_density": note_density
    }

# === RE-TUNED SHAPE FUNCTIONS ===

def get_shape_for_osc1(stats):
    """
    OSC1 → Attack Phase: Sharper = more aggression, smoother = more mellow.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_range = stats.get("velocity_range", 0)
    velocity_std = stats.get("velocity_std", 0)
    avg_pitch = stats.get("avg_pitch", 60)
    note_density = stats.get("note_density", 0.02)

    # High aggression
    if avg_velocity > 90 and velocity_range > 60:
        return "folded"

    # Fast-moving passages
    if note_density > 0.07:
        return "saw"

    # Dynamic expressiveness
    if velocity_std > 25:
        return "triangle"

    # Sparse or mellow
    if note_density < 0.015:
        return "sine"

    # Fallback based on pitch
    if avg_pitch > 75:
        return "saw"
    elif avg_pitch < 50:
        return "triangle"
    else:
        return "folded"


def get_shape_for_osc2(stats):
    """
    OSC2 → Harmonic Blend: richer or fuzzier based on pitch and note complexity.
    """
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    avg_pitch = stats.get("avg_pitch", 60)

    # Wild pitch motion = chaotic
    if pitch_range > 65:
        return "chaotic"

    # Busy textures = rich buzz
    if note_density > 0.05:
        return "harmonic_buzz"

    # Melodic and clear
    if avg_pitch > 68:
        return "triangle"

    # Simple, minimal range
    if pitch_range < 15:
        return "sine"

    # Mid-complexity fallback
    if pitch_range > 40:
        return "saw"
    else:
        return "triangle"


def get_shape_for_osc3(stats):
    """
    OSC3 → Final Release: smoother or noisier based on decay needs.
    No randomness — purely MIDI-driven.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_std = stats.get("velocity_std", 0)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    velocity_range = stats.get("velocity_range", 0)

    # Highly expressive: big swings in dynamics or sparse notes
    if velocity_std > 30 or (velocity_std > 25 and note_density < 0.02):
        return "triangle"

    # Rich, bright release needed for dense, varied pitch movement
    if note_density > 0.065 and pitch_range > 25:
        return "folded"

    # Low energy, soft touch
    if avg_velocity < 35 or velocity_range < 10:
        return "sine" if pitch_range < 50 else "triangle"

    # No dynamics at all, use shape based on pitch context
    if velocity_range == 0:
        if pitch_range > 60:
            return "folded"
        elif pitch_range < 10:
            return "triangle"
        else:
            return "saw"

    # Default deterministic fallback — based on pitch shape only
    if pitch_range > 40:
        return "folded"
    elif pitch_range > 20:
        return "triangle"
    else:
        return "sine"

def analyze_midi_folder(midi_dir, output_path="midi_shape_analysis.json"):
    results = []
    for filename in os.listdir(midi_dir):
        if filename.lower().endswith(".mid"):
            try:
                path = os.path.join(midi_dir, filename)
                data = parse_midi(path)
                stats = compute_midi_stats(data)
                result = {
                    "filename": filename,
                    "stats": stats,
                    "osc_shapes": {
                        "osc1": get_shape_for_osc1(stats),
                        "osc2": get_shape_for_osc2(stats),
                        "osc3": get_shape_for_osc3(stats)
                    }
                }
                results.append(result)
                print(f"✅ Processed {filename}")
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📁 Saved analysis to {output_path}")

# === USAGE ===
if __name__ == "__main__":
    midi_dir = "/Users/nathannguyen/Documents/Midi_To_serum/midi_files"
    analyze_midi_folder(midi_dir)