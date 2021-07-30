#!/bin/bash

NAMESPACE="cicd"

if [ -z "$VALUES" ]; then
  VALUES=$(pwd)/values.yaml
fi
echo "Using $VALUES gitlab configuration file "

RUNNER_NAME=${RUNNER_NAME:-vdk-gitlab-runner}
echo "Using $RUNNER_NAME as runner name "

if [ -z "$KUBECONFIG" ]; then
  KUBECONFIG=$(pwd)/kubeconfig.yaml
fi

if [ ! -e $KUBECONFIG ]; then
  echo "KUBECONFIG file is required. Provide path to existing one as env variable KUBECONFIG"
  echo "$KUBECONFIG does not exists."
  exit 1
fi
echo "Using $KUBECONFIG as KUBECONFIG "

if [ -z "$RUNNER_REGISTRATION_TOKEN" ]; then
  echo "RUNNER_REGISTRATION_TOKEN variable is required. PLease set token of your runners"
  echo "It can be taken from CICD page in gitlab. e.g "
  echo "https://gitlab.com/vmware-analytics/versatile-data-kit/-/settings/ci_cd"
  exit 1
fi
#echo "Using $RUNNER_REGISTRATION_TOKEN as RUNNER_REGISTRATION_TOKEN "

if ! which helm; then
    echo "helm 3 must be installed"
    exit 1
fi

if ! helm version | grep -q 'Version:"v3'; then
    echo "helm 3 is required"
    exit 1
fi

helm repo add gitlab https://charts.gitlab.io

# Before updating version, review changelog at https://docs.gitlab.com/runner/install/kubernetes.html .
helm upgrade --install \
  --set runnerRegistrationToken=$RUNNER_REGISTRATION_TOKEN \
  --kubeconfig $KUBECONFIG --namespace $NAMESPACE --version "0.22.0" $RUNNER_NAME -f $VALUES gitlab/gitlab-runner


