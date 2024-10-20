import os
from google.cloud import firestore
from google.cloud import storage
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, auth

# Path to your service account key JSON file
service_account_path = '../../terraform-sa-key.json'

# Create credentials using the service account key
firebase_credentials = credentials.Certificate(service_account_path)

# Initialize the Firestore client with the specific database and location
db = firestore.Client(project='cloud-ai-431400', credentials=service_account.Credentials.from_service_account_file(service_account_path), database='cloud-ai-431400-metadata')

# Initialize the Firebase Admin SDK
firebase_admin.initialize_app(firebase_credentials)

def delete_collection(collection_name, batch_size=10):
    """
    Delete all documents in a Firestore collection, except for '_dummy_document'.
    If '_dummy_document' doesn't exist, create it to keep the collection.

    :param collection_name: Name of the collection to delete documents from.
    :param batch_size: Number of documents to delete in each batch.
    """
    collection_ref = db.collection(collection_name)
    docs = collection_ref.limit(batch_size).stream()

    deleted = 0

    for doc in docs:
        if doc.id != '_dummy_document':
            print(f'Deleting doc {doc.id} => {doc.to_dict()}')
            doc.reference.delete()
            deleted += 1
        else:
            print(f'Skipping _dummy_document in {collection_name}')

    if deleted >= batch_size:
        return delete_collection(collection_name, batch_size)

    # # Check if '_dummy_document' exists, create it if it doesn't
    # dummy_doc = collection_ref.document('_dummy_document').get()
    # if not dummy_doc.exists:
    #     collection_ref.document('_dummy_document').set({'dummy_field': 'dummy_value'})
    #     print(f'Created _dummy_document in {collection_name}')

def delete_all_collections():
    """
    Delete all documents in all collections in the Firestore database, but keep the collections.
    """
    collections = db.collections()
    for collection in collections:
        print(f'Deleting documents in collection: {collection.id}')
        delete_collection(collection.id)

def delete_all_firebase_users():
    """
    Delete all users in the Firebase Authentication system.
    """
    page = auth.list_users()
    while page:
        for user in page.users:
            print(f'Deleting user: {user.uid}')
            auth.delete_user(user.uid)
        page = page.get_next_page()

from google.cloud import storage
from google.oauth2 import service_account

from google.cloud import storage
from google.oauth2 import service_account

from google.cloud import storage
from google.oauth2 import service_account

def purge_bucket(bucket_name, service_account_path):
    # Load credentials from the service account file
    credentials = service_account.Credentials.from_service_account_file(service_account_path)

    # Initialize a client with the specified credentials
    storage_client = storage.Client(credentials=credentials)

    # Get the bucket
    bucket = storage_client.get_bucket(bucket_name)

    # List all objects and delete them (including any "empty folder" prefixes)
    blobs = list(bucket.list_blobs())  # Get a list of all objects in the bucket
    
    # Ensure reverse deletion order for nested folders
    folders_to_delete = sorted([blob.name for blob in blobs if blob.name.endswith('/')], reverse=True)

    # Delete all objects, both files and folder-like objects
    for blob in blobs:
        blob.delete()

    # Delete all folders (even if empty)
    for folder in folders_to_delete:
        folder_blob = bucket.blob(folder)
        folder_blob.delete()

    print(f"All objects and folders deleted from bucket {bucket_name}.")




# Call the function to delete all documents in all collections
delete_all_collections()

# Call the function to delete all users
delete_all_firebase_users()

# Call the function to delete all files and folders in the specified bucket
purge_bucket('cloud-ai-431400-chat',service_account_path)
