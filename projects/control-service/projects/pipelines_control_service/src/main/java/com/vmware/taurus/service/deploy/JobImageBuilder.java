/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import static java.util.Map.entry;

import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import io.kubernetes.client.openapi.ApiException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Map;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Responsible for building docker images for data jobs. The images are pushed to a docker
 * repository and then deployed on kubernetes.
 */
@Component
public class JobImageBuilder {
  private static final Logger log = LoggerFactory.getLogger(JobImageBuilder.class);

  private static final String REGISTRY_TYPE_ECR = "ecr";
  private static final String REGISTRY_TYPE_GENERIC = "generic";
  private static final String REGISTRY_TYPE_JFROG = "jfrog";

  @Value("${datajobs.git.url}")
  private String gitRepo;

  @Value("${datajobs.git.username}")
  private String gitUsername;

  @Value("${datajobs.git.password}")
  private String gitPassword;

  @Value("${datajobs.git.branch}")
  private String gitDataJobsBranch;

  @Value("${datajobs.docker.repositoryUrl}")
  private String dockerRepositoryUrl;

  @Value("${datajobs.docker.registryType}")
  private String registryType;

  @Value("${datajobs.docker.registryUsername:}")
  private String registryUsername;

  @Value("${datajobs.docker.registryPassword:}")
  private String registryPassword;

  @Value("${datajobs.deployment.builder.extraArgs:}")
  private String builderJobExtraArgs;

  @Value("${datajobs.deployment.builder.imagePullPolicy:IfNotPresent}")
  private String builderJobImagePullPolicy;

  @Value("${datajobs.git.ssl.enabled}")
  private boolean gitDataJobsSslEnabled;

  @Value("${datajobs.deployment.builder.securitycontext.runAsUser}")
  private long builderSecurityContextRunAsUser;

  @Value("${datajobs.deployment.builder.securitycontext.runAsGroup}")
  private long builderSecurityContextRunAsGroup;

  @Value("${datajobs.deployment.builder.securitycontext.fsGroup}")
  private long builderSecurityContextFsGroup;

  @Value("${datajobs.deployment.builder.serviceAccountName}")
  private String builderServiceAccountName;

  @Value("${datajobs.deployment.builder.builderTimeoutSeconds:1800}")
  private int builderTimeoutSeconds;

  private final ControlKubernetesService controlKubernetesService;
  private final DockerRegistryService dockerRegistryService;
  private final DeploymentNotificationHelper notificationHelper;
  private final KubernetesResources kubernetesResources;
  private final AWSCredentialsService awsCredentialsService;
  private final SupportedPythonVersions supportedPythonVersions;
  private final EcrRegistryInterface ecrRegistryInterface;
  private final JfrogRegistryInterface jfrogRegistryInterface;

  public JobImageBuilder(
      ControlKubernetesService controlKubernetesService,
      DockerRegistryService dockerRegistryService,
      DeploymentNotificationHelper notificationHelper,
      KubernetesResources kubernetesResources,
      AWSCredentialsService awsCredentialsService,
      SupportedPythonVersions supportedPythonVersions,
      EcrRegistryInterface ecrRegistryInterface,
      @Autowired(required = false) JfrogRegistryInterface jfrogRegistryInterface) {

    this.controlKubernetesService = controlKubernetesService;
    this.dockerRegistryService = dockerRegistryService;
    this.notificationHelper = notificationHelper;
    this.kubernetesResources = kubernetesResources;
    this.awsCredentialsService = awsCredentialsService;
    this.supportedPythonVersions = supportedPythonVersions;
    this.ecrRegistryInterface = ecrRegistryInterface;
    this.jfrogRegistryInterface = jfrogRegistryInterface;
  }

