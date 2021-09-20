# Pipelines Control Service
This directory contains the components of Versatile Data Kit. This readme focuses on building the control service.

## Components
The directory contains:
* base - Versatile Data Kit skeleton for Java services
* pipelines_control_service - Control Plane service for Versatile Data Kit
* helm_charts - contains the helm installation of the Versatile Data Kit bundle
* model - contains the Open API definitions of the Versatile Data Kit Rest APIs

## Prerequisites
* Java 11+ - make sure JAVA_HOME is set
* Docker latest - make sure "docker" is on the path
* (for the helm charts) Helm 3+ - make sure that "helm" is on the path
* (optional) AWS CLI configured with your account for the Taurus AWS account

* Kerberos related functionality depends on shell and kadmin binary tool  (see Docker image)

## Build and run the Control Plane service
run `./gradlew tasks` to see all possible tasks and descriptions

### Build

This will build project and create docker image
```bash
  ./cicd/build.sh
```

Or (without creating docker image)

```bash
./gradlew -p ./model build publishToMavenLocal --info --stacktrace
./gradlew build jacocoTestReport -x integrationTest --info --stacktrace
```

### Setup IntelliJ:
 * Install Lombok Plugin
 * Import the data-pipelines project using the root folder: Project from Existing Sources... -> Gradle
 * Build and upload the model to the Local Maven Repo: `./gradlew -p ./model build publishToMavenLocal`
 * Enable Annotation processing (Shift+Shift and search for it)

### Run the project
```
./gradlew :pipelines_control_service:docker  --info --stacktrace -Pversion=dev
./gradlew :pipelines_control_service:bootRun
```

## Running the service locally and in IDE
The service can be run directly in the IDE (by running the `com/vmware/taurus/ServiceApp.java` file),
and it will start without the need of any modifications.
However, depending on the intended usage, some external dependencies may need to be additionally configured.

### Datasource
By default, the service will use an in-memory H2 database for storing the data jobs metadata.
Alternatively, you can use an external db for persistence or for readily available data job information.
Better approach is to use a private (local) database (e.g. a containerized CockroachDB).

To specify the database, add these to the `application-dev.properties`:
```properties
spring.datasource.url=jdbc:postgresql://localhost:26257/<database_name>
spring.datasource.username=<username>
spring.datasource.password=<password>
```
where `<database_name>` is the name of the database.
The schema will be automatically created by Flyway on a startup.

### Kubernetes
If you intend to deploy data jobs, you should specify the target Kubernetes clusters and namespaces.
The service uses two clusters - one for the builder jobs, and one for the data jobs themselves.
They can be specified by the following `application-dev.properties` configurations respectively:
```properties
datajobs.control.k8s.kubeconfig=<path_to_kubeconfig_file>
datajobs.control.k8s.namespace=<k8s_namespace>

datajobs.deployment.k8s.kubeconfig=<path_to_kubeconfig_file>
datajobs.deployment.k8s.namespace=<k8s_namespace>
```

### GIT repository
The data jobs are stored in a git repository. Read access to this repository is already configured in `application-dev.properties`.
If you need to also push, you must configure read/write access to Git via:
```properties
datajobs.git.read.write.username=<username>
datajobs.git.read.write.password=<password_or_token>
```
If you decide to use your own credentials, make sure to generate a token rather than your plain password.

### VDK options
Runtime options for the VDK are passed in via the `vdk_options.ini` file. You can specify this file via:
```properties
datajobs.vdk_options_ini=<vdi_options_file>
```
You can use the `src/main/resources/vdk_options.ini` provided in the project.
If you need your data jobs to send telemetry, you may need to specify `VDK_INFLUX_DB_PASSWORD` inside `vdk_options.ini`.

### AWS credentials
When building a data job image, the job builder is pulling the VDK image from (and then pushing the data job image itself to) an AWS repository.
The credentials to this repository can be specified via the following properties in `application-dev.properties`:
```properties
datajobs.aws.accessKeyId=<access_key_id>
datajobs.aws.secretAccessKey=<secret_access_key>
```

## CICD
See [.gitlab-ci.yml](../.gitlab-ci.yml)

## Testing
* Unit tests (under test folder in each project). self-contained tests testing the class or method level. All tests should finish in minutes
  if not seconds. Flexible goal for (line) coverage is to be 60-70% range if possible (it depends on how algorithmitics/unit-testable the code is)
* Integration tests. (under integration_test folder in each project). collect modules together and test them as a subsystem in order to verify
  that they collaborate as intended to achieve some larger piece of behaviour. They generally mock external component when possible.
* Acceptance Tests (vdk-heartbeat project) - it tests Versatile Data Kit (include CLI tools) as an end-user will use them.
  They cover most frequent user workflows.
