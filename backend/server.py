from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

user_api_key = None
user_base_url = None
user_model_name = None

@app.route('/howdyworld/', methods=['GET'])
def howdy_horld():
    
    return jsonify({"message": "Howdy World!"})

@app.route('/env/', methods=['POST'])
def set_env_variables():
    global user_api_key, user_base_url, user_model_name

    data = request.get_json()

    user_api_key = data.get("api_key")
    user_base_url = data.get("base_url")
    user_model_name = data.get("model_name")

    return jsonify({"status": "Environment variables received."})

@app.route('/algorithm/', methods=['GET'])
def run_algorithm():
    if user_api_key == None or user_base_url == None or user_model_name == None:
        return jsonify({"error": "Environment variables not set"}), 400
    pass

if __name__ == '__main__':
    app.run(debug=True)