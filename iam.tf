resource "google_service_account" "response_parser" {
  account_id   = "response-parser"
  display_name = "Response Parser Service Account"
}

resource "google_cloud_run_service_iam_member" "noauth" {
  service  = google_cloud_run_service.response_parser.name
  location = google_cloud_run_service.response_parser.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_binding" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"

  members = [
    "serviceAccount:${google_service_account.response_parser.email}"
  ]
}

resource "google_project_iam_binding" "pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"

  members = [
    "serviceAccount:${google_service_account.response_parser.email}"
  ]
}
