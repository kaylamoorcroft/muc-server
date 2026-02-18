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
    # Check if have correct write key
    auth_header = request.headers.get('Authorization')
    provided_key = None
    
    if auth_header and auth_header.startswith("Bearer "):
        provided_key = auth_header.split(" ")[1]
    
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
    # provided_key = request.headers.get('X-API-Key')
    
    # if provided_key != READ_KEY:
    #     return {"error": "Unauthorized Read"}, 401
        
    # This returns everything we've collected so far
    return jsonify({
        "count": len(data_store),
        "history": data_store
    })

if __name__ == '__main__':
    # '0.0.0.0' allows external devices on your network to connect
    # Use the PORT environment variable if it exists, otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=TRUE)
