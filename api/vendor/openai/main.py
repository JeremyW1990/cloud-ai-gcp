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
        self.client = None

    def initialize_client(self, api_key):
        self.client = OpenAI(api_key=api_key)
        return self.client
    
    # def init_context(self, context):
    #     try:
    #         with open(context, 'r') as file:
    #             yaml_data = yaml.safe_load(file)
            
    #         context_data = yaml_data.get('Context', [])
    #         agents_data = yaml_data.get('Agents', [])
            
    #         # Extract context information
    #         context_info = [{"name": item['name'], "instructions": item['instructions']} for item in context_data]
            
    #         # Extract agent information
    #         agents_info = [{"name": agent['name'], "instructions": agent['instructions']} for agent in agents_data]
            
    #         # Initialize assistants
    #         created_assistants = self.init_assistants(agents_info)
            
    #         return context_info, created_assistants
    #     except Exception as e:
    #         print(f"Error initializing context: {str(e)}")
    #         return None, None

    def init_assistants(self, agents):
        created_assistants = []
        for agent in agents:
            assistant_info = self.init_assistant(agent["name"], agent["instructions"])
            if assistant_info:
                created_assistants.append(assistant_info)
        return created_assistants
    
    def init_assistant(self, name, instruction):
        try:
            assistant = self.client.beta.assistants.create(
                name=name,
                tools=[],
                instructions=instruction,
                model="gpt-4o-2024-05-13",
            )
            return {"name": name, f"{name.upper().replace(' ', '_')}_ID": assistant.id, "id": assistant.id}
        except Exception as e:
            print(f"Error creating assistant {name}: {str(e)}")
            return None

    def create_thread_with_context(self, context):
        thread = self.client.beta.threads.create()
        self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=context
        )
        return thread

    def create_thread_and_run(self, assistant_id, user_input):
        thread = self.client.beta.threads.create()
        run = self.submit_message(assistant_id, thread, user_input)
        return thread, run

    def submit_message(self, assistant_id, thread, user_message):
        self.client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=user_message
        )
        response = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )
        return response

    def wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def get_response(self, thread):
        return self.client.beta.threads.messages.list(thread_id=thread.id, order="asc")

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

def printout_chat_history(response):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        pretty_print(response)
    out = f.getvalue()

    with open("chat_history.md", "w") as file:
        file.write(out)

