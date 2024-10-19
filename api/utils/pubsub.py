from google.cloud import pubsub_v1
import json

def pubsub_push(project_id: str, topic_id: str, message: dict):
    """
    Push a message to a GCP Pub/Sub topic.

    Args:
        project_id (str): The GCP project ID.
        topic_id (str): The Pub/Sub topic ID.
        message (dict): The message to be published as a dictionary.

    Returns:
        str: The published message ID.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    
    message_json = json.dumps(message).encode('utf-8')
    future = publisher.publish(topic_path, message_json)
    
    return future.result()

def pubsub_pull(project_id: str, subscription_id: str, max_messages: int = 1):
    """
    Pull messages from a GCP Pub/Sub subscription.

    Args:
        project_id (str): The GCP project ID.
        subscription_id (str): The Pub/Sub subscription ID.
        max_messages (int, optional): The maximum number of messages to pull. Defaults to 1.

    Returns:
        list: A list of dictionaries containing the message data and ack_id.
    """
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    
    response = subscriber.pull(
        request={
            "subscription": subscription_path,
            "max_messages": max_messages,
        }
    )
    
    messages = []
    for received_message in response.received_messages:
        message_data = json.loads(received_message.message.data.decode('utf-8'))
        messages.append({
            'data': message_data,
            'ack_id': received_message.ack_id
        })
    
    return messages

