from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid
import logging
from api.utils.firestore import firestore_doc_set
from api.vendor.vendor_strategy import get_strategy

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

@app.route('/v1/user/<user_id>/thread', methods=['POST'])
def create_thread(user_id):
    logging.info(f"Creating thread for user_id: {user_id}")
    try:
        data = request.get_json()
        vendor = data.get('vendor')
        
        # Get the appropriate strategy based on the vendor
        strategy = get_strategy(vendor)
        
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Generate a frontend thread_id
        thread_id = str(uuid.uuid4())
        
        # Initialize the client and create the thread using the strategy
        api_key = data.get('api_key')  # Assume API key is provided in the request
        client = strategy.initialize_client(api_key)
        backend_thread = strategy.create_thread_with_context(client, data.get('context'))
        logging.info(f"Backend thread created: {backend_thread}")
        # Prepare thread data
        thread_data = {
            "thread_id": thread_id,
            "user_id": user_id,
            "backend_user_id": backend_user_id,
            "vendor_thread_id": backend_thread.id,
            "vendor": vendor,
            "context_id": data.get('context_id')
        }
        
        # Use the utility function to store the thread data
        backend_thread_id, error = firestore_doc_set(db, 'threads', thread_data)
        if error:
            logging.error(f"Error creating thread in Firestore: {error}")
            return jsonify({"error": f"Error creating thread: {error}"}), 400
        
        # Create thread_id to backend_thread_id mapping
        _, error = firestore_doc_set(db, 'thread_id_mapping', {'backend_thread_id': backend_thread_id}, thread_id)
        if error:
            logging.error(f"Error creating thread_id mapping in Firestore: {error}")
            return jsonify({"error": f"Error creating thread_id mapping: {error}"}), 400
        
        return jsonify({"thread_id": thread_id, "backend_thread_id": backend_thread_id}), 201
    except Exception as e:
        logging.error(f"An error occurred while creating thread: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

@app.route('/v1/user/<user_id>/thread/<thread_id>', methods=['GET'])
def get_thread(user_id, thread_id):
    logging.info(f"Retrieving thread with thread_id: {thread_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Thread ID
        thread_mapping_ref = db.collection('thread_id_mapping').document(thread_id)
        thread_mapping = thread_mapping_ref.get()
        
        if not thread_mapping.exists:
            logging.warning(f"Thread mapping not found for thread_id: {thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        backend_thread_id = thread_mapping.to_dict()['backend_thread_id']
        
        # Fetch the thread data
        thread_ref = db.collection('threads').document(backend_thread_id)
        thread = thread_ref.get()
        
        if not thread.exists:
            logging.warning(f"Thread not found for backend_thread_id: {backend_thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        thread_data = thread.to_dict()
        
        # Check if the thread belongs to the user
        if thread_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Thread {thread_id} does not belong to user {user_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        # Return only the required fields
        return jsonify({
            "thread_id": thread_data['thread_id'],
            "context_id": thread_data['context_id'],
            "vendor": thread_data['vendor']
        }), 200
    except Exception as e:
        logging.error(f"An error occurred while getting thread: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>/thread/<thread_id>', methods=['PUT'])
def update_thread(user_id, thread_id):
    logging.info(f"Updating thread with thread_id: {thread_id} for user_id: {user_id}")
    try:
        data = request.get_json()
        
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Thread ID
        thread_mapping_ref = db.collection('thread_id_mapping').document(thread_id)
        thread_mapping = thread_mapping_ref.get()
        
        if not thread_mapping.exists:
            logging.warning(f"Thread mapping not found for thread_id: {thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        backend_thread_id = thread_mapping.to_dict()['backend_thread_id']
        
        # Fetch the thread data
        thread_ref = db.collection('threads').document(backend_thread_id)
        thread = thread_ref.get()
        
        if not thread.exists:
            logging.warning(f"Thread not found for backend_thread_id: {backend_thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        thread_data = thread.to_dict()
        
        # Check if the thread belongs to the user
        if thread_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Thread {thread_id} does not belong to user {user_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        # Update the thread data
        update_data = {
            "context_id": data.get('context_id', thread_data['context_id'])
        }
        
        # Use the utility function to update the thread data
        _, error = firestore_doc_set(db, 'threads', update_data, backend_thread_id)
        if error:
            logging.error(f"Error updating thread in Firestore: {error}")
            return jsonify({"error": f"Failed to update thread: {error}"}), 500
        
        return jsonify({"message": "Thread updated successfully"}), 200
    except Exception as e:
        logging.error(f"An error occurred while updating thread: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

@app.route('/v1/user/<user_id>/thread/<thread_id>', methods=['DELETE'])
def delete_thread(user_id, thread_id):
    logging.info(f"Deleting thread with thread_id: {thread_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        
        # Look up the Backend Thread ID
        thread_mapping_ref = db.collection('thread_id_mapping').document(thread_id)
        thread_mapping = thread_mapping_ref.get()
        
        if not thread_mapping.exists:
            logging.warning(f"Thread mapping not found for thread_id: {thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        backend_thread_id = thread_mapping.to_dict()['backend_thread_id']
        
        # Fetch the thread data
        thread_ref = db.collection('threads').document(backend_thread_id)
        thread = thread_ref.get()
        
        if not thread.exists:
            logging.warning(f"Thread not found for backend_thread_id: {backend_thread_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        thread_data = thread.to_dict()
        
        # Check if the thread belongs to the user
        if thread_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Thread {thread_id} does not belong to user {user_id}")
            return jsonify({"error": "Thread not found"}), 404
        
        # Delete the thread from Firestore
        thread_ref.delete()
        
        # Delete the thread_id to backend_thread_id mapping
        thread_mapping_ref.delete()
        
        return jsonify({"message": "Thread deleted successfully"}), 200
    except Exception as e:
        logging.error(f"An error occurred while deleting thread: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)