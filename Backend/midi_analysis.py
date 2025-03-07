import pretty_midi

def parse_midi(file_path):
    """
    Parse a MIDI file to extract notes, control changes, tempo, pitch bends,
    and calculate envelope parameters (attack, decay, sustain, release).
    """
    try:
        midi_data = pretty_midi.PrettyMIDI(file_path)

        # Extract tempo
        tempo = midi_data.estimate_tempo()

        # Extract notes with ENV parameters
        notes = []
        attack_times = []
        decay_times = []
        sustain_levels = []
        release_times = []

        for instrument in midi_data.instruments:
            for i, note in enumerate(instrument.notes):
                # Attack time: time between this note and the previous note's start
                attack_time = 0.01 if i == 0 else max(0.01, note.start - instrument.notes[i - 1].end)

                # Decay time: fixed for now, but can be improved with MIDI CC
                decay_time = 0.1  # Placeholder value

                # Sustain level: velocity scaled to 0-1
                sustain_level = note.velocity / 127.0

                # Release time: estimated as 30% of note duration
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
                "value": cc.value / 127.0,  # Normalize CC values to 0-1
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

        # Compute average ADSR for the preset (fallback values)
        adsr = {
            "attack": sum(attack_times) / len(attack_times) if attack_times else 0.01,
            "decay": sum(decay_times) / len(decay_times) if decay_times else 0.1,
            "sustain": sum(sustain_levels) / len(sustain_levels) if sustain_levels else 0.8,
            "release": sum(release_times) / len(release_times) if release_times else 0.3
        }

        print("\n🔍 Debug: Parsed MIDI Data")
        print(f"Notes: {len(notes)}, CCs: {len(control_changes)}, Pitch Bends: {len(pitch_bends)}")
        print(f"ADSR -> Attack: {adsr['attack']:.3f}, Decay: {adsr['decay']:.3f}, Sustain: {adsr['sustain']:.3f}, Release: {adsr['release']:.3f}")

        return {
            "tempo": tempo,
            "notes": notes,
            "control_changes": control_changes,
            "pitch_bends": pitch_bends,
            "adsr": adsr  # ✅ Include overall ADSR
        }

    except Exception as e:
        print(f"❌ Error parsing MIDI file: {e}")
        return {
            "tempo": None,
            "notes": [],
            "control_changes": [],
            "pitch_bends": [],
            "adsr": {"attack": 0.01, "decay": 0.1, "sustain": 0.8, "release": 0.3}  # Default fallback
        }
