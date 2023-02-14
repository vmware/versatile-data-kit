
# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# helm repo add bitnami https://charts.bitnami.com/bitnami
# helm repo update



export APP_HOST=127.0.0.1
export APP_PORT=8080
#export APP_PASSWORD=$(kubectl get secret --namespace scdc1-staging-taurus-staging foo-airflow -o jsonpath="{.data.airflow-password}" | base64 --decode)
#export APP_DATABASE_PASSWORD=$(kubectl get secret --namespace scdc1-staging-taurus-staging foo-postgresql -o jsonpath="{.data.postgresql-password}" | base64 --decode)
#export APP_REDIS_PASSWORD=$(kubectl get secret --namespace scdc1-staging-taurus-staging foo-redis -o jsonpath="{.data.redis-password}" | base64 --decode)

export APP_PASSWORD="airflow"
export APP_DATABASE_PASSWORD="database"
export APP_REDIS_PASSWORD="redis"

# The namespace must have default limits (mem/cpu) set (see limit_range.yaml)
# Or airflow cannot be installed - some containers do not have resources configuration

helm upgrade --install airflow bitnami/airflow -f values.yaml \
    --set airflow.baseUrl=http://$APP_HOST:$APP_PORT \
    --set airflow.auth.password=$APP_PASSWORD \
    --set postgresql.postgresqlPassword=$APP_DATABASE_PASSWORD \
    --set redis.password=$APP_REDIS_PASSWORD

# NOTE on delete pvc do not get deleted automatically delete them manually kubectl get pvc
# Make sure there are enough resources.
# helm delete airflow and then running install.sh works after providing resources (usually storage are missing because I have not deleted unused PVC)

# TODO: Upgrade does not seem to work properly - the new replicasets are created but the old ones are not being deleted.
# In this case delete them manually.
