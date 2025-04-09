import os
import json
import logging
from typing import List, Tuple, Dict, Any

from virus_sysex_to_vital import apply_virus_sysex_params_to_vital_preset
from vital_wavetable_generator import (
    generate_osc1_frame_from_sysex,
    generate_osc2_frame_from_sysex,
    generate_osc3_frame_from_sysex,
    replace_three_wavetables,
)
from virus_lfo_generator import (
    inject_lfo1_shape_from_sysex,
    inject_lfo2_shape_from_sysex,
    inject_lfo3_shape_from_sysex,
)
from effects_mapper.master_fx import inject_all_effects  # 👈 NEW

# -------------------------------------------------------------------
# LOGGING CONFIGURATION
# -------------------------------------------------------------------
LOG_FILE_PATH = "/Users/nathannguyen/Documents/Midi_To_serum/logs/conversion.log"
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def load_vital_file_as_dict(vital_file_path: str) -> Dict[str, Any]:
    """Load a .vital file from disk and parse it as a JSON dictionary."""
    with open(vital_file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_sysex_txt_files(folder_path: str, default_vital_patch: str) -> List[Tuple[str, str]]:
    """
    Load all Virus SysEx parameter .txt files from a folder and use them
    to generate customised Vital patch files.

    Returns:
        List of tuples -> (preset_json_str, output_filename)
    """
    with open(default_vital_patch, "r", encoding="utf-8") as f:
        base_vital_json = f.read()

    sysex_files = sorted(
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".txt")
    )

    patches: List[Tuple[str, str]] = []

    for i, file_path in enumerate(sysex_files, start=1):
        with open(file_path, "r") as f:
            hex_values = f.read().strip().split()

        if len(hex_values) != 256:
            logging.warning(f"⚠️  Skipping {file_path}: expected 256 params, got {len(hex_values)}")
            continue

        param_block = [int(h, 16) for h in hex_values]

        from virus_sysex_param_map import virus_sysex_param_map

        virus_params = {
            virus_sysex_param_map.get(idx, f"undefined_{idx}"): val
            for idx, val in enumerate(param_block)
        }

        # ───── DEBUG: confirm byte alignment ─────────────────────────
        raw_lfo1_shape = param_block[68]
        parsed_lfo1_shape = virus_params["Lfo1_Shape"]
        logging.info(
            f"🪛  DEBUG | Byte 68 raw = {raw_lfo1_shape:02X} ({raw_lfo1_shape})"
            f" → virus_params['Lfo1_Shape'] = {parsed_lfo1_shape}"
        )
        # ─────────────────────────────────────────────────────────────

        base_dict = json.loads(base_vital_json)

        # 1) Apply scalar mappings
        apply_virus_sysex_params_to_vital_preset(param_block, base_dict)

        # 2) Inject LFOs
        inject_lfo1_shape_from_sysex(virus_params, base_dict)
        inject_lfo2_shape_from_sysex(virus_params, base_dict)
        inject_lfo3_shape_from_sysex(virus_params, base_dict)

        # 3) Inject effects
        inject_all_effects(virus_params, base_dict)

        # 4) Inject oscillator frames
        osc1_frame = generate_osc1_frame_from_sysex(virus_params)
        osc2_frame = generate_osc2_frame_from_sysex(virus_params)
        osc3_frame = generate_osc3_frame_from_sysex(virus_params)

        modified_json = json.dumps(base_dict)
        modified_json = replace_three_wavetables(
            modified_json,
            [osc1_frame, osc2_frame, osc3_frame],
            virus_params,
        )

        patch_filename = f"patch_{i:03}.vital"
        patches.append((modified_json, patch_filename))

    logging.info(f"✅ Prepared {len(patches)} patch(es) from SysEx files.")
    return patches


def save_vital_patches(
    patches: List[Tuple[str, str]],
    output_folder: str,
) -> None:
    """Save each JSON string as a .vital file in the specified output folder."""
    os.makedirs(output_folder, exist_ok=True)

    for preset_json, patch_filename in patches:
        if not patch_filename.lower().endswith(".vital"):
            patch_filename += ".vital"

        out_path = os.path.join(output_folder, patch_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(preset_json)

        logging.info(f"📎 Saved Vital patch: {out_path}")