  /**
   * Builds and pushes a docker image for a data job. Runs a job on k8s which is responsible for
   * building and pushing the data job image. This call will block until the builder job has
   * finished. Notifies the users on failure.
   *
   * @param imageName Full name of the image to build.
   * @param dataJob Information about the data job.
   * @param desiredDataJobDeployment Information about the desired data job deployment.
   * @param actualDataJobDeployment Information about the actual data job deployment.
   * @param sendNotification
   * @return True if build and push was successful. False otherwise.
   * @throws ApiException
   * @throws IOException
   * @throws InterruptedException
   */
  public boolean buildImage(
      String imageName,
      DataJob dataJob,
      DesiredDataJobDeployment desiredDataJobDeployment,
      ActualDataJobDeployment actualDataJobDeployment,
      Boolean sendNotification)
      throws ApiException, IOException, InterruptedException {

    log.trace("Build data job image for job {}. Image name: {}", dataJob.getName(), imageName);
    if (!StringUtils.isBlank(registryType)) {
      if (unsupportedRegistryType(registryType)) {
        log.warn(
            String.format(
                "Unsupported registry type: %s available options %s/%s/%s",
                registryType, REGISTRY_TYPE_ECR, REGISTRY_TYPE_GENERIC, REGISTRY_TYPE_JFROG));
        return false;
      }
    }

    if (desiredDataJobDeployment.getPythonVersion() == null) {
      log.warn("Missing pythonVersion. Data Job cannot be deployed.");
      return false;
    }

    String awsRegion;
    String builderAwsSecretAccessKey;
    String builderAwsAccessKeyId;
    String builderAwsSessionToken;

    // Rebuild the image if the Python version changes but the gitCommitSha remains the same.
    if (registryType.equalsIgnoreCase(REGISTRY_TYPE_ECR)) {
      var credentials = awsCredentialsService.createTemporaryCredentials();
      builderAwsSecretAccessKey = credentials.awsSecretAccessKey();
      builderAwsAccessKeyId = credentials.awsAccessKeyId();
      builderAwsSessionToken = credentials.awsSessionToken();
      awsRegion = credentials.region();
      if ((actualDataJobDeployment == null
              || desiredDataJobDeployment
                  .getPythonVersion()
                  .equals(actualDataJobDeployment.getPythonVersion()))
          && ecrRegistryInterface.checkEcrImageExists(imageName, credentials)) {
        log.trace("Data Job image {} already exists and nothing else to do.", imageName);
        return true;
      }
    } else {
      builderAwsSecretAccessKey = REGISTRY_TYPE_GENERIC;
      builderAwsAccessKeyId = REGISTRY_TYPE_GENERIC;
      builderAwsSessionToken = REGISTRY_TYPE_GENERIC;
      awsRegion = REGISTRY_TYPE_GENERIC;

      // Check if the image exists in the Jfrog artifactory
      if (registryType.equalsIgnoreCase(REGISTRY_TYPE_JFROG)
          && jfrogRegistryInterface != null
          && (actualDataJobDeployment == null
              || desiredDataJobDeployment
                  .getPythonVersion()
                  .equals(actualDataJobDeployment.getPythonVersion()))
          && jfrogRegistryInterface.checkJfrogImageExists(
              dataJob.getName() + "/" + desiredDataJobDeployment.getGitCommitSha())) {
        log.trace("Data Job image {} already exists and nothing else to do.", imageName);
        return true;
      }
    }

    String builderJobName = getBuilderJobName(desiredDataJobDeployment.getDataJobName());

    log.debug("Check if old builder job {} exists", builderJobName);
    if (controlKubernetesService.listJobs().contains(builderJobName)) {
      log.debug("Delete old builder job {}", builderJobName);
      controlKubernetesService.deleteJob(builderJobName);

      // Wait for the old job to be deleted to avoid conflicts
      while (controlKubernetesService.listJobs().contains(builderJobName)) {
        Thread.sleep(1000);
      }
    }

    if (REGISTRY_TYPE_ECR.equalsIgnoreCase(registryType)) {
      ecrRegistryInterface.createRepository(
          DockerImageName.getImagePath(dockerRepositoryUrl) + "/" + dataJob.getName(),
          awsCredentialsService.createTemporaryCredentials());
    }

    var args =
        Arrays.asList(
            builderAwsAccessKeyId,
            builderAwsSecretAccessKey,
            awsRegion,
            dockerRepositoryUrl,
            gitUsername,
            gitPassword,
            gitRepo,
            registryType,
            registryUsername,
            registryPassword,
            builderAwsSessionToken);
    var envs = getBuildParameters(dataJob, desiredDataJobDeployment);
    String builderImage =
        supportedPythonVersions.getBuilderImage(desiredDataJobDeployment.getPythonVersion());

    log.info(
        "Creating builder job {} for data job version {}",
        builderJobName,
        desiredDataJobDeployment.getGitCommitSha());
    controlKubernetesService.createJob(
        builderJobName,
        builderImage,
        dataJob.getJobConfig().getTeam(),
        false,
        false,
        envs,
        args,
        null,
        null,
        builderJobImagePullPolicy,
        kubernetesResources.builderRequests(),
        kubernetesResources.builderLimits(),
        builderSecurityContextRunAsUser,
        builderSecurityContextRunAsGroup,
        builderSecurityContextFsGroup,
        builderServiceAccountName,
        dockerRegistryService.registrySecret());

    log.debug(
        "Waiting for builder job {} for data job version {}",
        builderJobName,
        desiredDataJobDeployment.getGitCommitSha());

    var condition =
        controlKubernetesService.watchJob(
            builderJobName, builderTimeoutSeconds, s -> log.debug("Wait status: {}", s));

    log.debug("Finished watching builder job {}. Condition is: {}", builderJobName, condition);
    String logs = null;
    try {
      log.info("Get logs of builder job {}", builderJobName);
      logs = controlKubernetesService.getPodLogs(builderJobName);
    } catch (Exception e) {
      // wrap in Kubernetes exception in case it's ApiException - in order to log more details.
      String message =
          new KubernetesException("Could not get pod " + builderJobName + " logs", e).getMessage();
      log.warn("Could not find logs from builder job {}; reason: {}", builderJobName, message);
    }
    if (!condition.isSuccess()) {
      notificationHelper.verifyBuilderResult(
          builderJobName, dataJob, desiredDataJobDeployment, condition, logs, sendNotification);
    } else {
      log.info("Builder job {} finished successfully. Will delete it now", builderJobName);
      log.info(
          "Image {} has been built. Will now schedule job {} for execution",
          imageName,
          dataJob.getName());
      try {
        controlKubernetesService.deleteJob(builderJobName);
      } catch (Exception e) {
        log.warn("Failed to delete builder job {}; reason: {}", builderJobName, e.getMessage());
      }
    }
    // we are using Kubernetes TTL Controller with ttlSecondsAfterFinished to clean up jobs in case
    // of failure
    return condition.isSuccess();
  }

