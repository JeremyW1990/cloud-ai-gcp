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
    name               = string
    type               = string
    pubsub_endpoint    = optional(string)
    cloud_run_endpoint = optional(string)
  }))
  description = "A list of workflow items (Cloud Run services or Pub/Sub topics)"
}
