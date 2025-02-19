import sys
import os
import traceback

# Ensure Backend is accessible
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from Backend.midi_parser import parse_midi
from Backend.serum_mapper import load_mapping, map_midi_to_serum
from Backend.vital_mapper import (
    load_default_vital_preset, 
    modify_vital_preset, 
    save_vital_preset
)
from Backend.preset_generators import generate_fxp  # Serum preset generator

def get_valid_input(prompt, valid_options=None):
    """
    Helper function to get valid user input.
    If valid_options is provided, it ensures input is one of the valid choices.
    """
    while True:
        user_input = input(prompt).strip().lower()
        if valid_options and user_input not in valid_options:
            print(f"❌ Invalid input. Please choose from {', '.join(valid_options)}.")
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

    # Basic validation, default to "1" if invalid
    if method_choice not in ["1", "2", "3"]:
        print("Invalid choice, defaulting to method 1 (single first note).")
        method_choice = "1"

    return method_choice

def main():
    """
    Main function to handle user input and convert MIDI files to synthesizer presets.
    """
    try:
        # Step 1: Get MIDI file path
        midi_file = input("🎵 Enter the path to the MIDI file: ").strip()
        if not os.path.isfile(midi_file):
            print("❌ Error: The specified MIDI file does not exist.")
            return

        # Step 2: Get output format (Serum or Vital)
        output_format = get_valid_input("🎛 Enter preset type (Serum, Vital): ", ["serum", "vital"])

        # Step 3: Get output path and set default filename if necessary
        output_path = input("💾 Enter the output path for the preset file (including filename): ").strip()
        if os.path.isdir(output_path):
            default_filenames = {"serum": "output.fxp", "vital": "output.vital"}
            output_path = os.path.join(output_path, default_filenames[output_format])
            print(f"📁 No file name provided. Defaulting to: {output_path}")

        print("🎼 Parsing MIDI file...")
        midi_data = parse_midi(midi_file)

        if not midi_data["notes"]:
            print("⚠️ Warning: No MIDI notes found. The preset might not contain meaningful data.")

        print(f"🔄 Converting MIDI data to {output_format.capitalize()} preset...")

        # Step 4: Convert MIDI to selected synth format
        if output_format == "serum":
            # Serum flow remains unchanged
            mapping_file = os.path.join(parent_dir, "mappings", "SerumParameterMapping.csv")
            if not os.path.exists(mapping_file):
                print(f"❌ Error: Mapping file {mapping_file} not found.")
                return
            mapping_config = load_mapping(mapping_file)
            mapped_params = map_midi_to_serum(midi_data, mapping_config)
            generate_fxp(mapped_params, output_path)

        elif output_format == "vital":
            default_preset_path = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/Default.vital"

            if not os.path.exists(default_preset_path):
                print(f"❌ Error: Default Vital preset {default_preset_path} not found.")
                return

            # Prompt the user for snapshot method
            snapshot_method = get_snapshot_method()

            print("🎛 Loading default Vital preset...")
            vital_preset = load_default_vital_preset(default_preset_path)
            if not vital_preset:
                print("❌ Error: Failed to load the default Vital preset.")
                return

            print("🔧 Modifying Vital preset based on MIDI data...")
            mapped_preset = modify_vital_preset(vital_preset, midi_data, snapshot_method)

            print("💾 Saving new Vital preset...")
            save_vital_preset(mapped_preset, output_path)

        print(f"✅ Conversion complete! Preset saved to: {output_path}")

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
