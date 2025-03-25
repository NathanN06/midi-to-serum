# 🎛️ MIDI to Vital Preset Generator

A Python-based tool that dynamically converts MIDI files into expressive, musical, and complex Vital synth presets. Designed for producers, sound designers, and generative artists who want unique patches based on musical data.

---

## 🚀 Features

- 🎹 **MIDI-Aware Modulation Routing**  
  Dynamically routes mod wheel, expression pedal, macros, pitch bends, and envelopes based on MIDI CCs and note data.

- 🌊 **Custom Wavetable Frame Generation**  
  Creates three harmonically rich oscillator frames using Fourier synthesis, FM, and phase distortion—mapped to musical intent.

- 🧠 **Musical Intelligence**  
  Adapts filter curves, oscillator settings, stack modes, LFO targets, and effect parameters based on MIDI note density, pitch range, and velocity.

- 🔁 **LFO & Envelope Synthesis**  
  Injects four musically shaped LFOs and three dynamic envelopes with adaptive timing and sustain behavior.

- 🎛️ **Macro Control Mapping**  
  Automatically routes macros to expressive destinations based on filter/effect usage.

- 🧩 **Modular Design**  
  Codebase is modular and extensible—ideal for integration into DAW tools, UIs, or WebAudio systems.

---

## 📁 Folder Structure

```
├── app.py                  # Entry point script to convert MIDI → Vital preset
├── config.py               # Central config for mappings, constants, defaults
├── midi_parser.py          # MIDI file parsing using pretty_midi + mido
├── midi_analysis.py        # Stats & intelligence about note density, pitch, velocity
├── vital_mapper.py         # Main logic: modulation, LFOs, FX, envelopes, stack logic
├── preset_generators.py    # Handles wavetable synthesis, oscillator shaping, routing
├── assets/
│   └── sample.wav          # Embedded sample for Vital's sample oscillator
└── output/
    └── *.vital             # Output preset files
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
---

## 🧠 How It Works

### ✅ Step-by-step breakdown:

| Step | Description |
|------|-------------|
| 1️⃣   | **Parse MIDI**: Reads notes, control changes, and pitch bends |
| 2️⃣   | **Analyze**: Computes average pitch, velocity, note density, and CC usage |
| 3️⃣   | **Snapshot**: Sets base oscillator pitch & level using 3 optional strategies |
| 4️⃣   | **Envelope Synthesis**: Dynamically adjusts ADSR for 3 envelopes |
| 5️⃣   | **LFO Routing**: Adds 4 LFOs based on rhythmic/harmonic analysis |
| 6️⃣   | **Macro Assignment**: Routes macros to meaningful destinations |
| 7️⃣   | **Oscillator Stack Logic**: Selects stack mode (e.g. major, minor, octave) from note intervals |
| 8️⃣   | **Filter & FX Shaping**: Enables filters/FX based on CCs or musical fallback |
| 9️⃣   | **Sample Oscillator**: Activates if SMP-related CCs are detected |
| 🔟   | **Export**: Saves the preset as an uncompressed `.vital` JSON preset |
