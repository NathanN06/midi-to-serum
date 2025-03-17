# vital_mapper.py

import json
import copy
import zlib
import base64
import pretty_midi
import re
import numpy as np
import os

# Local imports
from midi_analysis import estimate_frame_count
from midi_parser import parse_midi
from config import (
    MIDI_TO_VITAL_MAP,
    DEFAULT_ADSR,
    DEFAULT_WAVEFORM,
    HARMONIC_SCALING,
    OUTPUT_DIR
)

def load_default_vital_preset(default_preset_path):
    """
    Loads the default Vital preset (handling both compressed and uncompressed JSON)
    and ensures a structure with 3 keyframes for Oscillator 1.
    """
    try:
        with open(default_preset_path, "rb") as f:
            file_data = f.read()

        # Try zlib decompression; if it fails, assume it's plain JSON
        try:
            json_data = zlib.decompress(file_data).decode()
        except zlib.error:
            json_data = file_data.decode()

        preset = json.loads(json_data)
        
        # Ensure we have at least 3 keyframes in the first oscillator
        if "groups" in preset and len(preset["groups"]) > 0:
            group = preset["groups"][0]
            if "components" in group and len(group["components"]) > 0:
                component = group["components"][0]
                if "keyframes" in component and len(component["keyframes"]) != 3:
                    print("Warning: Adjusting preset to use 3 keyframes for Oscillator 1")

                    # Placeholder wave data (shortened here for brevity)
                    default_wave_data = (
                        "ABAAugAYwLoAFCC7ABxguwASkLsAFrC7ABrQuwAe8LsAEQi8ABMYvAAVKLwAFzi8ABlIvAAbWLwAHWi8AB94vIAQhLyAEYy8gBKUvIATnLyAFKS8gBWsvIAWtLyAF7y8gBjEvIAZzLyAGtS8gBvcvIAc5LyAHey8gB70vIAf/LxAEAK9wBAGvUARCr3AEQ69QBISvcASFr1AExq9wBMevUAUIr3AFCa9QBUqvcAVLr1AFjK9wBY2vUAXOr3AFz69QBhCvcAYRr1AGUq9wBlOvUAaUr3AGla9QBtavcAbXr1AHGK9wBxmvUAdar3AHW69QB5yvcAedr1AH3q9wB9+vSAQgb1gEIO9oBCFveAQh70gEYm9YBGLvaARjb3gEY+9IBKRvWASk72gEpW94BKXvSATmb1gE5u9oBOdveATn70gFKG9YBSjvaAUpb3gFKe9IBWpvWAVq72gFa294BWvvSAWsb1gFrO9oBa1veAWt70gF7m9YBe7vaAXvb3gF7+9IBjBvWAYw72gGMW94BjHvSAZyb1gGcu9oBnNveAZz70gGtG9YBrTvaAa1b3gGte9IBvZvWAb272gG9294BvfvSAc4b1gHOO9oBzlveAc570gHem9YB3rvaAd7b3gHe+9IB7xvWAe872gHvW94B73vSAf+b1gH/u9oB/9veAf/70QkAC+MJABvlCQAr5wkAO+kJAEvrCQBb7QkAa+8JAHvhCRCL4wkQm+UJEKvnCRC76QkQy+sJENvtCRDr7wkQ++EJIQvjCSEb5QkhK+cJITvpCSFL6wkhW+0JIWvvCSF74Qkxi+MJMZvlCTGr5wkxu+kJMcvrCTHb7Qkx6+8JMfvhCUIL4wlCG+UJQivnCUI76QlCS+sJQlvtCUJr7wlCe+EJUovjCVKb5QlSq+cJUrvpCVLL6wlS2+0JUuvvCVL74QljC+MJYxvlCWMr5wljO+kJY0vrCWNb7Qlja+8JY3vhCXOL4wlzm+UJc6vnCXO76Qlzy+sJc9vtCXPr7wlz++EJhAvjCYQb5QmEK+cJhDvpCYRL6wmEW+0JhGvvCYR74QmUi+MJlJvlCZSr5wmUu+kJlMvrCZTb7QmU6+8JlPvhCaUL4wmlG+UJpSvnCaU76QmlS+sJpVvtCaVr7wmle+EJtYvjCbWb5Qm1q+cJtbvpCbXL6wm12+0JtevvCbX74QnGC+MJxhvlCcYr5wnGO+kJxkvrCcZb7QnGa+8JxnvhCdaL4wnWm+UJ1qvnCda76QnWy+sJ1tvtCdbr7wnW++EJ5wvjCecb5QnnK+cJ5zvpCedL6wnnW+0J52vvCed74Qn3i+MJ95vlCfer5wn3u+kJ98vrCffb7Qn36+8J9/vghQgL4c0IC+LFCBvjzQgb5MUIK+XNCCvmxQg7580IO+jFCEvpzQhL6sUIW+vNCFvsxQhr7c0Ia+7FCHvvzQh74MUYi+HNGIvixRib480Ym+TFGKvlzRir5sUYu+fNGLvoxRjL6c0Yy+rFGNvrzRjb7MUY6+3NGOvuxRj7780Y++DFKQvhzSkL4sUpG+PNKRvkxSkr5c0pK+bFKTvnzSk76MUpS+nNKUvqxSlb680pW+zFKWvtzSlr7sUpe+/NKXvgxTmL4c05i+LFOZvjzTmb5MU5q+XNOavmxTm75805u+jFOcvpzTnL6sU52+vNOdvsxTnr7c056+7FOfvvzTn74MVKC+HNSgvixUob481KG+TFSivlzUor5sVKO+fNSjvoxUpL6c1KS+rFSlvrzUpb7MVKa+3NSmvuxUp7781Ke+DFWovhzVqL4sVam+PNWpvkxVqr5c1aq+bFWrvnzVq76MVay+nNWsvqxVrb681a2+zFWuvtzVrr7sVa++/NWvvgxWsL4c1rC+LFaxvjzWsb5MVrK+XNayvmxWs7581rO+jFa0vpzWtL6sVrW+vNa1vsxWtr7c1ra+7Fa3vvzWt74MV7i+HNe4vixXub4817m+TFe6vlzXur5sV7u+fNe7voxXvL6c17y+rFe9vrzXvb7MV76+3Ne+vuxXv77817++DFjAvhzYwL4sWMG+PNjBvkxYwr5c2MK+bFjDvnzYw76MWMS+nNjEvqxYxb682MW+zFjGvtzYxr7sWMe+/NjHvgxZyL4c2ci+LFnJvjzZyb5MWcq+XNnKvmxZy7582cu+jFnMvpzZzL6sWc2+vNnNvsxZzr7c2c6+7FnPvvzZz74MWtC+HNrQvixa0b482tG+TFrSvlza0r5sWtO+fNrTvoxa1L6c2tS+rFrVvrza1b7MWta+3NrWvuxa17782te+DFvYvhzb2L4sW9m+PNvZvkxb2r5c29q+bFvbvnzb276MW9y+nNvcvqxb3b68292+zFvevtzb3r7sW9++/Nvfvgxc4L4c3OC+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znUuP8Y1Lj++9S0/trUtP651LT+mNS0/nvUsP5a1LD+OdSw/hjUsP371Kz92tSs/bnUrP2Y1Kz9e9So/VrUqP051Kj9GNSo/PvUpPza1KT8udSk/JjUpPx71KD8WtSg/DnUoPwY1KD/+9Cc/9rQnP+50Jz/mNCc/3vQmP9a0Jj/OdCY/xjQmP770JT+2tCU/rnQlP6Y0JT+e9CQ/lrQkP450JD+GNCQ/fvQjP3a0Iz9udCM/ZjQjP170Ij9WtCI/TnQiP0Y0Ij8+9CE/NrQhPy50IT8mNCE/HvQgPxa0ID8OdCA/BjQgP/7zHz/2sx8/7nMfP+YzHz/e8x4/1rMeP85zHj/GMx4/vvMdP7azHT+ucx0/pjMdP57zHD+Wsxw/jnMcP4YzHD9+8xs/drMbP25zGz9mMxs/XvMaP1azGj9Ocxo/RjMaPz7zGT82sxk/LnMZPyYzGT8e8xg/FrMYPw5zGD8GMxg//vIXP/ayFz/uchc/5jIXP97yFj/WshY/znIWP8YyFj++8hU/trIVP65yFT+mMhU/nvIUP5ayFD+OchQ/hjIUP37yEz92shM/bnITP2YyEz9e8hI/VrISP05yEj9GMhI/PvIRPzayET8uchE/JjIRPx7yED8WshA/DnIQPwYyED/+8Q8/9rEPP+5xDz/mMQ8/3vEOP9axDj/OcQ4/xjEOP77xDT+2sQ0/rnENP6YxDT+e8Qw/lrEMP45xDD+GMQw/fvELP3axCz9ucQs/ZjELP17xCj9WsQo/TnEKP0YxCj8+8Qk/NrEJPy5xCT8mMQk/HvEIPxaxCD8OcQg/BjEIP/7wBz/2sAc/7nAHP+YwBz/e8AY/1rAGP85wBj/GMAY/vvAFP7awBT+ucAU/pjAFP57wBD+WsAQ/jnAEP4YwBD9+8AM/drADP25wAz9mMAM/XvACP1awAj9OcAI/RjACPz7wAT82sAE/LnABPyYwAT8e8AA/FrAAPw5wAD8GMAA//N//Puxf/z7c3/4+zF/+Przf/T6sX/0+nN/8Poxf/D583/s+bF/7Plzf+j5MX/o+PN/5Pixf+T4c3/g+DF/4Pvze9z7sXvc+3N72Psxe9j683vU+rF71Ppze9D6MXvQ+fN7zPmxe8z5c3vI+TF7yPjze8T4sXvE+HN7wPgxe8D783e8+7F3vPtzd7j7MXe4+vN3tPqxd7T6c3ew+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"
                        # truncated base64 data
                    )

                    component["keyframes"] = [
                        {"position": 0.0, "wave_data": default_wave_data},
                        {"position": 0.5, "wave_data": default_wave_data},
                        {"position": 1.0, "wave_data": default_wave_data}
                    ]
        return preset

    except Exception as e:
        print(f"❌ Error loading default Vital preset: {e}")
        return None


