import pretty_midi

def parse_midi(file_path):
    """Parses a MIDI file and extracts notes, control changes, pitch bends, and tempo."""
    midi_data = pretty_midi.PrettyMIDI(file_path)

    # Extract tempo
    tempo = midi_data.estimate_tempo()

    # Extract notes
    notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            notes.append({
                "pitch": note.pitch,
                "velocity": note.velocity,
                "start_time": note.start,
                "end_time": note.end
            })

    # Extract control changes
    control_changes = []
    for instrument in midi_data.instruments:
        for cc in instrument.control_changes:
            control_changes.append({
                "controller": cc.number,
                "value": cc.value,
                "time": cc.time
            })

    # Extract pitch bends
    pitch_bends = []
    for instrument in midi_data.instruments:
        for pb in instrument.pitch_bends:
            pitch_bends.append({
                "pitch": pb.pitch,
                "time": pb.time
            })

    return {"tempo": tempo, "notes": notes, "control_changes": control_changes, "pitch_bends": pitch_bends}
