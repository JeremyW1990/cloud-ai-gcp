from flask import Flask, request, jsonify
from google.cloud import firestore
import os
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid
import logging
from api.vendor.vendor_strategy import get_strategy
from api.utils.vendor import create_agent_util
from api.utils.firestore import firestore_doc_set
from api.utils.bucket import upload_content_to_bucket
from api.utils.context import json_to_final_yaml_context
import json

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
    
@app.route('/v1/user/<user_id>/context', methods=['POST'])
def create_context(user_id):
    logging.info(f"Creating context for user_id: {user_id}")
    try:
        data = request.get_json()
        vendor = data.get('vendor')
        logging.info(f"data: {data}")
        # Get the appropriate strategy based on the vendor
        strategy = get_strategy(vendor)
        
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Generate a frontend context_id
        context_id = str(uuid.uuid4())
        
        # Initialize the client and create the context using the strategy
        api_key = data.get('api_key')  # Assume API key is provided in the request
        client = strategy.initialize_client(api_key)

        vendor_agent_ids = []
        agent_ids = []
        for agent in data.get('agents'):
            logging.info(f"Processing agent: {agent}")
            vendor_agent_id, error = create_agent_util(client, agent, strategy)


            agent_data = {
                "user_id": user_id,
                "backend_user_id": backend_user_id,
                "vendor_agent_id": vendor_agent_id,
                "vendor": vendor,
                "name": agent.get('name'),
                "instructions": agent.get('instructions'),
                "status": "active"
            }
            
            # Use the utility function to store the agent data
            agent_id, error = firestore_doc_set(db, 'agents', agent_data)
            if error:
                logging.error(f"Error creating agent in Firestore: {error}")
                return jsonify({"error": f"Error creating agent: {error}"}), 400
            
            # Create agent_id to vendor_agent_id mapping using the same utility function
            _, error = firestore_doc_set(db, 'agent_id_mapping', {'vendor_agent_id': vendor_agent_id}, agent_id)
            if error:
                logging.error(f"Error creating agent_id mapping in Firestore: {error}")
                return jsonify({"error": f"Error creating agent_id mapping: {error}"}), 400
            logging.info(f"Successfully created agent with vendor ID: {vendor_agent_id}")
            vendor_agent_ids.append(vendor_agent_id)
            agent_ids.append(agent_id)



        context_data = {
            "context_id": context_id,
            "user_id": user_id,
            "backend_user_id": backend_user_id,
            "instructions": data.get('context').get('instructions'),
            "vendor_agent_ids": vendor_agent_ids,
            "agent_ids": agent_ids
        }
        
        # Use the utility function to store the context data
        backend_context_id, error = firestore_doc_set(db, 'contexts', context_data, merge=False)

        if error:
            logging.error(f"Error creating context in Firestore: {error}")
            return jsonify({"error": f"Error creating context: {error}"}), 400
        
        # Create context_id to backend_context_id mapping
        _, error = firestore_doc_set(db, 'context_id_mapping', {'backend_context_id': backend_context_id}, context_id, merge=False)
        if error:
            logging.error(f"Error creating context_id mapping in Firestore: {error}")
            return jsonify({"error": f"Error creating context_id mapping: {error}"}), 400

        # Prepare context data
        yaml_context = json_to_final_yaml_context(data)
        
        upload_content_to_bucket(os.environ.get('BUCKET_NAME'), f'{backend_user_id}/{backend_context_id}/context.yaml', yaml_context)

        
        return jsonify({"context_id": context_id, "backend_context_id": backend_context_id}), 201
    except Exception as e:
        logging.error(f"An error occurred while creating context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400


@app.route('/v1/user/<user_id>/context/<context_id>', methods=['GET'])
def get_context(user_id, context_id):
    logging.info(f"Retrieving context with context_id: {context_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        logging.info(f"Looking up Backend User ID for user_id: {user_id}")
        user_mapping_ref = db.collection('user_id_mapping').document(user_id)
        user_mapping = user_mapping_ref.get()
        
        if not user_mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = user_mapping.to_dict()['backend_user_id']
        logging.info(f"Found backend_user_id: {backend_user_id} for user_id: {user_id}")
        
        # Look up the Backend Context ID
        logging.info(f"Looking up Backend Context ID for context_id: {context_id}")
        context_mapping_ref = db.collection('context_id_mapping').document(context_id)
        context_mapping = context_mapping_ref.get()
        
        if not context_mapping.exists:
            logging.warning(f"Context mapping not found for context_id: {context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        backend_context_id = context_mapping.to_dict()['backend_context_id']
        logging.info(f"Found backend_context_id: {backend_context_id} for context_id: {context_id}")
        
        # Fetch the context data
        logging.info(f"Fetching context data for backend_context_id: {backend_context_id}")
        context_ref = db.collection('contexts').document(backend_context_id)
        context = context_ref.get()
        
        if not context.exists:
            logging.warning(f"Context not found for backend_context_id: {backend_context_id}")
            return jsonify({"error": "Context not found"}), 404
        
        context_data = context.to_dict()
        logging.info(f"Fetched context data: {context_data}")
        
        # Check if the context belongs to the user
        if context_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Context {context_id} does not belong to user {user_id}")
            return jsonify({"error": "Context not found"}), 404
        
        # Return only the required fields
        logging.info(f"Returning context data for context_id: {context_id}")
        return jsonify({
            "context_id": context_data['context_id'],
            "instructions": context_data['instructions'],
            "agent_ids": context_data['agent_ids']
        }), 200
    except Exception as e:
        logging.error(f"An error occurred while getting context: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


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
            **data,
        }
        
        # Use the utility function to update the context data
        _, error = firestore_doc_set(db, 'contexts', update_data, backend_context_id, merge=True)
        if error:
            logging.error(f"Error updating context in Firestore: {error}")
            return jsonify({"error": f"Failed to update context: {error}"}), 500
        
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
