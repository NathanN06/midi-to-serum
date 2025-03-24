# config.py
from typing import Dict, List, Optional, Any

# File and directory names/paths relative to the project root
DEFAULT_VITAL_PRESET_FILENAME = "Default.vital"
DEFAULT_SERUM_PRESET_FILENAME = "output.fxp"
MAPPING_CSV_FILENAME = "SerumParameterMapping.csv"

# Define relative directories (these are relative to the project root)
PRESETS_DIR = "Presets"
MAPPINGS_DIR = "mappings"
OUTPUT_DIR = "output"

# MIDI configuration constants
MIDI_PITCH_REFERENCE = 69  # Middle A (A4)

# Default ADSR envelope values for fallback cases
DEFAULT_ADSR = {
    "attack": 0.01,
    "decay": 0.1,
    "sustain": 0.8,
    "release": 0.3
}

# Default waveform type for wavetable generation
DEFAULT_WAVEFORM = "saw"

# Harmonic scaling for different waveform types
HARMONIC_SCALING = {
    "sine": 10,
    "saw": 10,
    "square": 10,
    "triangle": 10,
    "pulse": 1  # Pulse wave typically doesn't use harmonics
}

# Mapping of MIDI CC numbers to Vital parameters
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
    63: "mod_matrix_4",
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

# Constants for oscillator settings
DEFAULT_DETUNE_POWER: float = 1.5
DEFAULT_UNISON_BLEND: float = 0.8
DEFAULT_RANDOM_PHASE: float = 0.0  # 0.0 for static phase; 1.0 for full randomness
DEFAULT_STACK_STYLE: float = 0.0   # 0.0 = normal unison stacking mode
DEFAULT_STEREO_SPREAD: float = 0.8
DEFAULT_SPECTRAL_MORPH_AMOUNT: float = 0.5
MAX_UNISON_VOICES: int = 8


DEFAULT_KEYFRAMES: int = 3
DEFAULT_WAVE_DATA: str = (
    "ABAAugAYwLoAFCC7ABxguwASkLsAFrC7ABrQuwAe8LsAEQi8ABMYvAAVKLwAFzi8ABlIvAAbWLwAHWi8AB94vIAQhLyAEYy8gBKUvIATnLyAFKS8gBWsvIAWtLyAF7y8gBjEvIAZzLyAGtS8gBvcvIAc5LyAHey8gB70vIAf/LxAEAK9wBAGvUARCr3AEQ69QBISvcASFr1AExq9wBMevUAUIr3AFCa9QBUqvcAVLr1AFjK9wBY2vUAXOr3AFz69QBhCvcAYRr1AGUq9wBlOvUAaUr3AGla9QBtavcAbXr1AHGK9wBxmvUAdar3AHW69QB5yvcAedr1AH3q9wB9+vSAQgb1gEIO9oBCFveAQh70gEYm9YBGLvaARjb3gEY+9IBKRvWASk72gEpW94BKXvSATmb1gE5u9oBOdveATn70gFKG9YBSjvaAUpb3gFKe9IBWpvWAVq72gFa294BWvvSAWsb1gFrO9oBa1veAWt70gF7m9YBe7vaAXvb3gF7+9IBjBvWAYw72gGMW94BjHvSAZyb1gGcu9oBnNveAZz70gGtG9YBrTvaAa1b3gGte9IBvZvWAb272gG9294BvfvSAc4b1gHOO9oBzlveAc570gHem9YB3rvaAd7b3gHe+9IB7xvWAe872gHvW94B73vSAf+b1gH/u9oB/9veAf/70QkAC+MJABvlCQAr5wkAO+kJAEvrCQBb7QkAa+8JAHvhCRCL4wkQm+UJEKvnCRC76QkQy+sJENvtCRDr7wkQ++EJIQvjCSEb5QkhK+cJITvpCSFL6wkhW+0JIWvvCSF74Qkxi+MJMZvlCTGr5wkxu+kJMcvrCTHb7Qkx6+8JMfvhCUIL4wlCG+UJQivnCUI76QlCS+sJQlvtCUJr7wlCe+EJUovjCVKb5QlSq+cJUrvpCVLL6wlS2+0JUuvvCVL74QljC+MJYxvlCWMr5wljO+kJY0vrCWNb7Qlja+8JY3vhCXOL4wlzm+UJc6vnCXO76Qlzy+sJc9vtCXPr7wlz++EJhAvjCYQb5QmEK+cJhDvpCYRL6wmEW+0JhGvvCYR74QmUi+MJlJvlCZSr5wmUu+kJlMvrCZTb7QmU6+8JlPvhCaUL4wmlG+UJpSvnCaU76QmlS+sJpVvtCaVr7wmle+EJtYvjCbWb5Qm1q+cJtbvpCbXL6wm12+0JtevvCbX74"
)

