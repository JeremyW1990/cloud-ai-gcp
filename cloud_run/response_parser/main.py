import base64
import re
import os
import logging
from google.cloud import pubsub_v1
from flask import Flask, request
from google.auth import default

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)


def extract_paths_and_contents(response: str) -> list[tuple[str, str]]:
    """
    Extracts PATH and code blocks from a given response with error handling.

    Parameters:
    - response: str - The long response from the LLM.

    Returns:
    - A list of tuples, each containing a path and its corresponding code content.
    """
    try:
        # Updated pattern to be case-insensitive for 'PATH'
        # Also, adjusted to use re.IGNORECASE flag
        # pattern = r"PATH: \"(.+?)\"\n```.*?\n(.*?)\n```"
        pattern = r'PATH: ["`](.+?)["`]\n```.*?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        if not matches:
            print("No PATH and code block patterns found in the response.")
            return []
        print(f"Extracting code from response. Found file {matches[0]}:")
        return [(match[0], match[1]) for match in matches]
    except Exception as e:
        print(f"An error occurred while extracting PATH and code blocks: {e}")
        return []

def update_codes_to_repo(extracted_codes):
    logging.info("update_codes_to_repo...")
    pass



@app.route('/', methods=['POST'])
def response_parser():
    logging.info("Received a request")
    # Parse the Pub/Sub message
    envelope = request.get_json()
    logging.info(f"Envelope: {envelope}")
    if not envelope:
        logging.error("No Pub/Sub message received")
        return 'No Pub/Sub message received', 400

    if not isinstance(envelope, dict) or 'message' not in envelope:
        logging.error("Invalid Pub/Sub message format")
        return 'Invalid Pub/Sub message format', 400

    pubsub_message = envelope['message']
    logging.info(f"Pub/Sub message: {pubsub_message}")

    if 'data' in pubsub_message:
        message_data = base64.b64decode(pubsub_message['data']).decode('utf-8')
        logging.info(f"Message data: {message_data}")
    else:
        logging.error("No data field in the message")
        return 'No data', 400

    extracted_codes = extract_paths_and_contents(message_data)
    if extracted_codes:
        update_codes_to_repo(extracted_codes)
    

    publisher = pubsub_v1.PublisherClient()
    destination_topic = os.environ.get('PUBSUB_ENDPOINT')
    project_id = os.environ.get("PROJECT_ID")
    topic_path = publisher.topic_path(project_id, destination_topic)

    publisher.publish(topic_path, data=message_data.strip().encode('utf-8'))

    return 'OK', 200

@app.route('/', methods=['GET'])
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

# def main_for_testing():
#     # Set up test environment
#     os.environ['REASONING_BRANCH_TOPIC'] = 'test-reasoning-branch-topic'
    
#     # Create a test client
#     client = app.test_client()
    
#     # Simulate a POST request
#     test_data = {
#         'message': {
#             'data': base64.b64encode(b'Test message data').decode('utf-8')
#         }
#     }
#     response = client.post('/', json=test_data)
    
#     # Print test results
#     print(f"Status Code: {response.status_code}")
#     print(f"Response: {response.data.decode('utf-8')}")

# if __name__ == '__main__':
#     main_for_testing()