# Cloud Run services
# resource "google_cloud_run_service" "orchestrator" {
#   name     = "orchestrator"
#   location = "us-central1"

#   template {
#     spec {
#       containers {
#         image = "gcr.io/your-project/orchestrator:latest"
#       }
#     }
#   }
# }

resource "google_cloud_run_service" "response_parser" {
  name     = "response-parser"
  location = "us-central1"

  template {
    metadata {
      annotations = {
        "terraform.io/force-redeploy" = timestamp()
      }
    }
    spec {
      service_account_name = google_service_account.response_parser.email
      containers {
        image = "gcr.io/${var.project_id}/response-parser:latest"
        env {
          name  = "REASONING_BRANCH_TOPIC"
          value = google_pubsub_topic.reasoning_branch.name
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.container_registry]
}

# resource "google_cloud_run_service" "file_processor" {
#   name     = "file-processor"
#   location = "us-central1"

#   template {
#     spec {
#       containers {
#         image = "gcr.io/your-project/file-processor:latest"
#       }
#     }
#   }
# }

# resource "google_cloud_run_service" "vector_search" {
#   name     = "vector-search"
#   location = "us-central1"

#   template {
#     spec {
#       containers {
#         image = "gcr.io/your-project/vector-search:latest"
#       }
#     }
#   }
# }

# resource "google_cloud_run_service" "llm_communicator" {
#   name     = "llm-communicator"
#   location = "us-central1"

#   template {
#     spec {
#       containers {
#         image = "gcr.io/your-project/llm-communicator:latest"
#       }
#     }
#   }
# }