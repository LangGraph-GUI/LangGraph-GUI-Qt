# server.py

from flask import Flask, Response, stream_with_context, request, jsonify
from flask_cors import CORS
import time
from ServerTee import ServerTee
from thread_handler import ThreadHandler

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

server_tee = ServerTee("server.log")
thread_handler = ThreadHandler.get_instance()

def hello_world_function():
    print("hello_world_function called")
    for i in range(10):
        print(f"Message {i}")
        time.sleep(1)
    print("Oh my god!")

@app.route('/run', methods=['POST'])
def run_script():
    print("Received request at /run endpoint")

    if thread_handler.is_running():
        return "Another instance is already running", 409

    def generate():
        try:
            thread_handler.start_thread(target=hello_world_function)
            yield from server_tee.stream_to_frontend()
        except Exception as e:
            print(str(e))
        finally:
            thread_handler.force_reset()

    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

@app.route('/stop', methods=['POST'])
def stop_script():
    print("Received request to stop script")

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
