import os

def load_sysex_txt_files(folder_path):
    """
    Loads all .txt files in the folder and returns a list of (param_block, patch_filename) tuples.
    """
    sysex_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ])

    patch_jobs = []

    for i, file_path in enumerate(sysex_files, start=1):
        with open(file_path, "r") as f:
            hex_values = f.read().strip().split()

        if len(hex_values) != 256:
            print(f"⚠️ Skipping {file_path}: expected 256 params, got {len(hex_values)}")
            continue

        param_block = [int(h, 16) for h in hex_values]
        patch_filename = f"patch_{i:03}.vital"
        patch_jobs.append((param_block, patch_filename))

    print(f"✅ Prepared {len(patch_jobs)} patch jobs from SysEx files.")
    return patch_jobs