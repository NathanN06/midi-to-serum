import os
import json
from typing import List, Tuple, Dict, Any
from typing import List, Dict, Any


from virus_sysex_to_vital import apply_virus_sysex_params_to_vital_preset
from vital_wavetable_generator import (
    generate_osc1_frame_from_sysex,
    generate_osc2_frame_from_sysex,
    replace_two_wavetables
)

def load_vital_file_as_dict(vital_file_path: str) -> Dict[str, Any]:
    """
    Loads a .vital file from disk and parses it as a JSON dictionary.

    Args:
        vital_file_path (str): Path to the .vital file.

    Returns:
        dict: Parsed Vital patch dictionary.
    """
    with open(vital_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_sysex_txt_files(folder_path: str, default_vital_patch: str) -> List[Tuple[str, str]]:
    """
    Loads all Virus SysEx parameter .txt files from a folder and uses them
    to generate customized Vital patch files.

    For each file:
      - Loads the 256-byte SysEx block.
      - Converts it into Virus parameter names.
      - Loads a base .vital preset.
      - Applies Virus parameters using your mapping logic.
      - Generates custom oscillator waveforms for OSC1 and OSC2.
      - Injects those wavetables directly into the JSON.
      - Returns a tuple of (updated JSON string, filename).

    Args:
        folder_path (str): Path to the folder with .txt SysEx files.
        default_vital_patch (str): Path to the base Vital preset to use.

    Returns:
        list[tuple]: A list of (updated_json_string, patch_filename) tuples.
    """
    with open(default_vital_patch, "r", encoding="utf-8") as f:
        base_vital_json = f.read()

    sysex_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ])

    patches = []

    for i, file_path in enumerate(sysex_files, start=1):
        with open(file_path, "r") as f:
            hex_values = f.read().strip().split()

        # Sanity check: must be exactly 256 values
        if len(hex_values) != 256:
            print(f"⚠️ Skipping {file_path}: expected 256 params, got {len(hex_values)}")
            continue

        # Convert to integers (Virus parameter values)
        param_block = [int(h, 16) for h in hex_values]

        # Map param block to Virus param names using virus_sysex_param_map
        from virus_sysex_param_map import virus_sysex_param_map
        virus_params = {
            virus_sysex_param_map.get(idx, f"undefined_{idx}"): val
            for idx, val in enumerate(param_block)
        }

        # Load a fresh copy of the Vital preset as a dict
        base_dict = json.loads(base_vital_json)

        # Apply Virus parameter values to the preset
        apply_virus_sysex_params_to_vital_preset(param_block, base_dict)

        # Generate custom oscillator frames from Virus parameters
        osc1_frame = generate_osc1_frame_from_sysex(virus_params)
        osc2_frame = generate_osc2_frame_from_sysex(virus_params)

        # Convert updated preset back to JSON
        modified_json = json.dumps(base_dict)

        # Inject the two waveforms into the JSON string
        modified_json = replace_two_wavetables(modified_json, [osc1_frame, osc2_frame])

        # Output file name
        patch_filename = f"patch_{i:03}.vital"
        patches.append((modified_json, patch_filename))

    print(f"✅ Prepared {len(patches)} patch(es) from SysEx files.")
    return patches

def save_vital_patches(
    patches: List[Tuple[str, str]],
    output_folder: str
) -> None:
    """
    Saves each JSON string as a .vital file in the specified output folder.

    Args:
        patches (list): List of (json_str, filename) tuples.
        output_folder (str): Destination folder path.
    """
    os.makedirs(output_folder, exist_ok=True)

    for preset_json, patch_filename in patches:
        if not patch_filename.lower().endswith(".vital"):
            patch_filename += ".vital"

        out_path = os.path.join(output_folder, patch_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(preset_json)

        print(f"💾 Saved Vital patch: {out_path}")
