# /Users/nathannguyen/Documents/Midi_To_serum/Backend/vital_mapper.py

import json
import copy
import zlib
import base64
import pretty_midi
import re
from midi_analysis import estimate_frame_count
import numpy as np
import os
from midi_parser import parse_midi
from config import MIDI_TO_VITAL_MAP, DEFAULT_ADSR, DEFAULT_WAVEFORM, HARMONIC_SCALING, OUTPUT_DIR

def load_default_vital_preset(default_preset_path):
    """
    Loads the default Vital preset (handling both compressed and uncompressed JSON)
    and ensures a structure with 3 keyframes for Oscillator 1.
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

        preset = json.loads(json_data)
        
        # Ensure the preset has a simple structure (e.g., 3 keyframes for Oscillator 1)
        if "groups" in preset and len(preset["groups"]) > 0:
            group = preset["groups"][0]
            if "components" in group and len(group["components"]) > 0:
                component = group["components"][0]
                if "keyframes" in component and len(component["keyframes"]) != 3:
                    print("Warning: Adjusting preset to use 3 keyframes for Oscillator 1")
                    # Use the default wave_data from the first three keyframes or a placeholder
                    default_wave_data = "ABAAugAYwLoAFCC7ABxguwASkLsAFrC7ABrQuwAe8LsAEQi8ABMYvAAVKLwAFzi8ABlIvAAbWLwAHWi8AB94vIAQhLyAEYy8gBKUvIATnLyAFKS8gBWsvIAWtLyAF7y8gBjEvIAZzLyAGtS8gBvcvIAc5LyAHey8gB70vIAf/LxAEAK9wBAGvUARCr3AEQ69QBISvcASFr1AExq9wBMevUAUIr3AFCa9QBUqvcAVLr1AFjK9wBY2vUAXOr3AFz69QBhCvcAYRr1AGUq9wBlOvUAaUr3AGla9QBtavcAbXr1AHGK9wBxmvUAdar3AHW69QB5yvcAedr1AH3q9wB9+vSAQgb1gEIO9oBCFveAQh70gEYm9YBGLvaARjb3gEY+9IBKRvWASk72gEpW94BKXvSATmb1gE5u9oBOdveATn70gFKG9YBSjvaAUpb3gFKe9IBWpvWAVq72gFa294BWvvSAWsb1gFrO9oBa1veAWt70gF7m9YBe7vaAXvb3gF7+9IBjBvWAYw72gGMW94BjHvSAZyb1gGcu9oBnNveAZz70gGtG9YBrTvaAa1b3gGte9IBvZvWAb272gG9294BvfvSAc4b1gHOO9oBzlveAc570gHem9YB3rvaAd7b3gHe+9IB7xvWAe872gHvW94B73vSAf+b1gH/u9oB/9veAf/70QkAC+MJABvlCQAr5wkAO+kJAEvrCQBb7QkAa+8JAHvhCRCL4wkQm+UJEKvnCRC76QkQy+sJENvtCRDr7wkQ++EJIQvjCSEb5QkhK+cJITvpCSFL6wkhW+0JIWvvCSF74Qkxi+MJMZvlCTGr5wkxu+kJMcvrCTHb7Qkx6+8JMfvhCUIL4wlCG+UJQivnCUI76QlCS+sJQlvtCUJr7wlCe+EJUovjCVKb5QlSq+cJUrvpCVLL6wlS2+0JUuvvCVL74QljC+MJYxvlCWMr5wljO+kJY0vrCWNb7Qlja+8JY3vhCXOL4wlzm+UJc6vnCXO76Qlzy+sJc9vtCXPr7wlz++EJhAvjCYQb5QmEK+cJhDvpCYRL6wmEW+0JhGvvCYR74QmUi+MJlJvlCZSr5wmUu+kJlMvrCZTb7QmU6+8JlPvhCaUL4wmlG+UJpSvnCaU76QmlS+sJpVvtCaVr7wmle+EJtYvjCbWb5Qm1q+cJtbvpCbXL6wm12+0JtevvCbX74QnGC+MJxhvlCcYr5wnGO+kJxkvrCcZb7QnGa+8JxnvhCdaL4wnWm+UJ1qvnCda76QnWy+sJ1tvtCdbr7wnW++EJ5wvjCecb5QnnK+cJ5zvpCedL6wnnW+0J52vvCed74Qn3i+MJ95vlCfer5wn3u+kJ98vrCffb7Qn36+8J9/vghQgL4c0IC+LFCBvjzQgb5MUIK+XNCCvmxQg7580IO+jFCEvpzQhL6sUIW+vNCFvsxQhr7c0Ia+7FCHvvzQh74MUYi+HNGIvixRib480Ym+TFGKvlzRir5sUYu+fNGLvoxRjL6c0Yy+rFGNvrzRjb7MUY6+3NGOvuxRj7780Y++DFKQvhzSkL4sUpG+PNKRvkxSkr5c0pK+bFKTvnzSk76MUpS+nNKUvqxSlb680pW+zFKWvtzSlr7sUpe+/NKXvgxTmL4c05i+LFOZvjzTmb5MU5q+XNOavmxTm75805u+jFOcvpzTnL6sU52+vNOdvsxTnr7c056+7FOfvvzTn74MVKC+HNSgvixUob481KG+TFSivlzUor5sVKO+fNSjvoxUpL6c1KS+rFSlvrzUpb7MVKa+3NSmvuxUp7781Ke+DFWovhzVqL4sVam+PNWpvkxVqr5c1aq+bFWrvnzVq76MVay+nNWsvqxVrb681a2+zFWuvtzVrr7sVa++/NWvvgxWsL4c1rC+LFaxvjzWsb5MVrK+XNayvmxWs7581rO+jFa0vpzWtL6sVrW+vNa1vsxWtr7c1ra+7Fa3vvzWt74MV7i+HNe4vixXub4817m+TFe6vlzXur5sV7u+fNe7voxXvL6c17y+rFe9vrzXvb7MV76+3Ne+vuxXv77817++DFjAvhzYwL4sWMG+PNjBvkxYwr5c2MK+bFjDvnzYw76MWMS+nNjEvqxYxb682MW+zFjGvtzYxr7sWMe+/NjHvgxZyL4c2ci+LFnJvjzZyb5MWcq+XNnKvmxZy7582cu+jFnMvpzZzL6sWc2+vNnNvsxZzr7c2c6+7FnPvvzZz74MWtC+HNrQvixa0b482tG+TFrSvlza0r5sWtO+fNrTvoxa1L6c2tS+rFrVvrza1b7MWta+3NrWvuxa17782te+DFvYvhzb2L4sW9m+PNvZvkxb2r5c29q+bFvbvnzb276MW9y+nNvcvqxb3b68292+zFvevtzb3r7sW9++/Nvfvgxc4L4c3OC+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znUuP8Y1Lj++9S0/trUtP651LT+mNS0/nvUsP5a1LD+OdSw/hjUsP371Kz92tSs/bnUrP2Y1Kz9e9So/VrUqP051Kj9GNSo/PvUpPza1KT8udSk/JjUpPx71KD8WtSg/DnUoPwY1KD/+9Cc/9rQnP+50Jz/mNCc/3vQmP9a0Jj/OdCY/xjQmP770JT+2tCU/rnQlP6Y0JT+e9CQ/lrQkP450JD+GNCQ/fvQjP3a0Iz9udCM/ZjQjP170Ij9WtCI/TnQiP0Y0Ij8+9CE/NrQhPy50IT8mNCE/HvQgPxa0ID8OdCA/BjQgP/7zHz/2sx8/7nMfP+YzHz/e8x4/1rMeP85zHj/GMx4/vvMdP7azHT+ucx0/pjMdP57zHD+Wsxw/jnMcP4YzHD9+8xs/drMbP25zGz9mMxs/XvMaP1azGj9Ocxo/RjMaPz7zGT82sxk/LnMZPyYzGT8e8xg/FrMYPw5zGD8GMxg//vIXP/ayFz/uchc/5jIXP97yFj/WshY/znIWP8YyFj++8hU/trIVP65yFT+mMhU/nvIUP5ayFD+OchQ/hjIUP37yEz92shM/bnITP2YyEz9e8hI/VrISP05yEj9GMhI/PvIRPzayET8uchE/JjIRPx7yED8WshA/DnIQPwYyED/+8Q8/9rEPP+5xDz/mMQ8/3vEOP9axDj/OcQ4/xjEOP77xDT+2sQ0/rnENP6YxDT+e8Qw/lrEMP45xDD+GMQw/fvELP3axCz9ucQs/ZjELP17xCj9WsQo/TnEKP0YxCj8+8Qk/NrEJPy5xCT8mMQk/HvEIPxaxCD8OcQg/BjEIP/7wBz/2sAc/7nAHP+YwBz/e8AY/1rAGP85wBj/GMAY/vvAFP7awBT+ucAU/pjAFP57wBD+WsAQ/jnAEP4YwBD9+8AM/drADP25wAz9mMAM/XvACP1awAj9OcAI/RjACPz7wAT82sAE/LnABPyYwAT8e8AA/FrAAPw5wAD8GMAA//N//Puxf/z7c3/4+zF/+Przf/T6sX/0+nN/8Poxf/D583/s+bF/7Plzf+j5MX/o+PN/5Pixf+T4c3/g+DF/4Pvze9z7sXvc+3N72Psxe9j683vU+rF71Ppze9D6MXvQ+fN7zPmxe8z5c3vI+TF7yPjze8T4sXvE+HN7wPgxe8D783e8+7F3vPtzd7j7MXe4+vN3tPqxd7T6c3ew+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"
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
    Converts CC values into normalized LFO points.
    """
    if not cc_data:
        print("⚠️ No MIDI CC data found. Skipping LFO generation.")
        return None

    # Sort CCs by time and normalize time range (0.0 to 1.0)
    cc_data = sorted(cc_data, key=lambda x: x["time"])
    times = np.array([cc["time"] for cc in cc_data])
    values = np.array([cc["value"] / 127.0 for cc in cc_data])  # Normalize CC values

    # Resample CC points to fit `num_points`
    resampled_times = np.linspace(times[0], times[-1], num_points)
    resampled_values = np.interp(resampled_times, times, values)  # Interpolate

    # Convert to LFO JSON format
    lfo_shape = {
        "name": "MIDI_CC_LFO",
        "num_points": num_points,
        "points": list(resampled_times) + list(resampled_values),
        "powers": [0.0] * num_points,  # Linear interpolation
        "smooth": True
    }

    print(f"✅ Created LFO from MIDI CC: {lfo_shape}")
    return lfo_shape


