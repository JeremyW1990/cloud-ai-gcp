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


def retrieve_content_from_bucket(bucket_name, source):
    """
    Retrieves content from a GCP bucket.

    :param bucket_name: The name of the bucket.
    :param source: The path in the bucket where the content is stored.
    :return: The content retrieved from the bucket.
    """
    logging.info(f"Starting retrieve_content_from_bucket with bucket_name={bucket_name}, "
                 f"source={source}")

    # Initialize a storage client
    storage_client = storage.Client()
    logging.info("Initialized storage client.")

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)
    logging.info(f"Retrieved bucket: {bucket_name}")

    # Create a blob object from the bucket
    blob = bucket.blob(source)
    logging.info(f"Created blob object for source: {source}")

    # Download the content from the bucket
    content = blob.download_as_text()
    logging.info("Downloaded content from the bucket.")

    print(f"Content retrieved from {source}.")
    return content

# Example usage
# content = retrieve_content_from_bucket('my-bucket', 'path/to/source/file.txt')
# print(content)
