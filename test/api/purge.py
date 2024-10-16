import os
from google.cloud import firestore
from google.oauth2 import service_account

# Path to your service account key JSON file
service_account_path = '../../terraform-sa-key.json'

# Create credentials using the service account key
credentials = service_account.Credentials.from_service_account_file(service_account_path)

# Initialize the Firestore client with the specific database and location
db = firestore.Client(project='cloud-ai-431400', credentials=credentials, database='cloud-ai-431400-metadata')

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
    collection_ref.document('placeholder').set({'status': 'empty'})

def delete_all_collections():
    """
    Delete all documents in all collections in the Firestore database, but keep the collections.
    """
    collections = db.collections()
    for collection in collections:
        print(f'Deleting documents in collection: {collection.id}')
        delete_collection(collection.id)

# Call the function to delete all documents in all collections
delete_all_collections()