# config.py additions for LFO settings
DEFAULT_LFO_POINTS: int = 16
LFO_RATE_MULTIPLIER: float = 4.0  # Scales CC value for LFO rate (1.0 to 5.0)
LFO_DEPTH_MIN: float = 0.2        # Minimum depth scaling for LFO
LFO_DEPTH_MULTIPLIER: float = 0.8  # Multiplier for LFO depth (to map CC11 from 0.2 to 1.0)
DEFAULT_LFO_TEMPO_OPTIONS: List[float] = [2.0, 4.0, 8.0]
DEFAULT_LFO_SYNC: float = 0.0     # Free running mode


# Envelope scaling constants
ENVELOPE_ATTACK_MULTIPLIER: float = 0.05
ENVELOPE_ATTACK_MAX: float = 0.2
ENVELOPE_DECAY_MULTIPLIER: float = 0.15
ENVELOPE_DECAY_MAX: float = 0.7
ENVELOPE_RELEASE_MULTIPLIER: float = 0.3
ENVELOPE_RELEASE_MAX: float = 1.5

# ENV2 scaling factors (relative to ENV1)
ENV2_ATTACK_SCALE: float = 0.7
ENV2_DECAY_SCALE: float = 0.8
ENV2_SUSTAIN_SCALE: float = 0.9
ENV2_RELEASE_SCALE: float = 1.2


# Envelope dynamic scaling constants
ENV_ATTACK_MIN: float = 0.3
ENV_ATTACK_MAX: float = 34.0
ENV_DECAY_MIN: float = 0.0
ENV_DECAY_MAX: float = 32.0
ENV_RELEASE_MIN: float = 0.0
ENV_RELEASE_MAX: float = 32.0
ENV_DELAY_MAX: float = 4.0
ENV_HOLD_MIN: float = 0.4
ENV_HOLD_MAX: float = 1.0


# config.py

# Default output filename for the generated Vital preset
DEFAULT_OUTPUT_FILENAME = "output.vital"

# Snapshot method options
SNAPSHOT_METHODS = {"1", "2", "3"}

# Error message for invalid snapshot method input
SNAPSHOT_ERROR_MESSAGE = "⚠️ Invalid input! Please enter 1, 2, or 3, or 'q' to quit."

# Default fallback values for MIDI statistics
DEFAULT_MIDI_STATS = {
    "avg_pitch": 60.0,     # Middle C4
    "avg_velocity": 0.7,   # Default normalized velocity
    "pitch_range": 0.0,    # No range if no notes exist
    "note_density": 1.0    # Assume at least one note per second
}

# Default frame settings
DEFAULT_FRAME_COUNT = 3   # Default to 3 frames if no notes exist
FRAME_SCALING_FACTOR = 10  # Scaling factor for estimating frame count

# Default frame size for wavetables
DEFAULT_FRAME_SIZE = 2048

# Default Sample Settings
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_SAMPLE_LENGTH = 44100
DEFAULT_SAMPLE_NAME = "Unknown Sample"

# Default Sample Settings
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_SAMPLE_LENGTH = 44100
DEFAULT_SAMPLE_NAME = "Unknown Sample"

# Filter Frequency Range for Scaling
MIN_FILTER_FREQ = 20.0
MAX_FILTER_FREQ = 20000.0

# Wavetable Generation Defaults
DEFAULT_NUM_WAVETABLE_FRAMES = 3
DEFAULT_FRAME_SIZE = 2048

# Default file extension for generated presets
PRESET_FILE_EXTENSION = ".vital"

# Default number of wavetable frames
DEFAULT_NUM_WAVETABLE_FRAMES = 3  

# Default frame size for wavetable generation
DEFAULT_FRAME_SIZE = 2048  

# Default mod index and frequency range for FM synthesis
FM_MOD_INDEX = 0.7
FM_MOD_FREQ_BASE = 3.0  
FM_MOD_FREQ_RANGE = 5.0  

# Default pitch reference
DEFAULT_PITCH_REFERENCE = 69  # Middle A (A4)

# Harmonic limits for synthesis
DEFAULT_MIN_HARMONICS = 1  
DEFAULT_MAX_HARMONICS = 15  

# Default waveform type for wavetable generation
DEFAULT_WAVEFORM_TYPE = "saw"

# Phase distortion factor
DEFAULT_PHASE_DISTORTION = 3.5  
DEFAULT_PHASE_DISTORTION_AMOUNT = 0.4  

