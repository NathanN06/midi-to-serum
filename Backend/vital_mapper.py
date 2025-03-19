# vital_mapper.py

import json

import zlib
import base64

import re
import numpy as np
import os
import logging
from midi_analysis import compute_midi_stats

# Local imports

from config import (
    MIDI_TO_VITAL_MAP,
    DEFAULT_ADSR,
    DEFAULT_WAVEFORM,
    HARMONIC_SCALING,
    OUTPUT_DIR
)


def load_default_vital_preset(default_preset_path):
    """
    Loads a default Vital preset, handling both compressed and uncompressed JSON,
    and ensures a structure with 3 keyframes for Oscillator 1.
    
    Args:
        default_preset_path (str): Path to the default Vital preset file.

    Returns:
        dict: The parsed preset data if successful, None otherwise.
    """
    try:
        with open(default_preset_path, "rb") as f:
            file_data = f.read()

        # Try decompressing; fallback to plain JSON if it's not compressed
        try:
            json_data = zlib.decompress(file_data).decode()
        except zlib.error:
            json_data = file_data.decode()

        # Parse JSON safely
        try:
            preset = json.loads(json_data)
        except json.JSONDecodeError as e:
            logging.error(f"❌ Error decoding Vital preset JSON: {e}")
            return None

        # Ensure we have at least 3 keyframes in the first oscillator
        if "groups" in preset and preset["groups"]:
            group = preset["groups"][0]
            if "components" in group and group["components"]:
                component = group["components"][0]
                if "keyframes" in component:
                    keyframes = component["keyframes"]
                    if len(keyframes) < 3:
                        logging.warning("⚠️ Adjusting preset to ensure 3 keyframes for Oscillator 1.")

                        # Placeholder base64 wave data (truncated for brevity)
                        default_wave_data = (
                            "ABAAugAYwLoAFCC7ABxguwASkLsAFrC7ABrQuwAe8LsAEQi8ABMYvAAVKLwAFzi8ABlIvAAbWLwAHWi8AB94vIAQhLyAEYy8gBKUvIATnLyAFKS8gBWsvIAWtLyAF7y8gBjEvIAZzLyAGtS8gBvcvIAc5LyAHey8gB70vIAf/LxAEAK9wBAGvUARCr3AEQ69QBISvcASFr1AExq9wBMevUAUIr3AFCa9QBUqvcAVLr1AFjK9wBY2vUAXOr3AFz69QBhCvcAYRr1AGUq9wBlOvUAaUr3AGla9QBtavcAbXr1AHGK9wBxmvUAdar3AHW69QB5yvcAedr1AH3q9wB9+vSAQgb1gEIO9oBCFveAQh70gEYm9YBGLvaARjb3gEY+9IBKRvWASk72gEpW94BKXvSATmb1gE5u9oBOdveATn70gFKG9YBSjvaAUpb3gFKe9IBWpvWAVq72gFa294BWvvSAWsb1gFrO9oBa1veAWt70gF7m9YBe7vaAXvb3gF7+9IBjBvWAYw72gGMW94BjHvSAZyb1gGcu9oBnNveAZz70gGtG9YBrTvaAa1b3gGte9IBvZvWAb272gG9294BvfvSAc4b1gHOO9oBzlveAc570gHem9YB3rvaAd7b3gHe+9IB7xvWAe872gHvW94B73vSAf+b1gH/u9oB/9veAf/70QkAC+MJABvlCQAr5wkAO+kJAEvrCQBb7QkAa+8JAHvhCRCL4wkQm+UJEKvnCRC76QkQy+sJENvtCRDr7wkQ++EJIQvjCSEb5QkhK+cJITvpCSFL6wkhW+0JIWvvCSF74Qkxi+MJMZvlCTGr5wkxu+kJMcvrCTHb7Qkx6+8JMfvhCUIL4wlCG+UJQivnCUI76QlCS+sJQlvtCUJr7wlCe+EJUovjCVKb5QlSq+cJUrvpCVLL6wlS2+0JUuvvCVL74QljC+MJYxvlCWMr5wljO+kJY0vrCWNb7Qlja+8JY3vhCXOL4wlzm+UJc6vnCXO76Qlzy+sJc9vtCXPr7wlz++EJhAvjCYQb5QmEK+cJhDvpCYRL6wmEW+0JhGvvCYR74QmUi+MJlJvlCZSr5wmUu+kJlMvrCZTb7QmU6+8JlPvhCaUL4wmlG+UJpSvnCaU76QmlS+sJpVvtCaVr7wmle+EJtYvjCbWb5Qm1q+cJtbvpCbXL6wm12+0JtevvCbX74QnGC+MJxhvlCcYr5wnGO+kJxkvrCcZb7QnGa+8JxnvhCdaL4wnWm+UJ1qvnCda76QnWy+sJ1tvtCdbr7wnW++EJ5wvjCecb5QnnK+cJ5zvpCedL6wnnW+0J52vvCed74Qn3i+MJ95vlCfer5wn3u+kJ98vrCffb7Qn36+8J9/vghQgL4c0IC+LFCBvjzQgb5MUIK+XNCCvmxQg7580IO+jFCEvpzQhL6sUIW+vNCFvsxQhr7c0Ia+7FCHvvzQh74MUYi+HNGIvixRib480Ym+TFGKvlzRir5sUYu+fNGLvoxRjL6c0Yy+rFGNvrzRjb7MUY6+3NGOvuxRj7780Y++DFKQvhzSkL4sUpG+PNKRvkxSkr5c0pK+bFKTvnzSk76MUpS+nNKUvqxSlb680pW+zFKWvtzSlr7sUpe+/NKXvgxTmL4c05i+LFOZvjzTmb5MU5q+XNOavmxTm75805u+jFOcvpzTnL6sU52+vNOdvsxTnr7c056+7FOfvvzTn74MXei+HN3ovixd6b483em+TF3qvlzd6r5sXeu+fN3rvoxd7L6c3ey+rF3tvrzd7b7MXe6+3N3uvuxd77783e++DF7wvhze8L4sXvG+PN7xvkxe8r5c3vK+bF7zvnze876MXvS+nN70vqxe9b683vW+zF72vtze9r7sXve+/N73vgxf+L4c3/i+LF/5vjzf+b5MX/q+XN/6vmxf+7583/u+jF/8vpzf/L6sX/2+vN/9vsxf/r7c3/6+7F//vvzf/74"
                        )
                        component["keyframes"] = [{"position": i / 2.0, "wave_data": default_wave_data} for i in range(3)]

        return preset

    except (OSError, json.JSONDecodeError) as e:
        logging.error(f"❌ Error loading default Vital preset: {e}")
        return None


