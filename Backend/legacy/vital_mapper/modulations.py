import logging
from typing import Any, Dict, List

# MIDI parsing/stats
from midi_analysis import compute_midi_stats

# Config maps and thresholds
from config import (
    MIDI_TO_VITAL_MAP,
    EFFECTS_CC_MAP
)


def apply_modulations_to_preset(preset: Dict[str, Any], midi_data: Dict[str, Any]) -> None:
    """
    Applies advanced modulation logic to the Vital preset, based on MIDI CCs, note features, and expressive controls.
    Dynamically adapts macro targets, routes mod wheel/expression, and enhances musicality.
    """

    preset.setdefault("settings", {})
    preset["settings"].setdefault("modulations", [])
    modulations = []

    # === Extract MIDI data ===
    ccs = midi_data.get("control_changes", [])
    cc_map = {cc["controller"]: cc["value"] / 127.0 for cc in ccs}
    stats = compute_midi_stats(midi_data)

    avg_vel = stats.get("avg_velocity", 80) / 127.0
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    expressive = any(cc in cc_map for cc in [1, 11])

    # === 1. Map CCs directly to parameters ===
    for cc_num, cc_val in cc_map.items():
        if cc_num in MIDI_TO_VITAL_MAP:
            param = MIDI_TO_VITAL_MAP[cc_num]
            preset["settings"][param] = cc_val
            print(f"✅ CC{cc_num} -> {param} = {cc_val:.2f}")

    # === 2. Mod Wheel / Expression ===
    if 1 in cc_map and cc_map[1] > 0.05:
        modulations.append({
            "source": "mod_wheel",
            "destination": "filter_1_cutoff",
            "amount": cc_map[1] * 0.8
        })
    if 11 in cc_map:
        modulations.append({
            "source": "cc_expression",
            "destination": "volume",
            "amount": cc_map[11]
        })

    # === 3. Dynamic Macro Routing ===
    # Detect active filters and dominant FX
    filter_dest = "filter_1_cutoff" if preset["settings"].get("filter_1_on", 0.0) else "filter_2_cutoff"
    fx_strengths = {
        fx: cc_map.get(cc, 0.0) for fx, cc in EFFECTS_CC_MAP.items()
    }
    main_fx = max(fx_strengths.items(), key=lambda x: x[1])[0] if fx_strengths else "reverb"
    main_fx_param = f"{main_fx}_dry_wet" if main_fx in ["reverb", "delay", "chorus"] else f"{main_fx}_drive"

    # Macro sources
    macros = {
        "macro_control_1": cc_map.get(20, 0.5),
        "macro_control_2": cc_map.get(21, 0.5),
        "macro_control_3": cc_map.get(22, 0.5),
        "macro_control_4": cc_map.get(23, 0.5),
    }
    preset["settings"].update(macros)

    modulations.extend([
        {"source": "macro_control_1", "destination": filter_dest, "amount": 0.8},
        {"source": "macro_control_2", "destination": "osc_1_warp", "amount": 0.7},
        {"source": "macro_control_3", "destination": main_fx_param, "amount": 0.6},
        {"source": "macro_control_4", "destination": "lfo_1_frequency", "amount": 0.5},
    ])

    # === 4. Envelope modulations ===
    modulations.extend([
        {"source": "env_2", "destination": filter_dest, "amount": 0.8},
        {"source": "env_3", "destination": "osc_1_frame", "amount": 0.6},
    ])

    # === 5. Adaptive pitch modulation ===
    if pitch_range > 12:
        modulations.append({
            "source": "lfo_2",
            "destination": "osc_1_pitch",
            "amount": 0.4 + (pitch_range / 48.0)
        })
    if note_density > 5.0:
        modulations.append({
            "source": "lfo_3",
            "destination": "filter_2_resonance",
            "amount": 0.3 + (note_density / 20.0)
        })

    # === 6. Pitch bend detection ===
    if any(pb["pitch"] > 0.1 for pb in midi_data.get("pitch_bends", [])):
        preset["settings"]["pitch_bend_range"] = 12

    # === Finalize ===
    preset["settings"]["modulations"] = modulations
    print(f"✅ {len(modulations)} modulations applied dynamically.")

