
project_id = "cloud-ai-431400"
credentials_file = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/terraform-sa-key.json"


# cloud_runs = ["response-parser", "file-processor", "vector-search", "llm-communicator", "orchestrator"]
cloud_runs = [
    { name = "response-parser", endpoint = "reasoning-branch-topic" }
]

pubsubs = [
#   { name = "llm-request-topic", endpoint = "" },
  { name = "llm-response-topic", endpoint = "response-parser" },
  { name = "reasoning-branch-topic", endpoint = "" },
#   { name = "vector-search-topic", endpoint = "" },
#   { name = "file-processing-topic", endpoint = "" }
]