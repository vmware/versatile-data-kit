#!/bin/bash
# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0



source env.sh || echo "Provide env.sh with exported environment variables: VDK_API_TOKEN and GIT_TOKEN"

helm repo add bitnami https://charts.bitnami.com/bitnami

if ! helm list | grep vdk-mysql ;
then
  helm upgrade --install --wait --timeout 10m0s  vdk-mysql bitnami/mysql
else
  export  MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace vdk-amld vdk-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode)
  helm upgrade --install --wait --timeout 10m0s  vdk-mysql bitnami/mysql --set auth.rootPassword=$MYSQL_ROOT_PASSWORD
fi

envsubst < values.yaml > values-secret.yaml

helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
helm upgrade --install --wait --timeout 10m0s amld-vdk vdk-gitlab/pipelines-control-service -f values-secret.yaml


export  MYSQL_ROOT_PASSWORD=$(kubectl get secret --namespace vdk-amld vdk-mysql -o jsonpath="{.data.mysql-root-password}" | base64 --decode)
envsubst < values-trino.yaml > values-trino-secret.yaml

helm repo add valeriano-manassero https://valeriano-manassero.github.io/helm-charts
helm upgrade --install test-trino valeriano-manassero/trino --version 1.11.0 -f  values-trino-secret.yaml
