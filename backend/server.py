from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/howdyworld/', methods=['GET'])
def Howdy_World():
    
    return jsonify({"message": "Howdy World!"})



if __name__ == '__main__':
    app.run(debug=True)