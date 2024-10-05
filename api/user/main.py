from flask import Flask, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)
db = firestore.Client(
    project=os.environ.get('PROJECT_ID'),
    database=os.environ.get('FIRESTORE_ID')
) 


@app.route('/v1/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if user.exists:
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/v1/user', methods=['POST'])
def create_user():
    data = request.get_json()
    user_ref = db.collection('users').document()
    user_ref.set(data)
    return jsonify({"user_id": user_ref.id}), 201

@app.route('/v1/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user_ref = db.collection('users').document(user_id)
    user_ref.update(data)
    return jsonify({"message": "User updated"}), 200

@app.route('/v1/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user_ref = db.collection('users').document(user_id)
    user_ref.delete()
    return jsonify({"message": "User deleted"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)