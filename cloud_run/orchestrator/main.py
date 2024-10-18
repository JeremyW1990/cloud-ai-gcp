import base64
import os
import logging
from google.cloud import pubsub_v1
from flask import Flask, request
from concurrent.futures import TimeoutError

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

def callback(message):
    logging.info(f"Received message: {message}")
    message_data = message.data.decode('utf-8')
    logging.info(f"Message data: {message_data}")

    # Process the message
    processed_data = message_data + " p/s from llm_communicator "

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