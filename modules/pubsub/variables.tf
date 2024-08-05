variable "pubsubs" {
  description = "The name of the Pub/Sub topic"
  type        = string
}

variable "endpoint_url" {
  description = "The endpoint URL for the push subscription"
  type        = string
}

variable "endpoint_email" {
  description = "The service account email for the push subscription"
  type        = string
}

variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string
}