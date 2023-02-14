#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

echo "image tag is $IMAGE_TAG"
export HELM_REPO=versatile-data-kit-helm-registry
# TODO: sign chart
helm pack --version "$CHART_VERSION" --app-version "$CHART_VERSION" --dependency-update "$CHART_NAME" --set image.tag="$IMAGE_TAG"
echo "Upload $CHART_NAME version $CHART_VERSION (if version already exists upload will fail)"
helm repo add $HELM_REPO "$VDK_HELM_REGISTRY_URL" \
      --username "$VDK_HELM_REGISTRY_USERNAME" \
      --password "$VDK_HELM_REGISTRY_PASSWORD"
# in v 0.10.0 the name of the push command was changed to cm-push
helm cm-push "$CHART_NAME-$CHART_VERSION.tgz" $HELM_REPO
echo "Check helm repo and new chart is accessible"
helm repo update
helm search repo "$CHART_NAME" --version "$CHART_VERSION"
