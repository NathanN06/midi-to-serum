import os
import json
from typing import List, Tuple, Dict, Any

from virus_sysex_to_vital import apply_virus_sysex_params_to_vital_preset
from vital_wavetable_generator import generate_osc1_frame_from_sysex, replace_single_wavetable

def load_vital_file_as_dict(vital_file_path: str) -> Dict[str, Any]:
    """
    Loads a .vital file which is actually just a plain JSON file.
    """
    with open(vital_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_sysex_txt_files(folder_path: str, default_vital_patch: str) -> List[Tuple[str, str]]:
    """
    1) Loads all .txt files in the folder as 256-byte Virus param blocks.
    2) For each block:
       - Load a copy of the default Vital preset as a raw JSON string.
       - Apply the Virus sysex params.
       - Generate a custom wavetable frame.
       - Inject it using regex logic.
       - Return (updated_json_string, patch_filename).

    Returns:
        A list of (vital_patch_json_str, patch_filename) tuples.
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

        if len(hex_values) != 256:
            print(f"⚠️ Skipping {file_path}: expected 256 params, got {len(hex_values)}")
            continue

        param_block = [int(h, 16) for h in hex_values]

        # Map Virus parameters to names
        from virus_sysex_param_map import virus_sysex_param_map
        virus_params = {
            virus_sysex_param_map.get(idx, f"undefined_{idx}"): val
            for idx, val in enumerate(param_block)
        }

        # Apply parameter mapping to base dict
        base_dict = json.loads(base_vital_json)
        apply_virus_sysex_params_to_vital_preset(param_block, base_dict)

        # Generate wavetable frame
        frame = generate_osc1_frame_from_sysex(virus_params)

        # Inject it using regex
        modified_json = replace_single_wavetable(json.dumps(base_dict), frame)

        patch_filename = f"patch_{i:03}.vital"
        patches.append((modified_json, patch_filename))

    print(f"✅ Prepared {len(patches)} patch(es) from SysEx files.")
    return patches

def save_vital_patches(
    patches: List[Tuple[str, str]],
    output_folder: str
) -> None:
    """
    Writes each (vital_json_str, filename) to disk as a .vital file.
    """
    os.makedirs(output_folder, exist_ok=True)

    for preset_json, patch_filename in patches:
        if not patch_filename.lower().endswith(".vital"):
            patch_filename += ".vital"

        out_path = os.path.join(output_folder, patch_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(preset_json)

        print(f"💾 Saved Vital patch: {out_path}")
