# /Users/nathannguyen/Documents/Midi_To_serum/Backend/vital_mapper.py

import json
import copy
import zlib
import base64
import pretty_midi

# MIDI CC -> Vital parameter mapping (labels here are just examples)
MIDI_TO_VITAL_MAP = {
    0: "bank_select",
    1: "mod_wheel",
    2: "macro2",
    3: "macro3",
    4: "macro4",
    5: "portamento_time",
    6: "data_entry",
    7: "osc_1_level",
    8: "osc_2_level",
    9: "osc_3_level",
    10: "osc_1_pan",
    11: "macro4",
    12: "effect_1_mix",
    13: "effect_2_mix",
    14: "lfo_1_rate",
    15: "lfo_2_rate",
    16: "lfo_3_rate",
    17: "lfo_4_rate",
    18: "osc_1_transpose",
    19: "osc_2_transpose",
    20: "macro1",
    21: "macro2",
    22: "macro3",
    23: "macro4",
    24: "osc_1_wavetable_position",
    25: "osc_2_wavetable_position",
    26: "osc_3_wavetable_position",
    27: "lfo_1_phase",
    28: "lfo_2_phase",
    29: "lfo_3_phase",
    30: "lfo_4_phase",
    31: "effect_1_depth",
    32: "effect_2_depth",
    33: "effect_3_depth",
    34: "effect_4_depth",
    35: "effect_5_depth",
    36: "osc_1_sync",
    37: "osc_2_sync",
    38: "osc_3_sync",
    39: "osc_1_detune",
    40: "osc_2_detune",
    41: "osc_3_detune",
    42: "filter_1_cutoff",
    43: "filter_1_resonance",
    44: "filter_1_drive",
    45: "filter_2_cutoff",
    46: "filter_2_resonance",
    47: "filter_2_drive",
    48: "env_1_attack",
    49: "env_1_decay",
    50: "env_1_sustain",
    51: "env_1_release",
    52: "env_2_attack",
    53: "env_2_decay",
    54: "env_2_sustain",
    55: "env_2_release",
    56: "env_3_attack",
    57: "env_3_decay",
    58: "env_3_sustain",
    59: "env_3_release",
    60: "env_4_attack",
    61: "env_4_decay",
    62: "env_4_sustain",
    63: "env_4_release",
    64: "env_1_sustain",
    65: "portamento_on",
    66: "osc_1_wavetable_blend",
    67: "osc_2_wavetable_blend",
    68: "osc_3_wavetable_blend",
    69: "filter_1_blend",
    70: "filter_1_drive",
    71: "filter_1_resonance",
    72: "env_1_release",
    73: "env_1_attack",
    74: "filter_1_cutoff",
    75: "env_1_decay",
    76: "lfo_1_depth",
    77: "lfo_2_depth",
    78: "lfo_3_depth",
    79: "lfo_4_depth",
    80: "osc_2_level",
    81: "osc_3_level",
    82: "osc_1_phase",
    83: "osc_2_phase",
    84: "osc_3_phase",
    85: "filter_2_drive",
    86: "filter_2_blend",
    87: "filter_2_resonance",
    88: "effect_1_feedback",
    89: "effect_2_feedback",
    90: "effect_3_feedback",
    91: "reverb_dry_wet",
    92: "effect_2_rate",
    93: "chorus_dry_wet",
    94: "delay_time",
    95: "phaser_dry_wet",
    96: "data_increment",
    97: "data_decrement",
    98: "macro1",
    99: "macro2",
    100: "macro3",
    101: "macro4",
    102: "filter_2_cutoff",
    103: "filter_2_resonance",
    104: "filter_2_drive",
    105: "lfo_1_depth",
    106: "lfo_2_depth",
    107: "lfo_3_depth",
    108: "lfo_4_depth",
    109: "lfo_1_phase",
    110: "lfo_2_phase",
    111: "lfo_3_phase",
    112: "delay_feedback",
    113: "eq_low_gain",
    114: "eq_mid_gain",
    115: "eq_high_gain",
    116: "distortion_drive",
    117: "compressor_threshold",
    118: "compressor_ratio",
    119: "flanger_dry_wet",
    120: "all_sound_off",
    121: "reset_all_controllers",
    122: "local_control",
    123: "all_notes_off",
    124: "omni_off",
    125: "omni_on",
    126: "mono_on",
    127: "poly_on",
}

MIDI_TO_VITAL_MAP.update({
    32: "phaser_rate",
    33: "phaser_depth",
    34: "phaser_feedback",
    35: "eq_low_freq",
    36: "eq_low_gain",
    37: "eq_mid_freq",
    38: "eq_mid_gain",
    39: "eq_high_freq",
    40: "eq_high_gain",
    41: "compressor_threshold",
    42: "compressor_ratio",
    43: "compressor_attack",
    44: "compressor_release",
    45: "distortion_drive",
    46: "distortion_mix",
    47: "delay_time",
    48: "delay_feedback",
    49: "delay_wet",
    50: "reverb_size",
    51: "reverb_decay",
    52: "reverb_dry_wet",
    53: "chorus_rate",
    54: "chorus_depth",
    55: "chorus_mix",
    56: "custom_wavetable_1",
    57: "custom_wavetable_2",
    58: "custom_wavetable_3",
    59: "custom_wavetable_4",
    60: "mod_matrix_1",
    61: "mod_matrix_2",
    62: "mod_matrix_3",
    63: "mod_matrix_4"
})


