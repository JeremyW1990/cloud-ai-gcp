conda activate cloud-ai-env

pip install -r requirements.txt

terraform apply -auto-approve

docker build -t gcr.io/cloud-ai-431400/response-parser:latest .
docker push gcr.io/cloud-ai-431400/response-parser:latest


docker build -t gcr.io/cloud-ai-431400/llm-communicator:latest . 
docker push gcr.io/cloud-ai-431400/llm-communicator:latest

gcloud pubsub topics publish llm-request-topic --message "This is a mock message from Jeremy 9/8 7:02pm"
gcloud pubsub topics publish llm-response-topic --message "This is a mock message from Jeremy 6:24 pm"

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=response-parser" --limit 10 --format "value(textPayload)"

gcloud pubsub subscriptions pull llm-response-topic-subscription --auto-ack --limit=1
gcloud pubsub subscriptions pull reasoning-branch-topic-subscription --auto-ack --limit=1

