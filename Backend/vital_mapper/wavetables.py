import base64
import random
from typing import Any, Dict
import numpy as np
from midi_analysis import compute_midi_stats
from config import DEFAULT_FRAME_SIZE


def get_shape_for_osc1(stats):
    """
    OSC1 → Attack Phase: Sharper = more aggression, smoother = more mellow.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_range = stats.get("velocity_range", 0)
    velocity_std = stats.get("velocity_std", 0)
    avg_pitch = stats.get("avg_pitch", 60)
    note_density = stats.get("note_density", 0.02)

    # High aggression
    if avg_velocity > 90 and velocity_range > 60:
        return "folded"

    # Fast-moving passages
    if note_density > 0.07:
        return "saw"

    # Dynamic expressiveness
    if velocity_std > 25:
        return "triangle"

    # Sparse or mellow
    if note_density < 0.015:
        return "sine"

    # Fallback based on pitch
    if avg_pitch > 75:
        return "saw"
    elif avg_pitch < 50:
        return "triangle"
    else:
        return "folded"


def get_shape_for_osc2(stats):
    """
    OSC2 → Harmonic Blend: richer or fuzzier based on pitch and note complexity.
    """
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    avg_pitch = stats.get("avg_pitch", 60)

    # Wild pitch motion = chaotic
    if pitch_range > 65:
        return "chaotic"

    # Busy textures = rich buzz
    if note_density > 0.05:
        return "harmonic_buzz"

    # Melodic and clear
    if avg_pitch > 68:
        return "triangle"

    # Simple, minimal range
    if pitch_range < 15:
        return "sine"

    # Mid-complexity fallback
    if pitch_range > 40:
        return "saw"
    else:
        return "triangle"


def get_shape_for_osc3(stats):
    """
    OSC3 → Final Release: smoother or noisier based on decay needs.
    No randomness — purely MIDI-driven.
    """
    avg_velocity = stats.get("avg_velocity", 80)
    velocity_std = stats.get("velocity_std", 0)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 0.02)
    velocity_range = stats.get("velocity_range", 0)

    # Highly expressive: big swings in dynamics or sparse notes
    if velocity_std > 30 or (velocity_std > 25 and note_density < 0.02):
        return "triangle"

    # Rich, bright release needed for dense, varied pitch movement
    if note_density > 0.065 and pitch_range > 25:
        return "folded"

    # Low energy, soft touch
    if avg_velocity < 35 or velocity_range < 10:
        return "sine" if pitch_range < 50 else "triangle"

    # No dynamics at all, use shape based on pitch context
    if velocity_range == 0:
        if pitch_range > 60:
            return "folded"
        elif pitch_range < 10:
            return "triangle"
        else:
            return "saw"

    # Default deterministic fallback — based on pitch shape only
    if pitch_range > 40:
        return "folded"
    elif pitch_range > 20:
        return "triangle"
    else:
        return "sine"



def generate_osc1_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "sine") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    ccs = {cc["controller"]: cc["value"] / 127.0 for cc in midi_data.get("control_changes", [])}
    modwheel = ccs.get(1, 0.5)
    rng = random.Random(int(stats["avg_pitch"] * 1234))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "sine":
        waveform = np.sin(phase + modwheel * np.sin(phase * 2))
    elif shape == "saw":
        max_h = int(6 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase + rng.uniform(0, 0.2))
            for h in range(1, max_h)
        ], axis=0)
    elif shape == "triangle":
        base = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        harmonic = 0.3 * np.sin(phase * 3 + modwheel * 2)
        waveform = base + harmonic
    elif shape == "folded":
        folded = np.tanh(2.5 * np.sin(phase + modwheel * np.pi))
        noise = 0.1 * rng.uniform(-1, 1) * np.sin(phase * rng.randint(2, 5))
        waveform = folded + noise
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")


def generate_osc2_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "saw") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    note_density = stats.get("note_density", 4.0)
    rng = random.Random(int(stats["avg_pitch"] * 4321))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "saw":
        max_harm = int(8 + pitch_range + note_density)
        waveform = np.sum([
            (1.0 / h) * np.sin(h * phase + rng.uniform(0, 0.3))
            for h in range(1, max_harm)
        ], axis=0)
    elif shape == "harmonic_buzz":
        base = np.sum([
            np.sin(h * phase + rng.uniform(0, 0.1)) * (1.0 / (h ** 0.9))
            for h in range(1, 20)
        ], axis=0)
        detune = 0.1 * np.sin(phase * rng.randint(2, 6))
        waveform = base + detune
    elif shape == "chaotic":
        fm = np.sin(phase * (2 + note_density)) * 0.6
        waveform = np.tanh(np.sin(phase * 2 + fm) + np.cos(phase * 3))
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")


def generate_osc3_frame(midi_data: Dict[str, Any], frame_size: int = DEFAULT_FRAME_SIZE, shape: str = "triangle") -> str:
    import base64, random
    from midi_analysis import compute_midi_stats

    stats = compute_midi_stats(midi_data)
    velocity = stats.get("avg_velocity", 0.5)
    pitch_range = stats.get("pitch_range", 12)
    avg_pitch = stats.get("avg_pitch", 60.0)
    rng = random.Random(int(avg_pitch * 5678))

    phase = np.linspace(0, 2 * np.pi, frame_size, endpoint=False)

    if shape == "triangle":
        tri = 2 * np.abs(np.mod(phase / np.pi, 2) - 1) - 1
        shimmer = 0.2 * np.sin(phase * 4 + pitch_range * 0.1)
        waveform = tri + shimmer
    elif shape == "folded":
        base = np.tanh(3.0 * np.sin(phase + np.sin(phase * 3)))
        motion = 0.2 * np.sin(phase * rng.randint(2, 5) + avg_pitch * 0.05)
        waveform = base + motion
    elif shape == "sine":
        vibrato = 0.05 * np.sin(phase * 6)
        waveform = np.sin(phase + vibrato)
    else:
        waveform = np.sin(phase)

    waveform *= velocity
    waveform /= (np.max(np.abs(waveform)) or 1.0)
    return base64.b64encode(waveform.astype(np.float32).tobytes()).decode("utf-8")
