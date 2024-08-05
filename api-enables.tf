# Enable Container Registry API
resource "google_project_service" "container_registry" {
  service = "containerregistry.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "cloud_resource_manager" {
  service = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = false
}