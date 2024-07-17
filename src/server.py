# server.py

from flask import Flask, Response, stream_with_context, request, jsonify, send_file
from flask_cors import CORS
import os
from ServerTee import ServerTee
from thread_handler import ThreadHandler
from WorkFlow import run_workflow_as_server

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

server_tee = ServerTee("server.log")
thread_handler = ThreadHandler.get_instance()

# Define the workspace directory
WORKSPACE_FOLDER = 'workspace'
if not os.path.exists(WORKSPACE_FOLDER):
    os.makedirs(WORKSPACE_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400
    file.save(os.path.join(WORKSPACE_FOLDER, file.filename))
    return jsonify({'message': 'File successfully uploaded'}), 200

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(WORKSPACE_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

def server_func():
    run_workflow_as_server()

@app.route('/run', methods=['POST'])
def run_script():
    if thread_handler.is_running():
        return "Another instance is already running", 409

    def generate():
        try:
            thread_handler.start_thread(target=server_func)
            yield from server_tee.stream_to_frontend()
        except Exception as e:
            print(str(e))
        finally:
            thread_handler.force_reset()

    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

@app.route('/stop', methods=['POST'])
def stop_script():
    if thread_handler.is_running():
        thread_handler.force_reset()
        return "Script stopped", 200
    else:
        return "No script is running", 400

@app.route('/status', methods=['GET'])
def check_status():
    running = thread_handler.is_running()
    return jsonify({"running": running}), 200

if __name__ == '__main__':
    app.run(debug=True)
