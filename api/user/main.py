from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid
import logging
from api.utils.firestore import firestore_doc_set


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
        user_data = {
            **data,
            'backend_user_id': firebase_user.uid,
            'user_id': user_id
        }
        
        # Use the utility function to store the user data
        _, error = firestore_doc_set(db, 'users', user_data, firebase_user.uid)
        if error:
            logging.error(f"Error creating user in Firestore: {error}")
            return jsonify({"error": f"Error creating user: {error}"}), 500

        # Create a mapping document using the utility function
        _, error = firestore_doc_set(db, 'user_id_mapping', {'backend_user_id': firebase_user.uid}, user_id)
        if error:
            logging.error(f"Error creating user_id mapping in Firestore: {error}")
            return jsonify({"error": f"Error creating user_id mapping: {error}"}), 500

        return jsonify({"user_id": user_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v1/user/<user_id>', methods=['GET'])
def get_user(user_id):
    logging.info(f"Attempting to get user with user_id: {user_id}")
    try:
        # Look up the Backend User ID
        logging.info(f"Looking up Backend User ID for user_id: {user_id}")
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        logging.info(f"Found Backend User ID: {backend_user_id}")
        
        # Now fetch the user data using the Backend User ID
        logging.info(f"Fetching user data for Backend User ID: {backend_user_id}")
        user_ref = db.collection('users').document(backend_user_id)
        user = user_ref.get()
        if user.exists:
            logging.info(f"User data found for Backend User ID: {backend_user_id}")
            user_data = user.to_dict()
            # Remove sensitive information before sending
            user_data.pop('backend_user_id', None)
            logging.info("Returning user data")
            return jsonify(user_data), 200
        else:
            logging.warning(f"User data not found for Backend User ID: {backend_user_id}")
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        logging.error(f"An error occurred while getting user: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    logging.info(f"Updating user with user_id: {user_id}")
    
    data = request.get_json()
    logging.info(f"Received update data: {data}")
    
    # Look up the Backend User ID
    logging.info(f"Looking up Backend User ID for user_id: {user_id}")
    mapping_ref = db.collection('user_id_mapping').document(user_id)
    mapping = mapping_ref.get()
    
    if not mapping.exists:
        logging.warning(f"User mapping not found for user_id: {user_id}")
        return jsonify({"error": "User not found"}), 404
    
    backend_user_id = mapping.to_dict()['backend_user_id']
    logging.info(f"Found Backend User ID: {backend_user_id}")
    
    # Update the user document
    logging.info(f"Updating user document for Backend User ID: {backend_user_id}")
    
    try:
        # Use the utility function to update the user data
        _, error = firestore_doc_set(db, 'users', data, backend_user_id)
        if error:
            logging.error(f"Error updating user in Firestore: {error}")
            return jsonify({"error": f"Failed to update user: {error}"}), 500
        
        logging.info(f"User document updated successfully")
    except Exception as e:
        logging.error(f"Error updating user document: {str(e)}")
        return jsonify({"error": f"Failed to update user: {str(e)}"}), 500
    
    logging.info(f"User update completed successfully")
    return jsonify({"message": "User updated"}), 200

@app.route('/v1/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Look up the Backend User ID
    mapping_ref = db.collection('user_id_mapping').document(user_id)
    mapping = mapping_ref.get()
    
    if not mapping.exists:
        return jsonify({"error": "User not found"}), 404
    
    backend_user_id = mapping.to_dict()['backend_user_id']
    
    # Delete the user document
    user_ref = db.collection('users').document(backend_user_id)
    user_ref.delete()
    
    # Delete the mapping document
    mapping_ref.delete()
    
    # Delete the user from Firebase Auth
    auth.delete_user(backend_user_id)
    
    return jsonify({"message": "User deleted"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