def generate_lfo_shape_from_cc(cc_data, num_points=16):
    """
    Generates an LFO shape based on MIDI CC automation.
    Converts CC values into a set of time/value points in Vital's LFO JSON format.
    """
    if not cc_data:
        print("⚠️ No MIDI CC data found. Skipping LFO generation.")
        return None

    # Sort CCs by time
    cc_data = sorted(cc_data, key=lambda x: x["time"])
    times = np.array([cc["time"] for cc in cc_data])
    values = np.array([cc["value"] / 127.0 for cc in cc_data])  # 0-1

    # Create a time axis for interpolation (num_points long, from min time to max time)
    resampled_times = np.linspace(times[0], times[-1], num_points)
    resampled_values = np.interp(resampled_times, times, values)

    # Combine times+values into the "points" array per Vital's LFO definition
    lfo_shape = {
        "name": "MIDI_CC_LFO",
        "num_points": num_points,
        "points": list(resampled_times) + list(resampled_values),  # [time1..timeN, val1..valN]
        "powers": [0.0] * num_points,  # Linear interpolation
        "smooth": True
    }

    print(f"✅ Created LFO from MIDI CC data: {lfo_shape}")
    return lfo_shape


def add_envelopes_to_preset(preset, notes):
    """
    Adds ADSR envelope settings to the Vital preset based on MIDI note characteristics.
    If no notes, uses a default ADSR from config.
    """
    if not notes:
        print("⚠️ No notes found. Using default envelope settings.")
        preset.update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Average note length => approximate A, D, R times
    avg_note_length = sum(n["end"] - n["start"] for n in notes) / len(notes)

    # Sustain level => average velocity
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level = (avg_velocity / 127.0) if avg_velocity > 0 else 0.5

    # Scale ADSR from average note length
    attack_time = min(avg_note_length * 0.05, 0.2)
    decay_time = min(avg_note_length * 0.15, 0.7)
    release_time = min(avg_note_length * 0.3, 1.5)

    preset.update({
        "env_1_attack":  attack_time,
        "env_1_decay":   decay_time,
        "env_1_sustain": sustain_level,
        "env_1_release": release_time
    })
    print(f"✅ ENV1: A={attack_time:.2f}, D={decay_time:.2f}, S={sustain_level:.2f}, R={release_time:.2f}")

    # Optionally apply similar logic to ENV2
    preset.update({
        "env_2_attack":  attack_time * 0.7,
        "env_2_decay":   decay_time * 0.8,
        "env_2_sustain": sustain_level * 0.9,
        "env_2_release": release_time * 1.2
    })
    print("✅ ENV2 applied with slightly different scaling.")


