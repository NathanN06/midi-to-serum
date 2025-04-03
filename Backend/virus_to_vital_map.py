virus_to_vital_map = {
    "Bank_Select": None,
    "Modulation_Wheel": {
    "vital_target": "macro_control_1",
    "scale": lambda x: x / 127  
    },
    "Breath_Controller": None,
    "Contr_3": None,
    "Foot_Controller": None,
    "Portamento_Time": {
    "vital_target": "portamento_time",
    "scale": lambda x: (x / 127) * 20 - 10  # Vital's range is approximately -10 to +10
    },
    "Data_Slider": None,
    "Channel_Volume": None,  # No direct amp/output volume parameter in Vital; consider macro or leave unmapped
    "Balance": {
    "vital_target": ["osc_1_level", "osc_2_level"],
    "scale": lambda x: {
        "osc_1_level": 1 - (x / 127),
        "osc_2_level": x / 127
    }   
    },
    "Contr_9": None,
    # Panorama likely controls overall stereo position — apply equally to all oscillator pans
    "Panorama": [
    {
        "vital_target": "osc_1_pan",
        "scale": lambda x: (x - 64) / 64
    },
    {
        "vital_target": "osc_2_pan",
        "scale": lambda x: (x - 64) / 64
    },
    {
        "vital_target": "osc_3_pan",
        "scale": lambda x: (x - 64) / 64
    }
    ],
    "Expression": {
    "vital_target": "macro_control_2",
    "scale": lambda x: x / 127
    },
    "Contr_12": None,
    "Contr_13": None,
    "Contr_14": None,
    "Contr_15": None,
    "Contr_16": None,
    
    "Osc1_Shape": {
    "handler": "inject_osc1_waveform_from_shape"
    },

    "Osc1_Pulsewidth": None,  # No direct mapping unless square waveform is explicitly selected
    "Osc1_Wave_Select": None,  # Shape is handled via injected wavetable; no direct float index in Vital
    "Osc1_Semitone": {
        # In actual list => keep
        "vital_target": "osc_1_transpose",
        "scale": lambda x: x - 64
    },
    "Osc1_Keyfollow": {
    # ❌ Not mappable: Vital does not support per-oscillator keytracking control
    "vital_target": None,
    "scale": lambda x: x / 127
    },
    "Osc2_Shape": {
    "handler": "inject_osc2_waveform_from_shape"
    },
     "Osc2_Pulsewidth": {
        # Not in actual list => None
        "vital_target": None,
        "scale": lambda x: x / 127
    },
    "Osc2_Wave_Select": {
    # Redundant — waveform is determined by Osc2_Shape
    "vital_target": None,
    "scale": lambda x: x / 64   
    },
    "Osc2_Semitone": {
        # In actual list => keep
        "vital_target": "osc_2_transpose",
        "scale": lambda x: x - 64
    },
    "Osc2_Detune": {
        # You requested mapping this to osc_2_tune specifically
        "vital_target": "osc_2_tune",
        "scale": lambda x: (x - 64) / 64
    },
    "Osc2_FM_Amount": {
        # Not in actual list => None
        "vital_target": None,
        "scale": lambda x: x / 127
    },
    "Osc2_FM_Amount": {
    # Approximated using spectral morph amount (no true FM in Vital)
    "vital_target": "osc_2_spectral_morph_amount",
    "scale": lambda x: x / 127
    },
   "Osc2_Filt_Env_Amt": {
    # Modulation: Filter envelope → Filter cutoff depth
    # No direct parameter in Vital — needs custom modulation handler later
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64
    },

    "FM_Filt_Env_Amt": {
    # Modulation: Filter envelope → FM amount
    # Needs modulation injection later
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64,
    "modulation_hint": {
        "source": "env_1",
        "target": "osc_2_phase_mod_amount"  # or whichever oscillator is FM'd
    }
    },
    "Osc2_Keyfollow": {
    # Modulation: note pitch → oscillator 2 tune
    "vital_target": None,
    "scale": lambda x: x / 127,
    "modulation_hint": {
        "source": "note",
        "target": "osc_2_tune"
    }
    },
    "Bank_Select_Alt": None,  # No parameters or scale
    
    "Osc_Balance": {
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64,
    "comment": "🟡 Maybe: could be mapped to osc_1_level and osc_2_level inversely"
    },

    "Suboscillator_Volume": {
        # In actual list => keep
        "vital_target": "osc_3_level",
        "scale": lambda x: x / 127
    },
    "Suboscillator_Shape": {
    "handler": "inject_osc3_waveform_from_shape"    
    },

    "Osc_Mainvolume": {
    # 🛈 No direct amp/output volume parameter in Vital — potentially use macro later?
    "vital_target": None,
    "scale": lambda x: x / 127
    },
    "Noise_Volume": {
    # No direct noise_level parameter in Vital; possibly use sample osc later
    "vital_target": None,
    "scale": lambda x: x / 127
    },
    "Ringmodulator_Volume": {
    # ❓ No native ring modulation in Vital — tag for supervisor review
    "vital_target": None,
    "scale": lambda x: x / 127
    },
    "Reserved_Unknown": None,
    "Cutoff": {
        "vital_target": "filter_1_cutoff",
        "scale": lambda x: x / 127
    },
    "Cutoff2": {
        "vital_target": "filter_2_cutoff",
        "scale": lambda x: (x - 64) / 64  # Relative offset (-1 to +1)
    },
    "Filter1_Resonance": {
        "vital_target": "filter_1_resonance",
        "scale": lambda x: x / 127
    },
    "Filter2_Resonance": {
        "vital_target": "filter_2_resonance",
        "scale": lambda x: x / 127
    },
    
    "Filter1_Env_Amt": {
    # 🔁 Modulation Only: Use this value to create a modulation route from Env1 → Filter1 Cutoff
    "modulation_target": "filter_1_cutoff",
    "modulation_source": "env_1",
    "scale": lambda x: (x - 64) / 64
    },
    "Filter2_Env_Amt": {
    # 🔁 Modulation Only: Use this value to create a modulation route from Env1 → Filter2 Cutoff
    "modulation_target": "filter_2_cutoff",
    "modulation_source": "env_1",
    "scale": lambda x: (x - 64) / 64
    },

    "Filter1_Keyfollow": {
        "vital_target": "filter_1_keytrack",
        "scale": lambda x: (x - 64) / 64  # -1 to +1 (negative to positive tracking)
    },
    "Filter2_Keyfollow": {
        "vital_target": "filter_2_keytrack",
        "scale": lambda x: (x - 64) / 64
    },
    "Filter_Balance": {
    "handler": "set_filter_balance_mix" 
    },
    "Saturation_Curve": {
    "vital_target": "distortion_type",
    "scale": lambda x: min(x, 6),
    "extra": lambda x, settings: settings.update({"distortion_on": 1.0}) if x > 0 else None
    },

    "Filter1_Mode": {
    "vital_target": "filter_1_model",  # this exists
    "scale": lambda x: min(x, 3)       # 0: LP, 1: HP, 2: BP, 3: Notch (or closest match)
    },
     "Filter2_Mode": {
    "vital_target": "filter_2_model",  # This exists in the JSON
    "scale": lambda x: min(x, 3)       # Clamp to range 0–3 to stay safe
    },

    "Filter_Routing": {
        "vital_target": "filter_routing",
        "scale": lambda x: min(x, 3)  # 0: Serial 4-pole, 1: Serial 6-pole, 2: Parallel, 3: Split
    },
    "Filter_Env_Attack": {
        "vital_target": "env_2_attack",
        "scale": lambda x: x / 127
    },
    "Filter_Env_Decay": {
        "vital_target": "env_2_decay",
        "scale": lambda x: x / 127
    },
    "Filter_Env_Sustain": {
        "vital_target": "env_2_sustain",
        "scale": lambda x: x / 127
    },
    "Filter_Env_Sustain_Time": {
        "vital_target": "env_2_hold",
        "scale": lambda x: (x - 64) / 64  # Negative: short hold, Positive: long hold
    },
    "Filter_Env_Release": {
        "vital_target": "env_2_release",
        "scale": lambda x: x / 127
    },
    "Amp_Env_Attack": {
        "vital_target": "env_1_attack",
        "scale": lambda x: x / 127
    },
    "Amp_Env_Decay": {
        "vital_target": "env_1_decay",
        "scale": lambda x: x / 127
    },
    "Amp_Env_Sustain": {
        "vital_target": "env_1_sustain",
        "scale": lambda x: x / 127
    },
    "Amp_Env_Sustain_Time": {
        "vital_target": "env_1_hold",
        "scale": lambda x: (x - 64) / 64  # -1 (shorter) to +1 (longer)
    },
    "Amp_Env_Release": {
        "vital_target": "env_1_release",
        "scale": lambda x: x / 127
    },
    "Hold_Pedal": None,  # Typically MIDI performance-related, not directly mapped
    "Portamento_Pedal": {
    "vital_target": "portamento_time",
    "scale": lambda x: 0.2 if x > 0 else -10.0  # 0.2 enables glide, -10 disables it
    },
    "Sostenuto_Pedal": {
    "vital_target": None,
    "scale": lambda x: x / 127,
    "note": "Performance controller, no Vital equivalent"
    },
    "Lfo1_Rate": {
        "vital_target": "lfo_1_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo1_Shape": {
    "handler": "inject_lfo1_shape_from_sysex"
    },

    "Lfo1_Env_Mode": {
        "vital_target": "lfo_1_env_mode",
        "scale": lambda x: 1 if x > 0 else 0  # Off/On (Envelope mode)
    },
    "Lfo1_Mode": {
    "vital_target": None,
    "scale": lambda x: 1 if x > 0 else 0,  # 0: Poly, 1: Mono
    "note": "No equivalent parameter in Vital — skipping"
    },
    "Lfo1_Symmetry": [
    {
        "vital_target": "lfo_1_smooth_mode",
        "scale": lambda x: 1 if x > 64 else 0
    },
    {
        "vital_target": "lfo_1_smooth_time",
        "scale": lambda x: ((x / 127) * 15.0) - 7.5
    }
    ],
    "Lfo1_Keyfollow": [
    {
        "vital_target": "lfo_1_keytrack_transpose",
        "scale": lambda x: (x / 127) * 24 - 12  # Maps 0–127 to -12 to +12 semitones
    },
    {
        "vital_target": "lfo_1_keytrack_tune",
        "scale": lambda x: (x / 127) * 1.0  # Fine tune 0 to 1.0
    }
    ],
    "Lfo1_Keytrigger": {
    "vital_target": None,  # Vital doesn't expose a direct key trigger switch
    "scale": lambda x: 1 if x > 0 else 0,
    "note": "No direct equivalent in Vital; key triggering is usually implicit via sync/phase."
    },

    "Osc1_Lfo1_Amount": {
    # Modulation → LFO1 to Osc1 Pitch (no direct Vital target yet)
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64
    },
    "Osc2_Lfo1_Amount": {
    # Modulation → LFO1 to Osc2 Pitch (no direct Vital target yet)
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64
    },
    "PW_Lfo1_Amount": {
        # ⚠️ Modulation: LFO1 → Pulse Width (target not yet mapped in Vital)
        "vital_target": None,
        "scale": lambda x: (x - 64) / 64
    },
    "Reso_Lfo1_Amount": {
        # ⚠️ Modulation: LFO1 → Filter Resonance (target not yet mapped in Vital)
        "vital_target": None,
        "scale": lambda x: (x - 64) / 64
    },
    "FiltGain_Lfo1_Amount": {
        # ⚠️ Modulation: LFO1 → Filter Drive (target not yet mapped in Vital)
        "vital_target": None,
        "scale": lambda x: (x - 64) / 64
    },

    "Lfo2_Rate": {
        "vital_target": "lfo_2_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo2_Shape": {
    "handler": "inject_lfo2_shape_from_sysex"
    },
   "Lfo2_Env_Mode": {
    # No matching Vital parameter found — tagging as unsupported
    "vital_target": None,
    "scale": lambda x: 1 if x > 0 else 0
    },

    "Lfo2_Mode": {
        # No matching Vital parameter found — tagging as unsupported
        "vital_target": None,
        "scale": lambda x: 1 if x > 0 else 0
    },
    "Lfo2_Symmetry": [
    {
        "vital_target": "lfo_2_smooth_mode",
        "scale": lambda x: 1 if x > 64 else 0  # enable smoothing if above center
    },
    {
        "vital_target": "lfo_2_smooth_time",
        "scale": lambda x: ((x / 127) * 15.0) - 7.5  # Normalize 0–127 to -7.5 to +7.5
    }
    ],
    "Lfo2_Keyfollow": [
    {
        "vital_target": "lfo_2_keytrack_transpose",
        "scale": lambda x: (x / 127) * 24 - 12  # -12 to +12 semitones
    },
    {
        "vital_target": "lfo_2_keytrack_tune",
        "scale": lambda x: (x / 127) * 1.0  # 0.0 to 1.0 fine tune
    }
    ],

    "Lfo2_Keytrigger": {
    "vital_target": None,  # Not available in current Vital format
    "scale": lambda x: 1 if x > 0 else 0  # Still valid logic if added later
    },
   # 🧠 Modulation mappings — no known Vital targets yet, keep for later

    "OscShape_Lfo2_Amount": {
        "vital_target": None,  # Modulation: LFO2 → Oscillator Shape
        "scale": lambda x: (x - 64) / 64
    },

    "FmAmount_Lfo2_Amount": {
        "vital_target": None,  # Modulation: LFO2 → FM Amount
        "scale": lambda x: (x - 64) / 64
    },

    "Cutoff1_Lfo2_Amount": {
        "vital_target": None,  # Modulation: LFO2 → Filter 1 Cutoff
        "scale": lambda x: (x - 64) / 64
    },

    "Cutoff2_Lfo2_Amount": {
        "vital_target": None,  # Modulation: LFO2 → Filter 2 Cutoff
        "scale": lambda x: (x - 64) / 64
    },

    "Panorama_Lfo2_Amount": {
        "vital_target": None,  # Modulation: LFO2 → Panning
        "scale": lambda x: (x - 64) / 64
    },
    "Patch_Volume": {
    "vital_target": None,  # ⚠️ No direct Vital equivalent for global volume (possibly handled via macros or output gain)
    "scale": lambda x: x / 127
    },
    "undefined_92": None,
    "Transpose": {
    "vital_target": None,  # ⚠️ No global transpose param in Vital (consider applying to osc_X_transpose individually)
    "scale": lambda x: x - 64
    },
    "Key_Mode": {
    "vital_target": None,  # ⚠️ No direct 'voice_mode' param in Vital (mono/poly might be handled differently)
    "scale": lambda x: min(x, 4)  # Poly/Mono mode – revisit later if needed
    },
    "undefined_95": None,
    "undefined_96": None,
    "Unison_Mode": {
    "vital_target": [
        "osc_1_unison_voices",
        "osc_2_unison_voices",
        "osc_3_unison_voices"
    ],
    "scale": lambda x: {
        "osc_1_unison_voices": 2 if x > 0 else 1,
        "osc_2_unison_voices": 2 if x > 0 else 1,
        "osc_3_unison_voices": 2 if x > 0 else 1,
    }
    },
    "Unison_Detune": {
    "vital_target": ["osc_1_unison_detune", "osc_2_unison_detune", "osc_3_unison_detune"],
    "scale": lambda x: {
        "osc_1_unison_detune": x / 127,
        "osc_2_unison_detune": x / 127,
        "osc_3_unison_detune": x / 127,
    }
    },
    "Unison_Panorama_Spread": {
    "vital_target": None,
    "scale": lambda x: x / 127,  # stereo width 0 to 1
    "tag": "modulation"
    },
    "Unison_Lfo_Phase": {
    "vital_target": None,
    "scale": lambda x: (x - 64) / 64,  # phase spread from -1 to +1
    "tag": "modulation"
    },
    "Input_Mode": None,  # Not applicable, Virus audio input routing
    "Input_Select": None,  # Not applicable in Vital
    "undefined_103": None,
    "undefined_104": None,
    "Chorus_Mix": {
    "vital_target": "chorus_dry_wet",  # Assuming this is the correct parameter name for dry/wet mix in Vital
    "scale": lambda x: x / 127  # Maps 0 to 127 to 0 to 1 (dry to wet mix)
    },
    "Chorus_Rate": {
        "vital_target": "chorus_frequency",
        "scale": lambda x: x / 127
    },
    "Chorus_Depth": {
        "vital_target": "chorus_mod_depth",
        "scale": lambda x: x / 127
    },
    "Chorus_Delay": {
    "vital_target": "chorus_delay_1",
    "scale": lambda x: x / 127
    },

    "Chorus_Feedback": {
        "vital_target": "chorus_feedback",
        "scale": lambda x: (x - 64) / 64  # -1 to +1
    },
    "Chorus_Lfo_Shape": {
    "vital_target": None,
    "scale": lambda x: min(x, 5),  # Limit to valid Vital shapes (0-5)
    "note": "To be revisited - no direct mapping in Vital, needs custom solution."
    },
    "undefined_111": None,
    "undefined_112": None,
    "Effect_Send": {
    "vital_target": "delay_dry_wet",
    "scale": lambda x: x / 127  # Dry/Wet mix
    },

    "Delay_Time": {
        "vital_target": "delay_tempo",  # Vital uses delay tempo
        "scale": lambda x: x / 127  # Mapping the delay time to tempo
    },

    "Delay_Feedback": {
        "vital_target": "delay_feedback",
        "scale": lambda x: x / 127  # Feedback amount
    },

    "Delay_Rate": {
        "vital_target": "delay_frequency",
        "scale": lambda x: x / 127  # Delay rate or frequency
    },

    "Delay_Depth": {
        "vital_target": "delay_filter_cutoff",  # Vital doesn't have depth for delay, using filter cutoff as placeholder
        "scale": lambda x: x / 127  # Depth mapped to filter cutoff
    },

    "Delay_Lfo_Shape": {
    "vital_target": None,  # No equivalent in Vital at the moment
    "scale": None,  # No scaling since it's not implemented yet
    "note": "This parameter may need to be revisited in the future for LFO-related effects."
    },
    "undefined_119": None,
    "undefined_120": None,
    "undefined_121": None,
    "undefined_122": None,
    "All_Notes_Off": None,  # Not applicable (MIDI function)
    "undefined_124": None,
    "undefined_125": None,
    "undefined_126": None,
    "undefined_127": None,
    "undefined_128": None,
    "Arp_Mode": {
    "vital_target": None,  # No equivalent in Vital at the moment
    "scale": None,  # No scaling available
    "note": "This parameter may need to be revisited in the future for arpeggiator-related effects."
    },
    "undefined_130": None,
    "Arp_Octave_Range": {
    "vital_target": None,  # No equivalent in Vital for arpeggiator octave range
    "scale": None,  # No scaling available
    "note": "This parameter may need to be revisited in the future for arpeggiator-related effects."
    },
    "Arp_Hold_Enable": {
    "vital_target": None,  # No equivalent in Vital for arpeggiator hold
    "scale": None,  # No scaling available
    "note": "This parameter may need to be revisited in the future for arpeggiator hold functionality."
    },
    "undefined_133": None,
    "undefined_134": None,
    "Lfo3_Rate": {
        "vital_target": "lfo_3_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo3_Shape": {
    "handler": "inject_lfo3_shape_from_sysex"
    },
    "Lfo3_Mode": {
        "vital_target": "lfo_3_mode",
        "scale": lambda x: 1 if x > 0 else 0  # Poly(0)/Mono(1)
    },
    "Lfo3_Keyfollow": {
        "vital_target": "lfo_3_keytrack",
        "scale": lambda x: x / 127  # 0 (no tracking) to 1 (full key tracking)
    },
    "Lfo3_Destination": None,  # Dynamic modulation routing, requires advanced mapping logic
    "Osc_Lfo3_Amount": None,  # Depends on LFO3 destination routing logic
    "Lfo3_Fade-In_Time": {
        "vital_target": "lfo_3_delay_time",
        "scale": lambda x: x / 127
    },
    "undefined_142": None,
    "undefined_143": None,
    "Clock_Tempo": {
        "vital_target": "tempo",
        "scale": lambda x: (x / 127) * (190 - 63) + 63  # Map 0–127 to 63–190 BPM
    },
    "Arp_Clock": {
        "vital_target": "arpeggiator_tempo_sync",
        "scale": lambda x: min(x, 17)  # Map to closest available tempo divisions in Vital
    },
    "Lfo1_Clock": {
        "vital_target": "lfo_1_tempo_sync",
        "scale": lambda x: min(x, 19)  # Map tempo divisions
    },
    "Lfo2_Clock": {
        "vital_target": "lfo_2_tempo_sync",
        "scale": lambda x: min(x, 19)  # Map tempo divisions
    },
    "Delay_Clock": {
        "vital_target": "delay_tempo_sync",
        "scale": lambda x: min(x, 16)  # Tempo divisions in Vital
    },
    "Lfo3_Clock": {
        "vital_target": "lfo_3_tempo_sync",
        "scale": lambda x: min(x, 19)  # Map tempo divisions
    },
    # virus_to_vital_map "Page B" block from indices #150–255, corrected:
    "undefined_150": None,
    "undefined_151": None,
    "undefined_152": None,

    "Control_Smooth_Mode": None,  # B 25 => #153
    "Bender_Range_Up": {
        "vital_target": "pitch_wheel_range_up",
        "scale": lambda x: x - 64  # Range -64..+63 semitones
    },
    "Bender_Range_Down": {
        "vital_target": "pitch_wheel_range_down",
        "scale": lambda x: x - 64  # Range -64..+63 semitones
    },
    "Bender_Scale": None,  # B 28 => #156

    "undefined_157": None,  # B 29 (undocumented)

    "Filter1_Env_Polarity": {      # B 30 => #158
        "vital_target": "filter_1_env_polarity",
        "scale": lambda x: 1 if x > 0 else -1
    },
    "Filter2_Env_Polarity": {      # B 31 => #159
        "vital_target": "filter_2_env_polarity",
        "scale": lambda x: 1 if x > 0 else -1
    },
    "Filter2_Cutoff_Link": None,   # B 32 => #160
    "Filter_Keytrack_Base": {      # B 33 => #161
        "vital_target": "filter_keytrack_base",
        "scale": lambda x: (x / 127) * 120 - 60  # e.g. -60..+60 keytrack range
    },
    "undefined_162": None,         # B 34 (undocumented)

    "Osc_Init_Phase": {            # B 35 => #163
        "vital_target": "osc_phase",
        "scale": lambda x: x / 127  # 0..1
    },
    "Punch_Intensity": {           # B 36 => #164
        "vital_target": "env_1_attack_power",
        "scale": lambda x: x / 127
    },
    "undefined_165": None,         # B 37
    "undefined_166": None,         # B 38

    "Vocoder_Mode": None,          # B 39 => #167 (No Vital equivalent)

    "undefined_168": None,
    "undefined_169": None,
    "undefined_170": None,
    "undefined_171": None,
    "undefined_172": None,
    "undefined_173": None,
    "undefined_174": None,
    "undefined_175": None,
    "undefined_176": None,
    "undefined_177": None,
    "undefined_178": None,
    "undefined_179": None,
    "undefined_180": None,
    "undefined_181": None,
    "undefined_182": None,
    "undefined_183": None,
    "undefined_184": None,
    "undefined_185": None,
    "undefined_186": None,
    "undefined_187": None,
    "undefined_188": None,
    "undefined_189": None,
    "undefined_190": None,
    "undefined_191": None,

    "Osc1_Shape_Velocity": {
        "vital_target": "osc_1_warp_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "Osc2_Shape_Velocity": {
        "vital_target": "osc_2_warp_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "PulseWidth_Velocity": {
        "vital_target": "pulse_width_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "Fm_Amount_Velocity": {
        "vital_target": "fm_amount_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "undefined_196": None,
    "undefined_197": None,

    "Filter1_EnvAmt_Velocity": {
        "vital_target": "filter_1_env_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "Filter1_EnvAmt_Velocity_dup": None,  # Possibly a duplicate param

    "Resonance1_Velocity": {
        "vital_target": "filter_1_resonance_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "Resonance2_Velocity": {
        "vital_target": "filter_2_resonance_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "undefined_202": None,
    "undefined_203": None,

    "Amp_Velocity": {
        "vital_target": "amp_level_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "Panorama_Velocity": {
        "vital_target": "pan_velocity",
        "scale": lambda x: (x - 64) / 64
    },
    "undefined_206": None,
    "undefined_207": None,

    "Definable1_Single": None,
    "Definable2_Single": None,

    "Assign1_Source": None,
    "Assign1_Destination": None,
    "Assign1_Amount": {
        "vital_target": "mod_matrix_1_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign2_Source": None,
    "Assign2_Destination1": None,
    "Assign2_Amount1": {
        "vital_target": "mod_matrix_2_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign2_Destination2": None,
    "Assign2_Amount2": {
        "vital_target": "mod_matrix_3_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Source": None,
    "Assign3_Destination1": None,
    "Assign3_Amount1": {
        "vital_target": "mod_matrix_4_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Destination2": None,
    "Assign3_Amount2": {
        "vital_target": "mod_matrix_5_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Destination3": None,
    "Assign3_Amount3": {
        "vital_target": "mod_matrix_6_amount",
        "scale": lambda x: (x - 64) / 64
    },

    "undefined_225": None,
    "undefined_226": None,
    "undefined_227": None,
    "undefined_228": None,
    "undefined_229": None,
    "undefined_230": None,
    "undefined_231": None,
    "undefined_232": None,
    "undefined_233": None,
    "undefined_234": None,
    "undefined_235": None,
    "undefined_236": None,
    "undefined_237": None,
    "undefined_238": None,
    "undefined_239": None,

    "Single_Name_Char1": None,   # Characters for naming a single
    "Single_Name_Char2": None,
    "Single_Name_Char3": None,
    "Single_Name_Char4": None,
    "Single_Name_Char5": None,
    "Single_Name_Char6": None,
    "Single_Name_Char7": None,
    "Single_Name_Char8": None,
    "Single_Name_Char9": None,
    "Single_Name_Char10": None,

    "Filter_Select": {           # B122 => #250 (still on page B)
        "vital_target": "filter_routing",
        "scale": lambda x: x / 127
    },
    "undefined_251": None,
    "undefined_252": None,
    "undefined_253": None,
    "undefined_254": None,
    "undefined_255": None
}
