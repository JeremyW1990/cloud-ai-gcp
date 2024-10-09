import requests

def test_create_user():
    url = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1/user/'
    data = {
        "name": "Jeremy Wang",
        "email": "shijie.wang1990@gmail.com",
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

def test_delete_user(frontend_user_id):
    delete_url = f'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1/user/{frontend_user_id}'
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

def test_get_user(frontend_user_id):
    get_url = f'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1/user/{frontend_user_id}'


    
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
        return None  # or handle the error as appropriate for your use case
    
    # Add assertions to check the response
    # assert get_response.status_code == 200, f"Expected status code 200, but got {get_response.status_code}"
    
    # assert 'email' in user_data, "User data should contain an email field"
    # assert 'frontend_user_id' in user_data, "User data should contain a frontend_user_id field"
    # assert user_data['frontend_user_id'] == frontend_user_id, "Returned frontend_user_id should match the requested ID"

    # Log the response for debugging
    print(f"Response status code: {get_response.status_code}")
    print(f"Response body: {get_response.json()}")

    return get_response

# Call the functions to test and print the output
# create_result = test_create_user()
# print(f"Create user result: {create_result}")

# Replace with an actual frontend_user_id obtained from the create_result
# delete_result = test_delete_user("2babc323-2aa2-4c99-9685-8bf3e13b794e")
# print(f"Delete user result: {delete_result}")

# Example usage:
get_result = test_get_user("2babc323-2aa2-4c99-9685-8bf3e13b794e")
# print(f"Get user result: {get_result}")