def add_lfos_to_preset(preset, cc_data, notes, lfo_target="filter_1_cutoff"):
    """
    Adds an LFO to the Vital preset. If CC data is provided, we build the LFO from it;
    otherwise, we build a simple "adaptive" LFO from note duration.
    """
    if not cc_data:
        print("⚠️ No MIDI CC data. Generating LFO from average note timing.")
        if notes:
            avg_len = sum(n["end"] - n["start"] for n in notes) / len(notes)
            # Just pick an LFO rate in range [0.5..8] inversely related to avg note length
            lfo_rate = max(0.5, min(8.0, 1.0 / avg_len))
        else:
            lfo_rate = 1.0

        # Build a simple up-down LFO shape
        lfo_shape = {
            "name": "Adaptive_LFO",
            "num_points": 16,
            "points": [0.0, 0.25, 0.5, 0.75, 1.0] * 2,
            "powers": [0.0]*16,
            "smooth": True
        }
        print(f"✅ Generated a default LFO at {lfo_rate}Hz.")
    else:
        lfo_shape = generate_lfo_shape_from_cc(cc_data)
        if not lfo_shape:
            print("❌ Could not generate LFO from CC. Exiting LFO step.")
            return
        # Random slight variation
        lfo_rate = 2.0 + np.random.uniform(-0.5, 0.5)

    if "lfos" not in preset:
        preset["lfos"] = []

    # Add the shape
    preset["lfos"].append(lfo_shape)
    preset["lfo_1_frequency"] = lfo_rate

    # Add a modulation (LFO1 -> `lfo_target`)
    if "modulations" not in preset:
        preset["modulations"] = []
    preset["modulations"].append({
        "source": "lfo_1",
        "destination": lfo_target,
        "amount": 0.7
    })

    print(f"✅ LFO1 -> {lfo_target} at {lfo_rate:.2f}Hz applied.")


