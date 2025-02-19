import pandas as pd

# Define the mapped and not mapped parameters (corrected lengths)
data = {
    "Category": [
        "Oscillators", "Oscillators", "Oscillators", "Oscillators", 
        "Oscillators", "Oscillators", "Filters", "Filters", 
        "Filters", "Envelopes", "Envelopes", "Envelopes", 
        "Envelopes", "LFOs", "LFOs", "Effects", "Effects", 
        "Global", "Global", "Global"
    ],
    "Parameter": [
        "A Vol", "B Vol", "A Semi", "B Semi", 
        "A WTPos", "B WTPos", "Fil Cutoff", "Fil Reso", 
        "Fil Driv", "Env1 Atk", "Env1 Dec", "Env1 Sus", 
        "Env1 Rel", "LFO1Rate", "LFO1 Depth", "Reverb Wet", 
        "Delay Wet", "MasterVol", "PortTime", "Pitch Bend"
    ],
    "Mapped": [
        "Yes", "Yes", "Yes", "Yes", 
        "No", "No", "No", "No", 
        "Yes", "No", "Yes", "No", 
        "No", "Yes", "No", "Yes", 
        "Yes", "No", "Yes", "Yes" 
    ]
}

# Ensure all arrays in the dictionary are of the same length
assert len(data["Category"]) == len(data["Parameter"]) == len(data["Mapped"]), "Array lengths do not match!"

# Create a DataFrame
mapping_table = pd.DataFrame(data)

# Save the table as a CSV file
output_path = 'Parameter_Mapping_Status.csv'
mapping_table.to_csv(output_path, index=False)
print(f"Mapping table saved as {output_path}")