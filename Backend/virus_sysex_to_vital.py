# virus_sysex_to_vital.py

from typing import Dict, Any
from virus_sysex_param_map import virus_sysex_param_map
from virus_to_vital_map import virus_to_vital_map

def apply_virus_sysex_params_to_vital_preset(param_block: list[int], vital_preset: Dict[str, Any]) -> None:
    """
    Given a 256-byte Virus parameter block, apply the parameter values to the provided
    Vital preset dictionary using virus_sysex_param_map and virus_to_vital_map.

    Args:
        param_block (list[int]): Exactly 256 ints representing Virus sysex parameter bytes.
        vital_preset (dict): Vital preset dictionary, where Vital parameters typically reside 
                             in vital_preset["settings"].
    """
    if len(param_block) != 256:
        raise ValueError("Virus param_block must have exactly 256 entries.")

    for idx, virus_value in enumerate(param_block):
        # 1) Get the Virus parameter name from the sysex param map
        virus_param_name = virus_sysex_param_map.get(idx)
        if not virus_param_name:
            continue  # No mapping for this index

        # 2) Get mapping from Virus param to Vital
        mapping = virus_to_vital_map.get(virus_param_name)
        if not mapping:
            continue  # No mapping defined

        # 3) Check if it's a direct dictionary-based mapping
        if isinstance(mapping, dict):
            vital_target = mapping.get("vital_target")
            scale_fn = mapping.get("scale", lambda x: x)
            scaled_value = scale_fn(virus_value)

            if isinstance(vital_target, list):
                # Special case: multiple targets from one Virus parameter
                for target_key in vital_target:
                    # Assume scale_fn returns a dictionary of target -> value
                    vital_preset["settings"][target_key] = scaled_value[target_key]
            else:
                vital_preset["settings"][vital_target] = scaled_value

        # 4) Check if it's a list of mappings (multi-target entries like Panorama)
        elif isinstance(mapping, list):
            for item in mapping:
                vital_target = item.get("vital_target")
                scale_fn = item.get("scale", lambda x: x)
                scaled_value = scale_fn(virus_value)
                vital_preset["settings"][vital_target] = scaled_value

        # 5) If mapping is None or invalid, skip
        else:
            continue
