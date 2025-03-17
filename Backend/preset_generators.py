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

def apply_effects_to_preset(preset, cc_map):
    """
    Applies effects settings to the Vital preset, setting defaults if no MIDI CCs are mapped.
    """
    print("🔹 Applying effects to preset...")

    # Ensure 'modulations' list exists
    if "modulations" not in preset:
        preset["modulations"] = []

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

    # --- DISTORTION --- (No CC => defaults; optionally controlled by Macro 1)
    preset["distortion_drive"] = 0.5
    preset["distortion_mix"] = 0.3
    preset["distortion_type"] = 4.0
    preset["distortion_on"] = 1.0

    preset["modulations"].append({
        "source": "macro_control_1",
        "destination": "distortion_drive",
        "amount": 0.5
    })

    # --- PHASER --- (No CC => default; optionally LFO 2)
    preset["phaser_dry_wet"] = 0.2
    preset["phaser_feedback"] = 0.3
    preset["phaser_frequency"] = -2.0
    preset["phaser_on"] = 1.0
    preset["modulations"].append({
        "source": "lfo_2",
        "destination": "phaser_frequency",
        "amount": 0.4
    })

    # --- FLANGER --- (No CC => default; optionally LFO 3)
    preset["flanger_dry_wet"] = 0.3
    preset["flanger_feedback"] = 0.4
    preset["flanger_frequency"] = 1.5
    preset["flanger_on"] = 1.0
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

    # --- COMPRESSOR (Defaults) ---
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
    Adds Random Modulators (Random 1–4) to the preset, with CC-based overrides if available.
    """
    print("🔹 Applying Random Modulators to preset...")

    if "modulations" not in preset:
        preset["modulations"] = []

    for i in range(1, 5):  # Random 1..4
        freq_key = f"random_{i}_frequency"
        sync_key = f"random_{i}_sync"
        tempo_key = f"random_{i}_tempo"
        on_key = f"random_{i}_on"

        # If CC 51 => Random1 freq, CC 52 => Random2 freq, etc.
        preset[freq_key] = cc_map.get(50 + i, 1.0)
        preset[sync_key] = 1.0
        preset[tempo_key] = 8.0
        preset[on_key] = 1.0

    preset["random_values"] = [
        {"seed": 4},
        {"seed": 4},
        {"seed": 4},
        {"seed": 4}
    ]

    print("✅ Random Modulators applied successfully!")


def apply_global_settings_to_preset(preset, cc_map):
    """
    Configures various global Vital parameters (polyphony, legato, portamento, etc.).
    """
    print("🔹 Applying Global Settings to preset...")

    # Ensure modulations is present
    if "modulations" not in preset:
        preset["modulations"] = []

    # Polyphony => CC127 or default 8
    preset["polyphony"] = cc_map.get(127, 8.0)

    # Legato => CC68 toggle
    preset["legato"] = 1.0 if cc_map.get(68, 0) > 0 else 0.0

    # Portamento => CC5
    preset["portamento_time"] = cc_map.get(5, 0.2)
    preset["portamento_scale"] = 1.0
    preset["portamento_force"] = 0.0

    # Pitch Bend Range => CC100
    preset["pitch_bend_range"] = cc_map.get(100, 12.0)

    # Transpose / Tuning
    preset["voice_transpose"] = 0.0
    preset["voice_tune"] = 0.0

    # MPE => CC126
    preset["mpe_enabled"] = cc_map.get(126, 0.0)

    print("✅ Global Settings applied successfully!")


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