def apply_macro_controls_to_preset(preset: Dict[str, Any], cc_map: Dict[int, float]) -> None:
    """
    Apply macros to dynamic modulation targets based on active filters and FX.
    Velocity-based macro values should already be set. This only overrides with CCs if provided.
    """
    preset.setdefault("settings", {})
    preset["settings"].setdefault("modulations", [])
    settings = preset["settings"]

    # Step 1: Allow CCs to override macro values if present
    for i in range(1, 5):
        cc_num = 19 + i  # CC20-23
        macro_key = f"macro_control_{i}"
        if cc_num in cc_map:
            settings[macro_key] = cc_map[cc_num]

    # Step 2: Detect active filters and effects
    filter_1_active = settings.get("filter_1_on", 0.0) >= 1.0
    filter_2_active = settings.get("filter_2_on", 0.0) >= 1.0
    reverb_active = settings.get("reverb_on", 0.0) >= 1.0
    delay_active = settings.get("delay_on", 0.0) >= 1.0
    distortion_active = settings.get("distortion_on", 0.0) >= 1.0
    chorus_active = settings.get("chorus_on", 0.0) >= 1.0
    phaser_active = settings.get("phaser_on", 0.0) >= 1.0

    # Step 3: Dynamically assign macro modulations
    macro_mods = []

    # 🟣 Macro 1 → Main filter (whichever is on)
    existing_macro1_routes = [mod for mod in settings["modulations"] if mod.get("source") == "macro1"]
    if existing_macro1_routes:
        logging.info("🛡️ Skipping Macro 1 routing – already dynamically handled.")
    else:
        if filter_1_active:
            macro_mods.extend([
                {"source": "macro_control_1", "destination": "filter_1_cutoff", "amount": 0.8},
                {"source": "macro_control_1", "destination": "osc_1_frame", "amount": 0.4},
            ])
        elif filter_2_active:
            macro_mods.extend([
                {"source": "macro_control_1", "destination": "filter_2_cutoff", "amount": 0.8},
                {"source": "macro_control_1", "destination": "osc_2_frame", "amount": 0.4},
            ])

    # 🔥 Macro 2 → Distortion + filter2 resonance if used
    if distortion_active:
        macro_mods.append({"source": "macro_control_2", "destination": "distortion_drive", "amount": 0.7})
    if filter_2_active:
        macro_mods.append({"source": "macro_control_2", "destination": "filter_2_resonance", "amount": 0.5})

    # 🌊 Macro 3 → Reverb or Delay
    if reverb_active:
        macro_mods.extend([
            {"source": "macro_control_3", "destination": "reverb_dry_wet", "amount": 0.6},
            {"source": "macro_control_3", "destination": "reverb_feedback", "amount": 0.3},
        ])
    elif delay_active:
        macro_mods.extend([
            {"source": "macro_control_3", "destination": "delay_dry_wet", "amount": 0.6},
            {"source": "macro_control_3", "destination": "delay_feedback", "amount": 0.4},
        ])

    # 🎛️ Macro 4 → Chorus, Phaser, or fallback
    if chorus_active:
        macro_mods.append({"source": "macro_control_4", "destination": "chorus_dry_wet", "amount": 0.5})
    if phaser_active:
        macro_mods.append({"source": "macro_control_4", "destination": "phaser_feedback", "amount": 0.3})
    if not (chorus_active or phaser_active):
        macro_mods.append({"source": "macro_control_4", "destination": "delay_feedback", "amount": 0.3})

    # Add to preset
    settings["modulations"].extend(macro_mods)

    logging.info(f"✅ Macro routing complete. {len(macro_mods)} dynamic modulations applied.")