  /**
   * If building new deployment of a data job has started (by buildImage), it is canceled/stopped.
   *
   * @param dataJobName the name of the data job
   */
  public void cancelBuildingJob(String dataJobName) {
    log.info("Cancel builder job for data job {}", dataJobName);
    deleteBuilderJob(dataJobName);
  }

  /**
   * See if the data job is currently in progress of being built.
   *
   * @param dataJobName the name of the data job
   * @return true if there's builder running for the given data job
   */
  public boolean isBuildingJobInProgress(String dataJobName) {
    try {
      return controlKubernetesService.listJobs().contains(getBuilderJobName(dataJobName));
    } catch (ApiException e) {
      throw new KubernetesException("Cannot determine if deployment is in progress", e);
    }
  }

  private Map<String, String> getBuildParameters(
      DataJob dataJob, DesiredDataJobDeployment jobDeployment) {
    String jobName = dataJob.getName();
    String jobVersion = jobDeployment.getGitCommitSha();
    String pythonVersion = jobDeployment.getPythonVersion();

    String dataJobBaseImage = supportedPythonVersions.getJobBaseImage(pythonVersion);

    return Map.ofEntries(
        entry("JOB_NAME", jobName),
        entry("DATA_JOB_NAME", jobName),
        entry("GIT_COMMIT", jobVersion),
        entry("JOB_GITHASH", jobVersion),
        entry("GIT_BRANCH", gitDataJobsBranch),
        entry("IMAGE_REGISTRY_PATH", dockerRepositoryUrl),
        entry("BASE_IMAGE", dataJobBaseImage),
        entry("EXTRA_ARGUMENTS", builderJobExtraArgs),
        entry("GIT_SSL_ENABLED", Boolean.toString(gitDataJobsSslEnabled)));
  }

  private boolean unsupportedRegistryType(String registry) {
    return !registry.equalsIgnoreCase(REGISTRY_TYPE_GENERIC)
        && !registry.equalsIgnoreCase(REGISTRY_TYPE_ECR)
        && !registry.equalsIgnoreCase(REGISTRY_TYPE_JFROG);
  }

  private static String getBuilderJobName(String dataJobName) {
    return String.format("builder-%s", dataJobName);
  }

  private void deleteBuilderJob(String dataJobName) {
    String builderJobName = getBuilderJobName(dataJobName);
    try {
      if (controlKubernetesService.listJobs().contains(builderJobName)) {
        controlKubernetesService.deleteJob(builderJobName);
      }
    } catch (ApiException e) {
      if (e.getCode() == 404) {
        log.info("Builder job for {} has been already deleted.", dataJobName);
      } else {
        throw new ExternalSystemError(ExternalSystemError.MainExternalSystem.KUBERNETES, e);
      }
    }
  }
}
