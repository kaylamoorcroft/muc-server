from flask import Flask, request, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import datetime

WRITE_KEY = os.environ.get('WRITE_KEY')
READ_KEY = os.environ.get('READ_KEY')
URI = os.environ.get("DATABASE_URL") 

app = Flask(__name__)
CORS(app)  # enables CORS for all routes 
if URI:
    try:
        # Fix Render's 'postgres://' prefix to 'postgresql://'
        if URI.startswith("postgres://"):
            URI = URI.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = URI
        print("Using postgres database")
    except:
        # Fallback to local SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
        print("Using local SQLite database")
else:
    # Fallback to local SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    print("Using local SQLite database")

db = SQLAlchemy(app)

# model that represents Data table in db
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

# helper function    
def tupleToDict(tuple, field):
    return {'time': tuple[0], field: tuple[1]}

with app.app_context():
    db.create_all()

# -- ROUTES --

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
        
        # make sure to still send time if time cannot be retrieved on esp32
        if new_entry.time == "0000-00-00T00:00:00":
            new_entry.time = str(datetime.datetime.now())
            print("time created by server:", new_entry.time)
            
        db.session.add(new_entry)
        db.session.commit()
        print(f"New data added: {content}")
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No JSON"}), 400

# View data in browser (GET)
@app.route('/data', methods=['GET'])
def show_data():
    # Fetch all records from the Data table
    all_records = Data.query.all()
    for record in all_records:
        print(record.to_dict()) 
    # Convert each object into a dictionary
    return jsonify([record.to_dict() for record in all_records])

# Only retrieve the most recent record
@app.route('/data/latest', methods=['GET'])
def get_latest():
    record = Data.query.order_by(Data.id.desc()).first()
    
    if record:
        return jsonify(record.to_dict())
    
    return jsonify({"message": "No data found"}), 404

# View data in browser by field
@app.route('/data/<field>', methods=['GET'])
def getFieldData(field):
    if not field: # show all data for blank field
        return show_data()
    startDate = request.args.get('startDate', None)
    if startDate:
        startDate = startDate.replace(" ", "T")  # Convert to ISO format if needed
        results = db.session.query(Data.time, getattr(Data, field)).filter(Data.time > startDate).all()
    else:
        results = db.session.query(Data.time, getattr(Data, field)).all()
    for record in results:
        print(tupleToDict(record, field)) 
    # Convert each object into a dictionary
    return jsonify([tupleToDict(record, field) for record in results])

if __name__ == '__main__':
    db.create_all()
    # '0.0.0.0' allows external devices on network to connect
    # Use the PORT environment variable if it exists, otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
