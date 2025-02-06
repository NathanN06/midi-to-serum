import pandas as pd
import re

def load_mapping(csv_path):
    """
    Load the Serum parameter mapping from a CSV file.
    Returns a dictionary with parameter index keys and mapping info.
    """
    try:
        mapping_data = pd.read_csv(csv_path)
        mapping = {}
        for _, row in mapping_data.iterrows():
            index = int(row["Index"])  # Make sure the CSV column is present
            # You can store a dictionary of info for each parameter if needed
            mapping[index] = {
                "Category": row["Category"],
                "Parameter": row["Parameter"],
                "MIDI Input": row["MIDI Input"],
                "Notes": row["Notes"]
            }
        return mapping
    except Exception as e:
        print(f"Error loading mapping configuration: {e}")
        return {}


def map_midi_to_serum(midi_data, mapping_config):
    """
    Map MIDI data to Serum parameters using the mapping configuration.
    Returns a dictionary with keys like "Param 0", "Param 1", etc.
    """
    serum_parameters = {}

    for index, mapping in mapping_config.items():
        midi_input = mapping["MIDI Input"]
        param_key = f"Param {index}"
        try:
            # Initialize default value
            serum_parameters[param_key] = 0.0

            if "Velocity" in midi_input and midi_data["notes"]:
                serum_parameters[param_key] = midi_data["notes"][0]["velocity"] / 127

            elif "Note Pitch" in midi_input and midi_data["notes"]:
                serum_parameters[param_key] = midi_data["notes"][0]["pitch"] - 69

            elif "CC" in midi_input:
                import re
                match = re.search(r"CC (\d+)", midi_input)
                if match:
                    cc_number = int(match.group(1))
                    cc_value = next(
                        (cc["value"] / 127 for cc in midi_data["control_changes"]
                         if cc["controller"] == cc_number),
                        0.0
                    )
                    serum_parameters[param_key] = cc_value

            elif "Tempo" in midi_input:
                serum_parameters[param_key] = midi_data.get("tempo", 120) / 120

            elif "Pitch Bend" in midi_input and midi_data["pitch_bends"]:
                serum_parameters[param_key] = midi_data["pitch_bends"][0]["pitch"] / 8192

            elif "Default" in midi_input:
                defaults = {
                    "Env1 Atk": 0.5,
                    "Env1 Sus": 0.8,
                    "Env1 Rel": 0.4
                }
                # Use the original parameter name for default lookup, if needed.
                serum_parameters[param_key] = defaults.get(mapping["Parameter"], 0.0)

        except Exception as e:
            print(f"Error mapping parameter at index {index}: {e}")

    return serum_parameters
