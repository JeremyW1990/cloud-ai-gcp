import requests
import uuid
import time

 

def test_create_agent(user_id):
    url = f'{BASE_URL}/user/{user_id}/agent'
    data = {
        "vendor": "OpenAI",
        "name": "Test Agent",
        "description": "This is a test agent"
    }
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_get_agent(user_id, agent_id):
    url = f'{BASE_URL}/user/{user_id}/agent/{agent_id}'
    response = requests.get(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_update_agent(user_id, agent_id):
    url = f'{BASE_URL}/user/{user_id}/agent/{agent_id}'
    update_data = {
        "name": "Updated Test Agent"
    }
    response = requests.put(url, json=update_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_delete_agent(user_id, agent_id):
    url = f'{BASE_URL}/user/{user_id}/agent/{agent_id}'
    response = requests.delete(url)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def run_agent_api_tests():
    print("Starting Agent API Tests")
    
    # First, create a test user
    user_data = {
        "name": "Test User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "password": "testpassword123"
    }
    user_response = requests.post(f"{BASE_URL}/user", json=user_data)
    if user_response.status_code != 201:
        print("Failed to create test user. Aborting tests.")
        return
    
    user_id = user_response.json()['user_id']
    print(f"Test user created successfully. User ID: {user_id}")
    
    # Create agent
    print("\n1. Creating agent...")
    create_result = test_create_agent(user_id)
    if not create_result or 'agent_id' not in create_result:
        print("Failed to create agent. Aborting tests.")
        return
    
    agent_id = create_result['agent_id']
    print(f"Agent created successfully. Agent ID: {agent_id}")
    

    time.sleep(AGENT_API_WAIT_TIME)
    
    # Get agent
    print("\n2. Getting agent...")
    get_result = test_get_agent(user_id, agent_id)
    if not get_result:
        print("Failed to get agent. Aborting tests.")
        return
    print("Agent retrieved successfully.")
    

    time.sleep(AGENT_API_WAIT_TIME)
    
    # Update agent
    print("\n3. Updating agent...")
    update_result = test_update_agent(user_id, agent_id)
    if not update_result:
        print("Failed to update agent. Aborting tests.")
        return
    print("Agent updated successfully.")
    

    time.sleep(AGENT_API_WAIT_TIME)
    
    # Delete agent
    print("\n4. Deleting agent...")
    delete_result = test_delete_agent(user_id, agent_id)
    if not delete_result:
        print("Failed to delete agent.")
    else:
        print("Agent deleted successfully.")
    
    # Clean up: Delete the test user
    requests.delete(f"{BASE_URL}/user/{user_id}")
    
    print("\nAll Agent API Tests Completed.")


BASE_URL = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1'
AGENT_API_WAIT_TIME = 20
if __name__ == "__main__":
    run_agent_api_tests()