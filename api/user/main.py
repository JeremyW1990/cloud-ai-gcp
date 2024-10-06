from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid

app = Flask(__name__)

# Initialize Firebase app
try:
    initialize_app()
except ValueError:
    # Firebase app already initialized
    pass

# Create a global Firestore client
try:
    db = firestore.Client(
        project=os.environ.get('PROJECT_ID'),
        database=os.environ.get('FIRESTORE_ID')
    )
except DefaultCredentialsError:
    print("Error: Unable to initialize Firestore client. Check your credentials.")
    db = None

@app.before_request
def before_request():
    if db is None:
        return jsonify({"error": "Database connection not available"}), 500

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
        firebase_user = auth.create_user(
            email=email,
            password=password
        )

        # Generate a custom user_id for frontend use
        custom_user_id = str(uuid.uuid4())

        # Store additional user data in Firestore
        user_ref = db.collection('users').document(firebase_user.uid)
        user_data = {
            **data,
            'custom_user_id': custom_user_id,
            'firebase_uid': firebase_user.uid
        }
        user_ref.set(user_data)

        # Create a mapping document
        db.collection('user_id_mapping').document(custom_user_id).set({
            'firebase_uid': firebase_user.uid
        })

        return jsonify({"user_id": custom_user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/user/<custom_user_id>', methods=['GET'])
def get_user(custom_user_id):
    try:
        # Look up the Firebase UID
        mapping_ref = db.collection('user_id_mapping').document(custom_user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            return jsonify({"error": "User not found"}), 404
        
        firebase_uid = mapping.to_dict()['firebase_uid']
        
        # Now fetch the user data using the Firebase UID
        user_ref = db.collection('users').document(firebase_uid)
        user = user_ref.get()
        if user.exists:
            user_data = user.to_dict()
            # Remove sensitive information before sending
            user_data.pop('firebase_uid', None)
            return jsonify(user_data), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<custom_user_id>', methods=['PUT'])
def update_user(custom_user_id):
    data = request.get_json()
    
    # Look up the Firebase UID
    mapping_ref = db.collection('user_id_mapping').document(custom_user_id)
    mapping = mapping_ref.get()
    
    if not mapping.exists:
        return jsonify({"error": "User not found"}), 404
    
    firebase_uid = mapping.to_dict()['firebase_uid']
    
    # Update the user document
    user_ref = db.collection('users').document(firebase_uid)
    user_ref.update(data)
    
    return jsonify({"message": "User updated"}), 200

@app.route('/v1/user/<custom_user_id>', methods=['DELETE'])
def delete_user(custom_user_id):
    # Look up the Firebase UID
    mapping_ref = db.collection('user_id_mapping').document(custom_user_id)
    mapping = mapping_ref.get()
    
    if not mapping.exists:
        return jsonify({"error": "User not found"}), 404
    
    firebase_uid = mapping.to_dict()['firebase_uid']
    
    # Delete the user document
    user_ref = db.collection('users').document(firebase_uid)
    user_ref.delete()
    
    # Delete the mapping document
    mapping_ref.delete()
    
    # Delete the user from Firebase Auth
    auth.delete_user(firebase_uid)
    
    return jsonify({"message": "User deleted"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)