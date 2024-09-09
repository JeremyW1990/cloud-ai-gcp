variable "workflow" {
  type = list(object({
    name                 = string
    type                 = string
    pubsub_pull_endpoint = optional(string)
    pubsub_push_endpoint = optional(string)
  }))
  description = "A list of workflow items (Cloud Run services or Pub/Sub topics)"
}

variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}