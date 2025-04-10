from typing import Dict, Any
from .chorus import inject_chorus_settings
from .delay import inject_delay_settings
# In the future: from .distortion import inject_distortion_settings, etc.

def inject_all_effects(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    """
    Master function that injects all Virus FX sections into the Vital preset.
    Currently supports:
    - Chorus
    - Delay
    """
    inject_chorus_settings(virus_params, preset)
    inject_delay_settings(virus_params, preset)

    # Future:
    # inject_distortion_settings(virus_params, preset)