# Scaling factors for waveform blending
TRIANGLE_BLEND_RATIO = 0.6  
SAW_BLEND_RATIO = 0.4  

EFFECTS_THRESHOLD = 0.1  # Minimum CC value to enable an effect

DEFAULT_OSC_1_TRANSPOSE = 0
DEFAULT_OSC_1_LEVEL = 0.5

WAVETABLE_NAME_REPLACEMENTS = ["Attack Phase", "Harmonic Blend", "Final Release"]

# Default CC thresholds for enabling effects
EFFECT_ENABLE_THRESHOLD = 0.1

# MIDI CC mappings for Vital effects
EFFECTS_CC_MAP = {
    "reverb": 91,
    "chorus": 93,
    "delay": 94,
    "phaser": 95,
    "distortion": 116,
    "compressor": 117,
    "flanger": 119
}

# Effect parameters that should be controlled by CC
EFFECTS_PARAM_MAP = {
    # Reverb
    "reverb": {
        "dry_wet": "reverb_dry_wet",
        "size": "reverb_size",
        "damp": "reverb_damp",
        "width": "reverb_width"
    },

    # Delay
    "delay": {
        "dry_wet": "delay_dry_wet",
        "feedback": "delay_feedback",
        "tempo": "delay_tempo",
        "cutoff": "delay_filter_cutoff"
    },

    # Chorus
    "chorus": {
        "dry_wet": "chorus_dry_wet",
        "feedback": "chorus_feedback",
        "rate": "chorus_rate"
    },

    # Phaser
    "phaser": {
        "dry_wet": "phaser_dry_wet",
        "feedback": "phaser_feedback",
        "rate": "phaser_rate"
    },

    # Distortion
    "distortion": {
        "drive": "distortion_drive",
        "mix": "distortion_mix",
        "type": "distortion_type"
    },

    # Compressor
    "compressor": {
        "amount": "compressor_amount"
    },

    # Flanger
    "flanger": {
        "dry_wet": "flanger_dry_wet",
        "feedback": "flanger_feedback"
    }
}


# Filter Frequency Range for Scaling
MIN_FILTER_FREQ = 20.0
MAX_FILTER_FREQ = 20000.0

# Threshold to enable an effect
EFFECT_ENABLE_THRESHOLD = 0.01  

# MIDI CC Assignments for Filters
FILTER_1_CUTOFF_CC = {74, 102}
FILTER_1_RESONANCE_CC = {71}
FILTER_1_CC_NUMBERS = FILTER_1_CUTOFF_CC | FILTER_1_RESONANCE_CC  # Combine

FILTER_2_CUTOFF_CC = {85, 103}
FILTER_2_RESONANCE_CC = {86, 104}
FILTER_2_CC_NUMBERS = FILTER_2_CUTOFF_CC | FILTER_2_RESONANCE_CC  # Combine

# Default stack mode if no MIDI data is available
DEFAULT_STACK_MODE = "Unison"

# Mapping MIDI intervals to stack settings
STACK_MODE_RULES = {
    "single_note": "Unison",
    "octave": "Octave",
    "double_octave": "2x Octave",
    "power_chord": "Power Chord",
    "double_power_chord": "2x Power Chord",
    "major_chord": "Major Chord",
    "minor_chord": "Minor Chord",
    "wide_interval_12": "Center Drop 12",
    "wide_interval_24": "Center Drop 24",
    "harmonics": "Harmonics",
    "odd_harmonics": "Odd Harmonics"
}


# Additional CC mappings for Filter 1
FILTER_1_DRIVE_CC = {73}           # Example: CC73 maps to drive
FILTER_1_KEYTRACK_CC = {75}        # Example: CC75 maps to keytrack
FILTER_1_MIX_CC = {76}             # Example: CC76 maps to mix

# Additional CC mappings for Filter 2
FILTER_2_DRIVE_CC = {87}
FILTER_2_KEYTRACK_CC = {88}
FILTER_2_MIX_CC = {89}

# Updated CC groups for detection
FILTER_1_CC_NUMBERS = FILTER_1_CUTOFF_CC | FILTER_1_RESONANCE_CC | FILTER_1_DRIVE_CC | FILTER_1_KEYTRACK_CC | FILTER_1_MIX_CC
FILTER_2_CC_NUMBERS = FILTER_2_CUTOFF_CC | FILTER_2_RESONANCE_CC | FILTER_2_DRIVE_CC | FILTER_2_KEYTRACK_CC | FILTER_2_MIX_CC


DEFAULT_FILTER_DRIVE = 0.5
DEFAULT_FILTER_KEYTRACK = 0.5
DEFAULT_FILTER_MIX = 1.0
