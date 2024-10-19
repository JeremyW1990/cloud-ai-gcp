resource "google_service_account" "api_service_account" {
  for_each     = toset(var.api_cloud_runs)
  account_id   = "${each.key}-sa"
  display_name = "Service account for ${each.key} Cloud Run service"
}

resource "google_project_iam_member" "datastore_user" {
  for_each = toset(var.api_cloud_runs)
  project  = var.project_id
  role     = "roles/datastore.user"
  member   = "serviceAccount:${google_service_account.api_service_account[each.key].email}"
}

# Add Firebase Authentication Admin role
resource "google_project_iam_member" "firebase_auth_admin" {
  for_each = toset(var.api_cloud_runs)
  project  = var.project_id
  role     = "roles/firebaseauth.admin"
  member   = "serviceAccount:${google_service_account.api_service_account[each.key].email}"
}

# Allow unauthenticated access if needed
resource "google_cloud_run_service_iam_member" "noauth" {
  for_each = toset(var.api_cloud_runs)
  location = var.region
  service  = google_cloud_run_service.api_service[each.key].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow Cloud Run to access Cloud Storage
resource "google_project_iam_member" "cloud_storage_access" {
  for_each = toset(var.api_cloud_runs)
  project  = var.project_id
  role     = "roles/storage.objectAdmin"
  member   = "serviceAccount:${google_service_account.api_service_account[each.key].email}"
}
