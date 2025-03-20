# /Users/nathannguyen/Documents/Midi_To_serum/Backend/preset_generators.py

import json
import struct
import os
from config import MIDI_TO_VITAL_MAP

##########################################
# (COMMENTED) Diva/Hive Preset Generation
# Uncomment if/when you want to use Diva/Hive
##########################################
"""
def generate_diva_preset(mapped_params, output_path):
    # Generates a Diva/Hive preset in a simple text-based key=value format.
    lines = []
    lines.append("PresetName=Converted Preset")
    for key, value in mapped_params.items():
        lines.append(f"{key}={value}")
    
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    print(f"Diva/Hive preset saved to {output_path}")
"""

##########################################
# (COMMENTED) Serum-like FXP Preset Generation
# Uncomment if/when you want to use Serum
##########################################
"""
def generate_fxp(serum_parameters, output_path):
    # Generates a minimal 'Serum-like' .fxp file. 
    # NOTE: Not a real Serum patch. Serum may fail to load.

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        chunk_magic = b'CcnK'
        fx_magic    = b'FPCh'
        version     = 1
        plugin_id   = b'XfsX'
        fxp_type    = 1

        preset_name = "MIDI Preset"
        preset_name_bytes = preset_name.encode('ascii').ljust(28, b'\x00')

        num_params = 288
        param_values = [
            serum_parameters.get(f"Param {i}", 0.0)
            for i in range(num_params)
        ]
        param_data = struct.pack(f'>{num_params}f', *param_values)

        header_format = '>4sI4sI4sI28sI'
        header_size = struct.calcsize(header_format)
        byte_size = header_size + len(param_data)

        header = struct.pack(
            header_format,
            chunk_magic,
            byte_size,
            fx_magic,
            version,
            plugin_id,
            fxp_type,
            preset_name_bytes,
            num_params
        )

        with open(output_path, "wb") as fxp_file:
            fxp_file.write(header)
            fxp_file.write(param_data)

        print(f"[INFO] Serum FXP preset written to: {output_path}")
        print("       (Likely not a valid Serum patch.)")

    except Exception as e:
        print(f"[ERROR] Failed to generate .fxp file: {e}")
"""



def apply_sample_oscillator_to_preset(preset, midi_data):
    """
    Checks if 'sample' info is present in midi_data. If so, configures a sample-based
    oscillator in the Vital preset.
    """
    print("🔹 Checking for Sample-Based Oscillator...")

    if not isinstance(midi_data, dict):
        print("⚠️ `midi_data` is invalid. Skipping sample oscillator.")
        return

    sample_info = midi_data.get("sample", {})
    if not isinstance(sample_info, dict) or "samples" not in sample_info:
        print("⚠️ No valid sample-based instrument detected. Skipping sample oscillator.")
        return

    preset["sample"] = {
        "name": sample_info.get("name", "Unknown Sample"),
        "sample_rate": sample_info.get("sample_rate", 44100),
        "length": sample_info.get("length", 44100),
        "samples": sample_info["samples"]
    }

    print(f"✅ Sample-Based Oscillator Applied: {preset['sample']['name']}")
