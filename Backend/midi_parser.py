import pretty_midi
import logging
import traceback
from config import DEFAULT_ADSR

# Configure logging (only if not already configured elsewhere)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def parse_midi(file_path):
    """
    Parse a MIDI file to extract notes, control changes, tempo, pitch bends,
    and calculate envelope parameters (attack, decay, sustain, release).
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)

        # Extract tempo
        tempo = midi_data.estimate_tempo()

        # Extract notes with envelope parameters
        notes = []
        attack_times = []
        decay_times = []
        sustain_levels = []
        release_times = []

        for instrument in midi_data.instruments:
            for i, note in enumerate(instrument.notes):
                attack_time = 0.01 if i == 0 else max(0.01, note.start - instrument.notes[i - 1].end)
                decay_time = 0.1  # Placeholder for future MIDI CC-based adjustments
                sustain_level = note.velocity / 127.0
                release_time = max(0.05, (note.end - note.start) * 0.3)

                # Store envelope values for averaging later
                attack_times.append(attack_time)
                decay_times.append(decay_time)
                sustain_levels.append(sustain_level)
                release_times.append(release_time)

                notes.append({
                    "pitch": note.pitch,
                    "velocity": note.velocity,
                    "start": note.start,
                    "end": note.end,
                    "attack": attack_time,
                    "decay": decay_time,
                    "sustain": sustain_level,
                    "release": release_time
                })

        # Extract control changes
        control_changes = [
            {
                "controller": cc.number,
                "value": cc.value / 127.0,
                "time": cc.time
            }
            for instrument in midi_data.instruments
            for cc in instrument.control_changes
        ]

        # Extract pitch bends
        pitch_bends = [
            {
                "pitch": pb.pitch,
                "time": pb.time
            }
            for instrument in midi_data.instruments
            for pb in instrument.pitch_bends
        ]

        # Compute average ADSR for the preset
        adsr = {
            "attack": sum(attack_times) / len(attack_times) if attack_times else DEFAULT_ADSR["attack"],
            "decay": sum(decay_times) / len(decay_times) if decay_times else DEFAULT_ADSR["decay"],
            "sustain": sum(sustain_levels) / len(sustain_levels) if sustain_levels else DEFAULT_ADSR["sustain"],
            "release": sum(release_times) / len(release_times) if release_times else DEFAULT_ADSR["release"]
        }

        return {
            "tempo": tempo,
            "notes": notes,
            "control_changes": control_changes,
            "pitch_bends": pitch_bends,
            "adsr": adsr
        }

    except Exception as e:
        logging.error(f"Error parsing MIDI file '{file_path}': {e}")
        logging.debug(traceback.format_exc())
        return {
            "tempo": None,
            "notes": [],
            "control_changes": [],
            "pitch_bends": [],
            "adsr": DEFAULT_ADSR
        }