def build_lfo_from_cc(preset, midi_data, lfo_idx=1, destination="filter_1_cutoff", one_shot=False):
    """
    Builds an LFO shape from a MIDI CC source or generates a fallback LFO if no CC is provided.

    - Uses different MIDI CCs to control LFO **Rate (Speed)**
    - Uses MIDI CC11 (Expression) to control **Depth (Modulation Strength)**
    - Supports free-running and one-shot LFOs
    """

    num_points = 16  # More points = smoother LFOs
    times_interp = np.linspace(0, 1, num_points)

    # Default LFO shapes
    lfo_shapes = {
        1: ("Sine LFO", np.sin(times_interp * 2 * np.pi)),  # Sine
        2: ("Square LFO", np.sign(np.sin(times_interp * 2 * np.pi))),  # Square
        3: ("Saw LFO", 2 * (times_interp % 1) - 1),  # Saw
        4: ("Triangle LFO", 2 * np.abs(2 * (times_interp % 1) - 1) - 1)  # Triangle
    }

    # Select LFO shape
    lfo_name, values_interp = lfo_shapes.get(lfo_idx, lfo_shapes[1])

    # Normalize values between 0 and 1
    values_interp = (values_interp + 1) / 2  
    values_interp = np.clip(values_interp, 0, 1)

    # Generate time/value pairs for Vital's LFO JSON format
    points = [val for pair in zip(times_interp, values_interp) for val in pair]
    powers = [0.0] * num_points  

    # Ensure "settings" exists
    preset.setdefault("settings", {})
    preset["settings"].setdefault("lfos", [])

    # Expand the list if needed
    while len(preset["settings"]["lfos"]) < lfo_idx:
        preset["settings"]["lfos"].append({
            "name": f"LFO {len(preset['settings']['lfos'])+1}",
            "num_points": 2,
            "points": [0.0, 1.0, 1.0, 0.0],
            "powers": [0.0, 0.0],
            "smooth": False
        })

    # 🎛 **Assign Unique CCs for LFO Rate**
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}

    lfo_rate_cc_map = {  
        1: cc_map.get(1, 0.5),  # CC1 → LFO1 Rate
        2: cc_map.get(2, 0.5),  # CC2 → LFO2 Rate
        3: cc_map.get(3, 0.5),  # CC3 → LFO3 Rate
        4: cc_map.get(4, 0.5)   # CC4 → LFO4 Rate
    }
    lfo_depth_cc = cc_map.get(11, 0.8)  # CC11 = Expression → Depth

    # Apply non-linear scaling for better control
    lfo_rate_scaled = 1.0 + (lfo_rate_cc_map[lfo_idx] * 4.0)  # 1x to 5x speed scaling
    lfo_depth_scaled = 0.2 + (lfo_depth_cc * 0.8)  # 20% to 100% depth

    # Update the correct LFO
    preset["settings"]["lfos"][lfo_idx - 1] = {
        "name": lfo_name,
        "num_points": num_points,
        "points": points,
        "powers": powers,
        "smooth": True  # Smooth LFO
    }

    # Apply dynamic speed & depth settings
    preset["settings"][f"lfo_{lfo_idx}_frequency"] = lfo_rate_scaled
    preset["settings"][f"lfo_{lfo_idx}_sync"] = 0.0  # Free running mode
    preset["settings"][f"lfo_{lfo_idx}_tempo"] = np.random.choice([2.0, 4.0, 8.0])  

    # Apply One-Shot Mode if enabled
    if one_shot:
        preset["settings"][f"lfo_{lfo_idx}_one_shot"] = 1.0  

    # Apply LFO Depth as Modulation Strength
    preset.setdefault("modulations", [])
    preset["modulations"].append({
        "source": f"lfo_{lfo_idx}",
        "destination": destination,
        "amount": lfo_depth_scaled  
    })

    print(f"✅ {lfo_name} -> {destination} applied (one_shot={one_shot}). Rate={lfo_rate_scaled:.2f}, Depth={lfo_depth_scaled:.2f}")


