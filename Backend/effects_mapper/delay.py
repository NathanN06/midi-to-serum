# delay.py

from typing import Dict, Any

def inject_delay_settings(virus_params: Dict[str, Any], preset: Dict[str, Any]) -> None:
    """
    Injects delay settings into the Vital preset if Virus parameters suggest it's in use.
    Heuristic: enable delay if time, feedback, or send level is above a minimal threshold.
    """
    feedback = virus_params.get("Delay_Feedback", 0)
    time = virus_params.get("Delay_Time", 0)
    send = virus_params.get("Effect_Send", 0)

    # Heuristic: consider delay active if any of these are non-zero
    delay_on = any(val > 5 for val in [feedback, time, send])

    settings = preset.setdefault("settings", {})
    settings["delay_on"] = 1 if delay_on else 0

    # Optional: map normalized values for more realism
    if delay_on:
        settings["delay_feedback"] = feedback / 127.0
        settings["delay_time"] = time / 127.0

    print(
        f"🌀 Delay {'ENABLED' if delay_on else 'disabled'}"
        f" — Time={time}, Feedback={feedback}, Send={send}"
    )
