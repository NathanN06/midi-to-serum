import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now you can import the backend modules
from Backend.midi_parser import parse_midi
from Backend.serum_mapper import load_mapping, map_midi_to_serum
from Backend.fxp_generator import generate_fxp


def main():
    # Get user input
    midi_file = input("Enter the path to the MIDI file: ")
    mapping_file = "SerumParameterMapping.csv"
    output_file = input("Enter the output path for the .fxp file: ")

    # Parse MIDI file
    midi_data = parse_midi(midi_file)

    # Load mapping configuration
    mapping_config = load_mapping(mapping_file)

    # Map MIDI data to Serum parameters
    serum_params = map_midi_to_serum(midi_data, mapping_config)

    # Generate .fxp file
    generate_fxp(serum_params, output_file)

if __name__ == "__main__":
    main()
