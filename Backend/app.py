import os
from sysex_parser import extract_sysex_from_midi
from virus_to_vital_converter import load_sysex_txt_files, save_vital_patches

# --- CONFIGURABLE PATHS ---
TEMP_SYSEX_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Temp_sysex_holders"
VITAL_OUTPUT_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Backend/output"
DEFAULT_VITAL_PATCH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/Default.vital"

def main():
    print("🎛️  Virus C SysEx to Vital Preset Converter")
    midi_path = input("🔍 Enter path to your Virus MIDI file: ").strip()

    if not os.path.exists(midi_path):
        print("❌ MIDI file not found. Please check the path.")
        return

    print("\n🔄 Extracting SysEx patches...")
    sysex_files = extract_sysex_from_midi(midi_path, TEMP_SYSEX_FOLDER)

    if not sysex_files:
        print("⚠️ No valid Virus patches found in this MIDI file.")
        return

    print("\n🔁 Converting patches to Vital format...")
    patches = load_sysex_txt_files(TEMP_SYSEX_FOLDER, DEFAULT_VITAL_PATCH)

    print("\n💾 Saving Vital patches...")
    save_vital_patches(patches, VITAL_OUTPUT_FOLDER)

    print("\n✅ Done! 🎉")

if __name__ == "__main__":
    main()