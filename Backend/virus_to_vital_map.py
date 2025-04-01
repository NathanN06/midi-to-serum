virus_to_vital_map = {
    "Bank_Select": None,
    "Modulation_Wheel": {
        "vital_target": "macro_1",
        "scale": lambda x: x / 127
    },
    "Breath_Controller": None,
    "Contr_3": None,
    "Foot_Controller": None,
    "Portamento_Time": {
        "vital_target": "portamento",
        "scale": lambda x: x / 127
    },
    "Data_Slider": None,
    "Channel_Volume": {
        "vital_target": "amp_level",
        "scale": lambda x: x / 127
    },
    "Balance": {
        "vital_target": "osc_mix",
        "scale": lambda x: (x - 64) / 64  # -1 to +1
    },
    "Contr_9": None,
    "Panorama": {
        "vital_target": "pan",
        "scale": lambda x: (x - 64) / 64  # -1 to +1
    },
    "Expression": {
        "vital_target": "macro_2",
        "scale": lambda x: x / 127
    },
    "Contr_12": None,
    "Contr_13": None,
    "Contr_14": None,
    "Contr_15": None,
    "Contr_16": None,
    "Osc1_Shape": {
        "vital_target": "osc_1_wave_frame",
        "scale": lambda x: x / 127  # Shape morph position
    },
    "Osc1_Pulsewidth": {
        "vital_target": "osc_1_pulse_width",
        "scale": lambda x: x / 127
    },
    "Osc1_Wave_Select": {
        "vital_target": "osc_1_wave_frame",
        "scale": lambda x: x / 64  # Wave selection normalized
    },
    "Osc1_Semitone": {
        "vital_target": "osc_1_transpose",
        "scale": lambda x: x - 64  # Semitone transpose
    },
    "Osc1_Keyfollow": {
        "vital_target": "osc_1_pitch_tracking",
        "scale": lambda x: x / 127  # Key tracking from 0% to 100%
    },
    "Osc2_Shape": {
        "vital_target": "osc_2_wave_frame",
        "scale": lambda x: x / 127  # Shape morph position
    },
    "Osc2_Pulsewidth": {
        "vital_target": "osc_2_pulse_width",
        "scale": lambda x: x / 127
    },
    "Osc2_Wave_Select": {
        "vital_target": "osc_2_wave_frame",
        "scale": lambda x: x / 64  # Wave selection normalized
    },
    "Osc2_Semitone": {
        "vital_target": "osc_2_transpose",
        "scale": lambda x: x - 64  # Semitone transpose
    },
    "Osc2_Detune": {
        "vital_target": "osc_2_detune",
        "scale": lambda x: (x - 64) / 64  # Detune from -1 to +1
    },
    "Osc2_FM_Amount": {
        "vital_target": "osc_2_fm_amount",
        "scale": lambda x: x / 127
    },
    "Osc2_Sync": {
        "vital_target": "osc_2_sync",
        "scale": lambda x: 1 if x > 0 else 0
    },
    "Osc2_Filt_Env_Amt": {
        "vital_target": "filter_1_env_amount",
        "scale": lambda x: (x - 64) / 64  # -1 to +1 envelope modulation
    },
    "FM_Filt_Env_Amt": {
        "vital_target": "filter_1_fm_env_amount",
        "scale": lambda x: (x - 64) / 64  # -1 to +1 modulation
    },
    "Osc2_Keyfollow": {
        "vital_target": "osc_2_pitch_tracking",
        "scale": lambda x: x / 127  # 0% to 100% tracking
    },
    "Bank_Select_Alt": None,
    "Osc_Balance": {
        "vital_target": "osc_mix",
        "scale": lambda x: (x - 64) / 64  # -1 (Osc1) to +1 (Osc2)
    },
    "Suboscillator_Volume": {
        "vital_target": "osc_3_level",
        "scale": lambda x: x / 127  # 0 (off) to 1 (max volume)
    },
    "Suboscillator_Shape": {
        "vital_target": "osc_3_wave_frame",
        "scale": lambda x: 0 if x == 0 else 1  # 0: square, 1: triangle
    },
    "Osc_Mainvolume": {
        "vital_target": "osc_global_volume",
        "scale": lambda x: x / 127  # 0 to 1
    },
    "Noise_Volume": {
        "vital_target": "noise_level",
        "scale": lambda x: x / 127
    },
    "Ringmodulator_Volume": {
        "vital_target": "ring_mod_level",
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
        "vital_target": "filter_1_env_amount",
        "scale": lambda x: (x - 64) / 64  # Envelope modulation -1 to +1
    },
    "Filter2_Env_Amt": {
        "vital_target": "filter_2_env_amount",
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
        "vital_target": "filter_mix",
        "scale": lambda x: (x - 64) / 64  # -1 (Filter1) to +1 (Filter2)
    },
    "Saturation_Curve": {
        "vital_target": "distortion_type",
        "scale": lambda x: min(x, 6)  # 0-6 maps to Vital distortion types
    },
    "Filter1_Mode": {
        "vital_target": "filter_1_type",
        "scale": lambda x: min(x, 3)  # 0:LP, 1:HP, 2:BP, 3:Notch
    },
    "Filter2_Mode": {
        "vital_target": "filter_2_type",
        "scale": lambda x: min(x, 3)
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
        "vital_target": "portamento",
        "scale": lambda x: 1 if x > 0 else 0  # Pedal on/off
    },
    "Sostenuto_Pedal": None,  # Not directly supported in Vital
    "Lfo1_Rate": {
        "vital_target": "lfo_1_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo1_Shape": {
        "vital_target": "lfo_1_waveform",
        "scale": lambda x: min(x, 5)  # Map Virus shapes to Vital waveforms (0-5)
    },
    "Lfo1_Env_Mode": {
        "vital_target": "lfo_1_env_mode",
        "scale": lambda x: 1 if x > 0 else 0  # Off/On (Envelope mode)
    },
    "Lfo1_Mode": {
        "vital_target": "lfo_1_mode",
        "scale": lambda x: 1 if x > 0 else 0  # 0: Poly, 1: Mono
    },
    "Lfo1_Symmetry": {
        "vital_target": "lfo_1_smooth",
        "scale": lambda x: (x - 64) / 64  # -1 to +1 symmetry/smoothing
    },
    "Lfo1_Keyfollow": {
        "vital_target": "lfo_1_keytrack",
        "scale": lambda x: x / 127  # 0 to 100%
    },
    "Lfo1_Keytrigger": {
        "vital_target": "lfo_1_key_trigger",
        "scale": lambda x: 1 if x > 0 else 0  # Off/On
    },
    "Osc1_Lfo1_Amount": {
        "vital_target": "osc_1_pitch_lfo_1_mod",
        "scale": lambda x: (x - 64) / 64  # Pitch mod amount
    },
    "Osc2_Lfo1_Amount": {
        "vital_target": "osc_2_pitch_lfo_1_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "PW_Lfo1_Amount": {
        "vital_target": "osc_pw_lfo_1_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "Reso_Lfo1_Amount": {
        "vital_target": "filter_resonance_lfo_1_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "FiltGain_Lfo1_Amount": {
        "vital_target": "filter_drive_lfo_1_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "Lfo2_Rate": {
        "vital_target": "lfo_2_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo2_Shape": {
        "vital_target": "lfo_2_waveform",
        "scale": lambda x: min(x, 5)  # Map to Vital shapes (0-5)
    },
    "Lfo2_Env_Mode": {
        "vital_target": "lfo_2_env_mode",
        "scale": lambda x: 1 if x > 0 else 0
    },
    "Lfo2_Mode": {
        "vital_target": "lfo_2_mode",
        "scale": lambda x: 1 if x > 0 else 0  # Poly (0) / Mono (1)
    },
    "Lfo2_Symmetry": {
        "vital_target": "lfo_2_smooth",
        "scale": lambda x: (x - 64) / 64
    },
    "Lfo2_Keyfollow": {
        "vital_target": "lfo_2_keytrack",
        "scale": lambda x: x / 127
    },
    "Lfo2_Keytrigger": {
        "vital_target": "lfo_2_key_trigger",
        "scale": lambda x: 1 if x > 0 else 0
    },
    "OscShape_Lfo2_Amount": {
        "vital_target": "osc_wave_frame_lfo_2_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "FmAmount_Lfo2_Amount": {
        "vital_target": "osc_fm_lfo_2_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "Cutoff1_Lfo2_Amount": {
        "vital_target": "filter_1_cutoff_lfo_2_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "Cutoff2_Lfo2_Amount": {
        "vital_target": "filter_2_cutoff_lfo_2_mod",
        "scale": lambda x: (x - 64) / 64
    },
    "Panorama_Lfo2_Amount": {
        "vital_target": "pan_lfo_2_mod",
        "scale": lambda x: (x - 64) / 64  # -1 (left) to +1 (right)
    },
    "Patch_Volume": {
        "vital_target": "master_volume",
        "scale": lambda x: x / 127
    },
    "undefined_92": None,
    "Transpose": {
        "vital_target": "global_transpose",
        "scale": lambda x: x - 64  # -64 to +63 semitones
    },
    "Key_Mode": {
        "vital_target": "voice_mode",
        "scale": lambda x: min(x, 4)  # 0: Poly, 1–4: Mono modes (limit to available modes)
    },
    "undefined_95": None,
    "undefined_96": None,
    "Unison_Mode": {
        "vital_target": "unison_voices",
        "scale": lambda x: 2 if x > 0 else 1  # 1 voice (off) or 2 voices (on)
    },
    "Unison_Detune": {
        "vital_target": "unison_detune",
        "scale": lambda x: x / 127  # 0 to 1 amount of detune
    },
    "Unison_Panorama_Spread": {
        "vital_target": "unison_spread",
        "scale": lambda x: x / 127  # stereo width 0 to 1
    },
    "Unison_Lfo_Phase": {
        "vital_target": "unison_phase",
        "scale": lambda x: (x - 64) / 64  # phase spread from -1 to +1
    },
    "Input_Mode": None,  # Not applicable, Virus audio input routing
    "Input_Select": None,  # Not applicable in Vital
    "undefined_103": None,
    "undefined_104": None,
    "Chorus_Mix": {
        "vital_target": "chorus_mix",
        "scale": lambda x: x / 127
    },
    "Chorus_Rate": {
        "vital_target": "chorus_frequency",
        "scale": lambda x: x / 127
    },
    "Chorus_Depth": {
        "vital_target": "chorus_depth",
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
        "vital_target": "chorus_lfo_type",
        "scale": lambda x: min(x, 5)  # Limit to valid Vital shapes (0-5)
    },
    "undefined_111": None,
    "undefined_112": None,
    "Effect_Send": {
        "vital_target": "delay_mix",
        "scale": lambda x: x / 127
    },
    "Delay_Time": {
        "vital_target": "delay_time",
        "scale": lambda x: x / 127
    },
    "Delay_Feedback": {
        "vital_target": "delay_feedback",
        "scale": lambda x: x / 127
    },
    "Delay_Rate": {
        "vital_target": "delay_frequency",
        "scale": lambda x: x / 127
    },
    "Delay_Depth": {
        "vital_target": "delay_stereo_offset",
        "scale": lambda x: x / 127
    },
    "Delay_Lfo_Shape": {
        "vital_target": "delay_lfo_type",
        "scale": lambda x: min(x, 5)  # Limit to Vital waveform shapes
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
        "vital_target": "arpeggiator_mode",
        "scale": lambda x: min(x, 6)  # 0:Off, 1:Up, 2:Down, etc.
    },
    "undefined_130": None,
    "Arp_Octave_Range": {
        "vital_target": "arpeggiator_octaves",
        "scale": lambda x: min(x, 3)  # 0–3 octaves
    },
    "Arp_Hold_Enable": {
        "vital_target": "arpeggiator_hold",
        "scale": lambda x: 1 if x > 0 else 0
    },
    "undefined_133": None,
    "undefined_134": None,
    "Lfo3_Rate": {
        "vital_target": "lfo_3_frequency",
        "scale": lambda x: x / 127
    },
    "Lfo3_Shape": {
        "vital_target": "lfo_3_waveform",
        "scale": lambda x: min(x, 5)  # Virus waveforms: 0–5, Vital matches similarly
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
    "undefined_150": None,
    "undefined_151": None,
    "undefined_152": None,
    "undefined_153": None,
    "undefined_154": None,
    "undefined_155": None,
    "undefined_156": None,
    "undefined_157": None,
    "undefined_158": None,
    "undefined_159": None,
    "Control_Smooth_Mode": None,  # No direct Vital equivalent
    "Bender_Range_Up": {
        "vital_target": "pitch_wheel_range_up",
        "scale": lambda x: x - 64  # Range -64 to +63 semitones
    },
    "Bender_Range_Down": {
        "vital_target": "pitch_wheel_range_down",
        "scale": lambda x: x - 64  # Range -64 to +63 semitones
    },
    "Bender_Scale": None,  # No direct equivalent in Vital
    "undefined_164": None,
    "undefined_165": None,
    "Filter1_Env_Polarity": {
        "vital_target": "filter_1_env_polarity",
        "scale": lambda x: 1 if x > 0 else -1  # Positive or negative envelope modulation
    },
    "Filter2_Env_Polarity": {
        "vital_target": "filter_2_env_polarity",
        "scale": lambda x: 1 if x > 0 else -1
    },
    "Filter2_Cutoff_Link": None,  # Vital doesn't link filter cutoffs directly
    "Filter_Keytrack_Base": {
        "vital_target": "filter_keytrack_base",
        "scale": lambda x: (x / 127) * 120 - 60  # Assuming mapping to -60 to +60 MIDI notes
    },
    "Osc_Init_Phase": {
        "vital_target": "osc_phase",
        "scale": lambda x: x / 127  # Normalized phase 0–1
    },
    "Punch_Intensity": {
        "vital_target": "env_1_attack_power",
        "scale": lambda x: x / 127  # Map punch intensity to envelope punchiness
    },
    "undefined_172": None,
    "undefined_173": None,
    "undefined_174": None,
    "undefined_175": None,
    "Vocoder_Mode": None,  # Vital has no direct vocoder equivalent
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
        "scale": lambda x: (x - 64) / 64  # Velocity modulation from -1 to +1
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
    "Filter1_EnvAmt_Velocity_dup": None,  # Duplicate or undefined parameter
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
    "Definable1_Single": None,  # Flexible modulation source, define later
    "Definable2_Single": None,  # Flexible modulation source, define later
    "Assign1_Source": None,  # Flexible modulation source (assign manually)
    "Assign1_Destination": None,  # Flexible modulation destination (assign manually)
    "Assign1_Amount": {
        "vital_target": "mod_matrix_1_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign2_Source": None,  # Flexible modulation source (assign manually)
    "Assign2_Destination1": None,  # Flexible modulation destination (assign manually)
    "Assign2_Amount1": {
        "vital_target": "mod_matrix_2_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign2_Destination2": None,  # Second destination, manually assigned
    "Assign2_Amount2": {
        "vital_target": "mod_matrix_3_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Source": None,  # Flexible modulation source (assign manually)
    "Assign3_Destination1": None,  # Destination 1, manually assigned
    "Assign3_Amount1": {
        "vital_target": "mod_matrix_4_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Destination2": None,  # Destination 2, manually assigned
    "Assign3_Amount2": {
        "vital_target": "mod_matrix_5_amount",
        "scale": lambda x: (x - 64) / 64
    },
    "Assign3_Destination3": None,  # Destination 3, manually assigned
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
    "Single_Name_Char1": None,  # Preset name character; not relevant for Vital parameters
    "Single_Name_Char2": None,
    "Single_Name_Char3": None,
    "Single_Name_Char4": None,
    "Single_Name_Char5": None,
    "Single_Name_Char6": None,
    "Single_Name_Char7": None,
    "Single_Name_Char8": None,
    "Single_Name_Char9": None,
    "Single_Name_Char10": None,
    "Filter_Select": {
        "vital_target": "filter_routing", 
        "scale": lambda x: x / 127  # Assuming continuous filter selection
    },
    "undefined_251": None,
    "undefined_252": None,
    "undefined_253": None,
    "undefined_254": None,
    "undefined_255": None,
}