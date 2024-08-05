variable "project_id" {
  description = "The ID of the Google Cloud project"
  type        = string

}

variable "credentials_file" {
  type        = string
  description = "Path to the Google Cloud service account key file"
}