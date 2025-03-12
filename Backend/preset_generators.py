# /Users/nathannguyen/Documents/Midi_To_serum/Backend/preset_generators.py

import json
import struct
import os
from config import MIDI_TO_VITAL_MAP

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



def apply_effects_to_preset(preset, cc_map):
    """
    Applies effects settings to the Vital preset, setting defaults if no MIDI CCs are mapped.
    """
    print("🔹 Applying effects to preset...")

    # --- REVERB --- (Mapped to CC 91, or use defaults)
    preset["reverb_dry_wet"] = cc_map.get(91, 0.3)  # Default to 30% mix
    preset["reverb_size"] = 0.8
    preset["reverb_decay_time"] = 0.7
    preset["reverb_pre_high_cutoff"] = 100.0
    preset["reverb_high_shelf_cutoff"] = 90.0
    preset["reverb_on"] = 1.0

    # --- CHORUS --- (Mapped to CC 93, or use defaults)
    preset["chorus_dry_wet"] = cc_map.get(93, 0.2)  # Default to 20% mix
    preset["chorus_feedback"] = 0.4
    preset["chorus_frequency"] = -3.0
    preset["chorus_mod_depth"] = 0.5
    preset["chorus_on"] = 1.0

    # --- DELAY --- (Mapped to CC 94, or use defaults)
    preset["delay_dry_wet"] = cc_map.get(94, 0.25)  # Default to 25% mix
    preset["delay_feedback"] = 0.35
    preset["delay_sync"] = 1.0
    preset["delay_tempo"] = 9.0  # Default tempo subdivision
    preset["delay_on"] = 1.0

    # --- FX FILTER --- (Mapped to CC 74, or use defaults)
    preset["filter_fx_cutoff"] = cc_map.get(74, 80.0)  # Default cutoff at 80
    preset["filter_fx_resonance"] = 0.5
    preset["filter_fx_model"] = 6.0  # A common filter type
    preset["filter_fx_on"] = 1.0

    # --- DISTORTION --- (No CC, default values, optionally controlled by Macro 1)
    preset["distortion_drive"] = 0.5
    preset["distortion_mix"] = 0.3
    preset["distortion_type"] = 4.0  # Some distortion type
    preset["distortion_on"] = 1.0

    # Allow Macro 1 to control distortion if it's used
    preset["modulations"].append({
        "source": "macro_control_1",
        "destination": "distortion_drive",
        "amount": 0.5
    })

    # --- PHASER --- (No CC, default values, optionally controlled by LFO 2)
    preset["phaser_dry_wet"] = 0.2
    preset["phaser_feedback"] = 0.3
    preset["phaser_frequency"] = -2.0
    preset["phaser_on"] = 1.0

    # Link Phaser to LFO 2
    preset["modulations"].append({
        "source": "lfo_2",
        "destination": "phaser_frequency",
        "amount": 0.4
    })

    # --- FLANGER --- (No CC, default values, optionally controlled by LFO 3)
    preset["flanger_dry_wet"] = 0.3
    preset["flanger_feedback"] = 0.4
    preset["flanger_frequency"] = 1.5
    preset["flanger_on"] = 1.0

    # Link Flanger to LFO 3
    preset["modulations"].append({
        "source": "lfo_3",
        "destination": "flanger_frequency",
        "amount": 0.4
    })

    # --- EQ (Default settings, no CC) ---
    preset["eq_low_cutoff"] = 56.0
    preset["eq_low_gain"] = -3.0
    preset["eq_band_cutoff"] = 80.0
    preset["eq_band_gain"] = 0.0
    preset["eq_high_cutoff"] = 100.0
    preset["eq_high_gain"] = 2.0
    preset["eq_on"] = 1.0

    # --- COMPRESSOR (Default settings, no CC) ---
    preset["compressor_attack"] = 0.5
    preset["compressor_release"] = 0.5
    preset["compressor_mix"] = 1.0
    preset["compressor_low_gain"] = 2.0
    preset["compressor_band_gain"] = 0.0
    preset["compressor_high_gain"] = -1.0
    preset["compressor_on"] = 1.0

    print("✅ Effects applied successfully!")