def parse_midi(file_path):
    """
    Extracts MIDI data from a file.
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)

        tempo = midi_data.estimate_tempo()
        notes = []
        control_changes = []
        pitch_bends = []

        for instrument in midi_data.instruments:
            for note in instrument.notes:
                notes.append({
                    "pitch": note.pitch,
                    "velocity": note.velocity,
                    "start": note.start,
                    "end": note.end
                })

            for cc in instrument.control_changes:
                control_changes.append({
                    "controller": cc.number,
                    "value": cc.value,
                    "time": cc.time
                })

            for pb in instrument.pitch_bends:
                pitch_bends.append({
                    "pitch": pb.pitch,
                    "time": pb.time
                })

        return {
            "tempo": tempo,
            "notes": notes,
            "control_changes": control_changes,
            "pitch_bends": pitch_bends
        }

    except Exception as e:
        print(f"❌ Error parsing MIDI file: {e}")
        return {
            "tempo": None,
            "notes": [],
            "control_changes": [],
            "pitch_bends": []
        }


def load_default_vital_preset(default_preset_path):
    """
    Loads the default Vital preset (handling both compressed and uncompressed JSON).
    """
    try:
        with open(default_preset_path, "rb") as f:
            file_data = f.read()

        try:
            # Attempt to decompress (zlib)
            json_data = zlib.decompress(file_data).decode()
        except zlib.error:
            # If it fails, assume plain JSON
            json_data = file_data.decode()

        return json.loads(json_data)

    except Exception as e:
        print(f"❌ Error loading default Vital preset: {e}")
        return None


def set_vital_parameter(preset, param_name, value):
    """
    Safely set a Vital parameter, respecting whether it lives top-level or in 'settings'.
    """
    if param_name.startswith("macro"):
        # e.g. "macro2" -> "macro_control_2"
        macro_number = param_name[-1]
        control_key = f"macro_control_{macro_number}"
        if "settings" not in preset:
            preset["settings"] = {}
        preset["settings"][control_key] = value

    elif param_name in (
        "mod_wheel", "pitch_wheel",
        "env_1_sustain", "filter_1_cutoff",
        "filter_1_resonance", "reverb_dry_wet",
        "chorus_dry_wet", "osc_1_pan",
        "portamento", "portamento_on"
    ):
        # Store these at the top level
        preset[param_name] = value

    else:
        # If needed, check if it belongs in "settings" or top-level
        preset[param_name] = value


def modify_vital_preset(vital_preset, midi_data, snapshot_method="1"):
    """
    Modifies the default Vital preset using extracted MIDI data,
    based on the user's chosen 'snapshot_method'.
    """
    modified_preset = copy.deepcopy(vital_preset)

    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])
    pitch_bends = midi_data.get("pitch_bends", [])

    # Ensure 'modulations' key exists
    if "modulations" not in modified_preset:
        modified_preset["modulations"] = []

    #
    # --- Different Snapshot Methods ---
    #
    if snapshot_method == "1":
        # 1) Single first note
        if notes:
            first_note = notes[0]
            modified_preset["osc_1_transpose"] = first_note["pitch"] - 69
            modified_preset["osc_1_level"] = first_note["velocity"] / 127.0
        else:
            # No notes found
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "2":
        # 2) Average of all notes
        if notes:
            avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
            avg_vel = sum(n["velocity"] for n in notes) / len(notes)
            modified_preset["osc_1_transpose"] = avg_pitch - 69
            modified_preset["osc_1_level"] = avg_vel / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "3":
        # 3) Single moment in time
        print("Enter the time (in seconds) for the snapshot: ", end="")
        time_input = input().strip()
        try:
            target_time = float(time_input)
        except ValueError:
            target_time = 0.0

        active_notes = [n for n in notes if n["start"] <= target_time < n["end"]]
        if active_notes:
            # Average if multiple notes overlap
            avg_pitch = sum(n["pitch"] for n in active_notes) / len(active_notes)
            avg_vel = sum(n["velocity"] for n in active_notes) / len(active_notes)
            modified_preset["osc_1_transpose"] = avg_pitch - 69
            modified_preset["osc_1_level"] = avg_vel / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    #
    # --- Map CC -> Vital parameter ---
    #
    # NOTE: Currently this sets the parameter repeatedly for each CC event,
    # ending on the last CC's value. If you want a single aggregated approach,
    # you'll need to decide how to handle multiple CCs.
    #
    for cc in ccs:
        cc_num = cc["controller"]
        cc_val = cc["value"] / 127.0

        if cc_num in MIDI_TO_VITAL_MAP:
            vital_param = MIDI_TO_VITAL_MAP[cc_num]
            set_vital_parameter(modified_preset, vital_param, cc_val)

    #
    # --- Map pitch bends ---
    #
    # Also sets only the first pitch bend found. Or you can pick last or average.
    #
    if pitch_bends:
        first_bend = pitch_bends[0]
        bend_value = first_bend["pitch"] / 8192.0
        modified_preset["pitch_wheel"] = bend_value
    else:
        modified_preset["pitch_wheel"] = 0.0

    #
    # --- Example additional modulations ---
    #
    # These are optional. They just show how you might add to the "modulations" list.
    #
    modified_preset["modulations"].extend([
        {"destination": "reverb_dry_wet", "source": "macro1"},
        {"destination": "filter_1_cutoff", "source": "macro2"},
        {"destination": "osc_1_level", "source": "velocity"},
        {"destination": "pitch_wheel", "source": "aftertouch"}
    ])

    return modified_preset


def save_vital_preset(vital_preset, output_path):
    """
    Saves the modified Vital preset as uncompressed (human-readable) JSON.
    """
    try:
        json_data = json.dumps(vital_preset, indent=2)
        with open(output_path, "w") as f:
            f.write(json_data)

        print(f"✅ Modified Vital preset saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error saving Vital preset: {e}")
