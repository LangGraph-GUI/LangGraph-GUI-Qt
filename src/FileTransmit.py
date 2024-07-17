# FileTransmit.py

from flask import Blueprint, request, jsonify, send_file
import os

file_transmit_bp = Blueprint('file_transmit', __name__)

# Define the workspace directory
WORKSPACE_FOLDER = 'workspace'
if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

@file_transmit_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    file.save(os.path.join(WORKSPACE_FOLDER, file.filename))
    return jsonify({'message': 'File successfully uploaded'}), 200

@file_transmit_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(WORKSPACE_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404
