resource "google_service_account" "this" {
  for_each     = toset(var.cloud_runs)
  account_id   = each.key
  display_name = "${each.key} Service Account"
}

resource "google_cloud_run_service_iam_member" "noauth" {
  for_each = toset(var.cloud_runs)
  service  = google_cloud_run_service.this[each.key].name
  location = google_cloud_run_service.this[each.key].location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_project_iam_member" "pubsub_publisher" {
  for_each = toset(var.cloud_runs)
  project  = var.project_id
  role     = "roles/pubsub.publisher"
  member   = "serviceAccount:${google_service_account.this[each.key].email}"
}

resource "google_project_iam_member" "pubsub_subscriber" {
  for_each = toset(var.cloud_runs)
  project  = var.project_id
  role     = "roles/pubsub.subscriber"
  member   = "serviceAccount:${google_service_account.this[each.key].email}"
}