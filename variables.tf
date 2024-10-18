variable "region" {
  description = "The region where resources will be deployed"
  type        = string
}

variable "project_name" {
  type        = string
  description = "Name of the project"
}

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string

}

variable "credentials_file" {
  type        = string
  description = "Path to the Google Cloud service account key file"
}

variable "workflow" {
  type = list(object({
    name                 = string
    type                 = string
    pubsub_pull_endpoint = optional(string)
    pubsub_push_endpoint = optional(string)
  }))
  description = "A list of workflow items (Cloud Run services or Pub/Sub topics)"
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "default_user_id" {
  type        = string
  default     = "001"
  description = "The default user ID to be used in the project"
}

// Define the collections as an array variable
variable "firestore_collections" {
  type    = list(string)
}

variable "api_cloud_runs" {
  description = "List of API Cloud Run services to create"
  type        = list(string)
}

variable "orchestrator" {
  description = "Name of the orchestrator Cloud Run service"
  type        = string
}

variable "llm_communicator" {
  description = "Name of the LLM communicator Cloud Run service"
  type        = string
}

variable "embedding_search" {
  description = "Name of the embedding search Cloud Run service"
  type        = string
}

variable "data_processor" {
  description = "Name of the data processor Cloud Run service"
  type        = string
}

variable "cloud_runs" {
  description = "List of Cloud Run services"
  type        = list(string)
}

variable "pending_reasoning_topic" {
  description = "Name of the pending reasoning Pub/Sub topic"
  type        = string
}

variable "vector_search_topic" {
  description = "Name of the vector search Pub/Sub topic"
  type        = string
}

variable "llm_request_topic" {
  description = "Name of the LLM request Pub/Sub topic"
  type        = string
}

variable "llm_response_topic" {
  description = "Name of the LLM response Pub/Sub topic"
  type        = string
}

variable "pub_subs" {
  description = "List of Pub/Sub topics"
  type        = list(string)
}
