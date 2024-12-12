from flask import Flask, request, send_file, render_template, jsonify, url_for
from io import BytesIO
from zipfile import ZipFile
import rarfile
from PIL import Image
import pikepdf
from docx import Document
import openpyxl
import mutagen
import logging
from typing import BinaryIO

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

SUPPORTED_ARCHIVES = {"zip", "rar"}
SUPPORTED_FILES = {
    "jpg": "handle_image",
    "jpeg": "handle_image",
    "png": "handle_image",
    "pdf": "handle_pdf",
    "doc": "handle_doc",
    "docx": "handle_doc",
    "xls": "handle_xls",
    "xlsx": "handle_xls",
    "mp3": "handle_audio",
    "flac": "handle_audio",
    "wav": "handle_audio",
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check_pdf_signature", methods=["POST"])
def check_pdf_signature():
    """Check if the PDF is signed."""
    file = request.files["file"]
    try:
        with pikepdf.open(file) as pdf:
            signed = "/Sig" in pdf.Root
            return jsonify({"signed": signed})
    except Exception as e:
        logging.error(f"Error checking PDF signature: {e}")
        return jsonify({"error": str(e)}), 400

@app.route("/upload", methods=["POST"])
def upload_file():
    """Process uploaded files and remove metadata."""
    file = request.files["file"]
    file_ext = file.filename.split(".")[-1].lower()
    cleaned_file = BytesIO()

    try:
        if file_ext in SUPPORTED_ARCHIVES:
            cleaned_archive = handle_archive(file, file_ext)
            cleaned_archive.seek(0)
            download_url = url_for('download_file', filename=f"cleaned_{file.filename}")
            return jsonify({"message": "File successfully cleaned", "download_url": download_url})
        elif file_ext in SUPPORTED_FILES:
            cleaned_file = remove_metadata(file, file_ext)
            cleaned_file.seek(0)
            download_url = url_for('download_file', filename=f"cleaned_{file.filename}")
            return jsonify({"message": "File successfully cleaned", "download_url": download_url})
        else:
            raise ValueError("Unsupported file type")
    except ValueError as e:
        logging.error(f"Unsupported file type: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/download/<filename>")
def download_file(filename):
    """Serve the cleaned file for download."""
    return send_file(BytesIO(), as_attachment=True, download_name=filename)

def handle_archive(archive_file: BinaryIO, archive_ext: str) -> BytesIO:
    """Process archive files (ZIP, RAR)."""
    cleaned_archive = BytesIO()

    try:
        if archive_ext == "zip":
            with ZipFile(archive_file, "r") as zip_ref:
                with ZipFile(cleaned_archive, "w") as cleaned_zip:
                    for file_name in zip_ref.namelist():
                        with zip_ref.open(file_name) as file:
                            process_and_write_file(file, file_name, cleaned_zip)
        elif archive_ext == "rar":
            with rarfile.RarFile(archive_file) as rar_ref:
                with ZipFile(cleaned_archive, "w") as cleaned_zip:  # Output to a ZIP for simplicity
                    for file_name in rar_ref.namelist():
                        with rar_ref.open(file_name) as file:
                            process_and_write_file(file, file_name, cleaned_zip)
        else:
            raise ValueError("Unsupported archive type")
    except Exception as e:
        logging.error(f"Error processing archive: {e}")
        raise

    return cleaned_archive

def process_and_write_file(file: BinaryIO, file_name: str, cleaned_zip: ZipFile) -> None:
    """Process a single file and write it to the cleaned archive."""
    file_ext = file_name.split(".")[-1].lower()
    try:
        cleaned_file = remove_metadata(file, file_ext)
        cleaned_zip.writestr(file_name, cleaned_file.getvalue())
    except ValueError:
        cleaned_zip.writestr(file_name, file.read())

def remove_metadata(file: BinaryIO, file_ext: str) -> BytesIO:
    """Process a single file and remove metadata."""
    cleaned_file = BytesIO()

    handlers = {
        "jpg": handle_image,
        "jpeg": handle_image,
        "png": handle_image,
        "pdf": handle_pdf,
        "doc": handle_doc,
        "docx": handle_doc,
        "xls": handle_xls,
        "xlsx": handle_xls,
        "mp3": handle_audio,
        "flac": handle_audio,
        "wav": handle_audio,
    }

    if file_ext in handlers:
        handlers[file_ext](file, cleaned_file)
    else:
        raise ValueError("Unsupported file type")

    cleaned_file.seek(0)
    return cleaned_file

def handle_image(file: BinaryIO, cleaned_file: BytesIO) -> None:
    img = Image.open(file)
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)
    img_no_exif.save(cleaned_file, format=img.format)
    img.close()
    cleaned_file.seek(0)

def handle_pdf(file: BinaryIO, cleaned_file: BytesIO) -> None:
    pdf = pikepdf.open(file)
    pdf.save(cleaned_file)
    pdf.close()

def handle_doc(file: BinaryIO, cleaned_file: BytesIO) -> None:
    doc = Document(file)
    doc.save(cleaned_file)

def handle_xls(file: BinaryIO, cleaned_file: BytesIO) -> None:
    wb = openpyxl.load_workbook(file)
    wb.save(cleaned_file)

def handle_audio(file: BinaryIO, cleaned_file: BytesIO) -> None:
    audio = mutagen.File(file)
    audio.delete()
    audio.save(cleaned_file)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0",port=8000)
