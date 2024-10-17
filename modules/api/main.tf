# Collect the Cloud Run URLs
locals {
  api_services = {
    for name, service in google_cloud_run_service.api_service :name => service.status[0].url
  }
}

data "template_file" "yaml_file" {
  template = file("${path.module}/openapi.yaml.tpl")

  vars = {
    user_service_url = local.api_services["user"]
    agent_service_url = local.api_services["agent"]
    context_service_url = local.api_services["context"]
  }
}

data "local_file" "openapi_template" {
  filename = "${path.module}/openapi.yaml.tpl"
}

resource "google_cloud_run_service" "api_service" {
  for_each = toset(var.api_cloud_runs)
  name     = each.key
  location = var.region

  template {
      metadata {
      annotations = {
        "terraform-redeploy-timestamp" = timestamp()
      }
    }
    spec {
      service_account_name = google_service_account.api_service_account[each.key].email

      containers {
        image = "gcr.io/${var.project_id}/${each.key}:latest"

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }

        env {
          name  = "FIRESTORE_ID"
          value = var.firestore_id
        }

        env {
          name  = "FIRESTORE_REGION"
          value = var.region
        }

        env {
          name  = "BUCKET_NAME"
          value = var.chat_history_bucket
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
  api = google_api_gateway_api.api.api_id  
  api_config_id = "${var.project_id}-config-${substr(md5(data.template_file.yaml_file.rendered), 0, 8)}"

  openapi_documents {
    document {
      path     = "${path.module}/openapi.yaml"
      contents = base64encode(data.template_file.yaml_file.rendered)
    }
  }

}

resource "google_api_gateway_gateway" "gateway" {
  provider   = google-beta
  project    = var.project_id
  region     = var.region
  gateway_id = "${var.project_id}-gateway"
  api_config = google_api_gateway_api_config.api_config.id

  lifecycle {
    replace_triggered_by = [
      google_api_gateway_api_config.api_config
    ]
  }

  depends_on = [google_api_gateway_api_config.api_config]
}

