import requests
import uuid
import time
import json
from datetime import datetime

BASE_URL = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1'
THREAD_API_WAIT_TIME = 10

# Load secrets from secrets.auto.tfvars
secrets = {}
with open('../../secrets.auto.tfvars', 'r') as secrets_file:
    for line in secrets_file:
        key, value = line.strip().split(' = ')
        secrets[key] = value.strip('"')

# Load thread.json
# with open('thread.json', 'r') as file:
#     thread_data = json.load(file)

def test_create_thread(user_id=None):
    url = f'{BASE_URL}/user/{user_id}/thread'
    data = {
        "vendor": "OpenAI",
        "api_key": secrets['openai_api_key'],
        "context": "Mock context"
    }
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_get_thread(user_id, thread_id):
    url = f'{BASE_URL}/user/{user_id}/thread/{thread_id}'
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_update_thread(user_id, thread_id):
    url = f'{BASE_URL}/user/{user_id}/thread/{thread_id}'
    update_data = {
        "instructions": "Updated test instructions for thread",
    }
    response = requests.put(url, json=update_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_delete_thread(user_id, thread_id):
    url = f'{BASE_URL}/user/{user_id}/thread/{thread_id}'
    response = requests.delete(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def run_thread_api_tests():
    print("Starting Thread API Tests")
    
    # First, create a test user
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_data = {
        "name": f"Test User {current_time}",
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "testpassword123"
    }
    user_response = requests.post(f"{BASE_URL}/user", json=user_data)
    if user_response.status_code != 201:
        print("Failed to create test user. Aborting tests.")
        return
    
    user_id = user_response.json()['user_id']
    print(f"Test user created successfully. User ID: {user_id}")
    
    # Create thread
    print("\n1. Creating thread...")
    create_result = test_create_thread(user_id)
    if not create_result or 'thread_id' not in create_result:
        print("Failed to create thread. Aborting tests.")
        return
    
    thread_id = create_result['thread_id']
    backend_thread_id = create_result['backend_thread_id']
    print(f"Thread created successfully.")
    print(f"Thread ID: {thread_id}")
    print(f"Backend Thread ID: {backend_thread_id}")
    
    time.sleep(THREAD_API_WAIT_TIME)
    
    # Get thread
    print("\n2. Getting thread...")
    get_result = test_get_thread(user_id, thread_id)
    if not get_result:
        print("Failed to get thread. Aborting tests.")
        return
    print("Thread retrieved successfully.")
    
    time.sleep(THREAD_API_WAIT_TIME)
    
    # Update thread
    print("\n3. Updating thread...")
    update_result = test_update_thread(user_id, thread_id)
    if not update_result:
        print("Failed to update thread. Aborting tests.")
        return
    print("Thread updated successfully.")
    
    time.sleep(THREAD_API_WAIT_TIME)
    
    # Delete thread
    print("\n4. Deleting thread...")
    delete_result = test_delete_thread(user_id, thread_id)
    if delete_result is None:
        print("Failed to delete thread.")
    else:
        print("Thread deleted successfully.")
    
    # Clean up: Delete the test user
    requests.delete(f"{BASE_URL}/user/{user_id}")
    
    print("\nAll Thread API Tests Completed.")

if __name__ == "__main__":
    run_thread_api_tests()