resource "google_cloud_run_service" "this" {
  for_each = toset(var.cloud_runs)
  name     = each.value
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

        dynamic "env" {
          for_each = var.pub_subs
          content {
            name  = env.value
            value = env.value
          }
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
  for_each = toset(var.pub_subs)
  name     = each.value
}

resource "google_pubsub_subscription" "this" {
  for_each = toset(var.pub_subs)
  name     = each.value
  topic    = google_pubsub_topic.this[each.value].name

  ack_deadline_seconds = 600
  
  // Add message retention duration
  message_retention_duration = "604800s" // 7 days
}



