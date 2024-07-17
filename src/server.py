# server.py

from flask import Flask, Response, stream_with_context
from flask_cors import CORS
import time
from ServerTee import ServerTee

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

server_tee = ServerTee("server.log")

def hello_world_function():
    print("hello_world_function called")
    for i in range(10):
        print(f"Message {i}")
        time.sleep(1)
    print("Oh my god!")

@app.route('/run', methods=['POST'])
def run_script():
    print("Received request at /run endpoint")
    try:
        def generate():
            hello_world_function()
            yield from server_tee.stream_to_frontend()
        
        return Response(stream_with_context(generate()), content_type='text/plain; charset=utf-8')
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)