# server.py

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

def hello_world_function():
    print("hello_world_function called")
    return "Oh my god!"

@app.route('/run', methods=['POST'])
def run_script():
    print("Received request at /run endpoint")
    try:
        output = hello_world_function()
        print("Returning output:", output)
        return output, 200
    except Exception as e:
        print("Error occurred:", str(e))
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)
