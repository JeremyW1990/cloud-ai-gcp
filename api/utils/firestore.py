def firestore_doc_set(db, collection_name, data, doc_id=None, merge=True):
    try:
        # Use the provided doc_id or generate a new one
        if doc_id:
            doc_ref = db.collection(collection_name).document(doc_id)
        else:
            doc_ref = db.collection(collection_name).document()
        
        # Set the data in Firestore with merge option
        doc_ref.set(data, merge=merge)
        
        # Return the document ID and no error
        return doc_ref.id, None
    except Exception as e:
        # Return None and the error message
        return None, str(e)
