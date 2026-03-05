from flask import Flask, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

WRITE_KEY = os.environ.get('WRITE_KEY')
READ_KEY = os.environ.get('READ_KEY')
URI = os.environ.get("DATABASE_URL") 

app = Flask(__name__)
CORS(app)  # enables CORS for all routes 
# Fallback to local SQLite for development
if URI:
    # Fix Render's 'postgres://' prefix to 'postgresql://'
    if URI.startswith("postgres://"):
        URI = URI.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = URI
    print("Using postgres database")
else:
    # ONLY used for local testing on your own computer
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    print("Using local SQLite database")

db = SQLAlchemy(app)

class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    humidity = db.Column(db.Integer)
    light = db.Column(db.Integer)
    moisture = db.Column(db.Integer)
    temperature = db.Column(db.Double)
    time = db.Column(db.String, unique=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f'<Data {self.time}>'

with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    return 'This is web server / api for the ESP32 data'

# Route to receive POST requests from the ESP32
@app.route('/data', methods=['POST'])
def receive_data():
    auth_header = request.headers.get('Authorization')
    provided_key = None
    
    if auth_header and auth_header.startswith("Bearer "):
        provided_key = auth_header.split(" ")[1]
    
    if provided_key != WRITE_KEY:
        return {"error": "Unauthorized"}, 401
    
    content = request.get_json(silent=True)
    if content:
        # This unpacks the dictionary keys directly into the model's arguments
        new_entry = Data(**content) 
        
        db.session.add(new_entry)
        db.session.commit()
        print(f"New data added: {content}")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No JSON"}), 400

# VIEW data in your browser (GET)
@app.route('/data', methods=['GET'])
def show_data():
    # Fetch all records from the Data table
    all_records = Data.query.all()
    for record in all_records:
        print(record.to_dict())  # This will call the __repr__ method of the Data class
    # Convert each object into a dictionary
    return jsonify([record.to_dict() for record in all_records])

@app.route('/data/latest', methods=['GET'])
def get_latest():
    record = Data.query.order_by(Data.id.desc()).first()
    
    if record:
        return jsonify(record.to_dict())
    
    return jsonify({"message": "No data found"}), 404

if __name__ == '__main__':
    db.create_all()
    # '0.0.0.0' allows external devices on your network to connect
    # Use the PORT environment variable if it exists, otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
