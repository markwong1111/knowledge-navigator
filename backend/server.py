from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import base64
from app import generate_knowledge_graph_html_sync

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

@app.route('/algorithm/', methods=['POST'])
def run_algorithm():
    if user_api_key == None or user_base_url == None or user_model_name == None:
        return jsonify({"error": "Environment variables not set"}), 400
    data = request.get_json()

# what it takes in 
#     files = [
#     {
#         'name': 'my_document.pdf',           # The filename
#         'content': 'base64 data',   # The actual file content (encoded in base64)
#         'extension': '.pdf'                  # File type (.txt, .pdf, .csv, .docx)
#     },
#     {
#         'name': 'notes.txt',
#         'content': 'This is text content',
#         'extension': '.txt'
#     }
# ]
    files = data.get("files", [])

    processed_files = []

    for f in files:
        decoded_content = base64.b64decode(f["content"])
        processed_files.append({
            "name": f["name"],
            "extension": f["extension"],
            "content": decoded_content,  # <-- now real bytes
        })

    html = generate_knowledge_graph_html_sync(processed_files) #need to make sure data is the right type to pass in
    return {"html": html}

if __name__ == '__main__':
    app.run(debug=True)