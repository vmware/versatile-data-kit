# Pipelines Control Service

## Project Structure

```
control-service
├── cicd - Configurations and scripts for GitLab pipelines
└── projects
    ├── base - VDK skeleton for Java services
    ├── helm_charts - helm installation of the VDK bundle
    ├── model - Open API definitions of the VDK Rest APIs
    └── pipelines_control_service - Control Plance service for VDK
```

## HOW TO

### Run the Control Service locally

**Prerequisites**

* Java 11 or greater - make sure JAVA_HOME is set
* Docker latest - make sure "docker" is on the path
* A git repository and a docker registry you'll use for the datajobs code and docker images
  * easiest way is to create a throwaway GitHub account and use the GitHub
    container registry
  * note when creating the account that the name has to be lower-case. The registry does not support namespaces that have upper-case symbols. The namespace for the registry is copied from the account name
  * you should also create a personal access token and make sure the
`read:packages`, `write:packages` and `delete:packages` scopes are selected
* A `kind` k8s cluster running locally
  * https://kind.sigs.k8s.io/
  * make sure your kubeconfig lists the local cluster at the top

**Required configuration**

Navigate to `application-dev.properties` and set the following properties to match your local setup

```properties
datajobs.docker.registryUsername=<your-github-username>
datajobs.docker.registryPassword=<your-personal-access-token>
​
datajobs.deployment.k8s.kubeconfig=<path-to-kubeconfig>

datajobs.git.url=github.com/<your-github-username/<your-github-repo>.git
datajobs.git.username=<your-github-username>
datajobs.git.password=<your-personal-access-token>

datajobs.proxy.repositoryUrl=ghcr.io/<your-github-username/your-github-repo>
datajobs.git.read.write.username=<your-github-username>
datajobs.git.read.write.password=<your-personal-access-token>
```

**Build the project**

```bash
./gradlew -p ./model build publishToMavenLocal --info --stacktrace
./gradlew build jacocoTestReport -x integrationTest --info --stacktrace
```

**Run the project**

```bash
./gradlew :pipelines_control_service:docker  --info --stacktrace -Pversion=dev
./gradlew :pipelines_control_service:bootRun
```

Note: You can also build and run using IntelliJ by running the
`com/vmware/taurus/ServiceApp.java` file

### Setup IntelliJ:

* Import `control-service/projects` in IntelliJ
* Build and upload the model to the Local Maven Repo: `./gradlew -p ./model build publishToMavenLocal`


### Run the Control Service using helm and k8s

**Prerequisites**

* Java 11 or greater - make sure JAVA_HOME is set
* Docker latest - make sure "docker" is on the path
* (for the helm charts) Helm 3+ - make sure that "helm" is on the path
* (optional) AWS CLI configured with your account for the Taurus AWS account
* Kerberos related functionality depends on shell and kadmin binary tool  (see Docker image)


Build the project and create a docker image

```bash
  ./cicd/build.sh
```

Versatile Data Kit would work in a variety of Kubernetes environments. If you want to get started with a local deployment, we recommend kind.
To deploy kind follow the `Deploy kubernetes cluster` and `Deploy local image registry` shown in the readme in ./data_pipelines_operator  without the `docker push`.

To install the service, we will push its components to the Docker regsitry and deploy it through helm.

From inside `` run:
```
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 012285273210.dkr.ecr.us-west-2.amazonaws.com
./gradlew :pipelines_control_service:dockerPush
helm dependency update ./helm_charts/pipelines-control-service
helm install taurus-data-pipelines ./helm_charts/pipelines-control-service
```

**Call the service**
Service always run on external port `31108`:
```
curl "http://$(KIND IP):31108/data-jobs/debug/servertime"
```

**Purge the service**
In order to remove the service from the cluster run:

```
helm uninstall taurus-data-pipelines
```

### Release

New releases of the Versatile Data Kit Control Service are done automatically on each PR merge. As part of the PR, make sure to do the following:
* If necessary, update the version in [helm_charts/pipelines-control-service/version.txt](projects/helm_charts/pipelines-control-service/version.txt) - follows https://semver.org, but only the MAJOR and MINOR components are specified. The PATCH component is generated automatically during release.
* Check if [CHANGELOG.md](CHANGELOG.md) needs to be updated. New entries should include &lt;MAJOR&gt;.&lt;MINOR&gt; - &lt;dd&gt;.&lt;MM&gt;.&lt;yyyy&gt; as a heading.
* Post review and merge to main.
* The CI/CD automatically triggers the new release so only monitor the CI/CD pipeline.
    * https://gitlab.com/vmware-analytics/versatile-data-kit/-/pipelines
    * Once released it will be uploaded in Helm repo: https://gitlab.com/api/v4/projects/28814611/packages/helm/stable

## Configuration Guide

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
Note:
If you do not have access to Kubernetes, you could provision it somehow (kind, kind, ...).

### Git Repository

The data jobs are stored in a git repository. Read access to this repository is
configured using

```properties
datajobs.git.url=github.com/<your-github-username/<your-github-repo>.git
datajobs.git.username=<your-github-username>
datajobs.git.password=<your-personal-access-token>
```
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

### Authentication
Authentication against the service is disabled by default.
You could enable it by specifying the following property in `application-dev.properties`:
```properties
featureflag.security.enabled=true
```

## Testing
* Unit tests (under test folder in each project). Based on JUnit. They are self-contained tests testing the class or method level. All tests should finish in minutes
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
