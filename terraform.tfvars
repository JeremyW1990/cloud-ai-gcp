
project_id = "cloud-ai-431400"
credentials_file = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/terraform-sa-key.json"


workflow = [
  { name = "llm-request-topic", type = "pubsub" },
  { name = "llm-communicator", type = "cloud_run", pubsub_pull_endpoint = "llm-request-topic", pubsub_push_endpoint = "llm-response-topic"  },
  { name = "llm-response-topic", type = "pubsub", },
  { name = "response-parser", type = "cloud_run", pubsub_pull_endpoint = "llm-response-topic", pubsub_push_endpoint = "reasoning-branch-topic" },
  { name = "reasoning-branch-topic", type = "pubsub" },
]