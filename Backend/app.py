from flask import Flask, render_template, request, redirect, url_for, send_file, after_this_request
import os
import tempfile
import shutil
import logging
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename

from config import DEFAULT_VITAL_PRESET_FILENAME, PRESETS_DIR
from midi_parser import parse_midi
from vital_mapper import load_default_vital_preset, modify_vital_preset, save_vital_preset

# Set up Flask and folders
template_dir = Path(__file__).resolve().parents[1] / "Frontend" / "templates"
app = Flask(__name__, template_folder=str(template_dir))

UPLOAD_FOLDER = tempfile.mkdtemp()
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "midi_file" not in request.files:
            return "No MIDI file uploaded.", 400

        files = request.files.getlist("midi_file")
        if not files or all(f.filename == '' for f in files):
            return "No valid MIDI files.", 400

        output_paths = []
        midi_paths = []

        # Load default Vital preset once
        default_preset_path = os.path.join(PRESETS_DIR, DEFAULT_VITAL_PRESET_FILENAME)
        vital_preset = load_default_vital_preset(default_preset_path)
        if not vital_preset:
            return "Failed to load default Vital preset.", 500

        for file in files:
            filename = secure_filename(file.filename)
            if not filename.lower().endswith(('.mid', '.midi')):
                continue

            midi_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(midi_path)
            logging.info(f"📥 Saved: {midi_path}")

            midi_data = parse_midi(midi_path)
            modified_preset, frame_data = modify_vital_preset(vital_preset, midi_data)

            output_filename = f"{os.path.splitext(filename)[0]}.vital"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            save_vital_preset(modified_preset, output_path, frame_data)
            output_paths.append(output_path)
            midi_paths.append(midi_path)

        if not output_paths:
            return "No valid .mid files processed.", 400

        # Clean up uploaded .mid files
        for midi in midi_paths:
            try:
                os.remove(midi)
                logging.info(f"🧹 Deleted: {midi}")
            except Exception as e:
                logging.warning(f"⚠️ Could not delete {midi}: {e}")

        if len(output_paths) == 1:
            filepath = output_paths[0]

            @after_this_request
            def remove_file(response):
                try:
                    os.remove(filepath)
                    logging.info(f"🧹 Deleted preset: {filepath}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not delete file: {e}")
                return response

            return send_file(filepath, as_attachment=True)

        else:
            zip_path = os.path.join(OUTPUT_FOLDER, "batch_presets.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in output_paths:
                    zipf.write(file, os.path.basename(file))

            # Cleanup individual presets
            for file in output_paths:
                try:
                    os.remove(file)
                    logging.info(f"🧹 Deleted: {file}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not delete {file}: {e}")

            @after_this_request
            def remove_zip(response):
                try:
                    os.remove(zip_path)
                    logging.info(f"🧹 Deleted ZIP: {zip_path}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not delete ZIP: {e}")
                return response

            return send_file(zip_path, as_attachment=True)

    except Exception as e:
        logging.exception("❌ Error during batch upload.")
        return f"Internal Server Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)