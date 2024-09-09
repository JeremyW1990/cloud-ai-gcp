locals {
  cloud_run_services = { for item in var.workflow : item.name => item if item.type == "cloud_run" }
  pubsub_topics = { for item in var.workflow : item.name => item if item.type == "pubsub" }
}

resource "google_cloud_run_service" "this" {
  for_each = local.cloud_run_services
  name     = each.key
  location = "us-central1"

  template {
    metadata {
      annotations = {
        "terraform-redeploy-timestamp" = timestamp()
      }
    }

    spec {
      service_account_name = google_service_account.this[each.key].email
      containers {
        image = "gcr.io/${var.project_id}/${each.key}:latest"
        env {
          name  = "PUBSUB_ENDPOINT"
          value = each.value.pubsub_endpoint
        }
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_pubsub_topic" "this" {
  for_each = local.pubsub_topics
  name     = each.key
}

resource "google_pubsub_subscription" "this" {
  for_each = local.pubsub_topics
  name     = "${each.key}-subscription"
  topic    = google_pubsub_topic.this[each.key].name

  dynamic "push_config" {
    for_each = each.value.cloud_run_endpoint != "" ? [1] : []
    content {
      push_endpoint = google_cloud_run_service.this[each.value.cloud_run_endpoint].status[0].url
      oidc_token {
        service_account_email = google_service_account.this[each.value.cloud_run_endpoint].email
      }
    }
  }

  ack_deadline_seconds = 600
}
