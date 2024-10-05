locals {
  cloud_run_services = { for item in var.workflow : item.name => item if item.type == "cloud_run" }
  pubsub_topics = { for item in var.workflow : item.name => item if item.type == "pubsub" }
}

resource "google_cloud_run_service" "this" {
  for_each = local.cloud_run_services
  name     = each.key
  location = var.region

  template {
    metadata {
      annotations = {
        # "terraform-redeploy-timestamp" = timestamp()
      }
    }

    spec {
      service_account_name = google_service_account.this[each.key].email
      containers {
        image = "gcr.io/${var.project_id}/${each.key}:latest"
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "PUBSUB_PULL_ENDPOINT"
          value = each.value.pubsub_pull_endpoint
        }
        env {
          name  = "PUBSUB_PUSH_ENDPOINT"
          value = each.value.pubsub_push_endpoint
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

  ack_deadline_seconds = 600
  
  // Add message retention duration
  message_retention_duration = "604800s" // 7 days
}
