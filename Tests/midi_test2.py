import pretty_midi
import pandas as pd

# Load the MIDI file
midi_path = "/Users/nathannguyen/Documents/Midi_To_serum/Tests/VivalaVida(2).mid"  # Update with your file path
midi_data = pretty_midi.PrettyMIDI(midi_path)

# Extract note data
notes = []
for instrument in midi_data.instruments:
    for note in instrument.notes:
        notes.append({
            "start": note.start,
            "end": note.end,
            "pitch": note.pitch,
            "velocity": note.velocity
        })

# Compute envelope properties from the MIDI file
if notes:
    avg_note_length = sum(n["end"] - n["start"] for n in notes) / len(notes)
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level = min(1.0, avg_velocity / 127.0)

    # Adaptive envelope timing based on note length
    attack_time = max(0.02, min(avg_note_length * 0.04, 0.3))  # Min 0.02s, Max 0.3s
    decay_time = min(avg_note_length * 0.15, 1.0)   # Max 1.0s
    release_time = min(avg_note_length * 0.4, 2.0)  # Max 2.0s

    # Apply curvature shaping (more natural response)
    attack_curve = 0.4  # 0 = Linear, Negative = Exponential
    decay_curve = -1.2  # Negative values give smoother decay
    release_curve = -1.0  # Smooth tail-off

    # Envelope looping mode (None by default, could be "loop" or "one-shot")
    loop_mode = "none"  # Set to "loop" for LFO-like behavior

    # Envelope trigger mode (retrigger per note or legato)
    trigger_mode = "retrigger"  # Options: "legato", "retrigger"

    # Sustain power (controls sustain curve shape)
    sustain_power = 0.8  # Higher = more sustain emphasis

    # Construct a dictionary for display
    midi_env_analysis = {
        "Calculated Attack Time": attack_time,
        "Calculated Decay Time": decay_time,
        "Calculated Sustain Level": sustain_level,
        "Calculated Release Time": release_time,
        "Attack Curve": attack_curve,
        "Decay Curve": decay_curve,
        "Release Curve": release_curve,
        "Loop Mode": loop_mode,
        "Trigger Mode": trigger_mode,
        "Sustain Power": sustain_power
    }

    # Convert to DataFrame for better readability
    midi_env_df = pd.DataFrame(list(midi_env_analysis.items()), columns=["Parameter", "Value"])
    print(midi_env_df)
else:
    print("No notes detected in the MIDI file.")
