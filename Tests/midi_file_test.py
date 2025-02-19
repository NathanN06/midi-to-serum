import pretty_midi

# Load MIDI file
midi_file_path = "/Users/nathannguyen/Documents/MIDI_library_test/Midi_files/VivalaVida(2).mid"  # Replace with your actual file path
midi_data = pretty_midi.PrettyMIDI(midi_file_path)

# Extract MIDI parameters
def extract_midi_parameters(midi_data):
    parameters = []

    for instrument in midi_data.instruments:
        instrument_name = pretty_midi.program_to_instrument_name(instrument.program)
        for note in instrument.notes:
            parameters.append({
                "instrument": instrument_name,
                "note": note.pitch,
                "velocity": note.velocity,
                "start_time": note.start,
                "end_time": note.end,
                "duration": note.end - note.start
            })

    return parameters

# Extract data
midi_parameters = extract_midi_parameters(midi_data)

# Display extracted MIDI information
for param in midi_parameters[:10]:  # Show first 10 notes
    print(param)
