region = "us-central1"
project_id = "cloud-ai-431400"
credentials_file = "C:/Users/cjwan/Documents/MY_CODE_MY_WORLD/Cloud-AI/cloud-ai-gcp/terraform-sa-key.json"

project_name = "cloud-ai"
default_user_id = "001"


# Define variables for cloud run names
orchestrator = "orchestrator"
llm_communicator = "llm-communicator"
embedding_search = "embedding-search"
data_processor = "data-processor"


# Define variables for topic 
pending_reasoning_topic = "pending-reasoning-topic"
vector_search_topic = "vector-search-topic"
llm_request_topic = "llm-request-topic"
llm_response_topic = "llm-response-topic"


firestore_collections = ["users", "agents", "threads", "contexts", "user_id_mapping", "agent_id_mapping", "context_id_mapping"]
api_cloud_runs = ["user", "agent", "context"]
