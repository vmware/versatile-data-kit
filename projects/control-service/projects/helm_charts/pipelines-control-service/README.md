# Versatile Data Kit Service
Versatile Data Kit is a platform that enables Data Engineers to implement automated pull ingestion (E in ELT) and batch data transformation into a database (T in ELT).

## Prerequisites
- Kubernetes 1.19<=x>1.25 works with no config changes
- for kubernetes 1.25+ the datajob template needs to be changed in the [values.yaml](./values.yaml). Specifically `enabled` needs to be set to `true` and `apiVersion` needs to be set to `batch/v1`
- Helm 3.0
- PV provisioner support in the underlying infrastructure if using the embedded database.
- During helm install - CRUD on Kubernetes Deployment, Service, ServiceAccount, Role, Rolebindings. Control Service itself manages CronJob(Job and Pod as well), Secret resources. Statefulset and PVC if using the embedded database

### Optional
- Kerberos (see [Parameters](#parameters) section on how to configure it)
- Docker repository to store Data Job images (see [Parameters](#parameters) section on how to configure it)
- Git repository to store Data Jobs source code (see [Parameters](#parameters) section on how to configure it)

## TL;DR;
```console
$ helm repo add vdk-gitlab https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
$ helm install my-release vdk-gitlab/pipelines-control-service
```

Note: integration with bitnami is being planned which will replace above repo.

## Introduction
This chart bootstraps a Versatile Data Kit deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

It also packages a requirement for bootstrapping a database deployment for Versatile Data Kit's metadata:
- [Bitnami PostgreSQL chart](https://github.com/bitnami/charts/tree/main/bitnami/postgresql)
- [Cockroach chart](https://github.com/helm/charts/tree/master/stable/cockroachdb)

## Installing the Chart
To install the chart with the release name `my-release`:

```console
$ helm install my-release vdk-gitlab/pipelines-control-service
```

The command deploys Versatile Data Kit on the Kubernetes cluster in the default configuration.
The default configuration will not enable all features of Versatile Data Kit.
The [Parameters](#parameters) section lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart
To uninstall/delete the `my-release` deployment:

```console
$ helm delete my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters
For a full list of configuration parameters of the Versatile Data Kit chart, and their documentation see [values.yaml](values.yaml) file.
Look through it and make sure to have set all [Required] Parameters as per instruction in the property doc.

For PostgreSQL database parameters see https://github.com/bitnami/charts/tree/main/bitnami/postgresql
For Cockroach database parameters see https://github.com/helm/charts/tree/master/stable/cockroachdb

Specify each parameter using the `--set key=value` or `--set-file key=filePath` argument to `helm install`. For example,

```console
$ helm install my-release \
    --set cockroachdb.storage.persistentVolume.storageClass="3671cd71625c4312a2aee130db182e4c" \
    vdk-gitlab/pipelines-control-service
```

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart. For example,

```console
$ helm install my-release -f my-values.yaml vdk-gitlab/pipelines-control-service
```


## Configuration and installation details
### [Rolling VS Immutable tags](https://docs.bitnami.com/containers/how-to/understand-rolling-tags-containers/)
It is strongly recommended to use immutable tags in a production environment. This ensures your deployment does not change automatically if the same tag is updated with a different image.

### Debug
Under /data-jobs/debug can be found debug utilities provided by Spring actuator.
/data-jobs/debug/prometheus holds metrics which can be used for alerting and tracking state of the service.

#### Metrics
Standard Spring actuator provided metrics

Custom metrics are:

* taurus.deployment.status.summary (tracked as DistributionSummary)
    * tags:
        * dataJob - the data job name
        * status - the status of the data job last deployment - success, user_error, platform_error
* taurus.deployment.status.gauge (tracked as Gauge on deploy status of a job)
    * tags:
        * dataJob - the data job name
    * semantics of the metric:
        * -1 - if the deployment process was not started
        * 0 - if the deployment was successful and there were no exceptions
        * 1 - if during the deployment there were only exceptions caused by problems
                in  infrastructure (e.g. Database was down, no HDFS/S3 access, etc.)
        * 3 - if deployment error was caused by a problem in Data Job Configuration
                or scripts (developed by Data Engineers), e.g. bad syntax of config.ini.
* taurus.datajob.info (A Gauge that exposes the configuration info of a job)
    * tags:
        * data_job - the data job name
        * team - the data job team
        * email_notified_on_success - a list of emails that should be notified on successful job executions;
          these emails are configured in the data job config.ini
        * email_notified_on_user_error - a list of emails that should be notified on job execution failures
          that are caused by user error (e.g. wrong SQL script or broken dependency);
          these emails are configured in the data job config.ini
        * email_notified_on_platform_error - a list of emails that should be notified on job execution failures
          that are caused by problems with the infrastructure (e.g. wrong SQL script or broken dependency);
          these emails are configured in the data job config.ini
* taurus.datajob.termination.status (A Gauge that tracks the last execution status of a job)
    * tags:
        * data_job - the data job name
        * execution_id - an identifier of the last data job execution
    * semantics of the metrics:
        * -1 - there are no job executions
        * 0 - the last data job execution was successful and there were no exceptions
        * 1 - the last data job execution failed due to problems with the infrastructure
          (e.g. database was down, no HDFS/S3 access, etc.)
        * 3 - the last data job execution failed due to a problem with the job configuration
          or scripts (developed by Data Engineers), e.g. bad SQL syntax in one of the scripts
* taurus.datajob.notification.delay (A gauge that exposes the time (in minutes) a job execution
  is allowed to be delayed from its schedule before an alert is triggered)
   * tags:
     * data_job - the data job name
* taurus.datajob.watch.task.invocations.counter (A counter that exposes the number of executions
  of the data job monitoring task)


### Alerting
Based on the metrics above (taurus.datajob.info, taurus.datajob.termination.status and
taurus.datajob.notification.delay) as well as some metrics exposed by kube-state-metrics
there are several Prometheus rules that are deployed as part of the Control service.
In order to send notifications based on the alerts produced by those Prometheus rules,
use the Alertmanager configuration below.

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'your.smtp.host.com:port'
  smtp_require_tls: false
route:
  receiver: 'dp-receiver'
  routes:
    - match:
        source: 'data-pipelines'
      group_by: [alertname, execution_id]
      group_wait: 0s
      group_interval: 1m
      # By default firing alerts are resent every 4 hours; increase repeat_interval to prevent this
      repeat_interval: 720h
      receiver: 'dp-receiver'
receivers:
  - name: 'dp-receiver'
    email_configs:
    - to: '{{ .CommonAnnotations.email_to }}'
      from: sender@company.com
      headers:
        subject: '{{ .CommonAnnotations.subject | safeHtml }}'
      html: '{{ .CommonAnnotations.content | safeHtml }}'
```

Notice that the recipient's email, subject and content are all coming in as annotations of the alert.
If you need to modify those, you can have a look at the rules definitions in [values.yaml](./values.yaml)
under the `alerting.prometheusRules.rules` section.

### Resource Requirements
##### Rest API (Kubernetes Deployment)
Those are tunable (see Parameters section) but good starting defaults are:
* CPU - 1 cpu per pod
* Memory - 1GB per pod

1 pod should be able to handle under thousand jobs. It's recommended to have at least 2 pods for high availability

##### Helper tasks (Kubernetes Batch Jobs)
Those are tasks executed as Kubernetes Job when deploying a Data Job.

The expected total resource requirements can be calculated: How many concurrent deployments of data jobs expected (times) resources for a single task:

A single builder task resources are configured by [deploymentBuilderResourcesDefault](values.yaml) property.
Good starting default limits per builder task are
* CPU - 1 cpu
* Memory - 1GB

##### Database Storage
1KB per data job

##### Data Job resource requirements
Data Job should be in separate namespace from Control service.
This is because Data Jobs execute user code and per user schedule and can fill up the resource quota not leaving enough for Control Service.

The expected total resource requirements can be calculated: Maximum number concurrently running jobs (times) configured resource limits per data job.

A single Data Job default resources and limits are configured by [deploymentDefaultDataJobsResources](values.yaml) property.
Good starting default limits per Data Job are:
* CPU - 1 cpu
* Memory - 4GB

## Persistence
Persistent Volume Claims are used to keep the data across deployments.
See the [Parameters](#parameters) section to configure the PVC or to disable persistence and use external database.
You may want to review the [PV reclaim policy](https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/) and update as required. By default, it's set to delete, and when Versatile Data Kit is uninstalled, data is also removed.
