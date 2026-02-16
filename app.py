from flask import Flask, request, jsonify
import os

WRITE_KEY = os.environ.get('WRITE_KEY')
READ_KEY = os.environ.get('READ_KEY')

app = Flask(__name__)

# A simple list to store data in memory (clears if you restart the script)
data_store = []

@app.route('/')
def hello_world():
    return 'This is web server / api for the ESP32 data'

# Route to receive POST requests from the ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    # Get the key sent by the ESP32 from the request headers
    provided_key = request.headers.get('WRITE_KEY')
    
    if provided_key != WRITE_KEY:
        return {"error": "Unauthorized"}, 401
    
    content = request.get_json(silent=True)
    if content:
        data_store.append(content) # Save the data
        print(f"New data added: {content}")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No JSON"}), 400

# VIEW data in your browser (GET)
@app.route('/data', methods=['GET'])
def show_data():
    # Looks for 'X-API-Key' in the request headers
    # provided_key = request.headers.get('READ_KEY')
    
    # if provided_key != READ_KEY:
    #     return {"error": "Unauthorized Read"}, 401
        
    # This returns everything we've collected so far
    return jsonify({
        "count": len(data_store),
        "history": data_store
    })

if __name__ == '__main__':
    # '0.0.0.0' allows external devices on your network to connect
    app.run(host='0.0.0.0', port=8080, debug=True)