def add_lfos_to_preset(preset, cc_data, notes):
    """
    Adds 4 different LFOs to the preset, each with its own waveform.
    If CC data is provided, it will shape the LFO dynamically.
    """

    if "settings" not in preset:
        preset["settings"] = {}

    if "lfos" not in preset["settings"]:
        preset["settings"]["lfos"] = []

    print("🔹 Adding LFOs to preset...")

    # Assign each LFO to a unique destination and shape
    build_lfo_from_cc(preset, midi_data=cc_data, lfo_idx=1, destination="filter_1_cutoff")  # **Sine → Filter Cutoff**
    build_lfo_from_cc(preset, midi_data=cc_data, lfo_idx=2, destination="osc_1_pitch", one_shot=True)  # **Square → Pitch**
    build_lfo_from_cc(preset, midi_data=cc_data, lfo_idx=3, destination="volume")  # **Saw → Volume Tremolo**
    build_lfo_from_cc(preset, midi_data=cc_data, lfo_idx=4, destination="filter_2_resonance")  # **Triangle → Filter Resonance**

    print("✅ 4 LFOs added with unique waveforms!")


def generate_lfo_shape_from_cc(cc_data, num_points=16, lfo_type="sine"):
    """
    Generates an LFO shape based on MIDI CC automation.
    Converts CC values into a set of time/value points in Vital's LFO JSON format.
    """

    if not cc_data:
        print("⚠️ No MIDI CC data found. Skipping LFO generation.")
        return None

    cc_data = sorted(cc_data, key=lambda x: x["time"])
    times = np.array([cc["time"] for cc in cc_data])
    values = np.array([cc["value"] / 127.0 for cc in cc_data])

    resampled_times = np.linspace(times[0], times[-1], num_points)
    resampled_values = np.interp(resampled_times, times, values)

    if lfo_type == "sine":
        waveform = np.sin(resampled_times * 2 * np.pi)
    elif lfo_type == "square":
        waveform = np.sign(np.sin(resampled_times * 2 * np.pi))
    elif lfo_type == "saw":
        waveform = 2 * (resampled_times % 1) - 1
    elif lfo_type == "triangle":
        waveform = 2 * np.abs(2 * (resampled_times % 1) - 1) - 1
    else:
        waveform = np.sin(resampled_times * 2 * np.pi)

    lfo_shape = {
        "name": "MIDI_CC_LFO",
        "num_points": num_points,
        "points": list(resampled_times) + list(resampled_values),
        "powers": list(waveform),
        "smooth": True
    }

    print(f"✅ Created LFO with type {lfo_type} from MIDI CC data.")
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