* Stress test


## Spring Profiles
The Java components in Versatile Data Kit are built with the Spring Boot flavor of the Spring Framework. Learn more
about Spring at <https://spring.io>. The build and run automation make use of
[Spring Boot profiles](https://docs.spring.io/spring-boot/docs/2.3.0.M1/reference/html/spring-boot-features.html#boot-features-profiles) .

The main profiles are:
 - prod - production configuration; intended to be used when deploying in Kubernetes via Helm
 - dev - configuration for running the service locally or in Docker, also used for integration tests

 Integration tests may also define other profiles, like "MockKubernetes" for re-using configuration between tests.

## Error handling
All user facing log errors, log warnings, error notifications, alerts must follow the format:
```
What:
Why:
Consequences:
Countermeasures:
```

* **_What:_** What operation failed, what was the system trying to achieve. Don't say anything technical here, e.g. don't say "Create file failed", because this means nothing to user. Explain what "user story" were you implementing, e.g. "Could not save customer contact details." instead.
* **_Why:_** Explain the problem that the user have (possible reasons). E.g. "Customer contact details are stored in folder %s, but a file with that name already exists."
* **_Consequences:_** Again, nothing technical here. Explain what will not be achieved, what is the state of the system from user perspective after this error.
* **_Countermeasures:_**  Explain what to do next so that we don't see this error again. Provide info how to recover from this error. E.g. "Make sure that %s is folder, not a file.". Or if user has no option, because our service failed - tell user what to do (e.g. "wait for notification that system is green")

Logging in Control Service should be printed to stderr (usually seen with `kubectl logs` command).
It's expected to be used by IT Ops Persona installing and maintaining the service

The following logging messages and errors are generally read by Data Engineer developing their data jobs:
* Any logs from VDK (development kit) during a data job execution
* Errors generated during Data Job deployment that can be categorized as "User errors" (e.g. incorrect configuration).
  Those errors usually generate mail notifications.

## Security (AuthN/Z)
Authentication in REST API is based on OAuth2
To authenticate specify OAuth2 access token as Authorization/Bearer Header;

The testing installation uses (Staging) CSP Authentication provider.
To get access token you need refresh or access token
To get refresh token go to https://console-stg.cloud.vmware.com/csp/gateway/portal/#/user/tokens

Then add HTTP Header : "Authorization: Bearer $access_token"
See example for Authentication flow in tools/oauth-curl.sh (the script executes curl with scp authentication)

## Deploy in Kubernetes
Versatile Data Kit would work in a variety of Kubernetes environments. If you want to get started with a local deployment, we recommend minikube.
To deploy minikube follow the `Deploy kubernetes cluster` and `Deploy local image registry` shown in the readme in ./data_pipelines_operator  without the `docker push`.

To install the service, we will push its components to the Docker regsitry and deploy it through helm.

From inside `` run:
```
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 012285273210.dkr.ecr.us-west-2.amazonaws.com
./gradlew :pipelines_control_service:dockerPush
helm dependency update ./helm_charts/pipelines-control-service
helm install taurus-data-pipelines ./helm_charts/pipelines-control-service
```

### Call the service
Service always run on external port `31108`:
```
curl "http://$(minikube IP):31108/data-jobs/debug/servertime"
```

### Purge the service
In order to remove the service from the cluster run:

```
helm uninstall taurus-data-pipelines
```


## Release

#### Control Service and Helm Chart

In order to make new release of Versatile Data Kit Control Service:
* Update version in [helm_charts/pipelines-control-service/version.txt](projects/helm_charts/pipelines-control-service/version.txt) - follows https://semver.org
* Make sure image.tag (in [values.yaml](projects/helm_charts/pipelines-control-service/values.yaml)) is updated accordingly
  * look at the latest successful CICD Pipeline on [main](https://gitlab.com/vmware-analytics/versatile-data-kit/-/pipelines?page=1&scope=all&ref=main) - get tag from logs of [stage pre_release](cicd/.gitlab-ci.yml) and ci job control_service_deploy_testing_data_pipelines. This job is a part of the pre_release pipeline. The new tag string should contain the short git commit hash of the last commit that changed the control-service.
* Check if [CHANGELOG.md](CHANGELOG.md) needs to be updated.
* Post review and merge to main. The release commit should not have other changes except those above.
* CICD automatically triggers new release on each update of the version.txt file - so only monitor CICD pipeline.
    * https://gitlab.com/vmware-analytics/versatile-data-kit/-/pipelines
    * Once released it will be uploaded in Helm repo: https://gitlab.com/api/v4/projects/28814611/packages/helm/stable
