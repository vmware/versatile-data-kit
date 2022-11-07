#!/bin/bash

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# The script will deploy/upgrade Control service using helm
# Set RUN_ENVIRONMENT_SETUP to 'y' to setup the test environment.

# For variables injected during the CICD see
# https://github.com/vmware/versatile-data-kit/wiki/Gitlab-CICD#cicd-demo-installation-variables
# The deployment can be run locally - you'd need to provide those variables manually

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"


export TAG=${TAG:-$(git rev-parse --short HEAD)}
export RELEASE_NAME=${RELEASE_NAME:-cicd-control-service}
export VDK_OPTIONS=${VDK_OPTIONS:-"$SCRIPT_DIR/vdk-options.ini"}
export TPCS_CHART=${TPCS_CHART:-"$SCRIPT_DIR/../projects/helm_charts/pipelines-control-service"}
export VDK_DOCKER_REGISTRY_URL=${VDK_DOCKER_REGISTRY_URL:-"registry.hub.docker.com/versatiledatakit"}


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

# TODO :change container images with official ones when they are being deployed (I've currently uploaded them once in ghcr.io/tozka)
#
# image.tag is fixed during release. It is set here to deploy using latest change in source code.
# We are using here embedded database, and we need to set the storageclass since in our test k8s no default storage class is not set.
helm template $RELEASE_NAME . \
      --set image.tag="$TAG" \
      --set resources.limits.memory=2G \
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
      --set security.authorizationEnabled=true \
      --set security.authorization.webhookUri=https://httpbin.org/post \
      --set extraEnvVars.LOGGING_LEVEL_COM_VMWARE_TAURUS=DEBUG \
      --set extraEnvVars.DATAJOBS_TELEMETRY_WEBHOOK_ENDPOINT="https://vcsa.vmware.com/ph-stg/api/hyper/send?_c=taurus.v0&_i=cicd-control-service"
