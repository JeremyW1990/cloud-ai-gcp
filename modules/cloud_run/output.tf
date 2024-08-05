output "cloud_run_url" {
  description = "The URL of the Cloud Run service"
  value       = google_cloud_run_service.this.status[0].url
}

output "cloud_run_service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.this.email
}
