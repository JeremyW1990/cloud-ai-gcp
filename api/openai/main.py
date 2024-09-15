from flask import Flask, request, jsonify
from pydantic import BaseModel
import os
import yaml
from openai_api import create_thread_with_context, init_assistants, initialize_openai_client

app = Flask(__name__)

class ContextRequest(BaseModel):
    user_id: str
    context: str
    OPENAI_API_KEY: str

@app.route("/context", methods=["POST"])
def create_context():
    try:
        # Extract variables from request JSON
        data = request.json
        user_id = data['user_id']
        context = data['context']
        api_key = data['OPENAI_API_KEY']

        client = initialize_openai_client(api_key)

        # Update the YAML file path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(current_dir, "agents.yaml")
        
        with open(yaml_path, 'r') as file:
            agents_data = yaml.safe_load(file)

        # Ensure agents_data is a dictionary and access the list correctly
        agents = agents_data.get('Agents', [])

        # Prepare agents data
        agents_list = [{"name": agent['name'], "instructions": agent['instructions']} for agent in agents]

        # Call init_assistants function with necessary parameters
        created_assistants = init_assistants(client, agents_list)
        thread = create_thread_with_context(client, context)
        thread_id = thread.id

        return jsonify({
            "message": f"Context created for user_id: {user_id}",
            "assistants": created_assistants,
            "thread_id": thread_id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)