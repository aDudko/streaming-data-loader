#!/bin/bash

set -e

MANIFEST_DIR="k8s"

echo "Stopping all port-forward processes..."
PORT_FORWARD_PIDS=$(ps aux | grep "kubectl port-forward" | grep -v grep | awk '{print $2}')
if [ -n "$PORT_FORWARD_PIDS" ]; then
  echo "$PORT_FORWARD_PIDS" | xargs kill -9
  echo "Port-forward processes stopped."
else
  echo "No port-forward processes found."
fi

echo "Deleting Kubernetes resources..."
kubectl delete -f $MANIFEST_DIR/ --ignore-not-found

echo "Clean up complete."

echo "Remaining pods:"
kubectl get pods
