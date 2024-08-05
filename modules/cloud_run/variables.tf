variable "cloud_run" {
  description = "The name of the Cloud Run service"
  type        = string
}

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}

variable "pubsub_endpoint" {
  description = "The Pub/Sub endpoint associated with the Cloud Run service"
  type        = string
}