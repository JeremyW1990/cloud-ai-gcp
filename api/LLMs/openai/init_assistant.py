import os
import json
from openai import OpenAI
import yaml


def init_assistants(agents, api_key):

    client = OpenAI(api_key=api_key)
    created_assistants = []

    for agent in agents:
        name = agent["name"]
        instructions = yaml.safe_load(agent["instructions"])
        
        try:
            # Create assistant
            assistant = client.beta.assistants.create(
                name=name,
                tools=[],
                instructions=yaml.dump(instructions),
                model="gpt-4o-2024-05-13",
            )
            
            created_assistants.append({"name": name, f"{name.upper().replace(' ', '_')}_ID": assistant.id})
        except Exception as e:
            print(f"Error creating assistant {name}: {str(e)}")

    return created_assistants

