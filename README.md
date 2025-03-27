# 🎛️ MIDI to Vital Preset Generator

A Python-based tool that dynamically converts MIDI files into expressive, musical, and complex Vital synth presets. Designed for producers, sound designers, and generative artists who want unique patches driven by real performance data.

---

## 🚀 Features

- 🎹 **MIDI-Aware Modulation Routing**  
  Dynamically routes mod wheel, expression pedal, macros, pitch bends, LFOs, and envelopes based on MIDI CCs and musical activity.

- 🌊 **Stat-Driven Wavetable Generation**  
  Builds harmonically rich oscillator frames using additive synthesis, FM, and phase distortion — customized based on pitch range, note density, and velocity.

- 🧠 **Musical Intelligence**  
  Analyzes note density, pitch range, velocity, and CC activity to shape filters, effects, oscillator stacks, and macro destinations.

- 🔁 **LFO & Envelope Synthesis**  
  Injects four musically reactive LFOs and three dynamic envelopes — tempo-aware and scaled to phrasing and articulation.

- 🎛️ **Macro Control Adaptivity**  
  Routes macros to destinations like filter cutoff, FX depth, oscillator morphing, or delay/reverb mix depending on CCs and MIDI stats.

- 🧩 **Modular & Extensible**  
  Modular backend ready for batch processing, DAW tools, or web UI integration (Flask/Tailwind frontend included).

- 📦 **Batch Conversion Support**  
  Drag-and-drop multiple MIDI files and receive a zipped bundle of `.vital` presets instantly.

---

## 📁 Folder Structure

```
├── app.py                  # Flask backend: handles upload, processing, and file delivery
├── config.py               # Central configuration file for CC mappings, ranges, and constants
├── midi_parser.py          # Parses MIDI files using pretty_midi
├── midi_analysis.py        # Extracts statistical features from MIDI (pitch, density, velocity)
├── vital_mapper.py         # Core logic for preset synthesis: mod routing, FX, LFOs, envelopes
├── preset_generators.py    # Generates wavetables and oscillator shapes dynamically
├── assets/
│   └── sample.wav          # Sample file for Vital’s sample oscillator if SMP CCs are triggered
├── output/
│   └── *.vital / *.zip     # Final converted presets or batch zip downloads
└── Frontend/
    ├── templates/index.html   # Drag-and-drop styled upload interface (Tailwind + Flask)
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
> `pretty_midi`, `mido`, `numpy`, `scipy`, `Flask`, and `matplotlib` (optional for debugging visuals)

---

## 🧠 How It Works

| Step | Description |
|------|-------------|
| 1️⃣   | **Parse MIDI**: Extracts notes, control changes, and pitch bends |
| 2️⃣   | **Analyze Performance**: Computes average pitch, pitch range, note density, velocity |
| 3️⃣   | **Wavetable Generation**: Creates dynamic, morphable oscillator frames tuned to MIDI stats |
| 4️⃣   | **Envelope Synthesis**: Builds 3 envelopes from phrasing and velocity |
| 5️⃣   | **LFO Routing**: Injects up to 4 LFOs with varied destinations and shapes |
| 6️⃣   | **Macro Assignment**: Routes macros dynamically based on filter/FX activity and pitch range |
| 7️⃣   | **Stack Mode Selection**: Infers stack voicing (e.g. power chord, octave) from note clusters |
| 8️⃣   | **Filter & FX Activation**: Enables filters/FX based on CCs or intelligent fallback logic |
| 9️⃣   | **Sample Oscillator Activation**: Triggers SMP section if CC31/74/85/86/etc. are present |
| 🔟   | **Export**: Outputs `.vital` preset or `.zip` of presets for multi-file batch uploads |

---

## 🌐 Web Interface

A modern drag-and-drop HTML + Tailwind CSS interface is included for testing or showcasing the tool.  
Use the Flask backend to host the site locally:

```bash
python app.py
```

Then visit:  
**http://localhost:5000/**
