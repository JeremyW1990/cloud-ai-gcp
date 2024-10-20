import sys
import os
from flask import Flask, request, jsonify
from google.cloud import firestore
from firebase_admin import initialize_app, auth
from google.auth.exceptions import DefaultCredentialsError
import uuid
import google.cloud.logging
from api.utils.vendor import create_agent_util
from api.utils.firestore import firestore_doc_set
# Setup Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

import logging


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
    logging.error("Error: Unable to initialize Firestore client. Check your credentials.")
    db = None

@app.before_request
def before_request():
    if db is None:
        return jsonify({"error": "Database connection not available"}), 500

# Log startup information
logging.info("Application starting")
logging.info(f"Python path: {sys.path}")
logging.info(f"Current working directory: {os.getcwd()}")

@app.route('/v1/user/<user_id>/agent', methods=['POST'])
def create_agent(user_id):
    logging.info(f"Creating agent for user_id: {user_id}")
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
        

        
        # Initialize the client and create the assistant using the strategy and client
        api_key = data.get('api_key')  # Assume API key is provided in the request
        client = strategy.initialize_client(api_key)
        vendor_agent_id, error = create_agent_util(client, {"name": data.get('name'), "instructions": data.get('instructions')}, strategy)
        if error:
            logging.error(f"Error creating agent: {error}")
            return jsonify({"error": f"Error creating agent: {error}"}), 400
        
        # Prepare agent data
        agent_data = {
            "user_id": user_id,
            "backend_user_id": backend_user_id,
            "vendor_agent_id": vendor_agent_id,
            "vendor": vendor,
            "name": data.get('name'),
            "instructions": data.get('instructions'),
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
        
        return jsonify({
            "agent_id": agent_id,
            "vendor_agent_id": vendor_agent_id,
            "status": agent_data["status"]
        }), 201
    except Exception as e:
        logging.error(f"An error occurred while creating agent: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>/agent/<agent_id>', methods=['GET'])
def get_agent(user_id, agent_id):
    logging.info(f"Attempting to get agent with agent_id: {agent_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Fetch the agent data
        agent_ref = db.collection('agents').document(agent_id)
        agent = agent_ref.get()
        
        if not agent.exists:
            logging.warning(f"Agent not found for agent_id: {agent_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        agent_data = agent.to_dict()
        
        # Check if the agent belongs to the user
        if agent_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Agent {agent_id} does not belong to user {user_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        # Return only the required fields
        return jsonify({
            "vendor": agent_data['vendor'],
            "name": agent_data['name'],
            "instructions": agent_data['instructions'],
            "vendor_agent_id": agent_data['vendor_agent_id'],
            "status": agent_data['status']
        }), 200
    except Exception as e:
        logging.error(f"An error occurred while getting agent: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>/agent/<agent_id>', methods=['PUT'])
def update_agent(user_id, agent_id):
    logging.info(f"Updating agent with agent_id: {agent_id} for user_id: {user_id}")
    try:
        data = request.get_json()
        
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Fetch the agent data
        agent_ref = db.collection('agents').document(agent_id)
        agent = agent_ref.get()
        
        if not agent.exists:
            logging.warning(f"Agent not found for agent_id: {agent_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        agent_data = agent.to_dict()
        
        # Check if the agent belongs to the user
        if agent_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Agent {agent_id} does not belong to user {user_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        # Update the agent data
        update_data = {
            "vendor": data.get('vendor', agent_data['vendor']),
            "name": data.get('name', agent_data['name']),
            "instructions": data.get('instructions', agent_data['instructions'])
        }
        
        # If vendor has changed, update vendor_agent_id
        if 'vendor' in data and data['vendor'] != agent_data['vendor']:
            # Use hardcoded vendor_agent_id
            update_data['vendor_agent_id'] = "mock_vendor_agent_id"
        
        # Use the utility function to update the agent data
        _, error = firestore_doc_set(db, 'agents', update_data, agent_id)
        if error:
            logging.error(f"Error updating agent in Firestore: {error}")
            return jsonify({"error": f"Error updating agent: {error}"}), 400
        
        # Update agent_id to vendor_agent_id mapping if vendor_agent_id has changed
        if 'vendor_agent_id' in update_data:
            _, error = firestore_doc_set(db, 'agent_id_mapping', {'vendor_agent_id': update_data['vendor_agent_id']}, agent_id)
            if error:
                logging.error(f"Error updating agent_id mapping in Firestore: {error}")
                return jsonify({"error": f"Error updating agent_id mapping: {error}"}), 400
        
        return jsonify({
            "message": "Agent updated successfully",
            "status": agent_data['status']
        }), 200
    except Exception as e:
        logging.error(f"An error occurred while updating agent: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/v1/user/<user_id>/agent/<agent_id>', methods=['DELETE'])
def delete_agent(user_id, agent_id):
    logging.info(f"Deleting agent with agent_id: {agent_id} for user_id: {user_id}")
    try:
        # Look up the Backend User ID
        mapping_ref = db.collection('user_id_mapping').document(user_id)
        mapping = mapping_ref.get()
        
        if not mapping.exists:
            logging.warning(f"User mapping not found for user_id: {user_id}")
            return jsonify({"error": "User not found"}), 404
        
        backend_user_id = mapping.to_dict()['backend_user_id']
        
        # Fetch the agent data
        agent_ref = db.collection('agents').document(agent_id)
        agent = agent_ref.get()
        
        if not agent.exists:
            logging.warning(f"Agent not found for agent_id: {agent_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        agent_data = agent.to_dict()
        
        # Check if the agent belongs to the user
        if agent_data['backend_user_id'] != backend_user_id:
            logging.warning(f"Agent {agent_id} does not belong to user {user_id}")
            return jsonify({"error": "Agent not found"}), 404
        
        # Delete the agent from the vendor (you may want to add actual vendor API call here)
        vendor_agent_id = "mock_vendor_agent_id"
        logging.info(f"Deleting vendor agent with vendor_agent_id: {vendor_agent_id}")
        
        # Delete the agent_id to vendor_agent_id mapping
        db.collection('agent_id_mapping').document(agent_id).delete()
        
        # Delete the agent from Firestore
        agent_ref.delete()
        
        return '', 204
    except Exception as e:
        logging.error(f"An error occurred while deleting agent: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port)
