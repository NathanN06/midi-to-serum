import os
from mido import MidiFile

def extract_sysex_from_midi(
    midi_path: str,
    output_dir: str,
    verbose: bool = True
) -> list[str]:
    """
    Extracts Virus SysEx messages from a .mid file and saves each as a .txt file.

    Returns:
        List of full paths to saved SysEx .txt files.
    """
    midi = MidiFile(midi_path)
    os.makedirs(output_dir, exist_ok=True)

    sysex_files = []
    sysex_count = 0

    for i, track in enumerate(midi.tracks):
        for msg in track:
            if msg.type == 'sysex':
                sysex_count += 1
                hex_data = [f'{byte:02X}' for byte in msg.data]

                # Try to extract only the 256-byte Single Dump data at the end
                try:
                    # Search for the 0x10 message type (Single Dump)
                    if hex_data[5] == "10":
                        param_data = hex_data[8:-1]  # slice to skip headers and trailing checksum
                        if len(param_data) >= 256:
                            param_data = param_data[:256]  # truncate to exact length
                        else:
                            continue  # skip invalid
                    else:
                        continue  # skip non-Single Dumps
                except IndexError:
                    continue

                filename = os.path.join(output_dir, f"sysex_{sysex_count:03}.txt")
                with open(filename, "w") as f:
                    f.write(" ".join(param_data))
                sysex_files.append(filename)

    if verbose:
        print(f"✅ Extracted {len(sysex_files)} valid Virus SysEx patches to '{output_dir}'")

    return sysex_files


# Example usage (only runs if executed directly)
if __name__ == "__main__":
    MIDI_PATH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/404studio_Virus_C_Soundset.mid"
    OUTPUT_DIR = "/Users/nathannguyen/Documents/Midi_To_serum/Presets"
    extract_sysex_from_midi(MIDI_PATH, OUTPUT_DIR)