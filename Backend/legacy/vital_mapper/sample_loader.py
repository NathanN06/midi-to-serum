import base64
from typing import Any, Dict



def enable_sample_in_preset(preset: Dict[str, Any], sample_path: str = "assets/sample.wav") -> None:
    """
    Reads a WAV file from sample_path, base64-encodes its bytes, and embeds the data in the preset's "sample" key.
    
    Args:
        preset (Dict[str, Any]): The Vital preset dictionary to update.
        sample_path (str, optional): Path to the sample WAV file. Defaults to "assets/sample.wav".
    """
    try:
        with open(sample_path, "rb") as f:
            raw = f.read()
        encoded = base64.b64encode(raw).decode("utf-8")
        preset["sample"] = {
            "enabled": True,
            "playback_mode": "one_shot",
            "sample_bytes": encoded
        }
        print("Sample oscillator enabled with sample from:", sample_path)
    except Exception as e:
        print(f"Error loading sample from {sample_path}: {e}")
