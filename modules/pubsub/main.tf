resource "google_pubsub_topic" "this" {
  name = var.pubsubs
}

resource "google_pubsub_subscription" "this" {
  name  = "${var.pubsubs}-subscription"
  topic = google_pubsub_topic.this.name

  dynamic "push_config" {
    for_each = var.endpoint_url != "" ? [1] : []
    content {
      push_endpoint = var.endpoint_url
      oidc_token {
        service_account_email = var.endpoint_email
      }
    }
  }

  ack_deadline_seconds = 600
}