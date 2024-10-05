resource "google_firestore_database" "main" {
  name     = "${var.project_id}-metadata"
  project     = var.project_id
  location_id = var.region # You can change this to your preferred location
  type        = "FIRESTORE_NATIVE"
  depends_on = [
    google_project_service.firestore_api
  ]
}


// Create Firestore collections
resource "google_firestore_document" "collections" {
  for_each = toset(var.firestore_collections)
  collection  = each.value
  document_id = "_dummy_document"
  fields      = jsonencode({
    dummy_field = {
      stringValue = "dummy_value"
    }
  })
  database = google_firestore_database.main.name

  lifecycle {
    ignore_changes = [fields]
  }
}