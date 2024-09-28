resource "google_firestore_database" "main" {
  name     = "${var.project_id}-metadata"
  project     = var.project_id
  location_id = var.region # You can change this to your preferred location
  type        = "FIRESTORE_NATIVE"
  depends_on = [
    google_project_service.firestore_api
  ]
}