def apply_random_modulators_to_preset(preset, cc_map):
    """
    Adds Random Modulators (Random 1–4) to the preset, with CC mapping if available.
    """
    print("🔹 Applying Random Modulators to preset...")

    for i in range(1, 5):  # Random 1 to 4
        random_freq_key = f"random_{i}_frequency"
        random_sync_key = f"random_{i}_sync"
        random_tempo_key = f"random_{i}_tempo"
        random_on_key = f"random_{i}_on"

        # Assign default values
        preset[random_freq_key] = cc_map.get(50 + i, 1.0)  # Default frequency = 1Hz (CC 51–54 could override)
        preset[random_sync_key] = 1.0  # Synced to tempo
        preset[random_tempo_key] = 8.0  # Default tempo sync subdivision
        preset[random_on_key] = 1.0  # Enable the random modulator

    # Add `random_values` array to store seeds
    preset["random_values"] = [
        {"seed": 4},
        {"seed": 4},
        {"seed": 4},
        {"seed": 4}
    ]

    print("✅ Random Modulators applied successfully!")



def apply_global_settings_to_preset(preset, cc_map):
    """
    Configures global settings like polyphony, legato, portamento, tuning, and MPE.
    """
    print("🔹 Applying Global Settings to preset...")

    # --- POLYPHONY --- (Default to 8 voices, or user-defined)
    preset["polyphony"] = cc_map.get(127, 8.0)  # Default to 8 voices if no CC 127 is mapped

    # --- LEGATO MODE --- (If active, notes glide into each other)
    preset["legato"] = 1.0 if cc_map.get(68, 0) > 0 else 0.0  # CC 68 is Legato Toggle

    # --- PORTAMENTO (GLIDE) SETTINGS ---
    preset["portamento_time"] = cc_map.get(5, 0.2)  # CC 5 can control glide time (Default: 0.2s)
    preset["portamento_scale"] = 1.0  # Standard glide behavior
    preset["portamento_force"] = 0.0  # Off unless explicitly enabled

    # --- PITCH BEND RANGE ---
    preset["pitch_bend_range"] = cc_map.get(100, 12.0)  # Default to 12 semitones unless overridden

    # --- TRANSPOSE & TUNING ---
    preset["voice_transpose"] = 0.0  # No transposition by default
    preset["voice_tune"] = 0.0  # No fine-tuning by default

    # --- MPE (MIDI Polyphonic Expression) ---
    preset["mpe_enabled"] = cc_map.get(126, 0.0)  # CC 126 enables/disables MPE

    print("✅ Global Settings applied successfully!")



def apply_sample_oscillator_to_preset(preset, midi_data):
    """
    Detects if a sample-based MIDI instrument is used and sets the `sample` field in the Vital preset.
    """
    print("🔹 Checking for Sample-Based Oscillator...")

    # Check if MIDI contains sample-based instruments (e.g., drums, one-shot samples)
    if "sample" in midi_data:
        sample_info = midi_data["sample"]

        preset["sample"] = {
            "name": sample_info.get("name", "Unknown Sample"),
            "sample_rate": sample_info.get("sample_rate", 44100),  # Default 44.1kHz
            "length": sample_info.get("length", 44100),  # Default 1 second at 44.1kHz
            "samples": sample_info.get("samples", "")  # Base64-encoded sample data
        }

        print(f"✅ Sample-Based Oscillator Applied: {preset['sample']['name']}")
    else:
        print("⚠️ No sample-based instrument detected. Skipping sample oscillator.")



def apply_sample_oscillator_to_preset(preset, midi_data):
    """
    Detects if a sample-based MIDI instrument is used and sets the `sample` field in the Vital preset.
    Ensures `midi_data` contains valid sample information before processing.
    """
    print("🔹 Checking for Sample-Based Oscillator...")

    # Validate `midi_data` and check for sample information
    if not isinstance(midi_data, dict):
        print("⚠️ Warning: `midi_data` is not a valid dictionary. Skipping sample oscillator.")
        return

    sample_info = midi_data.get("sample", {})
    if not isinstance(sample_info, dict) or "samples" not in sample_info:
        print("⚠️ No valid sample-based instrument detected. Skipping sample oscillator.")
        return

    # Apply sample settings
    preset["sample"] = {
        "name": sample_info.get("name", "Unknown Sample"),
        "sample_rate": sample_info.get("sample_rate", 44100),  # Default 44.1kHz
        "length": sample_info.get("length", 44100),  # Default 1 second at 44.1kHz
        "samples": sample_info["samples"]  # Base64-encoded sample data
    }

    print(f"✅ Sample-Based Oscillator Applied: {preset['sample']['name']}")



