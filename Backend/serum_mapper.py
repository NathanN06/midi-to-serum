import pandas as pd

def load_mapping(csv_path):
    """Loads the Serum parameter mapping from a CSV file."""
    mapping_data = pd.read_csv(csv_path)
    mapping = {}
    for _, row in mapping_data.iterrows():
        category = row["Category"]
        parameter = row["Parameter"]
        midi_input = row["MIDI Input"]

        if category not in mapping:
            mapping[category] = {}
        mapping[category][parameter] = midi_input
    return mapping

def map_midi_to_serum(midi_data, mapping_config):
    """Maps MIDI data to Serum parameters using the mapping configuration."""
    serum_parameters = {}

    # Iterate over categories and parameters
    for category, params in mapping_config.items():
        for parameter, midi_input in params.items():
            if "Velocity" in midi_input:
                for note in midi_data["notes"]:
                    serum_parameters[parameter] = note["velocity"] / 127
            elif "Pitch" in midi_input:
                for note in midi_data["notes"]:
                    serum_parameters[parameter] = note["pitch"] - 69
            elif "CC" in midi_input:
                cc_number = int(midi_input.split()[1])
                for cc in midi_data["control_changes"]:
                    if cc["controller"] == cc_number:
                        serum_parameters[parameter] = cc["value"] / 127
            elif "Tempo" in midi_input:
                serum_parameters[parameter] = midi_data["tempo"]
            elif "Pitch Bend" in midi_input:
                for pb in midi_data["pitch_bends"]:
                    serum_parameters[parameter] = pb["pitch"] / 8192

    return serum_parameters
