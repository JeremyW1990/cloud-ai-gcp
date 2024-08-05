resource "google_service_account" "this" {
  account_id  = var.cloud_run
  display_name = "${var.cloud_run} Service Account"
}

resource "google_cloud_run_service_iam_member" "noauth" {
  service  = google_cloud_run_service.this.name
  location = google_cloud_run_service.this.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_binding" "pubsub_publisher" {
  project  = var.project_id
  role     = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${google_service_account.this.email}"
  ]
}

resource "google_project_iam_binding" "pubsub_subscriber" {
  project  = var.project_id
  role     = "roles/pubsub.subscriber"

  members = [
    "serviceAccount:${google_service_account.this.email}"
  ]
}