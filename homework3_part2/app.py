import os
import sqlite3
import pymongo
from flask import Flask, jsonify, render_template, request
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()


SQLITE_DB_PATH = os.path.join(os.getcwd(), 'db/applicants.db')

if not os.path.exists(os.path.dirname(SQLITE_DB_PATH)):
    os.makedirs(os.path.dirname(SQLITE_DB_PATH))

def init_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Dummy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_sqlite_db()

# MongoDB Connection 
client = pymongo.MongoClient(os.getenv("ATLAS_URI", "mongodb://localhost:27017/"))
db = client["acme_financial"]
applications = db["applications"]

#Routes 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/applications', methods=['GET'])
def get_all_applications():
    apps = list(applications.find({}, {'_id': 1, 'name': 1, 'address': 1, 'zipcode': 1, 'status': 1}))
    for app in apps:
        app['app_id'] = str(app['_id'])
        del app['_id']
    return jsonify({'applications': apps})

@app.route('/api/submit_application', methods=['POST'])
def submit_application():
    data = request.get_json()
    name = data.get('name')
    address = data.get('address')
    zipcode = data.get('zipcode')
    if not name or not address or not zipcode:
        return jsonify({'message': 'All fields are required'}), 400

    application = {
        'name': name,
        'address': address,
        'zipcode': zipcode,
        'status': 'received',
        'notes': [{'text': 'Application submitted', 'date': datetime.now()}],
        'created_at': datetime.now()
    }
    result = applications.insert_one(application)
    return jsonify({'message': f'Application submitted! Application ID: {result.inserted_id}'})

@app.route('/api/status/<app_id>', methods=['GET'])
def get_status(app_id):
    try:
        application = applications.find_one({'_id': ObjectId(app_id)}, {'_id': 1, 'name': 1, 'address': 1, 'zipcode': 1, 'status': 1})
        if application:
            application['app_id'] = str(application['_id'])
            del application['_id']
            return jsonify({'application': application})
        return jsonify({'message': 'Application not found'}), 404
    except:
        return jsonify({'message': 'Invalid Application ID'}), 400

@app.route('/api/change_status', methods=['POST'])
def change_status():
    data = request.get_json()
    app_id = data.get('app_id')
    new_status = data.get('status')
    note = data.get('note')
    valid_statuses = ['received', 'processing', 'accepted', 'rejected']
    if new_status not in valid_statuses:
        return jsonify({'message': 'Invalid status'}), 400
    try:
        result = applications.update_one(
            {'_id': ObjectId(app_id)},
            {
                '$set': {'status': new_status},
                '$push': {
                    'notes': {
                        'text': note or f'Status changed to {new_status}',
                        'date': datetime.now()
                    }
                }
            }
        )
        if result.modified_count:
            return jsonify({'message': 'Status updated successfully'})
        return jsonify({'message': 'Application not found'}), 404
    except:
        return jsonify({'message': 'Invalid Application ID'}), 400

@app.route('/api/notes/<app_id>', methods=['GET'])
def get_notes(app_id):
    try:
        application = applications.find_one({'_id': ObjectId(app_id)}, {'_id': 1, 'name': 1, 'notes': 1})
        if application:
            application['app_id'] = str(application['_id'])
            del application['_id']
            return jsonify({'application': application})
        return jsonify({'message': 'Application not found'}), 404
    except:
        return jsonify({'message': 'Invalid Application ID'}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
