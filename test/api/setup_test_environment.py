import json
import os
from datetime import datetime
import uuid
import time
import requests
from user import test_create_user
from context import test_create_context, CONTEXT_API_WAIT_TIME
from thread import test_delete_thread

# File to store the test environment IDs
TEST_ENV_FILE = 'test_environment.json'
BASE_URL = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1'
CONTEXT_API_WAIT_TIME = 1

secrets = {}
with open('../../secrets.auto.tfvars', 'r') as secrets_file:
    for line in secrets_file:
        key, value = line.strip().split(' = ')
        secrets[key] = value.strip('"')

def create_thread(user_id, context_id):
    url = f'{BASE_URL}/user/{user_id}/thread'
    data = {
        "context_id": context_id,
        "vendor": "openai",
        "api_key": secrets['openai_api_key']
    }
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        return response.json().get('thread_id')
    else:
        print(f"Failed to create thread. Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")
        return None

def setup_test_environment():
    env_data = {}
    if os.path.exists(TEST_ENV_FILE):
        with open(TEST_ENV_FILE, 'r') as f:
            env_data = json.load(f)
            print("Loaded existing test environment:")
            print(f"User ID: {env_data['user_id']}")
            print(f"Context ID: {env_data['context_id']}")
            print(f"Thread ID: {env_data['thread_id']}")
    
    user_id = env_data.get('user_id')
    context_id = env_data.get('context_id')
    thread_id = env_data.get('thread_id')
    
    if not user_id:
        print("Creating new user...")
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        email = f"test_{uuid.uuid4()}@example.com"
        user_result = test_create_user(email)
        if not user_result or 'user_id' not in user_result:
            print("Failed to create user. Aborting setup.")
            return None
        user_id = user_result['user_id']
        print(f"User created successfully. User ID: {user_id}")
        
        time.sleep(CONTEXT_API_WAIT_TIME)
    
    if not context_id:
        print("Creating new context...")
        context_result = test_create_context(user_id)
        if not context_result or 'context_id' not in context_result:
            print("Failed to create context. Aborting setup.")
            return None
        context_id = context_result['context_id']
        print(f"Context created successfully. Context ID: {context_id}")
        
        time.sleep(CONTEXT_API_WAIT_TIME)
    
    if thread_id:
        print(f"Deleting existing thread: {thread_id}")
        delete_result = test_delete_thread(user_id, thread_id)
        if delete_result is None:
            print("Failed to delete existing thread. Aborting setup.")
            return None
        thread_id = None
    
    # Create thread
    thread_id = create_thread(user_id, context_id)
    if not thread_id:
        print("Failed to create thread. Aborting setup.")
        return None
    print(f"Thread created successfully. Thread ID: {thread_id}")
    
    # Save the environment data
    env_data = {
        'user_id': user_id,
        'context_id': context_id,
        'thread_id': thread_id
    }
    with open(TEST_ENV_FILE, 'w') as f:
        json.dump(env_data, f)
    
    print("Test environment setup completed and saved.")
    return env_data

if __name__ == "__main__":
    setup_test_environment()
