import requests
import time



def test_create_user(email=None):
    if email is None:
        email = "test@gmail.com"
    
    url = f'{BASE_URL}/user/'
    data = {
        "name": "Jeremy Wang",
        "email": email,
        "password": "123456"
    }
    response = requests.post(url, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    return response_json

def test_delete_user(user_id):
    delete_url = f'{BASE_URL}/user/{user_id}'
    delete_response = requests.delete(delete_url)
    
    print(f"Delete Status Code: {delete_response.status_code}")
    print(f"Delete Response Content: {delete_response.content}")
    
    try:
        response_json = delete_response.json()
    except ValueError:
        response_json = None
    
    assert delete_response.status_code == 200, f"Failed to delete user: {delete_response.content}"
    assert response_json is not None, "Response is not JSON"
    
    return response_json

def test_get_user(user_id):
    get_url = f'{BASE_URL}/user/{user_id}'
    get_response = requests.get(get_url)
    
    print(f"Response status code: {get_response.status_code}")
    print(f"Response headers: {get_response.headers}")
    print(f"Raw response content: {get_response.text}")
    
    try:
        user_data = get_response.json()
        print(f"Parsed JSON response: {user_data}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to parse JSON. Error: {str(e)}")
        print(f"Response content type: {get_response.headers.get('Content-Type')}")
        return None
    
    print(f"Response status code: {get_response.status_code}")
    print(f"Response body: {get_response.json()}")

    return get_response

def test_update_user(user_id):
    update_url = f'{BASE_URL}/user/{user_id}'
    update_data = {
        "email": "shijie.wang1990_2@gmail.com"
    }
    update_response = requests.put(update_url, json=update_data)
    
    print(f"Update Status Code: {update_response.status_code}")
    print(f"Update Response Content: {update_response.content}")
    
    try:
        response_json = update_response.json()
    except ValueError:
        response_json = None
    
    return response_json

def run_user_api_tests():
    print("Starting User API Tests")
    
    # Create user
    print("\n1. Creating user...")
    create_result = test_create_user()
    if not create_result or 'user_id' not in create_result:
        print("Failed to create user. Aborting tests.")
        return
    
    user_id = create_result['user_id']
    print(f"User created successfully. User ID: {user_id}")
    
    time.sleep(USER_API_WAIT_TIME)
    
    # Get user
    print("\n2. Getting user...")
    get_result = test_get_user(user_id)
    if not get_result or get_result.status_code != 200:
        print("Failed to get user. Aborting tests.")
        return
    print("User retrieved successfully.")
    
    time.sleep(USER_API_WAIT_TIME)
    
    # Update user
    print("\n3. Updating user...")
    update_result = test_update_user(user_id)
    if not update_result:
        print("Failed to update user. Aborting tests.")
        return
    print("User updated successfully.")
    
    time.sleep(USER_API_WAIT_TIME)
    
    # Delete user
    print("\n4. Deleting user...")
    delete_result = test_delete_user(user_id)
    if not delete_result:
        print("Failed to delete user.")
    else:
        print("User deleted successfully.")
    
    print("\nAll User API Tests Completed.")

# Run the tests
if __name__ == "__main__":
    BASE_URL = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1'
    USER_API_WAIT_TIME = 10
    run_user_api_tests()
