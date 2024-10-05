import requests

def test_create_user():
    url = 'https://cloud-ai-431400-gateway-2ywxoonu.uc.gateway.dev/v1/user'
    data = {
        "name": "Jeremy Wang",
        "email": "shijie.wang1990@gmail.com"
    }
    response = requests.post(url, json=data)
    
    # Print the status code and response content for debugging
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content}")
    
    # Check if the response is JSON
    try:
        response_json = response.json()
    except ValueError:
        response_json = None
    
    # assert response.status_code == 201
    # assert response_json is not None and 'user_id' in response_json
    return response_json

def call_test_create_user():
    result = test_create_user()
    print(result)

# Call the function to test and print the output
call_test_create_user()