def set_filter_balance_mix(value: int, vital_preset: dict) -> None:
    """
    Adjusts filter_1_mix and filter_2_mix in Vital based on Virus Filter_Balance.
    - value: 0–127 → maps to -1 to +1
    """
    balance = (value - 64) / 64.0  # Normalize to -1 to +1
    f1_mix = max(0.0, 1.0 - balance)
    f2_mix = max(0.0, 1.0 + balance)

    vital_preset["settings"]["filter_1_mix"] = round(min(f1_mix, 1.0), 4)
    vital_preset["settings"]["filter_2_mix"] = round(min(f2_mix, 1.0), 4)
