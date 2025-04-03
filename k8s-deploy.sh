#!/bin/bash

set -e

NAMESPACE="default"
MANIFEST_DIR="k8s"

echo "Applying Kubernetes manifests..."
kubectl apply -f $MANIFEST_DIR/

echo "Waiting for all pods to be Running..."
while true; do
  PENDING=$(kubectl get pods --namespace $NAMESPACE --no-headers | grep -v "Running\|Completed" || true)
  if [ -z "$PENDING" ]; then
    echo "All pods are running."
    break
  else
    echo "Still waiting for pods:"
    echo "$PENDING"
    sleep 15
  fi
done

echo "Starting port-forwarding (Grafana, Kafka UI, Prometheus)..."
echo "(Please, press Ctrl+C to stop port-forward.)"

kubectl port-forward service/grafana 3000:3000 &
kubectl port-forward service/kafka-ui 8080:8080 &
kubectl port-forward service/prometheus 9090:9090 &

wait
