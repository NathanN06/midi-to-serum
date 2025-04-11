def apply_virus_modulations(virus_params: dict, preset: dict, virus_to_vital_map: dict):
    """
    Injects modulation into Vital preset's settings block based on Virus modulation parameters.
    """
    settings = preset.get("settings")
    if not settings or not isinstance(settings.get("modulations"), list):
        settings["modulations"] = [{"source": "", "destination": ""} for _ in range(64)]

    mod_list = settings["modulations"]

    for virus_param, value in virus_params.items():
        if value == 0:
            continue  # Skip modulation if Virus value is 0

        if virus_param not in virus_to_vital_map:
            continue

        mapping = virus_to_vital_map[virus_param]
        if mapping is None:
            continue

        # Handle modulation routes
        if "modulation_target" in mapping and "modulation_source" in mapping:
            destination = mapping["modulation_target"]
            source = mapping["modulation_source"]
            amount = mapping["scale"](value)
        elif "modulate_target" in mapping and "modulator" in mapping:
            destination = mapping["modulate_target"]
            source = mapping["modulator"]
            amount = mapping["amount_scale"](value)
        else:
            continue  # Not a modulation entry

        # Skip zero modulation amount after scaling (safety check)
        if amount == 0:
            continue

        # Find empty modulation slot
        try:
            mod_index = next(
                i for i, mod in enumerate(mod_list)
                if mod.get("source") == "" and mod.get("destination") == ""
            )
        except StopIteration:
            print(f"⚠️ No modulation slots left — skipping {virus_param}")
            continue

        # Inject into settings
        mod_list[mod_index] = {"source": source, "destination": destination}
        prefix = f"modulation_{mod_index}"
        settings[f"{prefix}_amount"] = amount
        settings[f"{prefix}_bipolar"] = 0.0
        settings[f"{prefix}_bypass"] = 0.0
        settings[f"{prefix}_power"] = 0.0
        settings[f"{prefix}_stereo"] = 0.0
