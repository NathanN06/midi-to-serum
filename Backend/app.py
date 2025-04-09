import os
import uuid
import zipfile
import shutil
import logging

from flask import Flask, render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename

from sysex_parser import extract_sysex_from_midi
from virus_to_vital_converter import load_sysex_txt_files, save_vital_patches

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
FRONTEND_TEMPLATES = "/Users/nathannguyen/Documents/Midi_To_serum/Frontend/templates"
TEMP_SYSEX_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Temp_sysex_holders"
VITAL_OUTPUT_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Backend/output"
DEFAULT_VITAL_PATCH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/Default.vital"
LOG_FILE_PATH = "/Users/nathannguyen/Documents/Midi_To_serum/logs/conversion.log"

# Ensure necessary directories exist
os.makedirs(TEMP_SYSEX_FOLDER, exist_ok=True)
os.makedirs(VITAL_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

app = Flask(__name__, template_folder=FRONTEND_TEMPLATES)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------------------------------------------
# LOGGING SETUP (Console + File)
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.info("🚀 App started, logging initialized.")

# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "midi_file" not in request.files:
            return "No MIDI file uploaded.", 400

        uploaded_files = request.files.getlist("midi_file")
        if not uploaded_files or all(f.filename == "" for f in uploaded_files):
            return "No valid MIDI files.", 400

        session_id = str(uuid.uuid4())[:8]
        session_output_dir = os.path.join(VITAL_OUTPUT_FOLDER, f"session_{session_id}")
        os.makedirs(session_output_dir, exist_ok=True)

        all_vital_files = []

        for file in uploaded_files:
            filename = secure_filename(file.filename)
            if not filename.lower().endswith((".mid", ".midi")):
                continue

            saved_midi_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(saved_midi_path)
            logging.info(f"📥 Saved: {saved_midi_path}")

            sysex_files = extract_sysex_from_midi(saved_midi_path, TEMP_SYSEX_FOLDER, verbose=False)

            if not sysex_files:
                logging.info(f"No valid Virus patches found in {saved_midi_path}. Skipping.")
            else:
                patches = load_sysex_txt_files(TEMP_SYSEX_FOLDER, DEFAULT_VITAL_PATCH)
                save_vital_patches(patches, session_output_dir)

                # ✅ CLEANUP restored
                for sf in sysex_files:
                    if os.path.exists(sf):
                        os.remove(sf)

            if os.path.exists(saved_midi_path):
                os.remove(saved_midi_path)

        for root, dirs, files in os.walk(session_output_dir):
            for f in files:
                if f.lower().endswith(".vital"):
                    all_vital_files.append(os.path.join(root, f))

        if not all_vital_files:
            return "No .vital files generated.", 400

        if len(all_vital_files) == 1:
            vital_file = all_vital_files[0]

            @after_this_request
            def cleanup(response):
                try:
                    os.remove(vital_file)
                    logging.info(f"🧹 Deleted preset: {vital_file}")
                except Exception as e:
                    logging.warning(f"Could not delete file: {e}")
                try:
                    os.rmdir(session_output_dir)
                except OSError:
                    pass

                # ✅ CLEANUP restored
                cleanup_folders()
                return response

            logging.info(f"🎯 Sending single .vital: {vital_file}")
            return send_file(vital_file, as_attachment=True)

        else:
            zip_name = "virus_vital_patches.zip"
            zip_path = os.path.join(session_output_dir, zip_name)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for vfile in all_vital_files:
                    zf.write(vfile, os.path.basename(vfile))

            @after_this_request
            def cleanup(response):
                for vfile in all_vital_files:
                    try:
                        os.remove(vfile)
                        logging.info(f"🧹 Deleted: {vfile}")
                    except Exception as e:
                        logging.warning(f"Could not delete file: {e}")
                try:
                    os.remove(zip_path)
                    logging.info(f"🧹 Deleted ZIP: {zip_path}")
                except Exception as e:
                    logging.warning(f"Could not delete ZIP: {e}")
                try:
                    os.rmdir(session_output_dir)
                except OSError:
                    pass

                # ✅ CLEANUP restored
                cleanup_folders()
                return response

            logging.info(f"🎯 Sending ZIP with patches: {zip_path}")
            return send_file(zip_path, as_attachment=True)

    except Exception as e:
        logging.exception("❌ Error during upload.")
        return f"Internal Server Error: {str(e)}", 500


def cleanup_folders():
    try:
        if os.path.exists(TEMP_SYSEX_FOLDER):
            shutil.rmtree(TEMP_SYSEX_FOLDER)
            os.makedirs(TEMP_SYSEX_FOLDER, exist_ok=True)
        logging.info(f"🗑️ Cleaned: {TEMP_SYSEX_FOLDER}")

        if os.path.exists(VITAL_OUTPUT_FOLDER):
            shutil.rmtree(VITAL_OUTPUT_FOLDER)
            os.makedirs(VITAL_OUTPUT_FOLDER, exist_ok=True)
        logging.info(f"🗑️ Cleaned: {VITAL_OUTPUT_FOLDER}")

    except Exception as ex:
        logging.warning(f"⚠️ Cleanup error: {ex}")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
