# app.py
import os
import uuid
import zipfile
import shutil
import logging

from flask import Flask, render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename

# Import your new logic
from sysex_parser import extract_sysex_from_midi
from virus_to_vital_converter import load_sysex_txt_files, save_vital_patches

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
# Adjust these paths to match your actual folder structure
FRONTEND_TEMPLATES = "/Users/nathannguyen/Documents/Midi_To_serum/Frontend/templates"
TEMP_SYSEX_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Temp_sysex_holders"
VITAL_OUTPUT_FOLDER = "/Users/nathannguyen/Documents/Midi_To_serum/Backend/output"
DEFAULT_VITAL_PATCH = "/Users/nathannguyen/Documents/Midi_To_serum/Presets/Default.vital"

# Ensure output folders exist
os.makedirs(TEMP_SYSEX_FOLDER, exist_ok=True)
os.makedirs(VITAL_OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=FRONTEND_TEMPLATES)

# You might want to store uploaded .mid files in a subfolder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    # Renders your existing index.html from the templates folder
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """
    1) Receives one or more .mid/.midi files from the front-end.
    2) For each .mid:
       - Save to UPLOAD_FOLDER
       - Extract SysEx to .txt in TEMP_SYSEX_FOLDER
       - Convert to .vital patches in VITAL_OUTPUT_FOLDER
    3) If multiple patches => zip them, otherwise just send single.
    4) Cleanup everything after sending.
    """
    try:
        if "midi_file" not in request.files:
            return "No MIDI file uploaded.", 400

        uploaded_files = request.files.getlist("midi_file")
        if not uploaded_files or all(f.filename == "" for f in uploaded_files):
            return "No valid MIDI files.", 400

        # A unique subdirectory or ID for this "session"
        session_id = str(uuid.uuid4())[:8]
        session_output_dir = os.path.join(VITAL_OUTPUT_FOLDER, f"session_{session_id}")
        os.makedirs(session_output_dir, exist_ok=True)

        # We'll store the final .vital paths here
        all_vital_files = []

        # 1) PROCESS EACH UPLOADED MIDI
        for file in uploaded_files:
            filename = secure_filename(file.filename)
            if not filename.lower().endswith((".mid", ".midi")):
                continue  # skip anything not .mid

            saved_midi_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(saved_midi_path)
            logging.info(f"📥 Saved: {saved_midi_path}")

            # 2) Extract .txt SysEx
            sysex_files = extract_sysex_from_midi(saved_midi_path, TEMP_SYSEX_FOLDER, verbose=False)

            if not sysex_files:
                logging.info(f"No valid Virus patches found in {saved_midi_path}. Skipping.")
            else:
                # 3) Convert .txt -> Vital patches
                patches = load_sysex_txt_files(TEMP_SYSEX_FOLDER, DEFAULT_VITAL_PATCH)
                
                # 4) Save all patches into session_output_dir
                #    This function returns nothing, but we know it writes .vital files to session_output_dir
                save_vital_patches(patches, session_output_dir)

                # Clean up .txt Sysex in TEMP_SYSEX_FOLDER
                for sf in sysex_files:
                    if os.path.exists(sf):
                        os.remove(sf)

            # Clean up the uploaded .mid
            if os.path.exists(saved_midi_path):
                os.remove(saved_midi_path)

        # Collect all .vital files from the session_output_dir
        for root, dirs, files in os.walk(session_output_dir):
            for f in files:
                if f.lower().endswith(".vital"):
                    all_vital_files.append(os.path.join(root, f))

        if not all_vital_files:
            # If no .vital files were produced, let's just return
            return "No .vital files generated.", 400

        # ----------------------------------------------------------------
        # SINGLE vs. MULTIPLE PRESETS => ZIP OR DIRECT DOWNLOAD
        # ----------------------------------------------------------------
        if len(all_vital_files) == 1:
            # ONE FILE => SEND DIRECTLY
            vital_file = all_vital_files[0]

            @after_this_request
            def cleanup(response):
                # 1) Delete output .vital
                try:
                    os.remove(vital_file)
                    logging.info(f"🧹 Deleted preset: {vital_file}")
                except Exception as e:
                    logging.warning(f"Could not delete file: {e}")

                # 2) Remove the session folder
                try:
                    os.rmdir(session_output_dir)
                except OSError:
                    pass

                # 3) Remove entire Temp / Output folders if you want
                cleanup_folders()

                return response

            logging.info(f"Sending single .vital: {vital_file}")
            return send_file(vital_file, as_attachment=True)

        else:
            # MULTIPLE FILES => ZIP THEM
            zip_name = "virus_vital_patches.zip"
            zip_path = os.path.join(session_output_dir, zip_name)

            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for vfile in all_vital_files:
                    zf.write(vfile, os.path.basename(vfile))

            @after_this_request
            def cleanup(response):
                # 1) Remove all .vital
                for vfile in all_vital_files:
                    try:
                        os.remove(vfile)
                        logging.info(f"🧹 Deleted: {vfile}")
                    except Exception as e:
                        logging.warning(f"Could not delete file: {e}")

                # 2) Remove the ZIP
                try:
                    os.remove(zip_path)
                    logging.info(f"🧹 Deleted ZIP: {zip_path}")
                except Exception as e:
                    logging.warning(f"Could not delete ZIP: {e}")

                # 3) Remove the session folder
                try:
                    os.rmdir(session_output_dir)
                except OSError:
                    pass

                # 4) Remove entire Temp / Output folders if you want
                cleanup_folders()

                return response

            logging.info(f"Sending zipped .vital patches: {zip_path}")
            return send_file(zip_path, as_attachment=True)

    except Exception as e:
        logging.exception("❌ Error during upload.")
        return f"Internal Server Error: {str(e)}", 500

def cleanup_folders():
    """
    Removes everything in TEMP_SYSEX_FOLDER and VITAL_OUTPUT_FOLDER 
    (including subfolders) after the request is complete.
    Use carefully—this fully clears them out.
    """
    try:
        if os.path.exists(TEMP_SYSEX_FOLDER):
            shutil.rmtree(TEMP_SYSEX_FOLDER)
            os.makedirs(TEMP_SYSEX_FOLDER, exist_ok=True)
        logging.info(f"🗑  Cleaned up {TEMP_SYSEX_FOLDER}")

        if os.path.exists(VITAL_OUTPUT_FOLDER):
            shutil.rmtree(VITAL_OUTPUT_FOLDER)
            os.makedirs(VITAL_OUTPUT_FOLDER, exist_ok=True)
        logging.info(f"🗑  Cleaned up {VITAL_OUTPUT_FOLDER}")

    except Exception as ex:
        logging.warning(f"⚠️ Cleanup error: {ex}")

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
