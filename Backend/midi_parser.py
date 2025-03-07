import pretty_midi

def parse_midi(file_path):
    """
    Parse a MIDI file to extract notes, control changes, tempo, pitch bends,
    and calculate envelope parameters (attack, decay, sustain, release).
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)

        # Extract tempo
        tempo = midi_data.estimate_tempo()

        # Extract notes with ENV parameters
        notes = []
        prev_note_end = None

        for instrument in midi_data.instruments:
            for i, note in enumerate(instrument.notes):
                attack_time = 0 if i == 0 else note.start - instrument.notes[i - 1].start
                decay_time = 0.1  # Placeholder, could be determined via MIDI CC
                sustain_level = note.velocity / 127.0
                release_time = (note.end - note.start) * 0.3  # Rough estimate

                notes.append({
                    "pitch": note.pitch,
                    "velocity": note.velocity,
                    "start": note.start,
                    "end": note.end,
                    "attack": attack_time,
                    "decay": decay_time,
                    "sustain": sustain_level,
                    "release": release_time
                })

        # Extract control changes
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

        print("\n🔍 Debug: Parsed MIDI Data")
        print(f"Notes: {len(notes)}, CCs: {len(control_changes)}, Pitch Bends: {len(pitch_bends)}")

        return {
            "tempo": tempo,
            "notes": notes,
            "control_changes": control_changes,
            "pitch_bends": pitch_bends
        }
    
    except Exception as e:
        print(f"❌ Error parsing MIDI file: {e}")
        return {
            "tempo": None,
            "notes": [],
            "control_changes": [],
            "pitch_bends": []
        }
