# server.py

from flask import Flask, Response
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def hello_world_function():
    print("hello_world_function called")
    for i in range(10):
        yield f"Message {i}\n"
        time.sleep(1)
    yield "Oh my god!\n"

@app.route('/run', methods=['POST'])
def run_script():
    print("Received request at /run endpoint")
    try:
        return Response(hello_world_function(), content_type='text/plain; charset=utf-8')
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
