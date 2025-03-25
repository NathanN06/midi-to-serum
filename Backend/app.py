from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import logging
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import after_this_request


from config import DEFAULT_VITAL_PRESET_FILENAME, PRESETS_DIR
from midi_parser import parse_midi
from vital_mapper import load_default_vital_preset, modify_vital_preset, save_vital_preset

# Set up Flask and directories
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

        midi_file = request.files["midi_file"]
        if midi_file.filename == "":
            return "Empty filename.", 400

        filename = secure_filename(midi_file.filename)
        if not filename.lower().endswith((".mid", ".midi")):
            return "Only MIDI files are supported.", 400

        midi_path = os.path.join(UPLOAD_FOLDER, filename)
        midi_file.save(midi_path)
        logging.info(f"📥 Uploaded MIDI file saved to: {midi_path}")

        # Load default Vital preset
        default_preset_path = os.path.join(PRESETS_DIR, DEFAULT_VITAL_PRESET_FILENAME)
        vital_preset = load_default_vital_preset(default_preset_path)
        if not vital_preset:
            logging.error("❌ Failed to load default Vital preset.")
            return "Failed to load default Vital preset.", 500

        # Parse and process MIDI
        midi_data = parse_midi(midi_path)
        modified_preset, frame_data_list = modify_vital_preset(vital_preset, midi_data)

        # Save .vital file to OUTPUT_FOLDER
        output_filename = f"{os.path.splitext(filename)[0]}.vital"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        save_vital_preset(modified_preset, output_path, frame_data_list)

        # 🧹 Delete uploaded MIDI file to save memory
        try:
            os.remove(midi_path)
            logging.info(f"🧹 Deleted uploaded MIDI file: {midi_path}")
        except Exception as e:
            logging.warning(f"⚠️ Could not delete MIDI file: {e}")

        logging.info(f"✅ Preset saved: {output_path}")
        return redirect(url_for("download", filename=output_filename))

    except Exception as e:
        logging.exception("❌ Error during upload and processing.")
        return f"Internal Server Error: {str(e)}", 500


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(file_path):
        logging.error(f"❌ Download failed. File not found: {file_path}")
        return "File not found", 404

    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
            logging.info(f"🧹 Deleted temporary preset: {file_path}")
        except Exception as e:
            logging.warning(f"⚠️ Could not delete file: {e}")
        return response

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
