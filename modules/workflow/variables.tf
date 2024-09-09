variable "workflow" {
  type = list(object({
    name               = string
    type               = string
    pubsub_endpoint    = optional(string)
    cloud_run_endpoint = optional(string)
  }))
  description = "A list of workflow items (Cloud Run services or Pub/Sub topics)"
}

variable "project_id" {
  type        = string
  description = "The ID of the Google Cloud project"
}