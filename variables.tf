variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string

}

variable "credentials_file" {
  type        = string
  description = "Path to the Google Cloud service account key file"
}

variable "cloud_runs" {
  type = list(object({
    name     = string
    endpoint = string
  }))
  description = "A list of Cloud Run names and their corresponding Pub/Sub endpoints"
}

variable "pubsubs" {
  type = list(object({
    name     = string
    endpoint = string
  }))
  description = "A list of Pub/Sub topics and their corresponding endpoints"
}
