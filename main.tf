module "workflow" {
  source   = "./modules/workflow"
  workflow = var.workflow
  project_id = var.project_id
  region = var.region

  depends_on = [
    google_project_service.container_registry,
    google_project_service.cloud_resource_manager
  ]
}

module "api" {
  source = "./modules/api"

  api_cloud_runs   = var.api_cloud_runs
  project_id       = var.project_id
  region           = var.region
}