def apply_dynamic_env_to_preset(preset, midi_data):
    """
    Dynamically adjusts Envelope 1, 2, and 3 based on MIDI note data.

    - ENV1: **Amplitude (volume envelope)**
    - ENV2: **Filter cutoff envelope**
    - ENV3: **Oscillator shape/pitch envelope**
    
    Each envelope has different timing & sustain characteristics based on:
      - Note length (short = pluck, long = pad)
      - Note density (fast sequences = snappier envelopes)
      - MIDI CC data (expression/mod wheel influence)
    """

    if "settings" not in preset:
        preset["settings"] = {}

    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])

    if not notes:
        print("⚠️ No MIDI notes detected. Using default envelopes.")
        preset["settings"].update({
            "env_1_attack":  DEFAULT_ADSR["attack"],
            "env_1_decay":   DEFAULT_ADSR["decay"],
            "env_1_sustain": DEFAULT_ADSR["sustain"],
            "env_1_release": DEFAULT_ADSR["release"]
        })
        return

    ### 🔹 Compute Average Note Properties ###
    avg_note_length = sum(n["end"] - n["start"] for n in notes) / len(notes)
    avg_velocity = sum(n["velocity"] for n in notes) / len(notes)
    sustain_level = min(1.0, avg_velocity / 127.0)

    ### 🔹 Determine Note Density (How Fast Notes are Played) ###
    if len(notes) > 1:
        time_gaps = [notes[i+1]["start"] - notes[i]["end"] for i in range(len(notes)-1)]
        avg_gap = sum(time_gaps) / len(time_gaps)
    else:
        avg_gap = avg_note_length  # Single note case

    note_density_factor = max(0.2, min(1.0, 1.0 - (avg_gap / 2.0)))  # More notes = faster envelopes

    ### 🔹 Check for CC Influence (e.g., Expression, Mod Wheel) ###
    expression_value = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 11), None)
    mod_wheel_value = next((cc["value"] / 127.0 for cc in ccs if cc["controller"] == 1), None)

    def clamp(value, min_val, max_val):
        """Ensures value stays within the min-max range."""
        return max(min_val, min(value, max_val))

    ### ✅ Envelope 1: Amplitude Envelope (Volume) ###
    env1_attack = clamp(avg_note_length ** 1.2 * note_density_factor, 0.3, 34)  # **Non-linear scaling**
    env1_decay = clamp(avg_note_length * 0.5 * note_density_factor, 0, 32)   
    env1_sustain = clamp(sustain_level * (1.0 - note_density_factor * 0.5), 0, 1)  # **Density-based scaling**
    env1_release = clamp(avg_note_length * 0.8 * note_density_factor, 0, 32)
    env1_delay = clamp(avg_gap * 0.5, 0, 4)  
    env1_hold = clamp(avg_note_length * 1.5 * note_density_factor, 0.4, 1.0)  

    preset["settings"].update({
        "env_1_attack":  env1_attack,
        "env_1_decay":   env1_decay,
        "env_1_sustain": env1_sustain,
        "env_1_release": env1_release,
        "env_1_delay": env1_delay,
        "env_1_hold": env1_hold,  
    })
    print(f"✅ ENV1 → A={env1_attack:.2f}s, D={env1_decay:.2f}s, S={env1_sustain:.2f}, R={env1_release:.2f}s, H={env1_hold:.2f}, Delay={env1_delay:.2f}")

    ### ✅ Envelope 2: Filter Envelope ###
    env2_attack = clamp(avg_note_length ** 1.1 * note_density_factor, 0.3, 34)  # **Slightly nonlinear**
    env2_decay = clamp(avg_note_length * 0.7 * note_density_factor, 0, 32)  
    env2_sustain = clamp(sustain_level * (1.0 - note_density_factor * 0.4), 0, 1)  
    env2_release = clamp(avg_note_length * 1.2 * note_density_factor, 0, 32)
    env2_delay = clamp(avg_gap * 0.4, 0, 4)  
    env2_hold = clamp(avg_note_length * 1.2 * note_density_factor, 0.4, 1.0)  

    if mod_wheel_value:
        env2_sustain = clamp(env2_sustain * (0.7 + mod_wheel_value * 0.3), 0, 1)  

    preset["settings"].update({
        "env_2_attack":  env2_attack,
        "env_2_decay":   env2_decay,
        "env_2_sustain": env2_sustain,
        "env_2_release": env2_release,
        "env_2_delay": env2_delay,
        "env_2_hold": env2_hold,  
    })
    print(f"✅ ENV2 → A={env2_attack:.2f}s, D={env2_decay:.2f}s, S={env2_sustain:.2f}, R={env2_release:.2f}s, H={env2_hold:.2f}, Delay={env2_delay:.2f}")

    ### ✅ Envelope 3: Oscillator Morphing/Pitch ###
    env3_attack = clamp(avg_note_length ** 1.15 * note_density_factor, 0.3, 34)  
    env3_decay = clamp(avg_note_length * 0.6 * note_density_factor, 0, 32)  
    env3_sustain = clamp(sustain_level * (1.0 - note_density_factor * 0.3), 0, 1)  
    env3_release = clamp(avg_note_length * 1.5 * note_density_factor, 0, 32)
    env3_delay = clamp(avg_gap * 0.3, 0, 4)  
    env3_hold = clamp(avg_note_length * 1.8 * note_density_factor, 0.4, 1.0)  

    preset["settings"].update({
        "env_3_attack":  env3_attack,
        "env_3_decay":   env3_decay,
        "env_3_sustain": env3_sustain,
        "env_3_release": env3_release,
        "env_3_delay": env3_delay,
        "env_3_hold": env3_hold,  
    })
    print(f"✅ ENV3 → A={env3_attack:.2f}s, D={env3_decay:.2f}s, S={env3_sustain:.2f}, R={env3_release:.2f}s, H={env3_hold:.2f}, Delay={env3_delay:.2f}")

    print("✅ Envelope modulations added: ENV2 → Filter, ENV3 → Warp")