def apply_dynamic_env1_from_midi(preset, midi_data):
    """
    Sets Env1 ADSR based on average note length and velocity in midi_data.
    If no notes, uses fallback values.
    """

    notes = midi_data.get("notes", [])
    if not notes:
        # Fallback if no notes
        avg_length = 0.5
        avg_vel = 80
    else:
        # Average note length
        total_length = sum(n["end"] - n["start"] for n in notes)
        avg_length = total_length / len(notes)
        # Average velocity
        total_vel = sum(n["velocity"] for n in notes)
        avg_vel = total_vel / len(notes)

    # Scale times from avg_length
    attack_time   = max(0.01, 0.1 * avg_length)
    decay_time    = max(0.05, 0.3 * avg_length)
    release_time  = max(0.1, 0.5 * avg_length)
    sustain_level = min(1.0, avg_vel / 127.0)

    # Clamp so they don’t get too large
    attack_time   = min(attack_time, 2.0)
    decay_time    = min(decay_time, 3.0)
    release_time  = min(release_time, 5.0)

    # Power (curvature) examples
    attack_power  = 0.0   # 0=linear, negative=exp, positive=log
    decay_power   = -2.0
    release_power = -2.0

    preset["env_1_attack"]        = attack_time
    preset["env_1_attack_power"]  = attack_power
    preset["env_1_decay"]         = decay_time
    preset["env_1_decay_power"]   = decay_power
    preset["env_1_sustain"]       = sustain_level
    preset["env_1_release"]       = release_time
    preset["env_1_release_power"] = release_power
    preset["env_1_delay"]         = 0.0
    preset["env_1_hold"]          = 0.0

    print(f"✅ Env1 set dynamically from MIDI notes. "
          f"(Attack={attack_time:.2f}s, Decay={decay_time:.2f}s, "
          f"Sustain={sustain_level:.2f}, Release={release_time:.2f}s)")


def build_lfo_from_cc1(preset, midi_data, lfo_idx=1, one_shot=False):
    """
    Builds a multi-point LFO shape from CC1 (mod wheel) data.
    If none found, uses a fallback. Then automatically modulates `filter_1_cutoff`.

    :param preset:    The Vital preset dictionary.
    :param midi_data: Parsed MIDI dict with "control_changes", "notes", etc.
    :param lfo_idx:   Which LFO number to overwrite (1..8 typically).
    :param one_shot:  If True, treat LFO as one-shot (acts like an envelope).
                      You may need to set the actual one-shot key in Vital depending on version.
    """

    # Gather all CC1 events
    cc_events = [cc for cc in midi_data.get("control_changes", []) if cc["controller"] == 1]
    if not cc_events:
        print("⚠️ No CC1 (mod wheel) data found. Using fallback LFO shape.")
        # Basic triangle fallback
        times  = [0.0, 0.5, 1.0]
        values = [0.0, 1.0, 0.0]
    else:
        # Sort by time
        cc_events.sort(key=lambda x: x["time"])
        times  = [cc["time"] for cc in cc_events]
        values = [cc["value"] / 127.0 for cc in cc_events]
        # Normalize times to [0..1]
        max_t = times[-1] if times[-1] != 0 else 1e-6
        times = [t / max_t for t in times]

    # Flatten times + values into Vital’s "points" format
    points = times + values
    num_points = len(times)
    powers = [0.0] * num_points  # Use 0 for linear segments

    # Ensure "lfos" array exists
    if "lfos" not in preset:
        preset["lfos"] = []

    # Make sure we have enough entries for LFO #lfo_idx
    while len(preset["lfos"]) < lfo_idx:
        preset["lfos"].append({
            "name": f"LFO {len(preset['lfos'])+1}",
            "num_points": 2,
            "points": [0.0, 1.0,  1.0, 0.0],
            "powers": [0.0, 0.0],
            "smooth": False
        })

    # Overwrite the chosen LFO
    lfo_array_index = lfo_idx - 1
    preset["lfos"][lfo_array_index] = {
        "name": f"CC1_LFO{lfo_idx}",
        "num_points": num_points,
        "points": points,
        "powers": powers,
        "smooth": False
    }

    # Set top-level LFO parameters
    prefix = f"lfo_{lfo_idx}"
    preset[f"{prefix}_frequency"] = 1.0
    preset[f"{prefix}_sync"]      = 0.0
    preset[f"{prefix}_tempo"]     = 4.0

    # If you know Vital’s key for one-shot, set it here:
    # Example guess:
    # if one_shot:
    #     preset["lfo_1_trigger_mode"] = 1  # or whichever key your Vital version uses

    # Add a modulation to filter_1_cutoff
    if "modulations" not in preset:
        preset["modulations"] = []
    preset["modulations"].append({
        "source": f"lfo_{lfo_idx}",
        "destination": "filter_1_cutoff",
        "amount": 0.5
    })

    print(f"✅ Built LFO{lfo_idx} from CC1 data (points={num_points}). one_shot={one_shot} -> filter_1_cutoff.")


