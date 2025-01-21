import pandas as pd

# Define the mapping table for the 20 Serum parameters
data = {
    "Category": [
        "Oscillators", "Oscillators", "Oscillators", "Oscillators", 
        "Oscillators", "Oscillators", "Filters", "Filters", 
        "Filters", "Envelopes", "Envelopes", "Envelopes", "Envelopes", 
        "LFOs", "LFOs", "Effects", "Effects", "Global", "Global", "Global"
    ],
    "Parameter": [
        "A Vol", "B Vol", "A Semi", "B Semi", 
        "A WTPos", "B WTPos", "Fil Cutoff", "Fil Reso", 
        "Fil Driv", "Env1 Atk", "Env1 Dec", "Env1 Sus", "Env1 Rel", 
        "LFO1Rate", "LFO1 Depth", "Reverb Wet", "Delay Wet", 
        "MasterVol", "PortTime", "Pitch Bend"
    ],
    "MIDI Input": [
        "MIDI Velocity", "MIDI Velocity", "MIDI Note Pitch", "MIDI Note Pitch", 
        "MIDI CC 74 (Brightness)", "MIDI CC 74 (Brightness)", "MIDI CC 74 (Brightness)", 
        "MIDI CC 71 (Resonance)", "MIDI Velocity", "MIDI CC 64 (Sustain Pedal)", 
        "MIDI Velocity", "MIDI CC 64 (Sustain Pedal)", "MIDI CC 1 (Mod Wheel)", 
        "MIDI Tempo", "MIDI CC 1 (Mod Wheel)", "MIDI CC 91 (Reverb Send)", 
        "MIDI CC 93 (Delay Send)", "MIDI CC 7 (Volume)", "MIDI CC 5 (Portamento Time)", 
        "MIDI Pitch Bend"
    ],
    "Notes": [
        "Oscillator A volume", "Oscillator B volume", "Oscillator A semitone tuning", 
        "Oscillator B semitone tuning", "Wavetable position for A", "Wavetable position for B", 
        "Filter cutoff frequency", "Filter resonance", "Filter drive based on velocity", 
        "Envelope 1 attack time", "Envelope 1 decay time", "Envelope 1 sustain level", 
        "Envelope 1 release time", "LFO 1 rate synced to tempo", "LFO 1 modulation depth", 
        "Reverb mix level", "Delay mix level", "Master volume control", 
        "Glide time between notes", "Pitch modulation for all oscillators"
    ]
}

# Create a DataFrame
mapping_table = pd.DataFrame(data)

# Save the table as a CSV file
output_path = 'SerumParameterMapping.csv'
mapping_table.to_csv(output_path, index=False)
print(f"Mapping table saved as {output_path}")
