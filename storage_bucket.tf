resource "google_storage_bucket" "chat_history_bucket" {
  name     = "${var.project_id}-chat-history"
  location =  var.region
}
