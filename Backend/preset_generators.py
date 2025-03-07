# /Users/nathannguyen/Documents/Midi_To_serum/Backend/preset_generators.py

import json
import struct
import os

def generate_diva_preset(mapped_params, output_path):
    """
    Generate a u-he Diva/Hive preset in a simple text format.
    This example writes key=value pairs.
    """
    lines = []
    lines.append("PresetName=Converted Preset")
    for key, value in mapped_params.items():
        lines.append(f"{key}={value}")
    
    with open(output_path, 'w') as f:
        f.write("\n".join(lines))
    print(f"Diva/Hive preset saved to {output_path}")


def generate_fxp(serum_parameters, output_path):
    """
    Generates a minimally "Serum-like" .fxp preset header.
    NOTE: The param_data here is NOT real Serum patch data.
    Serum will likely ignore or fail to load these presets.
    """
    try:
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Typical Steinberg chunk-based FXP header for Serum (VST2):
        chunk_magic = b'CcnK'  # Standard Steinberg header "CcnK"
        fx_magic    = b'FPCh'  # Serum's chunk identifier for .fxp
        version     = 1        # Format version (often 1)
        plugin_id   = b'XfsX'  # Serum's VST2 plugin ID
        fxp_type    = 1        # 1 = Single preset, 2 = Bank

        # Preset name (Serum often uses up to 28 ASCII chars for .fxp)
        preset_name = "MIDI Preset"
        preset_name_bytes = preset_name.encode('ascii').ljust(28, b'\x00')

        # ----------------------------------------------------------------
        # WARNING: The code below just packs an array of floats. 
        # Serum does NOT store patch data as a simple float array.
        # It's a proprietary chunk with wavetables, LFOs, filter data, etc.
        # ----------------------------------------------------------------

        # For demonstration, let's assume you want up to 288 "parameters."
        num_params = 288
        # Fill them from your serum_parameters dict; default to 0.0 if missing:
        param_values = [
            serum_parameters.get(f"Param {i}", 0.0)
            for i in range(num_params)
        ]
        # Pack them as 32-bit (big-endian) floats:
        param_data = struct.pack(f'>{num_params}f', *param_values)

        # Calculate header sizes
        header_format = '>4sI4sI4sI28sI'
        header_size = struct.calcsize(header_format)
        byte_size = header_size + len(param_data)

        # Pack the header
        header = struct.pack(
            header_format,
            chunk_magic,      # "CcnK"
            byte_size,        # total size (header + param_data)
            fx_magic,         # "FPCh"
            version,          # 1
            plugin_id,        # "XfsX"
            fxp_type,         # 1 for single preset
            preset_name_bytes,# 28-byte name
            num_params        # number of floats (placeholder)
        )

        # Write the FXP file (header + param_data)
        with open(output_path, "wb") as fxp_file:
            fxp_file.write(header)
            fxp_file.write(param_data)

        print(f"[INFO] Serum FXP preset written to: {output_path}")
        print("       (Likely *not* a valid Serum patch yet.)")

    except Exception as e:
        print(f"[ERROR] Failed to generate .fxp file: {e}")
