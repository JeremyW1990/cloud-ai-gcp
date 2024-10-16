# Enable Container Registry API
resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_resource_manager" {
  service = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "secretmanager_api" {
  project = var.project_id
  service = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# Enable Cloud Firestore API
resource "google_project_service" "firestore_api" {
  project = var.project_id
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

// Enable Firebase Management API
resource "google_project_service" "firebase_api" {
  project = var.project_id
  service = "firebase.googleapis.com"

  disable_dependent_services = true
  disable_on_destroy         = false
}

resource "google_project_service" "apigateway" {
  project = var.project_id
  service = "apigateway.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "service_control" {
  project = var.project_id
  service = "servicecontrol.googleapis.com"
  disable_on_destroy = false
}