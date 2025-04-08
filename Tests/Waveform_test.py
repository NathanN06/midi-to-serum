import pretty_midi
import numpy as np
import matplotlib.pyplot as plt

# Load the MIDI file (Change this to your file path)
midi_path = "/Users/nathannguyen/Documents/Midi_To_serum/Tests/VivalaVida(2).mid"
midi_data = pretty_midi.PrettyMIDI(midi_path)

# Extract note pitches and velocities
notes = []
velocities = []
times = []

for instrument in midi_data.instruments:
    for note in instrument.notes:
        notes.append(note.pitch)
        velocities.append(note.velocity / 127.0)  # Normalize velocity
        times.append(note.start)

# Convert to NumPy arrays
notes = np.array(notes)
velocities = np.array(velocities)
times = np.array(times)

# Sort notes by time
sorted_indices = np.argsort(times)
notes = notes[sorted_indices]
velocities = velocities[sorted_indices]
times = times[sorted_indices]

# Generate a wavetable based on MIDI pitch & velocity
num_frames = 32  # Number of frames for the wavetable
frame_size = 256  # Samples per frame
wavetable = []

for i in range(num_frames):
    phase = np.linspace(0, 2 * np.pi, frame_size)

    # Use MIDI pitch to adjust frequency dynamically
    if len(notes) > 0:
        pitch = notes[min(i, len(notes) - 1)]
        freq = 440 * (2 ** ((pitch - 69) / 12))  # Convert MIDI pitch to frequency
    else:
        freq = 440  # Default to A4

    # Generate waveform (simple sine wave with velocity shaping)
    wave = np.sin(freq * phase / 1000) * velocities[min(i, len(velocities) - 1)]
    wavetable.append(wave)

wavetable = np.array(wavetable).flatten()

# Plot the generated wavetable
plt.figure(figsize=(12, 4))
plt.plot(wavetable[:frame_size * 4])  # Show first 4 frames
plt.title("Expected Wavetable from MIDI Data")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid()
plt.show()
