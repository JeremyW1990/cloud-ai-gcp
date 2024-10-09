from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid
import logging


logging.basicConfig(level=logging.INFO)

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

        # Generate a frontend user_id for frontend use
        user_id = str(uuid.uuid4())

        # Store additional user data in Firestore
        user_ref = db.collection('users').document(firebase_user.uid)
        user_data = {
            **data,
            'user_id': user_id,
            'firebase_uid': firebase_user.uid
        }
        user_ref.set(user_data)

        # Create a mapping document
        db.collection('user_id_mapping').document(user_id).set({
            'firebase_uid': firebase_user.uid
        })

        return jsonify({"user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/user/<user_id>', methods=['GET'])
def get_user(user_id):
    logging.info(f"Attempting to get user with user_id: {user_id}")
    try:
        # Look up the Firebase UID
        logging.info(f"Looking up Firebase UID for user_id: {user_id}")
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        firebase_uid = mapping.to_dict()['firebase_uid']
        logging.info(f"Found Firebase UID: {firebase_uid}")
        
        # Now fetch the user data using the Firebase UID
        logging.info(f"Fetching user data for Firebase UID: {firebase_uid}")
        user_ref = db.collection('users').document(firebase_uid)
        user = user_ref.get()
        if user.exists:
            logging.info(f"User data found for Firebase UID: {firebase_uid}")
            user_data = user.to_dict()
            # Remove sensitive information before sending
            user_data.pop('firebase_uid', None)
            logging.info("Returning user data")
            return jsonify(user_data), 200
        else:
            logging.warning(f"User data not found for Firebase UID: {firebase_uid}")
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logging.error(f"An error occurred while getting user: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

@app.route('/v1/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    logging.info(f"Updating user with user_id: {user_id}")
    
    data = request.get_json()
    logging.info(f"Received update data: {data}")
    
    # Look up the Firebase UID
    logging.info(f"Looking up Firebase UID for user_id: {user_id}")
    mapping_ref = db.collection('user_id_mapping').document(user_id)
    mapping = mapping_ref.get()
    
    if not mapping.exists:
        logging.warning(f"User mapping not found for user_id: {user_id}")
        return jsonify({"error": "User not found"}), 404
    
    firebase_uid = mapping.to_dict()['firebase_uid']
    logging.info(f"Found Firebase UID: {firebase_uid}")
    
    # Update the user document
    logging.info(f"Updating user document for Firebase UID: {firebase_uid}")
    user_ref = db.collection('users').document(firebase_uid)
    
    try:
        user_ref.update(data)
        logging.info(f"User document updated successfully")
    except Exception as e:
        logging.error(f"Error updating user document: {str(e)}")
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500
    
    logging.info(f"User update completed successfully")
    return jsonify({"message": "User updated"}), 200

@app.route('/v1/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Look up the Firebase UID
    mapping_ref = db.collection('user_id_mapping').document(user_id)
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