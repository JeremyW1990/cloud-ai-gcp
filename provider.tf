# Provider configuration
provider "google" {
  region      = var.region
  project = var.project_id
  credentials = file(var.credentials_file)
}

provider "google-beta" {
  region      = var.region
  project = var.project_id
  credentials = file(var.credentials_file)
}

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 3.53.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 3.53.0"
    }
  }
}
