# Pub/Sub topics (equivalent to SQS queues)

# Ready to send to next llm
# resource "google_pubsub_topic" "llm_request" {
#   name = "llm-request-topic"
# }

# Raw response from llm
resource "google_pubsub_topic" "llm_response" {
  name = "llm-response-topic"
}

resource "google_pubsub_subscription" "response_parser_subscription" {
  name  = "response-parser-subscription"
  topic = google_pubsub_topic.llm_response.name

  push_config {
    push_endpoint = google_cloud_run_service.response_parser.status[0].url
    oidc_token {
      service_account_email = google_service_account.response_parser.email
    }
  }

  ack_deadline_seconds = 600
}



# Only solution or possible solutions stored here, indivisually
resource "google_pubsub_topic" "reasoning_branch" {
  name = "reasoning-branch-topic"
}

resource "google_pubsub_subscription" "reasoning-branch-subscription" {
  name  = "reasoning-branch-subscription"
  topic = google_pubsub_topic.reasoning_branch.name

  ack_deadline_seconds = 600
}

# # response contains source codes, save it here
# resource "google_pubsub_topic" "file_processing" {
#   name = "file-processing-topic"
# }

# # messagse need extra source code context, save it here.
# resource "google_pubsub_topic" "vector_search" {
#   name = "vector-search-topic"
# }