import json
import re

def extract_json_from_vital(file_path, output_json_path):
    """
    Extracts the JSON portion of a .vital preset file and saves it as a .json file.
    """
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        # Convert binary data to a string (ignoring non-UTF-8 characters)
        text_data = data.decode("utf-8", errors="ignore")

        # Find the JSON portion using regex (assuming it starts with `{` and ends with `}`)
        match = re.search(r"\{.*\}", text_data, re.DOTALL)

        if match:
            json_data = match.group(0)
            
            # Try to format it properly
            json_obj = json.loads(json_data)  # Ensure valid JSON
            with open(output_json_path, "w", encoding="utf-8") as json_file:
                json.dump(json_obj, json_file, indent=2)

            print(f"✅ Extracted JSON saved to: {output_json_path}")
        else:
            print("❌ No JSON data found in the file.")

    except Exception as e:
        print(f"❌ Error extracting JSON: {e}")


# Example usage
if __name__ == "__main__":
    vital_file = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/Default.vital"  # Change to your file path
    output_json = "extracted_preset.json"
    
    extract_json_from_vital(vital_file, output_json)