def apply_filters_to_preset(preset, cc_map):
    """
    Enables and configures Filter 1 & 2 based on MIDI CC data.
    Maps cutoff and resonance values from CCs, using a log-scale mapping from 20 Hz to 20 kHz,
    and writes parameters under preset["filters"].
    """
    # Ensure filters structure exists
    preset.setdefault("filters", {})
    preset["filters"].setdefault("filter_1", {})
    preset["filters"].setdefault("filter_2", {})

    def scale_cutoff(cc_value):
        """
        Given cc_value (0.0–1.0), compute a target frequency between 20 Hz and 20 kHz,
        then convert that frequency back to a normalized value (0.0–1.0) using a logarithmic scale.
        """
        min_freq = 20.0
        max_freq = 20000.0
        # Compute target frequency (this step is optional if you want a non-linear mapping)
        freq = min_freq * (max_freq / min_freq) ** cc_value
        # Convert frequency back to normalized (0–1) using log scaling
        normalized = (math.log(freq) - math.log(min_freq)) / (math.log(max_freq) - math.log(min_freq))
        return max(0.0, min(1.0, normalized))

    # --- Filter 1 ---
    filter_1_ccs = {74, 71, 102}  # 74 & 102 for cutoff, 71 for resonance
    filter_1_detected = [cc for cc in filter_1_ccs if cc in cc_map and cc_map[cc] >= 0.01]
    if filter_1_detected:
        preset["filters"]["filter_1"]["enabled"] = True
        for cc in filter_1_detected:
            if cc in {74, 102}:
                preset["filters"]["filter_1"]["cutoff"] = scale_cutoff(cc_map[cc])
            elif cc == 71:
                preset["filters"]["filter_1"]["resonance"] = cc_map[cc]
    else:
        preset["filters"]["filter_1"]["enabled"] = False

    # --- Filter 2 ---
    filter_2_ccs = {85, 86, 103, 104}  # 85 & 103 for cutoff; 86 & 104 for resonance
    filter_2_detected = [cc for cc in filter_2_ccs if cc in cc_map and cc_map[cc] >= 0.01]
    if filter_2_detected:
        preset["filters"]["filter_2"]["enabled"] = True
        for cc in filter_2_detected:
            if cc in {85, 103}:
                preset["filters"]["filter_2"]["cutoff"] = scale_cutoff(cc_map[cc])
            elif cc in {86, 104}:
                preset["filters"]["filter_2"]["resonance"] = cc_map[cc]
    else:
        preset["filters"]["filter_2"]["enabled"] = False

    print(f"Filter 1 CCs detected: {filter_1_detected}")
    print(f"Filter 2 CCs detected: {filter_2_detected}")


