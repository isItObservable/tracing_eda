#!/usr/bin/env bash

################################################################################
### Script deploying the Observ-K8s environment
### Parameters:
### Clustern name: name of your k8s cluster
### dttoken: Dynatrace api token with ingest metrics and otlp ingest scope
### dturl : url of your DT tenant wihtout any / at the end for example: https://dedede.live.dynatrace.com
################################################################################


### Pre-flight checks for dependencies
if ! command -v jq >/dev/null 2>&1; then
    echo "Please install jq before continuing"
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "Please install git before continuing"
    exit 1
fi


if ! command -v helm >/dev/null 2>&1; then
    echo "Please install helm before continuing"
    exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
    echo "Please install kubectl before continuing"
    exit 1
fi
echo "parsing arguments"
while [ $# -gt 0 ]; do
  case "$1" in
  --dttoken)
    DTTOKEN="$2"
   shift 2
    ;;
  --dthost)
    DTURL="$2"
   shift 2
    ;;
  --solaceusername)
    SOLACEUSER="$2"
   shift 2
    ;;
  --solacepassword)
    SOLACEPWD="$2"
   shift 2
    ;;
   --solacehost)
    SOLACEHOST="$2"
   shift 2
    ;;
   --solacevpn)
    SOLACEVPN="$2"
   shift 2
    ;;
  *)
    echo "Warning: skipping unsupported option: $1"
    shift
    ;;
  esac
done
echo "Checking arguments"

if [ -z "$DTURL" ]; then
  echo "Error: Dt hostname not set!"
  exit 1
fi

if [ -z "$DTTOKEN" ]; then
  echo "Error: api-token not set!"
  exit 1
fi
if [ -z "$SOLACEUSER" ]; then
  echo "Error: solace user not set!"
  exit 1
fi
if [ -z "$SOLACEPWD" ]; then
  echo "Error: solace password not set!"
  exit 1
fi
if [ -z "$SOLACEHOST" ]; then
  echo "Error: Solace host not set!"
  exit 1
fi
if [ -z "$SOLACEVPN" ]; then
  echo "Error: Solace vpn not set!"
  exit 1
fi




#### Deploy the cert-manager
echo "Deploying Cert Manager ( for OpenTelemetry Operator)"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.10.0/cert-manager.yaml
# Wait for pod webhook started
kubectl wait pod -l app.kubernetes.io/component=webhook -n cert-manager --for=condition=Ready --timeout=2m
# Deploy the opentelemetry operator
sleep 10
echo "Deploying the OpenTelemetry Operator"
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml


kubectl create secret generic dynatrace  --from-literal=dynatrace_oltp_url="$DTURL" --from-literal=dt_api_token="$DTTOKEN"
kubectl apply -f Manifest/openTelemetry-manifest_debut.yaml
#Deploy the OpenTelemetry Collector

#deploy demo application
kubectl create ns eda
kubectl create secret generic solace -n eda --from-literal=solace_host="$SOLACEHOST" --from-literal=solace_vpn="$SOLACEVPN" --from-literal=solace_username="$SOLACEUSER" --from-literal=solace_password="$SOLACEPWD"
kubectl apply -f Manifest/deployment_publisher.yaml -n eda



