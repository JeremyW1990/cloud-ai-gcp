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
    spec {
      containers {
        image = "gcr.io/your-project/response-parser:latest"
      }
    }
  }
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
