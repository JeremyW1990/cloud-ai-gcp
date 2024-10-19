variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}

variable "region" {
  description = "The region where resources will be deployed"
  type        = string
}

variable "cloud_runs" {
  description = "List of Cloud Run services"
  type        = list(string)
}

variable "pub_subs" {
  description = "List of Pub/Sub topics"
  type        = list(string)
}
