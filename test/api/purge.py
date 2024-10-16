import os
from google.cloud import firestore
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
    Delete all documents in a Firestore collection, but keep the collection by adding a placeholder document.

    :param collection_name: Name of the collection to delete documents from.
    :param batch_size: Number of documents to delete in each batch.
    """
    collection_ref = db.collection(collection_name)
    docs = collection_ref.limit(batch_size).stream()

    deleted = 0

    for doc in docs:
        print(f'Deleting doc {doc.id} => {doc.to_dict()}')
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(collection_name, batch_size)

    # Add a placeholder document to keep the collection
    collection_ref.document('_dummy_document').set({'dummy_field': 'dummy_value'})

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

# Call the function to delete all documents in all collections
delete_all_collections()

# Call the function to delete all users
delete_all_firebase_users()
