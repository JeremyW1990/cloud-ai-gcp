// Enable Firebase Auth API
resource "google_project_service" "firebase_auth" {
  project = var.project_id
  service = "identitytoolkit.googleapis.com"

  disable_dependent_services = true
  disable_on_destroy         = false
}

// Create a Firebase project (if not already created)
resource "google_firebase_project" "main" {
  provider = google-beta
  project  = var.project_id

  depends_on = [
    google_project_service.firebase_auth
  ]
}

// Configure Firebase Auth
resource "google_identity_platform_config" "main" {
  provider = google-beta
  project  = var.project_id

  // You can customize sign-in providers here
  sign_in {
    allow_duplicate_emails = false

    email {
      enabled = true
    }
  }

  depends_on = [
    google_firebase_project.main,
    google_project_service.firebase_api
  ]
}