def add_envelopes_to_preset(preset, notes):
    """
    Adds ADSR envelope settings to the Vital preset based on MIDI note characteristics.
    If notes lack velocity variation, ADSR values are inferred from duration.
    """
    if not notes:
        print("⚠️ No notes found in MIDI. Using default envelope settings.")
        preset.update({
            "env_1_attack": DEFAULT_ADSR["attack"],
            "env_1_decay": DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    # Compute average note duration
    avg_note_length = sum(n["end"] - n["start"] for n in notes) / len(notes)
    
    # Compute velocity-based sustain
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level = avg_velocity / 127.0 if avg_velocity > 0 else 0.5  # Avoid division errors

    # Scale ADSR parameters based on note length
    attack_time = min(avg_note_length * 0.05, 0.2)  # Max 200ms attack
    decay_time = min(avg_note_length * 0.15, 0.7)   # Max 700ms decay
    release_time = min(avg_note_length * 0.3, 1.5)  # Max 1.5s release

    # Apply ADSR settings
    preset.update({
        "env_1_attack": attack_time,
        "env_1_decay": decay_time,
        "env_1_sustain": sustain_level,
        "env_1_release": release_time
    })

    print(f"✅ Adaptive ENV1: A={attack_time}s, D={decay_time}s, S={sustain_level}, R={release_time}s")

    # Apply a similar ADSR envelope to ENV2 (for filter modulation)
    preset.update({
        "env_2_attack": attack_time * 0.7,  # Slightly faster attack
        "env_2_decay": decay_time * 0.8,
        "env_2_sustain": sustain_level * 0.9,
        "env_2_release": release_time * 1.2
    })
    print("✅ ENV2 (Filter Envelope) Applied")


def add_lfos_to_preset(preset, cc_data, notes, lfo_target="filter_1_cutoff"):
    """
    Adds an LFO modulation to the Vital preset based on MIDI CC data.
    If no CC data is available, generates an adaptive LFO based on note timing.
    """
    # Check if CC data exists
    if not cc_data:
        print("⚠️ No MIDI CC data found. Generating LFO from note timing instead.")

        # Estimate LFO rate from average note duration
        if notes:
            avg_note_duration = sum(n["end"] - n["start"] for n in notes) / len(notes)
            lfo_rate = max(0.5, min(8.0, 1.0 / avg_note_duration))  # LFO rate between 0.5Hz and 8Hz
        else:
            lfo_rate = 1.0  # Default rate

        lfo_shape = {
            "name": "Adaptive_LFO",
            "num_points": 16,
            "points": [0.0, 0.25, 0.5, 0.75, 1.0] * 2,  # Simple up-down LFO
            "powers": [0.0] * 16,  # Linear interpolation
            "smooth": True
        }

        print(f"✅ Adaptive LFO generated at {lfo_rate}Hz")

    else:
        # Generate LFO from CC automation
        lfo_shape = generate_lfo_shape_from_cc(cc_data)
        if not lfo_shape:
            return

        # Set a random frequency to create slight variations
        lfo_rate = 2.0 + np.random.uniform(-0.5, 0.5)

    # Apply LFO to the preset
    if "lfos" not in preset:
        preset["lfos"] = []
    
    preset["lfos"].append(lfo_shape)

    # Assign modulation (LFO1 → target parameter)
    preset["modulations"].append({
        "source": "lfo_1",
        "destination": lfo_target,
        "amount": 0.7  # Adjust modulation depth
    })
    preset["lfo_1_frequency"] = lfo_rate

    print(f"✅ Applied LFO1 → {lfo_target} at {lfo_rate} Hz")


def set_vital_parameter(preset, param_name, value):
    """
    Safely set a Vital parameter, respecting whether it lives top-level or in 'settings'.
    """
    if "settings" not in preset:
        preset["settings"] = {}

    if param_name.startswith("macro"):
        # Fix: Ensure macro_number is correctly extracted as an integer
        macro_number = int(param_name.replace("macro", ""))
        control_key = f"macro_control_{macro_number}"
        preset["settings"][control_key] = value
    else:
        preset[param_name] = value


def update_settings(modified_preset, notes, snapshot_method):
    """
    Update Vital preset settings based on the chosen snapshot method.
    """
    if snapshot_method == "1":
        # 1) Single first note
        if notes:
            first_note = notes[0]
            modified_preset["osc_1_transpose"] = first_note["pitch"] - 69
            modified_preset["osc_1_level"] = first_note["velocity"] / 127.0
        else:
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
        # 3) Single moment in time: prompt for a time and select the active note at that moment
        try:
            snapshot_time = float(input("Enter the snapshot time (in seconds): ").strip())
        except ValueError:
            print("Invalid time input, defaulting to method 1 (first note).")
            snapshot_time = None

        active_note = None
        if snapshot_time is not None:
            for n in notes:
                if n["start"] <= snapshot_time < n["end"]:
                    active_note = n
                    break
        if active_note:
            modified_preset["osc_1_transpose"] = active_note["pitch"] - 69
            modified_preset["osc_1_level"] = active_note["velocity"] / 127.0
        else:
            print("No note active at that time, using default values.")
            modified_preset["osc_1_transpose"] = 0
            modified_preset["osc_1_level"] = 0.5


def add_modulations(modified_preset, ccs):
    """
    Map MIDI CC -> Vital parameter and add modulations.
    """
    print("\n🔍 Debug: Processing MIDI CCs...")

    cc_map = {}
    for cc in ccs:
        cc_map[cc["controller"]] = cc["value"] / 127.0  # Normalize CC values

    for cc_number, cc_value in cc_map.items():
        if cc_number in MIDI_TO_VITAL_MAP:
            vital_param = MIDI_TO_VITAL_MAP[cc_number]
            set_vital_parameter(modified_preset, vital_param, cc_value)
            print(f"✅ Applied CC{cc_number} -> {vital_param}: {cc_value}")

    print("\n🔍 Debug: Final Modulation Parameters")
    print(json.dumps(modified_preset.get("modulations", []), indent=2))


def generate_frame_waveform(midi_data, frame_idx, num_frames, frame_size, waveform_type="saw"):
    """
    Generates a single frame waveform in float32 format (Vital requirement).
    - Supports 'sine', 'saw', 'square', 'triangle', and 'pulse' waveforms.
    - Dynamically scales harmonics based on MIDI velocity & CC data.
    - Morphs the waveform across frames for richer wavetables.
    """

    notes = midi_data.get("notes", [])
    ccs = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    if not notes:
        notes = [{"pitch": 69, "velocity": 100}]  # Default to A4 with medium velocity

    note_idx = frame_idx % len(notes)
    note = notes[note_idx]
    pitch = note["pitch"]
    velocity = note["velocity"] / 127.0  # Normalize velocity (0-1)

    # Convert MIDI pitch to frequency
    freq = 440.0 * (2.0 ** ((pitch - 69.0) / 12.0))

    # Mod Wheel (CC1) can control harmonic intensity
    harmonic_boost = HARMONIC_SCALING.get(waveform_type, 1) * ccs.get(1, 0.5)  # Default to 0.5 if CC1 is absent

    # Create phase space
    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    # Determine harmonic scaling per frame (morphing effect)
    frame_morph = frame_idx / (num_frames - 1)  # Ranges from 0 to 1
    harmonic_intensity = (velocity * harmonic_boost) * (0.5 + 0.5 * frame_morph)  # More harmonics in later frames

    # Generate waveforms
    if waveform_type == "sine":
        waveform = np.sin(phase)

    elif waveform_type == "saw":
        waveform = np.sum([(1.0 / h) * np.sin(h * phase) for h in range(1, int(10 * harmonic_intensity))], axis=0)

    elif waveform_type == "square":
        waveform = np.sum([(1.0 / h) * np.sin(h * phase) for h in range(1, int(10 * harmonic_intensity), 2)], axis=0)

    elif waveform_type == "triangle":
        waveform = np.sum([(1.0 / h**2) * (-1)**((h-1)//2) * np.sin(h * phase) for h in range(1, int(10 * harmonic_intensity), 2)], axis=0)

    elif waveform_type == "pulse":
        pulse_width = ccs.get(2, 0.5)  # CC2 controls pulse width, default 0.5
        waveform = np.where(phase < (2 * np.pi * pulse_width), 1, -1)

    else:
        waveform = np.sin(phase)  # Default to sine

    # Apply harmonic intensity scaling
    waveform *= harmonic_intensity

    # Normalize the waveform
    waveform /= np.max(np.abs(waveform))

    return waveform.astype(np.float32)

def generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048, waveform_type="saw"):
    """
    Generates 'num_frames' separate Base64-encoded wave_data strings for Vital.
    - Supports multiple waveform types ('sine', 'saw', 'square', 'triangle')
    - Dynamically adjusts harmonics using MIDI velocity and CC data.
    """

    frame_data_list = []

    for frame_idx in range(num_frames):
        # Generate a waveform for this frame
        waveform = generate_frame_waveform(midi_data, frame_idx, num_frames, frame_size, waveform_type)
        
        # Convert waveform to raw bytes (float32 format)
        raw_bytes = waveform.tobytes()
        
        # Base64 encode
        encoded_str = base64.b64encode(raw_bytes).decode("utf-8")
        frame_data_list.append(encoded_str)

    return frame_data_list


def apply_cc_modulations(preset, cc_map):
    """
    Apply MIDI CC-based modulations to the Vital preset with expanded capabilities.
    """
    if "modulations" not in preset:
        preset["modulations"] = []
    
    # Apply direct parameter mappings
    for cc_number, cc_value in cc_map.items():
        if cc_number in MIDI_TO_VITAL_MAP:
            vital_param = MIDI_TO_VITAL_MAP[cc_number]
            set_vital_parameter(preset, vital_param, cc_value)
            print(f"✅ Applied CC{cc_number} -> {vital_param}: {cc_value}")
    
    # Special handling for common expression controllers
    if 1 in cc_map:  # Mod wheel
        mod_value = cc_map[1]
        if mod_value > 0.1:
            preset["modulations"].append({
                "source": "mod_wheel",
                "destination": "filter_1_cutoff",
                "amount": mod_value * 0.8
            })
    
    if 11 in cc_map:  # Expression
        exp_value = cc_map[11]
        preset["modulations"].append({
            "source": "cc_expression",
            "destination": "volume",
            "amount": exp_value
        })
    
    # Handle pitch bend range correctly
    if any(pb["pitch"] > 0.1 for pb in preset.get("pitch_bends", [])):
        preset["settings"]["pitch_bend_range"] = 12  # Set to +/- 12 semitones


def replace_three_wavetables(json_data, frame_data_list):
    """
    Replaces the first three 'wave_data' fields in the Vital preset JSON
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


def modify_vital_preset(vital_preset, midi_file, snapshot_method="1"):
    """
    Modifies the Vital preset using parsed MIDI data.
    Ensures wave_source = "sample" for each keyframe, so Vital sees custom wave_data.
    """

    # 🔍 Debug: Print what type of data is received
    print(f"🔍 Debug: Received midi_file of type {type(midi_file)}")

    # ✅ Ensure `midi_file` is processed correctly
    try:
        if isinstance(midi_file, dict):
            print("⚠️ Warning: Expected file path, but received a dictionary. Using existing parsed MIDI data.")
            midi_data = midi_file  # Already parsed, assign it directly
        elif isinstance(midi_file, str):
            print(f"📂 Parsing MIDI file: {midi_file}")
            midi_data = parse_midi(midi_file)  # ✅ Parse MIDI if it's a file path
        else:
            raise ValueError(f"Invalid type for midi_file: {type(midi_file)} (Expected str or dict)")

        if not midi_data:
            print("⚠️ Warning: MIDI parsing returned no data. Using default empty MIDI structure.")
            midi_data = {"notes": [], "control_changes": [], "pitch_bends": []}
    except Exception as e:
        print(f"❌ Error parsing MIDI file: {e}")
        midi_data = {"notes": [], "control_changes": [], "pitch_bends": []}

    # ✅ Create a deep copy to prevent modifying the original preset
    modified_preset = copy.deepcopy(vital_preset)
    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])
    pitch_bends = midi_data.get("pitch_bends", [])

    # --- Apply MIDI note-based settings ---
    update_settings(modified_preset, notes, snapshot_method)

    # --- Apply MIDI CC modulations / direct param mapping ---
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    apply_cc_modulations(modified_preset, cc_map)

    # --- Handle Pitch Bends ---
    if pitch_bends:
        last_bend = pitch_bends[-1]  # Use the last pitch bend event
        modified_preset["pitch_wheel"] = last_bend["pitch"] / 8192.0
    else:
        modified_preset["pitch_wheel"] = 0.0

    # --- Generate 3 separate frames of wavetable data ---
    frame_data_list = generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048, waveform_type=DEFAULT_WAVEFORM)

    # --- Ensure Oscillator 1 is Enabled and Set to Custom Wavetable ---
    modified_preset["osc_1_wave"] = 0
    modified_preset["osc_1_wavetable_position"] = 0.5
    modified_preset.setdefault("settings", {})
    modified_preset["settings"]["osc_1_on"] = 1.0
    modified_preset["settings"]["osc_1_wavetable_index"] = 0

    # --- Apply Envelope Modulation (Based on MIDI Envelope Extraction) ---
    if notes:
        avg_attack = sum(n["attack"] for n in notes) / len(notes)
        avg_decay = sum(n["decay"] for n in notes) / len(notes)
        avg_sustain = sum(n["sustain"] for n in notes) / len(notes)
        avg_release = sum(n["release"] for n in notes) / len(notes)

        # Assign envelope parameters to Vital's Envelope 1
        modified_preset["env_1_attack"] = avg_attack
        modified_preset["env_1_decay"] = avg_decay
        modified_preset["env_1_sustain"] = avg_sustain
        modified_preset["env_1_release"] = avg_release

        print(f"🔍 Applied ADSR Envelope: A={avg_attack}, D={avg_decay}, S={avg_sustain}, R={avg_release}")

    # --- Apply LFO Modulations (LFO Speed, Depth, etc.) ---
    if 1 in cc_map:  # Mod Wheel (LFO Rate Control)
        mod_value = cc_map[1]  # Normalized value 0 to 1
        modified_preset["lfo_1_frequency"] = mod_value * 5.0  # Scale for Vital's range

    if 11 in cc_map:  # Expression (LFO Depth)
        exp_value = cc_map[11]
        modified_preset["modulations"].append({
            "source": "lfo_1",
            "destination": "osc_1_level",
            "amount": exp_value
        })

    # --- Ensure LFO Modulation Exists ---
    modified_preset.setdefault("modulations", [])

    # Add LFO 1 -> Wavetable Position Modulation (if there are enough notes)
    if len(notes) > 4:
        modified_preset["lfo_1_frequency"] = 0.25
        modified_preset["lfo_1_shape"] = 0
        modified_preset["modulations"].append({
            "source": "lfo_1",
            "destination": "osc_1_wavetable_position",
            "amount": 0.5
        })

    # --- Replace `wave_data` in the preset with the generated frames ---
    if "groups" in modified_preset and modified_preset["groups"]:
        group0 = modified_preset["groups"][0]
        if "components" in group0 and group0["components"]:
            component0 = group0["components"][0]
            if "keyframes" in component0:
                keyframes = component0["keyframes"]

                # Ensure there are at least 3 keyframes
                while len(keyframes) < 3:
                    keyframes.append({"position": 0.0, "wave_data": "", "wave_source": {"type": "sample"}})

                # Assign new `wave_data` and set `wave_source` to "sample"
                for i in range(3):
                    keyframes[i]["wave_data"] = frame_data_list[i]
                    keyframes[i]["wave_source"] = {"type": "sample"}

    print("✅ Successfully applied LFOs, Envelopes, and Wavetables to Vital preset.")
    
    return modified_preset, frame_data_list


def get_preset_filename(midi_path):
    """Extracts the base name from the MIDI file and ensures it has a .vital extension."""
    base_name = os.path.splitext(os.path.basename(midi_path))[0]  # Remove .mid extension
    return f"{base_name}.vital"  # Append .vital extension


def save_vital_preset(vital_preset, midi_path, frame_data_list=None):
    """
    Saves the modified Vital preset as an uncompressed JSON file.
    Uses the MIDI filename as the preset name.
    """
    try:
        # Generate the output file path based on the MIDI filename
        output_path = os.path.join(OUTPUT_DIR, get_preset_filename(midi_path)) 
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Ensure modulations exist in the preset
        if "modulations" not in vital_preset:
            vital_preset["modulations"] = []

        # Convert preset to JSON
        json_data = json.dumps(vital_preset, indent=2)

        # Replace wave data if applicable
        if frame_data_list and len(frame_data_list) == 3:
            json_data = replace_three_wavetables(json_data, frame_data_list)
        else:
            print("⚠️ Warning: No valid wave_data to replace, or not exactly 3 frames given.")

        # Save as JSON file
        with open(output_path, "w") as f:
            f.write(json_data)

        print(f"✅ Successfully saved Vital preset as JSON: {output_path}")

    except Exception as e:
        print(f"❌ Error saving Vital preset: {e}")


def apply_macro_controls_to_preset(preset, cc_map):
    """
    Maps MIDI CCs 20-23 to Macro Controls 1-4 and assigns default modulations.
    """
    print("🔹 Applying Macro Controls to preset...")

    for i in range(1, 5):  # Macro 1 to 4
        macro_key = f"macro_control_{i}"
        midi_cc = 19 + i  # CC 20 → Macro 1, CC 21 → Macro 2, etc.

        # Assign default value, override with MIDI CC if present
        preset[macro_key] = cc_map.get(midi_cc, 0.5)  # Default to 0.5

    # Assign each Macro to at least one useful parameter
    macro_modulations = [
        {"source": "macro_control_1", "destination": "filter_1_cutoff", "amount": 0.8},
        {"source": "macro_control_2", "destination": "distortion_drive", "amount": 0.6},
        {"source": "macro_control_3", "destination": "reverb_dry_wet", "amount": 0.7},
        {"source": "macro_control_4", "destination": "chorus_dry_wet", "amount": 0.5}
    ]

    if "modulations" not in preset:
        preset["modulations"] = []

    preset["modulations"].extend(macro_modulations)

    print("✅ Macro Controls applied successfully!")
