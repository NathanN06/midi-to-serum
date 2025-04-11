import os
import json
from mido import MidiFile

def debug_file_content_to_json(midi_path, syx_path, output_json_path):
    """Save hex dump comparison of MIDI and SYX files to JSON."""
    result = {
        "midi_file": {
            "path": midi_path,
            "sysex_messages": []
        },
        "syx_file": {
            "path": syx_path,
            "data": None
        },
        "comparison": {}
    }
    
    # Extract SysEx from MIDI
    if os.path.exists(midi_path):
        midi = MidiFile(midi_path)
        for i, track in enumerate(midi.tracks):
            for j, msg in enumerate(track):
                if msg.type == 'sysex':
                    full_sysex = bytes([0xF0]) + bytes(msg.data) + bytes([0xF7])
                    result["midi_file"]["sysex_messages"].append({
                        "track": i,
                        "message_index": j,
                        "length": len(full_sysex),
                        "hex_dump": " ".join(f"{b:02X}" for b in full_sysex)
                    })
    else:
        result["midi_file"]["error"] = f"File not found: {midi_path}"
    
    # Extract SYX file content
    if os.path.exists(syx_path):
        with open(syx_path, 'rb') as f:
            syx_data = f.read()
        
        result["syx_file"]["data"] = {
            "length": len(syx_data),
            "hex_dump": " ".join(f"{b:02X}" for b in syx_data)
        }
    else:
        result["syx_file"]["error"] = f"File not found: {syx_path}"
    
    # Create comparison if both have data
    if (result["midi_file"].get("sysex_messages") and 
        result["syx_file"].get("data") and 
        len(result["midi_file"]["sysex_messages"]) > 0):
        
        # Get first SysEx from MIDI for comparison
        midi_sysex = bytes.fromhex(result["midi_file"]["sysex_messages"][0]["hex_dump"].replace(" ", ""))
        syx_data = bytes.fromhex(result["syx_file"]["data"]["hex_dump"].replace(" ", ""))
        
        # Compare byte by byte for first 20 bytes and around byte 41
        comparison = []
        for i in range(min(20, len(midi_sysex), len(syx_data))):
            comparison.append({
                "position": i,
                "midi_byte": f"{midi_sysex[i]:02X}",
                "syx_byte": f"{syx_data[i]:02X}",
                "match": midi_sysex[i] == syx_data[i]
            })
        
        # Also check around byte 41 (for the filter cutoff parameter)
        for i in range(max(20, 35), min(50, len(midi_sysex), len(syx_data))):
            comparison.append({
                "position": i,
                "midi_byte": f"{midi_sysex[i]:02X}",
                "syx_byte": f"{syx_data[i]:02X}",
                "match": midi_sysex[i] == syx_data[i]
            })
            
        result["comparison"]["byte_comparison"] = comparison
        
        # Calculate potential offsets
        result["comparison"]["potential_offsets"] = []
        for offset in range(-10, 11):
            matches = 0
            total = min(256, len(midi_sysex) - max(0, offset), len(syx_data) - max(0, -offset))
            
            midi_start = max(0, offset)
            syx_start = max(0, -offset)
            
            for i in range(total):
                if midi_sysex[midi_start + i] == syx_data[syx_start + i]:
                    matches += 1
            
            match_percentage = (matches / total) * 100 if total > 0 else 0
            result["comparison"]["potential_offsets"].append({
                "offset": offset,
                "match_percentage": match_percentage,
                "explanation": f"MIDI[{midi_start}:] matches SYX[{syx_start}:] at {match_percentage:.1f}%"
            })
    
    # Save to JSON file
    with open(output_json_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Comparison saved to {output_json_path}")

# Example usage
debug_file_content_to_json(
    "/Users/nathannguyen/Documents/Midi_To_serum/Presets/404studio_Virus_C_Soundset.mid",
    "/Users/nathannguyen/Documents/Midi_To_serum/1.syx",
    "/Users/nathannguyen/Documents/Midi_To_serum/comparison.json"
)