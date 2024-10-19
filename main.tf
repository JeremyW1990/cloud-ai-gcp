locals {
  pub_subs = [
    var.pending_reasoning_topic,
    var.vector_search_topic,
    var.llm_request_topic,
    var.llm_response_topic
  ]

  cloud_runs = [
    # var.orchestrator,
    var.llm_communicator,
    # var.embedding_search,
    # var.data_processor
  ]


}


module "workflow" {
  source   = "./modules/workflow"
  cloud_runs = local.cloud_runs
  pub_subs = local.pub_subs
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
  firestore_id     = google_firestore_database.main.name
  chat_history_bucket      = google_storage_bucket.chat_history_bucket.name
  region           = var.region
  depends_on = [google_project_service.apigateway, google_project_service.service_control] 
}