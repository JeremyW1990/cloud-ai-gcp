import requests
import uuid
import time
import json
from datetime import datetime

BASE_URL = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1'
CONTEXT_API_WAIT_TIME = 10
# Load secrets from secrets.auto.tfvars
secrets = {}
with open('../../secrets.auto.tfvars', 'r') as secrets_file:
    for line in secrets_file:
        key, value = line.strip().split(' = ')
        secrets[key] = value.strip('"')


# Load context.json
with open('context.json', 'r') as file:
    context_data = json.load(file)

def test_create_context(user_id=None):
    url = f'{BASE_URL}/user/{user_id}/context'
    data = {
        **context_data,  
        "vendor": "OpenAI",
        "api_key": secrets['openai_api_key']
    }
    # print(data)
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_get_context(user_id, context_id):
    url = f'{BASE_URL}/user/{user_id}/context/{context_id}'
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_update_context(user_id, context_id):
    url = f'{BASE_URL}/user/{user_id}/context/{context_id}'
    update_data = {
        "instructions": "Updated test instructions",
        "agents": ["agent1", "agent2", "agent3"]
    }
    response = requests.put(url, json=update_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_delete_context(user_id, context_id):
    url = f'{BASE_URL}/user/{user_id}/context/{context_id}'
    response = requests.delete(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def run_context_api_tests():
    print("Starting Context API Tests")
    
    # First, create a test user
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    user_data = {
        "name": f"Test User {current_time}",  # Append date and time to the user name
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "testpassword123"
    }
    user_response = requests.post(f"{BASE_URL}/user", json=user_data)
    if user_response.status_code != 201:
        print("Failed to create test user. Aborting tests.")
        return
    
    user_id = user_response.json()['user_id']
    print(f"Test user created successfully. User ID: {user_id}")
    
    # Create context
    print("\n1. Creating context...")
    create_result = test_create_context(user_id)
    if not create_result or 'context_id' not in create_result:
        print("Failed to create context. Aborting tests.")
        return
    
    context_id = create_result['context_id']
    print(f"Context created successfully. Context ID: {context_id}")
    
    time.sleep(CONTEXT_API_WAIT_TIME)
    
    # Get context
    print("\n2. Getting context...")
    get_result = test_get_context(user_id, context_id)
    if not get_result:
        print("Failed to get context. Aborting tests.")
        return
    print("Context retrieved successfully.")
    
    time.sleep(CONTEXT_API_WAIT_TIME)
    
    # # Update context
    # print("\n3. Updating context...")
    # update_result = test_update_context(user_id, context_id)
    # if not update_result:
    #     print("Failed to update context. Aborting tests.")
    #     return
    # print("Context updated successfully.")
    
    # time.sleep(CONTEXT_API_WAIT_TIME)
    
    # # Delete context
    # print("\n4. Deleting context...")
    # delete_result = test_delete_context(user_id, context_id)
    # if delete_result is None:
    #     print("Failed to delete context.")
    # else:
    #     print("Context deleted successfully.")
    
    # Clean up: Delete the test user
    requests.delete(f"{BASE_URL}/user/{user_id}")
    
    print("\nAll Context API Tests Completed.")

if __name__ == "__main__":
    # test_create_context()
    run_context_api_tests()