def set_vital_parameter(preset, param_name, value):
    """
    Safely set a Vital parameter, placing it in top-level or 'settings' as needed.
    Also handles macros specifically.
    """
    if "settings" not in preset:
        preset["settings"] = {}

    if param_name.startswith("macro"):
        # e.g. 'macro4' => 'macro_control_4'
        macro_number = int(param_name.replace("macro", ""))
        control_key = f"macro_control_{macro_number}"
        preset["settings"][control_key] = value
    else:
        preset[param_name] = value


def update_settings(modified_preset, notes, snapshot_method):
    """
    Sets Oscillator 1 transpose/level based on the chosen snapshot method:
      1 = first note
      2 = average note
      3 = single user-specified time
    """
    if snapshot_method == "1":
        if notes:
            note = notes[0]
            modified_preset["osc_1_transpose"] = note["pitch"] - 69
            modified_preset["osc_1_level"] = note["velocity"] / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "2":
        if notes:
            avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
            avg_vel = sum(n["velocity"] for n in notes) / len(notes)
            modified_preset["osc_1_transpose"] = avg_pitch - 69
            modified_preset["osc_1_level"] = avg_vel / 127.0
        else:
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5

    elif snapshot_method == "3":
        try:
            snap_time = float(input("Enter snapshot time (sec): ").strip())
        except ValueError:
            print("Invalid time input, defaulting to method 1.")
            snap_time = None

        chosen_note = None
        if snap_time is not None:
            for n in notes:
                if n["start"] <= snap_time < n["end"]:
                    chosen_note = n
                    break
        if chosen_note:
            modified_preset["osc_1_transpose"] = chosen_note["pitch"] - 69
            modified_preset["osc_1_level"] = chosen_note["velocity"] / 127.0
        else:
            print("No note active at that time. Using default.")
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5


def add_modulations(modified_preset, ccs):
    """
    Map MIDI CC -> Vital parameter directly, and store final modulations.
    """
    print("\n🔍 Debug: Processing MIDI CCs...")
    cc_map = {}
    for cc_event in ccs:
        val_normalized = cc_event["value"] / 127.0
        cc_map[cc_event["controller"]] = val_normalized

    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            set_vital_parameter(modified_preset, param, cc_val)
            print(f"✅ CC{cc_num} -> {param} = {cc_val}")

    print("\n🔍 Debug: Final modulations:")
    if "modulations" not in modified_preset:
        modified_preset["modulations"] = []
    print(json.dumps(modified_preset["modulations"], indent=2))


