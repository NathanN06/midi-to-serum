import os
import traceback
import logging

# Import configuration from the current directory (Backend)
from config import (
    DEFAULT_VITAL_PRESET_FILENAME,
    PRESETS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Calculate the parent directory (one level up from Backend)
parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

from midi_parser import parse_midi
from vital_mapper import (
    load_default_vital_preset,
    modify_vital_preset,
    save_vital_preset
)


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
    Prompts the user to select a snapshot method, ensuring valid input.
    """
    valid_options = {"1", "2", "3"}
    
    while True:
        print("\nChoose a snapshot method:")
        print("1: Use first note")
        print("2: Use average of all notes")
        print("3: Use a single moment in time")

        user_input = input("Enter 1, 2, or 3 (or 'q' to quit): ").strip()

        if user_input.lower() == "q":
            print("❌ Exiting snapshot selection.")
            return None  # User wants to quit

        if user_input in valid_options:
            return user_input  # Return valid choice

        print("⚠️ Invalid input! Please enter 1, 2, or 3.")


### Modular Functions
def get_user_inputs():
    """
    Collect user inputs: MIDI file path, output path, and snapshot method (for Vital).
    """
    # MIDI file path
    midi_file = input("🎵 Enter the path to the MIDI file: ").strip()
    while not os.path.isfile(midi_file):
        logging.error("The specified MIDI file does not exist.")
        midi_file = input("🎵 Enter the path to the MIDI file: ").strip()

    # Output path with default filename if necessary
    output_path = input("💾 Enter the output path for the Vital preset file (including filename): ").strip()
    if os.path.isdir(output_path):
        output_path = os.path.join(output_path, "output.vital")
        logging.info(f"No file name provided. Defaulting to: {output_path}")

    # Snapshot method for Vital
    snapshot_method = get_snapshot_method()

    return midi_file, output_path, snapshot_method


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


def generate_vital_preset(midi_data, output_path, snapshot_method):
    """
    Generate a Vital preset from MIDI data, integrating a 3-frame wavetable.
    """
    # 1) Find default Vital preset
    default_preset_path = os.path.join(parent_dir, PRESETS_DIR, DEFAULT_VITAL_PRESET_FILENAME)
    if not os.path.exists(default_preset_path):
        logging.error(f"Default Vital preset {default_preset_path} not found.")
        return

    logging.info("Loading default Vital preset...")
    vital_preset = load_default_vital_preset(default_preset_path)
    if not vital_preset:
        logging.error("Failed to load the default Vital preset.")
        return

    # 2) Modify the preset using MIDI data (this calls your updated logic in 'modify_vital_preset')
    logging.info("Modifying Vital preset to incorporate MIDI data and generate 3 wavetable frames...")
    modified_preset, frame_data_list = modify_vital_preset(
        vital_preset,
        midi_data,
        snapshot_method
    )

    # 3) Save the new preset
    logging.info("Saving new Vital preset with 3-frame wavetable data...")
    save_vital_preset(modified_preset, output_path, frame_data_list)
    logging.info("✅ Vital preset generated successfully!")


### Main Function
def main():
    """
    Main function to orchestrate the MIDI-to-Vital conversion process.
    """
    try:
        # Collect user inputs
        midi_file, output_path, snapshot_method = get_user_inputs()

        # Parse MIDI file into a data dict
        midi_data = parse_midi_file(midi_file)

        # Convert MIDI data into a Vital preset
        logging.info("Converting MIDI data to Vital preset...")
        generate_vital_preset(midi_data, output_path, snapshot_method)

        logging.info(f"🎉 Conversion complete! Preset saved to: {output_path}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
