import logging
from google.cloud import storage


def upload_content_to_bucket(bucket_name, destination, content):
    """
    Uploads content to a GCP bucket.

    :param bucket_name: The name of the bucket.
    :param destination: The path in the bucket where the content will be stored.
    :param content: The content to be uploaded.
    """
    logging.info(f"Starting upload_content_to_bucket with bucket_name={bucket_name}, "
                  f"destination={destination}, content={content}")

    # Initialize a storage client
    storage_client = storage.Client()
    logging.info("Initialized storage client.")

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    logging.info(f"Retrieved bucket: {bucket_name}")

    # Create a blob object from the bucket
    blob = bucket.blob(destination)
    logging.info(f"Created blob object for destination: {destination}")

    # Upload the content to the bucket
    blob.upload_from_string(content)
    logging.info("Uploaded content to the bucket.")

    print(f"Content uploaded to {destination}.")

# Example usage
# upload_content_to_gcp_bucket('my-bucket', 'path/to/destination/file.txt', 'This is the content to upload.')
