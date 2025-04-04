virus_sysex_param_map = {
    0: "Bank_Select",
    1: "Modulation_Wheel",
    2: "Breath_Controller",
    3: "Contr_3",
    4: "Foot_Controller",
    5: "Portamento_Time",
    6: "Data_Slider",
    7: "Channel_Volume",
    8: "Balance",
    9: "Contr_9",
    10: "Panorama",
    11: "Expression",
    12: "Contr_12",
    13: "Contr_13",
    14: "Contr_14",
    15: "Contr_15",
    16: "Contr_16",
    17: "Osc1_Shape",
    18: "Osc1_Pulsewidth",
    19: "Osc1_Wave_Select",
    20: "Osc1_Semitone",
    21: "Osc1_Keyfollow",
    22: "Osc2_Shape",
    23: "Osc2_Pulsewidth",
    24: "Osc2_Wave_Select",
    25: "Osc2_Semitone",
    26: "Osc2_Detune",
    27: "Osc2_FM_Amount",
    28: "Osc2_Sync",
    29: "Osc2_Filt_Env_Amt",
    30: "FM_Filt_Env_Amt",
    31: "Osc2_Keyfollow",
    32: "Bank_Select_Alt",
    33: "Osc_Balance",
    34: "Suboscillator_Volume",
    35: "Suboscillator_Shape",
    36: "Osc_Mainvolume",
    37: "Noise_Volume",
    38: "Ringmodulator_Volume",
    39: "Reserved_Unknown",
    40: "Cutoff",
    41: "Cutoff2",
    42: "Filter1_Resonance",
    43: "Filter2_Resonance",
    44: "Filter1_Env_Amt",
    45: "Filter2_Env_Amt",
    46: "Filter1_Keyfollow",
    47: "Filter2_Keyfollow",
    48: "Filter_Balance",
    49: "Saturation_Curve",
    50: "Reserved_Unknown",
    51: "Filter1_Mode",
    52: "Filter2_Mode",
    53: "Filter_Routing",
    54: "Filter_Env_Attack",
    55: "Filter_Env_Decay",
    56: "Filter_Env_Sustain",
    57: "Filter_Env_Sustain_Time",
    58: "Filter_Env_Release",
    59: "Amp_Env_Attack",
    60: "Amp_Env_Decay",
    61: "Amp_Env_Sustain",
    62: "Amp_Env_Sustain_Time",
    63: "Amp_Env_Release",
    64: "Hold_Pedal",
    65: "Portamento_Pedal",
    66: "Sostenuto_Pedal",
    67: "Lfo1_Rate",
    68: "Lfo1_Shape",
    69: "Lfo1_Env_Mode",
    70: "Lfo1_Mode",
    71: "Lfo1_Symmetry",
    72: "Lfo1_Keyfollow",
    73: "Lfo1_Keytrigger",
    74: "Osc1_Lfo1_Amount",
    75: "Osc2_Lfo1_Amount",
    76: "PW_Lfo1_Amount",
    77: "Reso_Lfo1_Amount",
    78: "FiltGain_Lfo1_Amount",
    79: "Lfo2_Rate",
    80: "Lfo2_Shape",
    81: "Lfo2_Env_Mode",
    82: "Lfo2_Mode",
    83: "Lfo2_Symmetry",
    84: "Lfo2_Keyfollow",
    85: "Lfo2_Keytrigger",
    86: "OscShape_Lfo2_Amount",
    87: "FmAmount_Lfo2_Amount",
    88: "Cutoff1_Lfo2_Amount",
    89: "Cutoff2_Lfo2_Amount",
    90: "Panorama_Lfo2_Amount",
    91: "Patch_Volume",
    92: "undefined_92",
    93: "Transpose",
    94: "Key_Mode",
    95: "undefined_95",
    96: "undefined_96",
    97: "Unison_Mode",
    98: "Unison_Detune",
    99: "Unison_Panorama_Spread",
    100: "Unison_Lfo_Phase",
    101: "Input_Mode",
    102: "Input_Select",
    103: "undefined_103",
    104: "undefined_104",
    105: "Chorus_Mix",
    106: "Chorus_Rate",
    107: "Chorus_Depth",
    108: "Chorus_Delay",
    109: "Chorus_Feedback",
    110: "Chorus_Lfo_Shape",
    111: "undefined_111",
    112: "undefined_112",
    113: "Effect_Send",
    114: "Delay_Time",
    115: "Delay_Feedback",
    116: "Delay_Rate",
    117: "Delay_Depth",
    118: "Delay_Lfo_Shape",
    119: "undefined_119",
    120: "undefined_120",
    121: "undefined_121",
    122: "undefined_122",
    123: "All_Notes_Off",
    124: "undefined_124",
    125: "undefined_125",
    126: "undefined_126",
    127: "undefined_127",
    128: "undefined_128",
    129: "Arp_Mode",
    130: "undefined_130",
    131: "Arp_Octave_Range",
    132: "Arp_Hold_Enable",
    133: "undefined_133",
    134: "undefined_134",
    135: "Lfo3_Rate",
    136: "Lfo3_Shape",
    137: "Lfo3_Mode",
    138: "Lfo3_Keyfollow",
    139: "Lfo3_Destination",
    140: "Osc_Lfo3_Amount",
    141: "Lfo3_Fade-In_Time",
    142: "undefined_142",
    143: "undefined_143",
    144: "Clock_Tempo",
    145: "Arp_Clock",
    146: "Lfo1_Clock",
    147: "Lfo2_Clock",
    148: "Delay_Clock",
    149: "Lfo3_Clock",
    150: "undefined_150",
    151: "undefined_151",
    152: "undefined_152",
    153: "Control_Smooth_Mode",     # B 25
    154: "Bender_Range_Up",         # B 26
    155: "Bender_Range_Down",       # B 27
    156: "Bender_Scale",            # B 28
    157: "undefined_157",           # (B 29 not documented)
    158: "Filter1_Env_Polarity",    # B 30
    159: "Filter2_Env_Polarity",    # B 31
    160: "Filter2_Cutoff_Link",     # B 32
    161: "Filter_Keytrack_Base",    # B 33
    162: "undefined_162",           # (B 34 not documented)
    163: "Osc_Init_Phase",          # B 35
    164: "Punch_Intensity",         # B 36
    165: "undefined_165",           # (B 37)
    166: "undefined_166",           # (B 38)
    167: "Vocoder_Mode",            # B 39
    168: "undefined_168",
    169: "undefined_169",
    170: "undefined_170",
    171: "undefined_171",
    172: "undefined_172",
    173: "undefined_173",
    174: "undefined_174",
    175: "undefined_175",
    176: "undefined_176",
    177: "undefined_177",
    178: "undefined_178",
    179: "undefined_179",
    180: "undefined_180",
    181: "undefined_181",
    182: "undefined_182",
    183: "undefined_183",
    184: "undefined_184",
    185: "undefined_185",
    186: "undefined_186",
    187: "undefined_187",
    188: "undefined_188",
    189: "undefined_189",
    190: "undefined_190",
    191: "undefined_191",
    192: "Osc1_Shape_Velocity",
    193: "Osc2_Shape_Velocity",
    194: "PulseWidth_Velocity",
    195: "Fm_Amount_Velocity",
    196: "undefined_196",
    197: "undefined_197",
    198: "Filter1_EnvAmt_Velocity",
    199: "Filter1_EnvAmt_Velocity_dup",
    200: "Resonance1_Velocity",
    201: "Resonance2_Velocity",
    202: "undefined_202",
    203: "undefined_203",
    204: "Amp_Velocity",
    205: "Panorama_Velocity",
    206: "undefined_206",
    207: "undefined_207",
    208: "Definable1_Single",
    209: "Definable2_Single",
    210: "Assign1_Source",
    211: "Assign1_Destination",
    212: "Assign1_Amount",
    213: "Assign2_Source",
    214: "Assign2_Destination1",
    215: "Assign2_Amount1",
    216: "Assign2_Destination2",
    217: "Assign2_Amount2",
    218: "Assign3_Source",
    219: "Assign3_Destination1",
    220: "Assign3_Amount1",
    221: "Assign3_Destination2",
    222: "Assign3_Amount2",
    223: "Assign3_Destination3",
    224: "Assign3_Amount3",
    225: "undefined_225",
    226: "undefined_226",
    227: "undefined_227",
    228: "undefined_228",
    229: "undefined_229",
    230: "undefined_230",
    231: "undefined_231",
    232: "undefined_232",
    233: "undefined_233",
    234: "undefined_234",
    235: "undefined_235",
    236: "undefined_236",
    237: "undefined_237",
    238: "undefined_238",
    239: "undefined_239",
    240: "Single_Name_Char1",
    241: "Single_Name_Char2",
    242: "Single_Name_Char3",
    243: "Single_Name_Char4",
    244: "Single_Name_Char5",
    245: "Single_Name_Char6",
    246: "Single_Name_Char7",
    247: "Single_Name_Char8",
    248: "Single_Name_Char9",
    249: "Single_Name_Char10",
    250: "Filter_Select",
    251: "undefined_251",
    252: "undefined_252",
    253: "undefined_253",
    254: "undefined_254",
    255: "undefined_255"
}