def apply_effects_to_preset(preset, cc_map):
    """
    Applies MIDI CC-based effect settings. This function creates or updates entries under
    preset["fx"] to enable effects (like reverb, chorus, delay, phaser, distortion, etc.)
    and sets their key parameters.
    """
    preset.setdefault("fx", {})

    # Reverb (e.g., CC91 controls reverb dry/wet)
    if 91 in cc_map and cc_map[91] > 0.1:
        preset["fx"].setdefault("reverb", {})
        preset["fx"]["reverb"]["enabled"] = True
        preset["fx"]["reverb"]["dry_wet"] = cc_map[91]
    else:
        if "reverb" in preset["fx"]:
            preset["fx"]["reverb"]["enabled"] = False

    # Chorus (e.g., CC93 controls chorus dry/wet)
    if 93 in cc_map and cc_map[93] > 0.1:
        preset["fx"].setdefault("chorus", {})
        preset["fx"]["chorus"]["enabled"] = True
        preset["fx"]["chorus"]["dry_wet"] = cc_map[93]
    else:
        if "chorus" in preset["fx"]:
            preset["fx"]["chorus"]["enabled"] = False

    # Delay (e.g., CC94 controls delay dry/wet)
    if 94 in cc_map and cc_map[94] > 0.1:
        preset["fx"].setdefault("delay", {})
        preset["fx"]["delay"]["enabled"] = True
        preset["fx"]["delay"]["dry_wet"] = cc_map[94]
    else:
        if "delay" in preset["fx"]:
            preset["fx"]["delay"]["enabled"] = False

    # Phaser (e.g., CC95 controls phaser dry/wet)
    if 95 in cc_map and cc_map[95] > 0.1:
        preset["fx"].setdefault("phaser", {})
        preset["fx"]["phaser"]["enabled"] = True
        preset["fx"]["phaser"]["dry_wet"] = cc_map[95]
    else:
        if "phaser" in preset["fx"]:
            preset["fx"]["phaser"]["enabled"] = False

    # Distortion (e.g., CC116 controls distortion drive)
    if 116 in cc_map and cc_map[116] > 0.1:
        preset["fx"].setdefault("distortion", {})
        preset["fx"]["distortion"]["enabled"] = True
        preset["fx"]["distortion"]["drive"] = cc_map[116]
    else:
        if "distortion" in preset["fx"]:
            preset["fx"]["distortion"]["enabled"] = False

    # Compressor (e.g., CC117 controls compressor amount)
    if 117 in cc_map and cc_map[117] > 0.1:
        preset["fx"].setdefault("compressor", {})
        preset["fx"]["compressor"]["enabled"] = True
        preset["fx"]["compressor"]["amount"] = cc_map[117]
    else:
        if "compressor" in preset["fx"]:
            preset["fx"]["compressor"]["enabled"] = False

    # Flanger (e.g., CC119 controls flanger dry/wet)
    if 119 in cc_map and cc_map[119] > 0.1:
        preset["fx"].setdefault("flanger", {})
        preset["fx"]["flanger"]["enabled"] = True
        preset["fx"]["flanger"]["dry_wet"] = cc_map[119]
    else:
        if "flanger" in preset["fx"]:
            preset["fx"]["flanger"]["enabled"] = False


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


def enable_sample_in_preset(preset, sample_path="assets/sample.wav"):
    """
    Reads a WAV file from sample_path, base64-encodes its bytes,
    and embeds the data in the preset's "sample" key.
    """
    try:
        with open(sample_path, "rb") as f:
            raw = f.read()
        encoded = base64.b64encode(raw).decode("utf-8")
        preset["sample"] = {
            "enabled": True,
            "playback_mode": "one_shot",
            "sample_bytes": encoded
        }
        print("Sample oscillator enabled with sample from:", sample_path)
    except Exception as e:
        print(f"Error loading sample from {sample_path}: {e}")


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


def derive_oscillator_params(stats, osc_index):
    avg_velocity = stats["avg_velocity"]
    pitch_range = stats["pitch_range"]
    note_density = stats["note_density"]

    # Oscillator Parameter Logic (adjust as desired)
    params = {
        "osc_{0}_unison_voices".format(osc_index): float(min(8, int(1 + note_density / 5))),
        "osc_{0}_unison_detune".format(osc_index): min(20, pitch_range / 2),
        "osc_{0}_phase".format(osc_index): 0.5,
        "osc_{0}_transpose".format(osc_index): 0.0,
        "osc_{0}_tune".format(osc_index): (stats["avg_pitch"] - 60) % 12,
        "osc_{0}_level".format(osc_index): min(1.0, avg_velocity + 0.1 * osc_index),
        "osc_{0}_pan".format(osc_index): (-0.5 + osc_index * 0.5),
        "osc_{0}_random_phase".format(osc_index): 1.0 if osc_index % 2 else 0.0,
        "osc_{0}_frame_spread".format(osc_index): min(1.0, pitch_range / 12),
        "osc_{0}_stereo_spread".format(osc_index): 0.8,
        "osc_{0}_spectral_unison".format(osc_index): 0.0,
        "osc_{0}_spectral_morph_amount".format(osc_index): 0.5,
    }

    return params


