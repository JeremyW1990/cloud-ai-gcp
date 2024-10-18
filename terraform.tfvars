region = "us-central1"
project_id = "cloud-ai-431400"
credentials_file = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/terraform-sa-key.json"

project_name = "cloud-ai"
default_user_id = "001"


# Define variables for cloud run names
orchestrator = "orchestrator"
llm_communicator = "llm_communicator"
embedding_search = "embedding_search"
data_processor = "data_processor"

cloud_runs = [orchestrator, llm_communicator, embedding_search, data_processor]

# Define variables for topic 
pending_reasoning_topic = "pending_reasoning_topic"
vector_search_topic = "vector_search_topic"
llm_request_topic = "llm_request_topic"
llm_response_topic = "llm_response_topic"

pub_subs = [pending_reasoning_topic, vector_search_topic, llm_request_topic, llm_response_topic]

workflow = {
  orchestrator = {
    pubsub_pull_endpoint = var.pending_reasoning_topic,
    pubsub_push_endpoints = [var.llm_request_topic, var.llm_response_topic, var.vector_search_topic]
  },
  llm_communicator = {
    pubsub_pull_endpoint = var.llm_request_topic,
    pubsub_push_endpoints = [var.pending_reasoning_topic, var.llm_response_topic]
  },
  embedding_search = {
    pubsub_pull_endpoint = var.vector_search_topic,
    pubsub_push_endpoints = [var.llm_request_topic]
  },
  data_processor = {
    pubsub_pull_endpoint = var.llm_response_topic,
    pubsub_push_endpoints = [var.pending_reasoning_topic]
  }
}

firestore_collections = ["users", "agents", "threads", "contexts", "user_id_mapping", "agent_id_mapping", "context_id_mapping"]
api_cloud_runs = ["user", "agent", "context"]
