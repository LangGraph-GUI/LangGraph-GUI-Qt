# server.py

from flask import Flask, Response, stream_with_context, request, jsonify
from flask_cors import CORS
import os
from ServerTee import ServerTee
from thread_handler import ThreadHandler
from WorkFlow import run_workflow_as_server
from FileTransmit import file_transmit_bp  # Import the Blueprint

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

app.register_blueprint(file_transmit_bp)  # Register the Blueprint

server_tee = ServerTee("workspace/server.log")
thread_handler = ThreadHandler.get_instance()

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