def apply_oscillator_params_to_preset(preset, midi_data):
    stats = compute_midi_stats(midi_data)

    for osc_index in range(1, 4):
        osc_params = derive_oscillator_params(stats, osc_index)
        preset["settings"].update(osc_params)

    print("✅ Oscillator parameters applied based on MIDI data.")



def modify_vital_preset(vital_preset, midi_file, snapshot_method="1"):
    """
    High-level function that modifies a Vital preset with MIDI data
    (notes, CCs, pitch bends, etc.) and returns the updated preset plus
    the generated wavetable frame data.
    """
    import copy, os, logging
    from midi_parser import parse_midi
    # Ensure that the following helper functions are available:
    # update_settings, apply_cc_modulations, apply_dynamic_env_to_preset,
    # generate_three_frame_wavetables, build_lfo_from_cc,
    # apply_filters_to_preset, apply_effects_to_preset, enable_sample_in_preset,
    # compute_midi_stats, derive_oscillator_params, apply_oscillator_params_to_preset

    logging.info(f"🔍 Debug: Received midi_file of type {type(midi_file)}")
    
    # 1) Parse MIDI data: either from an existing dict or a file path
    try:
        if isinstance(midi_file, dict):
            logging.warning("⚠️ Using existing parsed MIDI data instead of a file path.")
            midi_data = midi_file
        elif isinstance(midi_file, str):
            logging.info(f"📂 Parsing MIDI file: {midi_file}")
            midi_data = parse_midi(midi_file)
        else:
            raise ValueError(f"Invalid type for midi_file: {type(midi_file)}")
    except Exception as e:
        logging.error(f"❌ Error parsing MIDI: {e}")
        midi_data = {"notes": [], "control_changes": [], "pitch_bends": []}

    # 2) Deep-copy the preset so the original is not mutated
    modified = copy.deepcopy(vital_preset)

    # Extract MIDI components
    notes = midi_data.get("notes", [])
    ccs = midi_data.get("control_changes", [])
    pitch_bends = midi_data.get("pitch_bends", [])

    # Ensure "settings" exists
    modified.setdefault("settings", {})

    # 3) Snapshot method: update osc1 pitch/level based on chosen method
    update_settings(modified, notes, snapshot_method)

    # 4) Apply CC-based direct parameter mappings
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    apply_cc_modulations(modified, cc_map)

    # 5) Set pitch bend (final pitch wheel value)
    modified["pitch_wheel"] = pitch_bends[-1]["pitch"] / 8192.0 if pitch_bends else 0.0

    # 6) Apply dynamic envelopes based on MIDI note data
    apply_dynamic_env_to_preset(modified, midi_data)

    # ✅ Debug: Log final envelope values
    logging.info("\n🔍 **Final Envelope Values in Modified Preset:**")
    for env in ["env_1", "env_2", "env_3"]:
        logging.info(f"  {env}_attack: {modified.get(f'{env}_attack', 'N/A')}")
        logging.info(f"  {env}_decay: {modified.get(f'{env}_decay', 'N/A')}")
        logging.info(f"  {env}_sustain: {modified.get(f'{env}_sustain', 'N/A')}")
        logging.info(f"  {env}_release: {modified.get(f'{env}_release', 'N/A')}")

    # 7) **Apply dynamic oscillator settings based on MIDI data**
    # This function computes MIDI stats and updates oscillator parameters
    apply_oscillator_params_to_preset(modified, midi_data)

    # 8) Generate three wavetable frames
    frame_data = generate_three_frame_wavetables(midi_data, num_frames=3, frame_size=2048)

    # 9) Enable oscillators based on note count
    num_notes = len(notes)
    modified["settings"]["osc_1_on"] = 1.0 if num_notes > 0 else 0.0
    modified["settings"]["osc_2_on"] = 1.0 if num_notes > 1 else 0.0
    modified["settings"]["osc_3_on"] = 1.0 if num_notes > 2 else 0.0

    # 10) Enable Sample Oscillator if specific MIDI CCs are present
    SMP_CCS = {31, 39, 40, 74, 85, 86}  # List of CCs that can trigger the sample oscillator
    smp_detected = [cc for cc in SMP_CCS if cc in cc_map and cc_map[cc] > 0.01]
    if smp_detected:
        modified["settings"]["sample_on"] = 1.0
        logging.info(f"✅ Enabling SMP (Sample Oscillator) due to MIDI CCs: {smp_detected}.")
        enable_sample_in_preset(modified, sample_path="assets/sample.wav")
    else:
        modified["settings"]["sample_on"] = 0.0
        logging.info("❌ SMP NOT Enabled.")

    # 11) Apply filters using the updated, modular function
    apply_filters_to_preset(modified, cc_map)

    # 12) Apply effects using the new modular function (instead of inline mapping)
    apply_effects_to_preset(modified, cc_map)

    # 13) Apply LFO modulations (each with unique rate/depth settings)
    build_lfo_from_cc(modified, midi_data, lfo_idx=1, destination="filter_1_cutoff")
    build_lfo_from_cc(modified, midi_data, lfo_idx=2, destination="osc_1_pitch", one_shot=True)
    build_lfo_from_cc(modified, midi_data, lfo_idx=3, destination="volume")
    build_lfo_from_cc(modified, midi_data, lfo_idx=4, destination="filter_2_resonance")

    # 14) Append envelope modulations
    modified.setdefault("modulations", [])
    modified["modulations"].append({
        "source": "env_2",
        "destination": "filter_1_cutoff",
        "amount": 0.8
    })
    modified["modulations"].append({
        "source": "env_3",
        "destination": "osc_1_warp",
        "amount": 0.6
    })

    # 15) Apply generated wavetable frames to the first oscillator keyframes
    if "groups" in modified and modified["groups"]:
        group0 = modified["groups"][0]
        if "components" in group0 and group0["components"]:
            component0 = group0["components"][0]
            if "keyframes" in component0:
                keyframes = component0["keyframes"]
                while len(keyframes) < 3:
                    keyframes.append({
                        "position": 0.0,
                        "wave_data": "",
                        "wave_source": {"type": "sample"}
                    })
                wavetable_names = ["Attack Phase", "Harmonic Blend", "Final Release"]
                for i in range(3):
                    keyframes[i]["wave_data"] = frame_data[i]
                    keyframes[i]["wave_source"] = {"type": "sample"}
                component0["name"] = "Generated Wavetable"

    # 16) Update the preset name based on the MIDI file name
    if "preset_name" in modified:
        midi_base_name = os.path.splitext(os.path.basename(midi_file))[0] if isinstance(midi_file, str) else "Custom_Preset"
        modified["preset_name"] = f"Generated from {midi_base_name}"

    # 17) Rename the first three occurrences of "Init" names to descriptive ones
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

    logging.info("✅ Finished applying wavetables, envelopes, LFOs, filters, effects, sample oscillator, and custom oscillator settings.")
    return modified, frame_data


