import json

# Load the extracted preset JSON file
file_path = "/Users/nathannguyen/Documents/Midi_To_serum/MultiOrgan.vital"  # Replace with your actual file path

with open(file_path, "r") as f:
    preset_data = json.load(f)

# Extract all unique parameter names
parameters = list(preset_data.keys())

# If the preset contains nested parameters, extract them as well
for key, value in preset_data.items():
    if isinstance(value, dict):  # If it's a dictionary, get its keys too
        nested_keys = [f"{key}.{sub_key}" for sub_key in value.keys()]
        parameters.extend(nested_keys)

# Remove duplicates (if any)
parameters = sorted(set(parameters))

# Save to a text file
output_file = "vital_parameters.txt"
with open(output_file, "w") as f:
    for param in parameters:
        f.write(param + "\n")

# Print the total count of parameters and first few as a sample
print(f"✅ Extracted {len(parameters)} parameters. First 10:")
print("\n".join(parameters[:10]))
