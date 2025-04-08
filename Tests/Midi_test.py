import pretty_midi

def analyze_midi(file_path):
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)

        # Extract tempo
        tempo = midi_data.estimate_tempo()

        # Extract notes
        notes = [
            {
                "pitch": note.pitch,
                "velocity": note.velocity,
                "start": note.start,
                "end": note.end,
                "duration": note.end - note.start
            }
            for instrument in midi_data.instruments
            for note in instrument.notes
        ]

        # Extract control changes (CC)
        control_changes = [
            {
                "controller": cc.number,
                "value": cc.value,
                "time": cc.time
            }
            for instrument in midi_data.instruments
            for cc in instrument.control_changes
        ]

        # Extract pitch bends
        pitch_bends = [
            {
                "pitch": pb.pitch,
                "time": pb.time
            }
            for instrument in midi_data.instruments
            for pb in instrument.pitch_bends
        ]

        # Extract time signatures
        time_signatures = [
            {
                "numerator": ts.numerator,
                "denominator": ts.denominator,
                "time": ts.time
            }
            for ts in midi_data.time_signature_changes
        ]

        # Extract key signatures
        key_signatures = [
            {
                "key": ks.key_number,  # 0 = C, 1 = C#/Db, etc.
                "time": ks.time
            }
            for ks in midi_data.key_signature_changes
        ]

        # Print analysis results
        print("\n🔍 **MIDI Analysis Results**")
        print(f"🎼 Tempo: {tempo:.2f} BPM")
        print(f"🎵 Total Notes: {len(notes)}")
        print(f"🎚️ Control Changes: {len(control_changes)}")
        print(f"🎸 Pitch Bends: {len(pitch_bends)}")
        print(f"🕒 Time Signatures: {len(time_signatures)}")
        print(f"🎼 Key Signatures: {len(key_signatures)}\n")

        # Print sample notes (first 10)
        if notes:
            print("🎶 **First 10 Notes:**")
            for i, note in enumerate(notes[:10]):
                print(f" - Pitch: {note['pitch']}, Velocity: {note['velocity']}, "
                      f"Start: {note['start']:.2f}s, End: {note['end']:.2f}s, Duration: {note['duration']:.2f}s")

        # Print sample control changes (first 10)
        if control_changes:
            print("\n🎛️ **First 10 Control Changes:**")
            for i, cc in enumerate(control_changes[:10]):
                print(f" - Controller: {cc['controller']}, Value: {cc['value']}, Time: {cc['time']:.2f}s")

        # Print sample pitch bends (first 10)
        if pitch_bends:
            print("\n🎸 **First 10 Pitch Bends:**")
            for i, pb in enumerate(pitch_bends[:10]):
                print(f" - Pitch: {pb['pitch']}, Time: {pb['time']:.2f}s")

    except Exception as e:
        print(f"❌ Error analyzing MIDI file: {e}")

# Replace with your MIDI file path
midi_file_path = "/Users/nathannguyen/Documents/Midi_To_serum/Tests/VivalaVida(2).mid"  # Ensure this file is in the same directory
analyze_midi(midi_file_path)
