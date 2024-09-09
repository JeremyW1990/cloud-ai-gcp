import base64
import re
import os
import logging
from google.cloud import pubsub_v1
from flask import Flask
from concurrent.futures import TimeoutError

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
        pattern = r'PATH: ["`](.+?)["`]\n```.*?\n(.*?)\n```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        if not matches:
            logging.warning("No PATH and code block patterns found in the response.")
            return []
        logging.info(f"Extracting code from response. Found file {matches[0]}:")
        return [(match[0], match[1]) for match in matches]
    except Exception as e:
        logging.error(f"An error occurred while extracting PATH and code blocks: {e}")
        return []

def update_codes_to_repo(extracted_codes):
    logging.info("update_codes_to_repo...")
    # Implement your code update logic here
    pass

def callback(message):
    logging.info(f"Received message: {message}")
    message_data = message.data.decode('utf-8')
    logging.info(f"Message data: {message_data}")

    extracted_codes = extract_paths_and_contents(message_data)
    if extracted_codes:
        update_codes_to_repo(extracted_codes)
    
    processed_data = message_data + " p/s from parser "

    # Publish the processed message
    publisher = pubsub_v1.PublisherClient()
    destination_topic = os.environ.get('PUBSUB_PUSH_ENDPOINT')
    project_id = os.environ.get("PROJECT_ID")
    topic_path = publisher.topic_path(project_id, destination_topic)

    publisher.publish(topic_path, data=processed_data.strip().encode('utf-8'))

    # Acknowledge the message
    message.ack()

def pull_messages():
    project_id = os.environ.get("PROJECT_ID")
    pull_topic = os.environ.get("PUBSUB_PULL_ENDPOINT")
    
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, f"{pull_topic}-subscription")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logging.info(f"Listening for messages on {subscription_path}")

    try:
        streaming_pull_future.result(timeout=None)
    except TimeoutError:
        streaming_pull_future.cancel()
        logging.error("Streaming pull future timed out.")

@app.route('/', methods=['GET'])
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting Flask app on port {port}")
    
    # Start pulling messages in a separate thread
    import threading
    threading.Thread(target=pull_messages, daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=True)