variable "api_cloud_runs" {
  description = "List of API Cloud Run services to create"
  type        = list(string)
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "firestore_id" {
  description = "The ID of the Firestore database"
  type        = string
}
