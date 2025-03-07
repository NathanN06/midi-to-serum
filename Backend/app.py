import os
import traceback
import logging

# Import configuration from the current directory (Backend)
from config import (
    DEFAULT_VITAL_PRESET_FILENAME,
    DEFAULT_SERUM_PRESET_FILENAME,
    MAPPING_CSV_FILENAME,
    PRESETS_DIR,
    MAPPINGS_DIR
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Calculate the parent directory (one level up from Backend)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

from midi_parser import parse_midi
from serum_mapper import load_mapping, map_midi_to_serum
from vital_mapper import (
    load_default_vital_preset,
    modify_vital_preset,
    save_vital_preset
)  # <-- Notice we no longer import generate_base64_wavetable here
from preset_generators import generate_fxp  # Serum preset generator


### Helper Functions
def get_valid_input(prompt, valid_options=None):
    """
    Helper function to get valid user input.
    If valid_options is provided, ensures input is one of the valid choices.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if valid_options and user_input not in valid_options:
            logging.error(f"Invalid input. Please choose from {', '.join(valid_options)}.")
        else:
            return user_input

def get_snapshot_method():
    """
    Prompt the user for which snapshot method to use for Vital.
    """
    print("\nChoose a snapshot method for Vital:")
    print("1) Single first note (existing default)")
    print("2) Average of all notes")
    print("3) Single moment in time (enter a specific time in seconds)")
    method_choice = input("Enter your choice (1-3): ").strip()

    if method_choice not in ["1", "2", "3"]:
        logging.warning("Invalid choice, defaulting to method 1 (single first note).")
        method_choice = "1"
    return method_choice


### Modular Functions
def get_user_inputs():
    """
    Collect all user inputs: MIDI file path, output format, output path, and snapshot method (for Vital).
    """
    # MIDI file path
    midi_file = input("🎵 Enter the path to the MIDI file: ").strip()
    while not os.path.isfile(midi_file):
        logging.error("The specified MIDI file does not exist.")
        midi_file = input("🎵 Enter the path to the MIDI file: ").strip()

    # Output format (Serum or Vital)
    output_format = get_valid_input("🎛 Enter preset type (Serum, Vital): ", ["serum", "vital"])

    # Output path with default filename if necessary
    output_path = input("💾 Enter the output path for the preset file (including filename): ").strip()
    if os.path.isdir(output_path):
        default_filenames = {"serum": DEFAULT_SERUM_PRESET_FILENAME, "vital": "output.vital"}
        output_path = os.path.join(output_path, default_filenames[output_format])
        logging.info(f"No file name provided. Defaulting to: {output_path}")

    # Snapshot method for Vital
    snapshot_method = get_snapshot_method() if output_format == "vital" else None

    return midi_file, output_format, output_path, snapshot_method


def parse_midi_file(midi_file):
    """
    Parse the MIDI file and display a summary of its contents.
    """
    logging.info("Parsing MIDI file...")
    midi_data = parse_midi(midi_file)

    # Display summary
    logging.info("Summary:")
    logging.info(f"  - Notes: {len(midi_data['notes'])}")
    logging.info(f"  - Control Changes: {len(midi_data['control_changes'])}")
    logging.info(f"  - Pitch Bends: {len(midi_data['pitch_bends'])}")
    if "time_signatures" in midi_data:
        logging.info(f"  - Time Signatures: {len(midi_data['time_signatures'])}")
    if "key_signatures" in midi_data:
        logging.info(f"  - Key Signatures: {len(midi_data['key_signatures'])}")

    if not midi_data["notes"]:
        logging.warning("No MIDI notes found. The preset might not contain meaningful data.")

    return midi_data


def generate_serum_preset(midi_data, output_path):
    """
    Generate a Serum preset from MIDI data.
    """
    mapping_file = os.path.join(parent_dir, MAPPINGS_DIR, MAPPING_CSV_FILENAME)
    if not os.path.exists(mapping_file):
        logging.error(f"Mapping file {mapping_file} not found.")
        return

    mapping_config = load_mapping(mapping_file)
    mapped_params = map_midi_to_serum(midi_data, mapping_config)
    generate_fxp(mapped_params, output_path)
    logging.info("Serum preset generated successfully.")


def generate_vital_preset(midi_data, output_path, snapshot_method):
    """
    Generate a Vital preset from MIDI data with THREE-frame wavetable integration.
    """
    default_preset_path = os.path.join(parent_dir, PRESETS_DIR, DEFAULT_VITAL_PRESET_FILENAME)
    if not os.path.exists(default_preset_path):
        logging.error(f"Default Vital preset {default_preset_path} not found.")
        return

    logging.info("Loading default Vital preset...")
    vital_preset = load_default_vital_preset(default_preset_path)
    if not vital_preset:
        logging.error("Failed to load the default Vital preset.")
        return

    logging.info("Modifying Vital preset to incorporate MIDI data and generate 3 wavetable frames...")
    # modify_vital_preset now returns (modified_preset, frame_data_list)
    mapped_preset, frame_data_list = modify_vital_preset(vital_preset, midi_data, snapshot_method)

    logging.info("Saving new Vital preset with 3-frame wavetable data...")
    # We pass the 3 separate frames for the triple replacement
    save_vital_preset(mapped_preset, output_path, frame_data_list)
    logging.info("Vital preset generated successfully.")


### Main Function
def main():
    """
    Main function to orchestrate the MIDI-to-preset conversion process.
    """
    try:
        # Collect user inputs
        midi_file, output_format, output_path, snapshot_method = get_user_inputs()

        # Parse MIDI file
        midi_data = parse_midi_file(midi_file)

        # Convert MIDI to preset based on output format
        logging.info(f"Converting MIDI data to {output_format.capitalize()} preset...")
        if output_format == "serum":
            generate_serum_preset(midi_data, output_path)
        elif output_format == "vital":
            generate_vital_preset(midi_data, output_path, snapshot_method)

        logging.info(f"Conversion complete! Preset saved to: {output_path}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
