import os
import json
from typing import List, Tuple, Dict, Any

from virus_sysex_to_vital import apply_virus_sysex_params_to_vital_preset
from vital_wavetable_generator import (
    generate_osc1_frame_from_sysex,
    generate_osc2_frame_from_sysex,
    generate_osc3_frame_from_sysex,
    replace_three_wavetables
)
from virus_lfo_generator import (
    inject_lfo1_shape_from_sysex,
    inject_lfo2_shape_from_sysex,
    inject_lfo3_shape_from_sysex  # 👈 NEW: Inject LFO3
)

def load_vital_file_as_dict(vital_file_path: str) -> Dict[str, Any]:
    """
    Loads a .vital file from disk and parses it as a JSON dictionary.
    """
    with open(vital_file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_sysex_txt_files(folder_path: str, default_vital_patch: str) -> List[Tuple[str, str]]:
    """
    Loads all Virus SysEx parameter .txt files from a folder and uses them
    to generate customized Vital patch files.
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

        from virus_sysex_param_map import virus_sysex_param_map
        virus_params = {
            virus_sysex_param_map.get(idx, f"undefined_{idx}"): val
            for idx, val in enumerate(param_block)
        }

        base_dict = json.loads(base_vital_json)

        # Step 1: Apply Virus parameters to Vital settings
        apply_virus_sysex_params_to_vital_preset(param_block, base_dict)

        # Step 2: Inject LFO1, LFO2, LFO3 shapes
        inject_lfo1_shape_from_sysex(virus_params.get("Lfo1_Shape", 0), base_dict)
        inject_lfo2_shape_from_sysex(virus_params.get("Lfo2_Shape", 0), base_dict)
        inject_lfo3_shape_from_sysex(virus_params.get("Lfo3_Shape", 0), base_dict)

        # Step 3: Generate and inject custom oscillator frames
        osc1_frame = generate_osc1_frame_from_sysex(virus_params)
        osc2_frame = generate_osc2_frame_from_sysex(virus_params)
        osc3_frame = generate_osc3_frame_from_sysex(virus_params)

        modified_json = json.dumps(base_dict)
        modified_json = replace_three_wavetables(modified_json, [osc1_frame, osc2_frame, osc3_frame], virus_params)

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
    """
    os.makedirs(output_folder, exist_ok=True)

    for preset_json, patch_filename in patches:
        if not patch_filename.lower().endswith(".vital"):
            patch_filename += ".vital"

        out_path = os.path.join(output_folder, patch_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(preset_json)

        print(f"📎 Saved Vital patch: {out_path}")
