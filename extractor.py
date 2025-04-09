def extract_virus_param_block(syx_path):
    with open(syx_path, 'rb') as f:
        data = f.read()

    # Strip F0/F7 SysEx wrappers
    if data[0] == 0xF0:
        data = data[1:]
    if data[-1] == 0xF7:
        data = data[:-1]

    # Check for Virus C Single Dump (0x10 at byte 5)
    if len(data) >= 265 and data[5] == 0x10:
        param_block = data[8:8+256]
        print(f"🎛️ Extracted 256-byte Virus parameter block from: {syx_path}\n")
        print(" ".join(f"{b:02X}" for b in param_block))
        return list(param_block)
    else:
        print(f"❌ Not a valid Virus Single Dump or message too short: {syx_path}")
        return None

# Example usage
extract_virus_param_block("/Users/nathannguyen/Documents/Midi_To_serum/3.syx")