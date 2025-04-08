import os
from mido import MidiFile

def extract_sysex_from_midi(
    midi_path: str,
    output_dir: str,
    verbose: bool = True
) -> list[str]:
    """
    Extracts raw 256-byte Virus SysEx parameter blocks from a .mid file and saves each as a .txt file.

    Returns:
        List of full paths to saved SysEx .txt files.
    """
    midi = MidiFile(midi_path)
    os.makedirs(output_dir, exist_ok=True)

    sysex_files = []
    sysex_count = 0

    for track in midi.tracks:
        for msg in track:
            if msg.type == 'sysex' and len(msg.data) >= 265:
                data = list(msg.data)

                # Check for Virus Single Dump type (0x10 at index 5)
                if data[5] == 0x10:
                    param_block = data[8:8 + 256]

                    # Sanity check
                    if len(param_block) == 256:
                        sysex_count += 1
                        filename = os.path.join(output_dir, f"sysex_{sysex_count:03}.txt")
                        with open(filename, "w") as f:
                            f.write(" ".join(f"{b:02X}" for b in param_block))
                        sysex_files.append(filename)

    if verbose:
        print(f"✅ Extracted {len(sysex_files)} valid Virus SysEx patches to '{output_dir}'")

    return sysex_files


# Example usage (only runs if executed directly)
if __name__ == "__main__":
    MIDI_PATH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/404studio_Virus_C_Soundset.mid"
    OUTPUT_DIR = "/Users/nathannguyen/Documents/Midi_To_serum/Presets"
    extract_sysex_from_midi(MIDI_PATH, OUTPUT_DIR)