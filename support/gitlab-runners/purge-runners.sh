#!/bin/bash

# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

RUNNER_NAME="vdk-gitlab-runner"

NAMESPACE="cicd"

KUBECONFIG=$(pwd)/kubeconfig.yaml

if ! which helm; then
    echo "helm 3 must be installed"
    exit 1
fi

if ! helm version | grep -q 'Version:"v3'; then
    echo "helm 3 is required"
    exit 1
fi

helm delete --kubeconfig $KUBECONFIG --namespace $NAMESPACE $RUNNER_NAME
