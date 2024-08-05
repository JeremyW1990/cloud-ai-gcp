resource "google_cloud_run_service" "this" {
  name     = var.cloud_run
  location = "us-central1"

  template {
    metadata {
    #   annotations = {
    #     "terraform.io/force-redeploy" = timestamp()
    #   }
    }
    spec {
      service_account_name = google_service_account.this.email
      containers {
        image = "gcr.io/${var.project_id}/${var.cloud_run}:latest"
        env {
          name  = "PUBSUB_ENDPOINT"
          value = var.pubsub_endpoint
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