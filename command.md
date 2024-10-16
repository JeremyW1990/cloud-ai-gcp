conda activate cloud-ai-env

pip install -r requirements.txt

terraform init && terraform plan && terraform apply
terraform apply -auto-approve

docker build -t gcr.io/cloud-ai-431400/response-parser:latest . &&
docker push gcr.io/cloud-ai-431400/response-parser:latest

docker build -t gcr.io/cloud-ai-431400/llm-communicator:latest . &&
docker push gcr.io/cloud-ai-431400/llm-communicator:latest

docker build -t gcr.io/cloud-ai-431400/user:latest -f api/user/Dockerfile . &&
docker push gcr.io/cloud-ai-431400/user:latest && terraform apply --auto-approve

docker build -t gcr.io/cloud-ai-431400/agent:latest -f api/agent/Dockerfile . &&
docker push gcr.io/cloud-ai-431400/agent:latest && terraform apply --auto-approve

docker build -t gcr.io/cloud-ai-431400/context:latest -f api/context/Dockerfile . &&
docker push gcr.io/cloud-ai-431400/context:latest && terraform apply --auto-approve


gcloud pubsub topics publish llm-request-topic --message "This is a mock message from Jeremy 9/9 12:46pm"
gcloud pubsub topics publish llm-response-topic --message "This is a mock message from Jeremy 6:24 pm"

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=response-parser" --limit 10 --format "value(textPayload)"

gcloud pubsub subscriptions pull llm-response-topic-subscription --auto-ack --limit=1
gcloud pubsub subscriptions pull reasoning-branch-topic-subscription --auto-ack --limit=1

API test:
1. 
docker build -t openai-api . &&
docker run -p 8000:8000 openai-api
curl -X POST http://localhost:8000/context \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "context": "This is a test context",
    "OPENAI_API_KEY":"sk-"
  }'


Delete API resources:
  gcloud api-gateway gateways delete cloud-ai-431400-gateway --project=cloud-ai-431400 --location=us-central1
  gcloud api-gateway api-configs delete cloud-ai-431400-config --api=cloud-ai-431400-api --project=cloud-ai-431400
