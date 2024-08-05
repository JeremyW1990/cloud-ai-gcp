module "cloud_run_services" {
  source          = "./modules/cloud_run"
  for_each        = { for cloud_run in var.cloud_runs : cloud_run.name => cloud_run }
  cloud_run       = each.value.name
  project_id      = var.project_id
  pubsub_endpoint = each.value.endpoint

  depends_on = [
    google_project_service.container_registry,
    google_project_service.cloud_resource_manager
  ]
}

module "pubsub_topics" {
  source        = "./modules/pubsub"
  for_each      = { for pubsub in var.pubsubs : pubsub.name => pubsub }
  pubsubs       = each.value.name
  endpoint_url  = each.value.endpoint != "" ? module.cloud_run_services[each.value.endpoint].cloud_run_url : ""
  endpoint_email = each.value.endpoint != "" ? module.cloud_run_services[each.value.endpoint].cloud_run_service_account_email : ""
  project_id    = var.project_id

  depends_on = [
    google_project_service.container_registry,
    google_project_service.cloud_resource_manager
  ]
}