def get_preset_filename(midi_path):
    """
    Extracts the base name from the MIDI file and ensures it has a .vital extension.
    """
    base_name = os.path.splitext(os.path.basename(midi_path))[0]
    return f"{base_name}.vital"


def save_vital_preset(vital_preset, midi_path, frame_data_list=None):
    """
    Saves the modified Vital preset as an uncompressed JSON file
    named after the MIDI file (but with a .vital extension).
    
    Args:
        vital_preset (dict): The modified Vital preset data.
        midi_path (str): The path to the original MIDI file.
        frame_data_list (list): Optional list of three wavetables (base64 strings).
    
    Returns:
        str: The output file path if successful, None otherwise.
    """
    try:
        # Generate the output path based on MIDI file name
        output_path = os.path.join(OUTPUT_DIR, get_preset_filename(midi_path))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Ensure "modulations" key exists
        vital_preset.setdefault("modulations", [])

        # Convert the preset to JSON format
        json_data = json.dumps(vital_preset, indent=2)

        # If valid wavetables are provided, replace them
        if isinstance(frame_data_list, list) and len(frame_data_list) == 3:
            json_data = replace_three_wavetables(json_data, frame_data_list)
            logging.info("✅ Replaced wavetables in the preset.")
        else:
            logging.warning("⚠️ No valid wave_data provided or not exactly 3 frames.")

        # Write the preset to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_data)

        logging.info(f"✅ Successfully saved Vital preset as JSON: {output_path}")
        return output_path  # Return the path for reference

    except OSError as e:
        logging.error(f"❌ File error when saving Vital preset: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"❌ JSON encoding error: {e}")
    except Exception as e:
        logging.error(f"❌ Unexpected error in save_vital_preset: {e}")

    return None


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
 