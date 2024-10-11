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

@app.route('/v1/user/<user_id>/context/<context_id>', methods=['GET'])
def get_context(user_id, context_id):
    logging.info(f"Retrieving context with context_id: {context_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Context ID
        context_mapping_ref = db.collection('context_id_mapping').document(context_id)
        context_mapping = context_mapping_ref.get()
        
        if not context_mapping.exists:
            logging.warning(f"Context mapping not found for context_id: {context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        backend_context_id = context_mapping.to_dict()['backend_context_id']
        
        # Fetch the context data
        context_ref = db.collection('contexts').document(backend_context_id)
        context = context_ref.get()
        
        if not context.exists:
            logging.warning(f"Context not found for backend_context_id: {backend_context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        context_data = context.to_dict()
        
        # Check if the context belongs to the user
        if context_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Context {context_id} does not belong to user {user_id}")
            return jsonify({"error": "Context not found"}), 404
        
        # Return only the required fields
        return jsonify({
            "context_id": context_data['context_id'],
            "scenario": context_data['scenario'],
            "agents": context_data['agents']
        }), 200
    except Exception as e:
        logging.error(f"An error occurred while getting context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>/context', methods=['POST'])
def create_context(user_id):
    logging.info(f"Creating context for user_id: {user_id}")
    try:
        data = request.get_json()
        
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Generate a new context_id using Firestore's auto-generated ID
        context_ref = db.collection('contexts').document()
        backend_context_id = context_ref.id
        
        # Generate a frontend context_id
        context_id = str(uuid.uuid4())
        
        # Prepare context data
        context_data = {
            "context_id": context_id,
            "user_id": user_id,
            "backend_user_id": backend_user_id,
            "scenario": data.get('scenario'),
            "agents": data.get('agents', [])
        }
        
        # Store the context data
        context_ref.set(context_data)
        
        # Create context_id to backend_context_id mapping
        db.collection('context_id_mapping').document(context_id).set({
            'backend_context_id': backend_context_id
        })
        
        return jsonify({"context_id": context_id}), 201
    except Exception as e:
        logging.error(f"An error occurred while creating context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

@app.route('/v1/user/<user_id>/context/<context_id>', methods=['PUT'])
def update_context(user_id, context_id):
    logging.info(f"Updating context with context_id: {context_id} for user_id: {user_id}")
    try:
        data = request.get_json()
        
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Context ID
        context_mapping_ref = db.collection('context_id_mapping').document(context_id)
        context_mapping = context_mapping_ref.get()
        
        if not context_mapping.exists:
            logging.warning(f"Context mapping not found for context_id: {context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        backend_context_id = context_mapping.to_dict()['backend_context_id']
        
        # Fetch the context data
        context_ref = db.collection('contexts').document(backend_context_id)
        context = context_ref.get()
        
        if not context.exists:
            logging.warning(f"Context not found for backend_context_id: {backend_context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        context_data = context.to_dict()
        
        # Check if the context belongs to the user
        if context_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Context {context_id} does not belong to user {user_id}")
            return jsonify({"error": "Context not found"}), 404
        
        # Update the context data
        update_data = {
            "scenario": data.get('scenario', context_data['scenario']),
            "agents": data.get('agents', context_data['agents'])
        }
        
        context_ref.update(update_data)
        
        return jsonify({"message": "Context updated successfully"}), 200
    except Exception as e:
        logging.error(f"An error occurred while updating context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

@app.route('/v1/user/<user_id>/context/<context_id>', methods=['DELETE'])
def delete_context(user_id, context_id):
    logging.info(f"Deleting context with context_id: {context_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Context ID
        context_mapping_ref = db.collection('context_id_mapping').document(context_id)
        context_mapping = context_mapping_ref.get()
        
        if not context_mapping.exists:
            logging.warning(f"Context mapping not found for context_id: {context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        backend_context_id = context_mapping.to_dict()['backend_context_id']
        
        # Fetch the context data
        context_ref = db.collection('contexts').document(backend_context_id)
        context = context_ref.get()
        
        if not context.exists:
            logging.warning(f"Context not found for backend_context_id: {backend_context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        context_data = context.to_dict()
        
        # Check if the context belongs to the user
        if context_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Context {context_id} does not belong to user {user_id}")
            return jsonify({"error": "Context not found"}), 404
        
        # Delete the context from Firestore
        context_ref.delete()
        
        # Delete the context_id to backend_context_id mapping
        context_mapping_ref.delete()
        
        return '', 204
    except Exception as e:
        logging.error(f"An error occurred while deleting context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)