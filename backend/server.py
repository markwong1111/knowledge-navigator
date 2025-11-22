from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import base64
import io
from app import generate_knowledge_graph_html_sync

app = Flask(__name__)
CORS(app)

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

@app.route('/generate-graph/', methods=['POST'])
def run_algorithm():
    api_key = request.form.get('api_key')
    base_url = request.form.get('base_url')
    model_name = request.form.get('model_name')
    temperature = float(request.form.get('temperature'))
    chunk_size = int(request.form.get('chunk_size'))

    chunk_overlap = chunk_size // 20
    
    
    # Validate credentials are provided
    if not api_key or not base_url or not model_name:
        return jsonify({
            "error": "API credentials required. Please configure your API settings."
        }), 400

    # Get text from form data
    text = request.form.get('text', '')
    
    # Get uploaded files
    uploaded_files = request.files.getlist('files')
    
    processed_files = []
    
    # Process uploaded files
    for file in uploaded_files:
        extension = '.' + file.filename.split('.')[-1].lower()
        # Read file content into BytesIO
        file_content = io.BytesIO(file.read())
        processed_files.append({
            "name": file.filename,
            "extension": extension,
            "content": file_content,
        })
    
    # If text was provided, add it as a text file
    if text.strip():
        text_content = io.BytesIO(text.encode('utf-8'))
        processed_files.append({
            "name": "input_text.txt",
            "extension": ".txt",
            "content": text_content,
        })
    
    if not processed_files:
        return jsonify({"error": "No files or text provided"}), 400
    
    html = generate_knowledge_graph_html_sync(processed_files, api_key=api_key, api_base=base_url, llm_name=model_name, temp=temperature, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return jsonify({"html": html})


encoded_string = None
with open("paper1.pdf", "rb") as pdf_file:
    encoded_string = base64.b64encode(pdf_file.read()).decode("utf-8")

text_bytes = None
with open("lore.txt", "rb") as txt_file:
    text_bytes = txt_file.read()

decoded_content = base64.b64decode(encoded_string)
processed_files = [
    {
        'name': 'paper1.pdf',
        'content': io.BytesIO(decoded_content),
        'extension': '.pdf'
    },
    {
        'name': 'lore.txt',
        'content': io.BytesIO(text_bytes),
        'extension': '.txt'
    }
]

@app.route('/generate/', methods=['GET'])
def generate():
    html = generate_knowledge_graph_html_sync(processed_files, user_api_key, user_base_url, user_model_name)
    with open("output.html", "w", encoding="utf-8") as f:
        f.write(html)
    return "done"


if __name__ == '__main__':
    app.run(debug=True)
