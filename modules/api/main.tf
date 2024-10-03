# Collect the Cloud Run URLs
locals {
  api_services = {
    for name, service in google_cloud_run_service.api_service :name => service.status[0].url
  }
}

resource "google_cloud_run_service" "api_service" {
  for_each = toset(var.api_cloud_runs)
  name     = each.key
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.api_service_account[each.key].email

      containers {
        image = "gcr.io/${var.project_id}/${each.key}:latest"

        env {
          name  = "FIRESTORE_PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "FIRESTORE_REGION"
          value = var.region
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_project_iam_member.datastore_user
  ]
}

resource "google_api_gateway_api" "api" {
  provider = google-beta
  project = var.project_id
  api_id  = "${var.project_id}-api"
}

resource "google_api_gateway_api_config" "api_config" {
  provider = google-beta  
  project = var.project_id
  api         = google_api_gateway_api.api.api_id  
  api_config_id = "${var.project_id}-config"  

  openapi_documents {
    document {
      path     = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/modules/api/user.yaml"
      contents = base64encode(file("C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/modules/api/user.yaml"))
    }
  }
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [google_api_gateway_api.api] 
}

# output "rendered_openapi_document" {
#   value = templatefile("${path.module}/openapi.yaml.tpl", {
#     api_services = { for idx, service in var.api_cloud_runs : service => google_cloud_run_service.api_service[service].status[0].url }
#   })
# }

resource "google_api_gateway_gateway" "gateway" {
  provider = google-beta
  gateway_id = "${var.project_id}-gateway"
  api_config = google_api_gateway_api_config.api_config.id
  depends_on = [google_api_gateway_api_config.api_config]
}