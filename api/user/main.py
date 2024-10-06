from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import auth, initialize_app

# Initialize Firebase app
initialize_app()

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
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Check if the user already exists
        user = auth.get_user_by_email(email)
        return jsonify({"error": "User with this email already exists"}), 409
    except auth.UserNotFoundError:
        # Create a new user in Firebase Auth
        user = auth.create_user(
            email=email,
            password=password
        )

        # Store additional user data in Firestore
        user_ref = db.collection('users').document(user.uid)
        user_ref.set(data)

        return jsonify({"user_id": user.uid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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