def generate_frame_waveform(midi_data, frame_idx, num_frames, frame_size, waveform_type="saw"):
    """
    Generate a single float32 waveform frame for Vital.
    Dynamically scales harmonics based on velocity/CC, plus a morph factor.
    """
    notes = midi_data.get("notes", [])
    ccs = {
        cc["controller"]: cc["value"] / 127.0
        for cc in midi_data.get("control_changes", [])
    }

    if not notes:
        # fallback => single A4 note
        notes = [{"pitch": 69, "velocity": 100}]

    note = notes[frame_idx % len(notes)]
    pitch = note["pitch"]
    velocity = note["velocity"] / 127.0

    # CC1 => mod wheel => harmonic boost
    harmonic_boost = HARMONIC_SCALING.get(waveform_type, 1) * ccs.get(1, 0.5)

    # Build a phase array
    phase = np.linspace(0, 2*np.pi, frame_size, endpoint=False)

    # Morph factor => 0..1 across frames
    if num_frames > 1:
        morph = frame_idx / (num_frames - 1)
    else:
        morph = 0
    harmonic_intensity = (velocity * harmonic_boost) * (0.5 + 0.5 * morph)

    # Construct the wave
    if waveform_type == "sine":
        waveform = np.sin(phase)
    elif waveform_type == "saw":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / h) * np.sin(h * phase)
             for h in range(1, max_harm)],
            axis=0
        )
    elif waveform_type == "square":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / h) * np.sin(h * phase)
             for h in range(1, max_harm, 2)],
            axis=0
        )
    elif waveform_type == "triangle":
        max_harm = int(10 * harmonic_intensity) or 1
        waveform = np.sum(
            [(1.0 / (h**2)) * (-1)**((h-1)//2) * np.sin(h * phase)
             for h in range(1, max_harm, 2)],
            axis=0
        )
    elif waveform_type == "pulse":
        pulse_width = ccs.get(2, 0.5)  # CC2 => width
        waveform = np.where(
            phase < (2*np.pi*pulse_width),
            1.0,
            -1.0
        )
    else:
        waveform = np.sin(phase)  # fallback

    waveform *= harmonic_intensity
    # Normalize to avoid clipping
    max_val = np.max(np.abs(waveform)) or 1.0
    waveform /= max_val

    return waveform.astype(np.float32)


def generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048):
    """
    Generate 3 structured wavetable frames for Vital:
    - Frame 1: Blended sine & saw (attack phase)
    - Frame 2: Complex harmonics + **stronger FM synthesis** (sustain phase)
    - Frame 3: Pulsating saw-triangle blend with **deeper phase distortion** (release phase)
    """

    notes = midi_data.get("notes", [])
    ccs = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    if not notes:
        # Fallback to a single A4 note
        notes = [{"pitch": 69, "velocity": 100}]

    # Extract first, average, and last note characteristics
    first_note = notes[0]
    last_note = notes[-1]
    avg_pitch = sum(n["pitch"] for n in notes) / len(notes)
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)

    # Generate waveforms for each frame
    frames = []
    for i, note in enumerate([first_note, {"pitch": avg_pitch, "velocity": avg_velocity}, last_note]):
        pitch = note["pitch"]
        velocity = note["velocity"] / 127.0

        # Use CC1 (mod wheel) to affect harmonics
        harmonic_boost = HARMONIC_SCALING.get(DEFAULT_WAVEFORM, 1) * (ccs.get(1, 0.5) + 0.5)  # Boosted

        # Generate phase array
        phase = np.linspace(0, 2*np.pi, frame_size, endpoint=False)

        if i == 0:  # 🔹 Frame 1 (Attack) - Sine + Bright Saw
            sine_wave = np.sin(phase) * velocity
            saw_wave = np.sum([(1.0 / h) * np.sin(h * phase) for h in range(1, 8)], axis=0) * (velocity * 0.4)
            waveform = sine_wave + saw_wave  # Stronger saw harmonics

        elif i == 1:  # 🔹 Frame 2 (Sustain) - **Stronger FM Synthesis**
            mod_freq = 3.0 + 5.0 * velocity  # Higher modulation frequency
            mod_index = 0.7  # **Increased FM depth**
            fm_mod = np.sin(phase * mod_freq) * mod_index
            harmonics = np.sum([(1.0 / h) * np.sin(h * phase + fm_mod) for h in range(1, int(15 * harmonic_boost))], axis=0)
            waveform = harmonics * velocity

        else:  # 🔹 Frame 3 (Release) - **Deeper Phase Distortion**
            triangle_wave = np.abs(np.mod(phase / np.pi, 2) - 1) * 2 - 1  # Triangle wave
            saw_wave = np.sign(np.sin(phase * (pitch / 64.0))) * velocity  # Faster saw modulation
            phase_distortion = np.sin(phase * 3.5) * 0.4  # **Stronger phase warping**
            waveform = (triangle_wave * 0.6 + saw_wave * 0.4) + phase_distortion  # **More distortion applied**

        # Normalize the waveform
        max_val = np.max(np.abs(waveform)) or 1.0
        waveform /= max_val

        # Convert to Base64
        raw_bytes = waveform.astype(np.float32).tobytes()
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        frames.append(encoded)

    return frames


