# FileTransmit.py

from flask import Blueprint, request, jsonify, send_file
import os
import zipfile
import io
from datetime import datetime

file_transmit_bp = Blueprint('file_transmit', __name__)

# Define the workspace directory
WORKSPACE_FOLDER = './'
if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

@file_transmit_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files selected for uploading'}), 400

    for file in files:
        if file.filename == '':
            continue
        file.save(os.path.join(WORKSPACE_FOLDER, file.filename))
        print(f"upload file: {file.filename}")
    return jsonify({'message': 'Files successfully uploaded'}), 200

@file_transmit_bp.route('/download', methods=['GET'])
def download_workspace():
    zip_filename = f'workspace_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_STORED) as zip_file:
        for root, dirs, files in os.walk(WORKSPACE_FOLDER):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, WORKSPACE_FOLDER)
                zip_file.write(file_path, arcname)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name=zip_filename, mimetype='application/zip')
