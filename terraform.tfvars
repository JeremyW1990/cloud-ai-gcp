
project_id = "cloud-ai-431400"
credentials_file = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/terraform-sa-key.json"


# cloud_runs = ["response-parser", "file-processor", "vector-search", "llm-communicator", "orchestrator"]
# cloud_runs = [
#     { name = "llm-communicator", endpoint = "llm-response-topic"},
#     { name = "response-parser", endpoint = "reasoning-branch-topic" }
# ]

# pubsubs = [
#   { name = "llm-request-topic", endpoint = "llm-communicator" },
#   { name = "llm-response-topic", endpoint = "response-parser" },
#   { name = "reasoning-branch-topic", endpoint = "" },
# #   { name = "vector-search-topic", endpoint = "" },
# #   { name = "file-processing-topic", endpoint = "" }
# ]

workflow = [
  { name = "llm-request-topic", type = "pubsub", cloud_run_endpoint = "llm-communicator" },
  { name = "llm-communicator", type = "cloud_run", pubsub_endpoint = "llm-response-topic" },
  { name = "llm-response-topic", type = "pubsub", cloud_run_endpoint = "response-parser" },
  { name = "response-parser", type = "cloud_run", pubsub_endpoint = "reasoning-branch-topic" },
  { name = "reasoning-branch-topic", type = "pubsub", cloud_run_endpoint = "" },
]
