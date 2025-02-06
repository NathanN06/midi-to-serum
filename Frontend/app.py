import sys
import os

# Ensure Backend is accessible
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from Backend.midi_parser import parse_midi
from Backend.serum_mapper import load_mapping, map_midi_to_serum
from Backend.vital_mapper import map_midi_to_vital  # Ensure this file exists
from Backend.preset_generators import generate_fxp, generate_vital_preset

def main():
    """
    Main function to handle user input and convert MIDI files to synthesizer presets.
    """
    midi_file = input("🎵 Enter the path to the MIDI file: ").strip()
    output_format = input("🎛 Enter preset type (Serum, Vital): ").strip().lower()
    output_path = input("💾 Enter the output path for the preset file (including filename): ").strip()

    # Auto-assign default filename if a folder is given
    if os.path.isdir(output_path):
        if output_format == "serum":
            output_path = os.path.join(output_path, "output.fxp")
        elif output_format == "vital":
            output_path = os.path.join(output_path, "output.vital")
        print(f"📁 No file name provided. Defaulting to: {output_path}")

    try:
        # Step 1: Parse the MIDI file
        print("🎼 Parsing MIDI file...")
        midi_data = parse_midi(midi_file)

        # Step 2: Convert MIDI to the chosen synth format
        if output_format == "serum":
            mapping_file = "mappings/SerumParameterMapping.csv"
            mapping_config = load_mapping(mapping_file)
            mapped_params = map_midi_to_serum(midi_data, mapping_config)
            generate_fxp(mapped_params, output_path)

        elif output_format == "vital":
            mapped_params = map_midi_to_vital(midi_data)
            generate_vital_preset(mapped_params, output_path)

        else:
            print("❌ Unknown preset type. Please choose Serum or Vital.")
            return

        print(f"✅ Conversion complete! Preset saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
