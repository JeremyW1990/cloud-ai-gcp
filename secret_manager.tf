resource "google_secret_manager_secret" "user_001_openai_api_key" {
  secret_id = "user_${var.default_user_id}_openai_api_key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager_api]
}

resource "google_secret_manager_secret_version" "user_001_openai_api_key_version" {
  secret      = google_secret_manager_secret.user_001_openai_api_key.id
  secret_data = var.openai_api_key
}
