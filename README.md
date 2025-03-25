
# 🎛️ MIDI to Vital Preset Generator

A Python-based tool that dynamically converts MIDI files into expressive, musical, and complex Vital synth presets. Designed for producers, sound designers, and generative artists who want unique patches based on real MIDI performance data.

---

## 🚀 Features

- 🎹 **MIDI-Aware Modulation Routing**  
  Dynamically routes mod wheel, expression pedal, macros, pitch bends, LFOs, and envelopes based on MIDI CCs and musical activity.

- 🌊 **Custom Wavetable Frame Generation**  
  Creates three harmonically rich oscillator frames using additive synthesis, FM, and phase distortion—mapped to note and CC behavior.

- 🧠 **Musical Intelligence**  
  Analyzes note density, pitch range, velocity, and CC activity to shape filters, effects, oscillator stacks, and macro destinations.

- 🔁 **LFO & Envelope Synthesis**  
  Injects four uniquely shaped LFOs and three dynamic envelopes—tempo-aware and scaled to musical phrasing.

- 🎛️ **Macro Control Adaptivity**  
  Routes macros to destinations like filter cutoff, FX depth, oscillator morphing, or delay/reverb mix depending on usage.

- 🧩 **Modular & Extensible**  
  Modular backend ready for integration into DAW tools, web interfaces, or batch preset generation workflows.

---

## 📁 Folder Structure

```
├── app.py                  # Entry point script for command-line MIDI → Vital conversion
├── config.py               # Central configuration file for mappings, ranges, and constants
├── midi_parser.py          # Parses MIDI using pretty_midi and mido
├── midi_analysis.py        # Extracts stats: pitch range, note density, average velocity, etc.
├── vital_mapper.py         # Core logic: modulation, envelopes, LFOs, filters, FX, macros
├── preset_generators.py    # Wavetable generation, oscillator shaping, stack rules
├── assets/
│   └── sample.wav          # Embedded sample used by Vital’s sample oscillator
└── output/
    └── *.vital             # Final generated preset files
```

---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/midi-to-vital-generator.git
cd midi-to-vital-generator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Dependencies include:**  
> `pretty_midi`, `mido`, `numpy`, `pandas`, `scipy` (if extended), and `matplotlib` (optional for debugging visuals)

---

## 🧠 How It Works

| Step | Description |
|------|-------------|
| 1️⃣   | **Parse MIDI**: Reads notes, CCs, and pitch bend messages using `pretty_midi` |
| 2️⃣   | **Analyze Performance**: Calculates pitch range, note density, and average velocity |
| 3️⃣   | **Oscillator Setup**: Sets base pitch/level from average note data |
| 4️⃣   | **Envelope Synthesis**: Builds ENV1–ENV3 dynamically based on note duration, velocity, phrasing |
| 5️⃣   | **LFO Routing**: Adds 4 LFOs with waveform variety and CC-controlled rate/depth |
| 6️⃣   | **Macro Assignment**: Routes macros to musically useful destinations (e.g., filter cutoff or FX mix) |
| 7️⃣   | **Stack Mode Inference**: Chooses stack voicing (octave, power chord, harmonic) from note intervals |
| 8️⃣   | **Filter & FX Intelligence**: Enables and tunes filters/FX based on CC presence or musical fallback |
| 9️⃣   | **Sample Oscillator Activation**: Enables sample oscillator if related CCs are present |
| 🔟   | **Export**: Saves output as an uncompressed `.vital` JSON preset ready for use in Vital |

---
