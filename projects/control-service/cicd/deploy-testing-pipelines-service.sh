#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# The script will deploy/upgrade Control service using helm
# Set RUN_ENVIRONMENT_SETUP to 'y' to setup the test environment.

# For variables injected during the CICD see
# https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD#cicd-demo-installation-variables
# The deployment can be run locally - you'd need to provide those variables manually

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"


export TAG=${TAG:-$(git rev-parse --short HEAD)}
export FRONTEND_TAG=${FRONTEND_TAG:-$(git rev-parse --short HEAD)}
export RELEASE_NAME=${RELEASE_NAME:-cicd-control-service}
export VDK_OPTIONS=${VDK_OPTIONS:-"$SCRIPT_DIR/vdk-options.ini"}
export TPCS_CHART=${TPCS_CHART:-"$SCRIPT_DIR/../projects/helm_charts/pipelines-control-service"}
export VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}
export TESTING_PIPELINES_SERVICE_VALUES_FILE=${TESTING_PIPELINES_SERVICE_VALUES_FILE:-"$SCRIPT_DIR/testing-pipelines-service-values.yaml"}


RUN_ENVIRONMENT_SETUP=${RUN_ENVIRONMENT_SETUP:-'n'}

if [ "$RUN_ENVIRONMENT_SETUP" = 'y' ]; then
  helm repo add valeriano-manassero https://valeriano-manassero.github.io/helm-charts
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update

  helm upgrade --install test-trino valeriano-manassero/trino --version 1.1.7 -f "$SCRIPT_DIR/trino-values.yaml"

  # Prometheus is used for testing and monitoring our cicd (dev) environment
  # But as it is not pre-requisite for any of the tests it's commented out
  # install manually if necesary
  # helm upgrade --install test-prom bitnami/kube-prometheus

  # we are housing data jobs deployment container images in private repo used only for CICD purposes
  # So we need to set credentials of the service account used to pull images when starting jobs
  secret_name=docker-registry
  kubectl create secret docker-registry $secret_name \
                     --namespace="cicd-deployment" \
                     --docker-server="$CICD_CONTAINER_REGISTRY_URI" \
                     --docker-username="$CICD_CONTAINER_REGISTRY_USER_NAME" \
                     --docker-password="$CICD_CONTAINER_REGISTRY_USER_PASSWORD" \
                     --docker-email="versatiledatakit@groups.vmware.com" --dry-run=client -o yaml | kubectl apply -f -
  kubectl patch serviceaccount default -p '{"imagePullSecrets":[{"name":"'$secret_name'"}]}'

  if [ -n "$DOCKERHUB_READONLY_USERNAME" ]; then
    dockerhub_secretname='secret-dockerhub-docker'
    kubectl create secret docker-registry "$dockerhub_secretname" \
                         --namespace="cicd-deployment" \
                         --docker-server="https://index.docker.io/v1/" \
                         --docker-username="$DOCKERHUB_READONLY_USERNAME" \
                         --docker-password="$DOCKERHUB_READONLY_PASSWORD" \
                         --docker-email="versatiledatakit@groups.vmware.com" --dry-run=client -o yaml | kubectl apply -f -

    kubectl patch serviceaccount default -p '{"imagePullSecrets":[{"name":"'$secret_name'"},{"name":"'$dockerhub_secretname'"}]}'
    kubectl create namespace cicd-control
    kubectl create namespace cicd-deployment

  fi

fi

# this is the internal hostname of the Control Service.
# Since all tests (gitlab runners) are installed inside it's easier if we use it.
export CONTROL_SERVICE_URL=${CONTROL_SERVICE_URL:-"http://cicd-control-service-svc:8092"}
# Trino host used by data jobs
export TRINO_HOST=${TRINO_HOST:-"test-trino"}

# Update vdk-options with substituted variables like sensitive configuration (passwords)
export VDK_OPTIONS_SUBSTITUTED="${VDK_OPTIONS}.temp"
envsubst < $VDK_OPTIONS > $VDK_OPTIONS_SUBSTITUTED

cd $TPCS_CHART || exit
helm dependency update --kubeconfig=$KUBECONFIG


helm_latest_deployment=`helm history  cicd-control-service | tail -1`
echo $helm_latest_deployment
if [[ $helm_latest_deployment == *"pending-upgrade"* ]]; then
  echo "Pipeline failed because of an existing deployment in the pending-state.
  If the problem persists use 'helm history cicd-control-service' to see the last successful deployment.
  then use 'helm rollback cicd-control-service <revision number>' to rollback to that deployment. then re run this pipeline"
  exit 125
fi


#
# TODO :change container images with official ones when they are being deployed (I've currently uploaded them once in ghcr.io/tozka)
#
# image.tag is fixed during release. It is set here to deploy using latest change in source code.
# We are using here embedded database, and we need to set the storageclass since in our test k8s no default storage class is not set.
helm upgrade --install --debug --wait --timeout 10m0s $RELEASE_NAME . \
      -f "$TESTING_PIPELINES_SERVICE_VALUES_FILE" \
      --set image.tag="$TAG" \
      --set operationsUi.image.tag="$FRONTEND_TAG" \
      --set credentials.repository="EMPTY" \
      --set-file vdkOptions=$VDK_OPTIONS_SUBSTITUTED \
      --set deploymentGitUrl="$CICD_GIT_URI" \
      --set deploymentGitUsername="$CICD_GIT_USER" \
      --set deploymentGitPassword="$CICD_GIT_PASSWORD" \
      --set uploadGitReadWriteUsername="$CICD_GIT_USER" \
      --set uploadGitReadWritePassword="$CICD_GIT_PASSWORD" \
      --set deploymentDockerRegistryType=generic \
      --set deploymentDockerRegistryUsername="$CICD_CONTAINER_REGISTRY_USER_NAME" \
      --set deploymentDockerRegistryPassword="$CICD_CONTAINER_REGISTRY_USER_PASSWORD" \
      --set deploymentDockerRepository="$CICD_CONTAINER_REGISTRY_URI/cicd-data-jobs/$RELEASE_NAME" \
      --set proxyRepositoryURL="$CICD_CONTAINER_REGISTRY_URI/cicd-data-jobs/$RELEASE_NAME" \
      --set security.enabled=true \
      --set security.oauth2.jwtJwkSetUri=https://console-stg.cloud.vmware.com/csp/gateway/am/api/auth/token-public-key?format=jwks \
      --set security.oauth2.jwtIssuerUrl=https://gaz-preview.csp-vidm-prod.com \
      --set security.authorizationEnabled=false \
      --set extraEnvVars.LOGGING_LEVEL_COM_VMWARE_TAURUS=DEBUG \
      --set deploymentK8sNamespace="cicd-deployment" \
      --set controlK8sNamespace="cicd-control" \
      --set extraEnvVars.DATAJOBS_TELEMETRY_WEBHOOK_ENDPOINT="https://vcsa.vmware.com/ph-stg/api/hyper/send?_c=taurus.v0&_i=cicd-control-service"
