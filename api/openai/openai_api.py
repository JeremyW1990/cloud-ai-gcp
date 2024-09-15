import contextlib
import io
import json
import yaml
import re
import time
import os

from openai import OpenAI

def initialize_openai_client(api_key):
    client = OpenAI(api_key=api_key)
    return client


def init_assistants(client, agents):

    created_assistants = []

    for agent in agents:
        name = agent["name"]
        instruction = agent["instructions"]
        
        try:
            # Create assistant
            assistant = client.beta.assistants.create(
                name=name,
                tools=[],
                instructions=instruction,
                model="gpt-4o-2024-05-13",
            )
            
            created_assistants.append({"name": name, f"{name.upper().replace(' ', '_')}_ID": assistant.id})
        except Exception as e:
            print(f"Error creating assistant {name}: {str(e)}")

    return created_assistants


def show_json(obj):
    print(json.loads(obj.model_dump_json()))


def create_thread_with_context(client, context):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=context
    )
    return thread


def create_thread_and_run(client, assistant_id, user_input):
    thread = client.beta.threads.create()
    run = submit_message(assistant_id, thread, user_input)
    return thread, run


def submit_message(client, assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    response = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    return response


# Waiting in a loop
def wait_on_run(client, run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    # print(run)
    return run


def get_response(client, thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}:")
        print(f"{m.content[0].text.value}")
        print()


def get_latest_response(messages):
    messages_list = list(messages)
    # Now you can safely access the last message if the list is not empty
    if messages_list:
        last_message = messages_list[-1].content[0].text.value
        return last_message
    else:
        print("No messages found.")
        return "No messages found."


def printout_chat_history(response):
    # Assuming pretty_print prints the response to stdout
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        pretty_print(response)
    out = f.getvalue()

    # Now write the output to chat_history.md
    with open("chat_history.md", "w") as file:
        file.write(out)


def extract_current_agent(message):
    # Define the list of valid agent names
    valid_agents = ["COORDINATOR_AGENT", "CODE_AGENT", "CICD_AGENT"]

    # Check if the message starts with any of the valid agent names followed by a colon
    for agent in valid_agents:
        if message.startswith(agent + ":"):
            return agent  # Return the agent name in uppercase (already uppercase)

    # If no valid agent name is found, return "UNKNOWN_AGENT"
    return "UNKNOWN_AGENT"


def extract_next_agent(message):
    """Extracts the last occurring next assistant ID from the assistant's response."""
    pattern = r'NEXT_AGENT\s*:\s*"([^"]+)"'
    matches = re.findall(pattern, message, re.IGNORECASE)
    return matches[-1].upper() if matches else None
