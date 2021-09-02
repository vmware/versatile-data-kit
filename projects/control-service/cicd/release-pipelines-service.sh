#!/bin/bash

# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

export CHART_NAME=pipelines-control-service
export CHART_VERSION=$(cat $CHART_NAME/version.txt)
export HELM_REPO=versatile-data-kit-helm-registry
# TODO: sign chart
helm package --version $CHART_VERSION --app-version $CHART_VERSION --dependency-update $CHART_NAME
echo "Upload $CHART_NAME version $CHART_VERSION (if version already exists upload will fail)"
helm repo add $HELM_REPO $VDK_HELM_REGISTRY_URL \
      --username $VDK_HELM_REGISTRY_USERNAME \
      --password $VDK_HELM_REGISTRY_PASSWORD
helm push $CHART_NAME-$CHART_VERSION.tgz $HELM_REPO
echo "Check helm repo and new chart is accessible"
helm repo update
helm search repo $CHART_NAME --version $CHART_VERSION
