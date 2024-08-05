import base64
import re
import os
import logging
from google.cloud import pubsub_v1
from flask import Flask, request

# Set up logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

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

    # if "Solutions:" in message_data:
    # Extract solutions using regex
    # solutions = re.findall(r'Solution_\d+:\s*(.*?)(?=\s*Solution_\d+:|$)', message_data, re.DOTALL)
    solutions = message_data + 'Jeremy pending...'

    # Publish each solution to the reasoning branch topic
    publisher = pubsub_v1.PublisherClient()
    destination_topic = "reasoning-branch-topic"
    # project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    project_id = "cloud-ai-431400"
    
    topic_path = publisher.topic_path(project_id, destination_topic)

    # for solution in solutions:
    publisher.publish(topic_path, data=solutions.strip().encode('utf-8'))

    logging.info(f"Published {len(solutions)} solutions to {destination_topic}")
    logging.info(f"Extracted solutions: {solutions}")

    # else:
    #     print("No solutions found in the message")

    return 'OK', 200

@app.route('/', methods=['GET'])
def health_check():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)