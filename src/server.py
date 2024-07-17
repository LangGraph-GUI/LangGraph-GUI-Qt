# server.py

from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS
import time
import threading
from ServerTee import ServerTee

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

server_tee = ServerTee("server.log")

lock = threading.Lock()
current_thread = None
stop_event = threading.Event()

def hello_world_function():
    print("hello_world_function called")
    for i in range(10):
        if stop_event.is_set():
            print("Script stopped by user.")
            break
        print(f"Message {i}")
        time.sleep(1)
    print("Oh my god!")

@app.route('/run', methods=['POST'])
def run_script():
    global current_thread, stop_event
    print("Received request at /run endpoint")
    
    if lock.locked():
        return "Another instance is already running", 409

    def generate():
        global current_thread
        with lock:
            stop_event.clear()
            current_thread = threading.Thread(target=hello_world_function)
            current_thread.start()
            yield from server_tee.stream_to_frontend()
            current_thread.join()

    return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')

@app.route('/stop', methods=['POST'])
def stop_script():
    global current_thread, stop_event
    print("Received request to stop script")
    if lock.locked():
        stop_event.set()
        current_thread.join()
        return "Script stopped", 200
    else:
        return "No script is running", 400

if __name__ == '__main__':
    app.run(debug=True)
