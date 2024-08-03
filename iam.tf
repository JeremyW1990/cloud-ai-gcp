resource "google_project_iam_binding" "response_parser_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"

  members = [
    "serviceAccount:${google_cloud_run_service.response_parser.service_account}"
  ]
}
