from api.vendor.base_strategy import AIStrategy
from openai import OpenAI
import time
import contextlib
import io
import json
import re
import os

class OpenAIStrategy(AIStrategy):
    def __init__(self):
        # Removed self.client initialization
        pass

    def initialize_client(self, api_key):
        client = OpenAI(api_key=api_key)
        return client
    
    def init_context(self, client, context_json):
        try:
            # Load JSON data directly from the provided JSON object
            json_data = json.loads(context_json)
            
            # Extract context information (assuming it's a single object)
            context_info = json_data.get('context', {})
            
            # Extract agent information (assuming it's a list)
            agents_data = json_data.get('agents', [])
            agents_info = [{"name": agent['name'], "instructions": agent['instructions']} for agent in agents_data]
            
            # Initialize assistants
            created_assistants = self.init_assistants(client, agents_info)
            
            return created_assistants
        except Exception as e:
            print(f"Error initializing context: {str(e)}")
            return None, None

    def init_assistants(self, client, agents):
        created_assistants = []
        for agent in agents:
            assistant_info = self.init_assistant(client, agent["name"], agent["instructions"])
            if assistant_info:
                created_assistants.append(assistant_info)
        return created_assistants
    
    def init_assistant(self, client, name, instructions):
        try:
            assistant = client.beta.assistants.create(
                name=name,
                tools=[],
                instructions=instructions,
                model="gpt-4o-2024-05-13",
            )
            return {"name": name, f"{name.upper().replace(' ', '_')}_ID": assistant.id, "id": assistant.id}
        except Exception as e:
            print(f"Error creating assistant {name}: {str(e)}")
            return None

    def create_thread_with_context(self, client, context):
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=context
        )
        return thread

    def create_thread_and_run(self, client, assistant_id, user_input):
        thread = client.beta.threads.create()
        run = self.submit_message(client, assistant_id, thread, user_input)
        return thread, run

    def submit_message(self, client, assistant_id, thread, user_message):
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        response = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        return response

    def wait_on_run(self, client, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def get_response(self, client, thread):
        return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

    def get_latest_response(self, messages):
        messages_list = list(messages)
        if messages_list:
            last_message = messages_list[-1].content[0].text.value
            return last_message
        else:
            print("No messages found.")
            return "No messages found."

    def extract_next_agent(self, message):
        pattern = r'NEXT_AGENT\s*:\s*"([^"]+)"'
        matches = re.findall(pattern, message, re.IGNORECASE)
        return matches[-1].upper() if matches else None

    def extract_current_agent(self, message):
        valid_agents = ["COORDINATOR_AGENT", "CODE_AGENT", "CICD_AGENT"]
        for agent in valid_agents:
            if message.startswith(agent + ":"):
                return agent
        return "UNKNOWN_AGENT"

# Utility functions (you can keep these as they are or move them to a separate utility module)
def show_json(obj):
    print(json.loads(obj.model_dump_json()))

def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}:")
        print(f"{m.content[0].text.value}")
        print()


