conda activate cloud-ai-env

pip install -r requirements.txt

terraform apply -auto-approve

docker build -t gcr.io/cloud-ai-431400/response-parser:latest .
docker push gcr.io/cloud-ai-431400/response-parser:latest

gcloud pubsub topics publish llm-response-topic --message "This is a mock message"

gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=response-parser" --limit 10 --format "value(textPayload)"

gcloud pubsub subscriptions pull reasoning-branch-subscription --auto-ack --limit=1