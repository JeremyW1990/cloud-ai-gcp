import base64
import os
from google.cloud import pubsub_v1
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def response_parser(event, context):
    # Parse the Pub/Sub message
    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    else:
        print("No data field in the event")
        return 'No data', 400

    # Check if the message contains solutions
    if "Solutions:" in pubsub_message:
        # Extract solutions using regex
        solutions = re.findall(r'Solution_\d+:\s*(.*?)(?=\s*Solution_\d+:|$)', pubsub_message, re.DOTALL)

        # Publish each solution to the destination queue
        publisher = pubsub_v1.PublisherClient()
        destination_queue = os.getenv('DESTINATION_QUEUE')
        topic_path = publisher.topic_path(os.getenv('PROJECT_ID'), destination_queue)

        for solution in solutions:
            publisher.publish(topic_path, data=solution.strip().encode('utf-8'))

        print(f"Published {len(solutions)} solutions to {destination_queue}")
        print("Extracted solutions:", solutions)
    else:
        print("No solutions found in the message")

    return 'OK', 200

if __name__ == "__main__":
    # For local testing
    mock_event = {
        'data': base64.b64encode("""
        Solutions:
            Solution_1:  mock_solution_content_1
                        ... jeremy flag1
            Solution_2:  mock_solution_content_2
               jeremy flag2
        """.encode('utf-8'))
    }
    mock_context = None

    result = response_parser(mock_event, mock_context)
    print(f"Function returned: {result}")