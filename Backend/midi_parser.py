import pretty_midi

def parse_midi(file_path):
    """
    Parse a MIDI file to extract notes, control changes, tempo, and pitch bends.
    Returns a dictionary with structured MIDI data.
    """
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
                "end": note.end
            }
            for instrument in midi_data.instruments
            for note in instrument.notes
        ]

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

        return {
            "tempo": tempo,
            "notes": notes,
            "control_changes": control_changes,
            "pitch_bends": pitch_bends
        }

    except Exception as e:
        print(f"Error parsing MIDI file: {e}")
        return {
            "tempo": None,
            "notes": [],
            "control_changes": [],
            "pitch_bends": []
        }
