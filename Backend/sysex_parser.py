import os
from mido import MidiFile

def extract_sysex_from_midi(
    midi_path: str,
    output_dir: str,
    verbose: bool = True
) -> list[str]:
    """
    Extracts raw 256-byte Virus SysEx parameter blocks from a .mid file and saves each as a .txt file.

    Args:
        midi_path (str): Path to the input .mid file.
        output_dir (str): Directory to save extracted .txt patch files.
        verbose (bool): Whether to print status messages.

    Returns:
        List of full paths to saved SysEx .txt files.
    """
    midi = MidiFile(midi_path)
    os.makedirs(output_dir, exist_ok=True)

    sysex_files = []
    patch_index = 0

    for i, track in enumerate(midi.tracks):
        for j, msg in enumerate(track):
            if (
                msg.type == 'sysex' and 
                len(msg.data) >= 265 and
                list(msg.data[1:5]) == [0x20, 0x33, 0x01, 0x00] and 
                msg.data[5] == 0x10
            ):
                param_block = msg.data[8:8 + 256]

                if len(param_block) == 256:
                    patch_index += 1
                    filename = os.path.join(output_dir, f"track{i:02}_msg{j:03}_patch{patch_index:03}.txt")
                    with open(filename, "w") as f:
                        f.write(" ".join(f"{b:02X}" for b in param_block))
                    sysex_files.append(filename)

                    if verbose:
                        print(f"🎛️ Extracted patch #{patch_index} from Track {i}, Msg {j} → {filename}")

    if verbose and patch_index == 0:
        print("⚠️ No valid Virus SysEx patches found in the MIDI file.")

    return sysex_files

# Example usage
if __name__ == "__main__":
    MIDI_PATH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/404studio_Virus_C_Soundset.mid"
    OUTPUT_DIR = "/Users/nathannguyen/Documents/Midi_To_serum/Presets"
    extract_sysex_from_midi(MIDI_PATH, OUTPUT_DIR)