def apply_cc_modulations(preset, cc_map):
    """
    Apply MIDI CC-based modulations with extra logic, e.g. mod wheel -> filter cutoff.
    """
    if "modulations" not in preset:
        preset["modulations"] = []

    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            set_vital_parameter(preset, param, cc_val)
            print(f"✅ CC{cc_num} -> {param} = {cc_val}")

    # Example special handling
    if 1 in cc_map:  # mod wheel => filter_1_cutoff
        mod_val = cc_map[1]
        if mod_val > 0.1:
            preset["modulations"].append({
                "source": "mod_wheel",
                "destination": "filter_1_cutoff",
                "amount": mod_val * 0.8
            })

    if 11 in cc_map:  # expression => volume
        exp_val = cc_map[11]
        preset["modulations"].append({
            "source": "cc_expression",
            "destination": "volume",
            "amount": exp_val
        })

    # If any pitch bend is > 0.1, we might set pitch bend range
    if any(pb["pitch"] > 0.1 for pb in preset.get("pitch_bends", [])):
        preset["settings"]["pitch_bend_range"] = 12


def replace_three_wavetables(json_data, frame_data_list):
    """
    Find the first 3 "wave_data" fields in the JSON, replace them with the
    provided base64-encoded frames, and return the modified JSON string.
    """
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, json_data))

    if len(matches) < 3:
        print(f"⚠️ Warning: Only {len(matches)} 'wave_data' entries found. Need 3+.")
        replace_count = min(len(matches), 3)
    else:
        replace_count = 3

    result = json_data
    for i in range(replace_count):
        start, end = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        result = result[:start] + replacement + result[end:]

    print(f"✅ Replaced wave_data in {replace_count} place(s).")
    return result


def modify_vital_preset(vital_preset, midi_file, snapshot_method="1"):
    """
    High-level function that modifies a Vital preset with MIDI data
    (notes, CCs, pitch bends, etc.) and returns the updated preset + wave frames.
    """
    print(f"🔍 Debug: Received midi_file of type {type(midi_file)}")

    # 1) Parse MIDI data if midi_file is a string path; otherwise assume it's a dict
    try:
        if isinstance(midi_file, dict):
            print("⚠️ Using existing parsed MIDI data instead of a file path.")
            midi_data = midi_file
        elif isinstance(midi_file, str):
            print(f"📂 Parsing MIDI file: {midi_file}")
            midi_data = parse_midi(midi_file)
        else:
            raise ValueError(f"Invalid type for midi_file: {type(midi_file)}")
    except Exception as e:
        print(f"❌ Error parsing MIDI: {e}")
        midi_data = {"notes": [], "control_changes": [], "pitch_bends": []}

    # 2) Copy the preset so we don't mutate the original
    modified = copy.deepcopy(vital_preset)

    # Extract MIDI components
    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])
    pitch_bends = midi_data.get("pitch_bends", [])

    # 3) Snapshot method => set basic osc1 pitch/level
    update_settings(modified, notes, snapshot_method)

    # 4) Apply CC data => direct param mapping
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    apply_cc_modulations(modified, cc_map)

    # 5) Pitch bend => set final pitch_wheel
    modified["pitch_wheel"] = pitch_bends[-1]["pitch"] / 8192.0 if pitch_bends else 0.0

    # 6) Dynamic Env1 from MIDI
    apply_dynamic_env1_from_midi(modified, midi_data)

    # 7) Generate 3 distinct wavetable frames
    frame_data = generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048)

    # 8) Ensure "settings" exists in the preset
    modified.setdefault("settings", {})

    ### ✅ Conditionally Enable Oscillators ###
    if any(n["velocity"] > 0 for n in notes):
        modified["settings"]["osc_1_on"] = 1.0  

    if len(notes) > 1:
        modified["settings"]["osc_2_on"] = 1.0  

    if len(notes) > 2:
        modified["settings"]["osc_3_on"] = 1.0  

    if "sample" in midi_data:
        modified["settings"]["sample_on"] = 1.0  

    ### ✅ Conditionally Enable Filters ###
    if any(cc["controller"] in [74, 102] for cc in ccs):
        modified["settings"]["filter_1_on"] = 1.0  

    if any(cc["controller"] in [103, 104] for cc in ccs):
        modified["settings"]["filter_2_on"] = 1.0  

    if any(cc["controller"] in [75, 107] for cc in ccs):
        modified["settings"]["filter_fx_on"] = 1.0  

    ### ✅ Conditionally Enable Effects ###
    effects_mapping = {
        91: "reverb_on",
        93: "chorus_on",
        94: "delay_on",
        95: "phaser_on",
        117: "compressor_on",
        116: "distortion_on",
        119: "flanger_on",
    }
    for cc_num, setting in effects_mapping.items():
        if cc_num in cc_map and cc_map[cc_num] > 0.1:
            modified["settings"][setting] = 1.0  

    if any(cc["controller"] in [35, 36, 37, 38, 39, 40] for cc in ccs):
        modified["settings"]["eq_on"] = 1.0  

    # 9) Apply wavetables to the preset & rename them
    if "groups" in modified and modified["groups"]:
        group0 = modified["groups"][0]
        if "components" in group0 and group0["components"]:
            component0 = group0["components"][0]
            if "keyframes" in component0:
                keyframes = component0["keyframes"]
                while len(keyframes) < 3:
                    keyframes.append({"position": 0.0, "wave_data": "", "wave_source": {"type": "sample"}})

                # ✅ Define new names for the wavetables
                wavetable_names = ["Attack Phase", "Harmonic Blend", "Final Release"]

                for i in range(3):
                    keyframes[i]["wave_data"] = frame_data[i]
                    keyframes[i]["wave_source"] = {"type": "sample"}

                # ✅ Rename the **entire wavetable group/component**
                component0["name"] = "Generated Wavetable"

    # ✅ Update the **preset_name** field
    if "preset_name" in modified:
        midi_base_name = os.path.splitext(os.path.basename(midi_file))[0] if isinstance(midi_file, str) else "Custom_Preset"
        modified["preset_name"] = f"Generated from {midi_base_name}"

    # ✅ Rename the first three instances of `"name": "Init"`
    def replace_init_names(obj, replacement_names, count=[0]):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "name" and value == "Init" and count[0] < 3:
                    obj[key] = replacement_names[count[0]]
                    count[0] += 1
                else:
                    replace_init_names(value, replacement_names, count)
        elif isinstance(obj, list):
            for item in obj:
                replace_init_names(item, replacement_names, count)

    replace_init_names(modified, ["Attack Phase", "Harmonic Blend", "Final Release"])

    print("✅ Finished applying wavetables, envelopes, and LFOs to the preset.")
    return modified, frame_data


