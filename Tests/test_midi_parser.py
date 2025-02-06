from backend.midi_parser import parse_midi

def test_parse_midi():
    midi_file = "test_files/sample.mid"  # Use a sample MIDI file
    midi_data = parse_midi(midi_file)
    assert "tempo" in midi_data
    assert "notes" in midi_data
    assert len(midi_data["notes"]) > 0