def get_preset_filename(midi_path):
    """
    Extracts the base name from the MIDI file and ensures it has a .vital extension.
    """
    base_name = os.path.splitext(os.path.basename(midi_path))[0]
    return f"{base_name}.vital"


def replace_three_wavetables(json_data, frame_data_list):
    """
    Replaces the first 3 'wave_data' fields in the Vital preset JSON
    with three new Base64-encoded waveforms from 'frame_data_list'.
    """
    pattern = r'"wave_data"\s*:\s*"[^"]*"'
    matches = list(re.finditer(pattern, json_data))

    if len(matches) < 3:
        print(f"⚠️ Warning: Found only {len(matches)} 'wave_data' entries, expected >= 3.")
        count_to_replace = min(len(matches), 3)
    else:
        count_to_replace = 3

    result = json_data
    for i in range(count_to_replace):
        start_idx, end_idx = matches[i].span()
        replacement = f'"wave_data": "{frame_data_list[i]}"'
        result = result[:start_idx] + replacement + result[end_idx:]

    print(f"✅ Replaced wave_data in {count_to_replace} place(s).")
    return result


def save_vital_preset(vital_preset, midi_path, frame_data_list=None):
    """
    Saves the modified Vital preset as an uncompressed JSON file
    named after the MIDI file (but with .vital extension).
    """
    try:
        output_path = os.path.join(OUTPUT_DIR, get_preset_filename(midi_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if "modulations" not in vital_preset:
            vital_preset["modulations"] = []

        json_data = json.dumps(vital_preset, indent=2)

        # Optionally replace wave_data if exactly 3 frames are given
        if frame_data_list and len(frame_data_list) == 3:
            json_data = replace_three_wavetables(json_data, frame_data_list)
        else:
            print("⚠️ Warning: No valid wave_data to replace or not exactly 3 frames.")

        with open(output_path, "w") as f:
            f.write(json_data)

        print(f"✅ Successfully saved Vital preset as JSON: {output_path}")

    except Exception as e:
        print(f"❌ Error saving Vital preset: {e}")


def apply_macro_controls_to_preset(preset, cc_map):
    """
    Maps MIDI CCs (20-23) => Macro Controls (1-4), then assigns some example macro modulations.
    """
    print("🔹 Applying Macro Controls to preset...")

    for i in range(1, 5):  # Macro 1..4
        macro_key = f"macro_control_{i}"
        midi_cc = 19 + i  # e.g. CC20 => Macro1, CC21 => Macro2, ...
        preset[macro_key] = cc_map.get(midi_cc, 0.5)  # default 0.5

    macro_mods = [
        {"source": "macro_control_1", "destination": "filter_1_cutoff",   "amount": 0.8},
        {"source": "macro_control_2", "destination": "distortion_drive",  "amount": 0.6},
        {"source": "macro_control_3", "destination": "reverb_dry_wet",    "amount": 0.7},
        {"source": "macro_control_4", "destination": "chorus_dry_wet",    "amount": 0.5}
    ]

    if "modulations" not in preset:
        preset["modulations"] = []
    preset["modulations"].extend(macro_mods)

    print("✅ Macro Controls applied successfully!")
