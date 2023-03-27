/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import static java.util.Map.entry;

import com.vmware.taurus.exception.ExternalSystemError;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobDeployment;
import io.kubernetes.client.openapi.ApiException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Map;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * Responsible for building docker images for data jobs. The images are pushed to a docker
 * repository and then deployed on kubernetes.
 */
@Component
public class JobImageBuilder {
  private static final Logger log = LoggerFactory.getLogger(JobImageBuilder.class);

  private static final int BUILDER_TIMEOUT_SECONDS = 1800;
  private static final String REGISTRY_TYPE_ECR = "ecr";
  private static final String REGISTRY_TYPE_GENERIC = "generic";

  @Value("${datajobs.git.url}")
  private String gitRepo;

  @Value("${datajobs.git.username}")
  private String gitUsername;

  @Value("${datajobs.git.password}")
  private String gitPassword;

  @Value("${datajobs.docker.repositoryUrl}")
  private String dockerRepositoryUrl;

  @Value("${datajobs.docker.registryType}")
  private String registryType;

  @Value("${datajobs.docker.registryUsername:}")
  private String registryUsername;

  @Value("${datajobs.docker.registryPassword:}")
  private String registryPassword;

  @Value("${datajobs.deployment.dataJobBaseImage:python:3.9-slim}")
  private String deploymentDataJobBaseImage;

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

  private final ControlKubernetesService controlKubernetesService;
  private final DockerRegistryService dockerRegistryService;
  private final DeploymentNotificationHelper notificationHelper;
  private final KubernetesResources kubernetesResources;
  private final AWSCredentialsService awsCredentialsService;
  private final SupportedPythonVersions supportedPythonVersions;

  public JobImageBuilder(
      ControlKubernetesService controlKubernetesService,
      DockerRegistryService dockerRegistryService,
      DeploymentNotificationHelper notificationHelper,
      KubernetesResources kubernetesResources,
      AWSCredentialsService awsCredentialsService,
      SupportedPythonVersions supportedPythonVersions) {

    this.controlKubernetesService = controlKubernetesService;
    this.dockerRegistryService = dockerRegistryService;
    this.notificationHelper = notificationHelper;
    this.kubernetesResources = kubernetesResources;
    this.awsCredentialsService = awsCredentialsService;
    this.supportedPythonVersions = supportedPythonVersions;
  }

  /**
   * Builds and pushes a docker image for a data job. Runs a job on k8s which is responsible for
   * building and pushing the data job image. This call will block until the builder job has
   * finished. Notifies the users on failure.
   *
   * @param imageName Full name of the image to build.
   * @param dataJob Information about the data job.
   * @param jobDeployment Information about the data job deployment.
   * @param sendNotification
   * @return True if build and push was successful. False otherwise.
   * @throws ApiException
   * @throws IOException
   * @throws InterruptedException
   */
  public boolean buildImage(
      String imageName, DataJob dataJob, JobDeployment jobDeployment, Boolean sendNotification)
      throws ApiException, IOException, InterruptedException {
    var credentials = awsCredentialsService.createTemporaryCredentials();

    String builderAwsSecretAccessKey = credentials.awsSecretAccessKey();
    String builderAwsAccessKeyId = credentials.awsAccessKeyId();
    String builderAwsSessionToken = credentials.awsSessionToken();
    String awsRegion = credentials.region();

    log.info("Build data job image for job {}. Image name: {}", dataJob.getName(), imageName);
    if (!StringUtils.isBlank(registryType)) {
      if (unsupportedRegistryType(registryType)) {
        log.debug(
            String.format(
                "Unsupported registry type: %s available options %s/%s",
                registryType, REGISTRY_TYPE_ECR, REGISTRY_TYPE_GENERIC));
        return false;
      }
    }

    if (dockerRegistryService.dataJobImageExists(imageName)) {
      log.debug("Data Job image {} already exists and nothing else to do.", imageName);
      return true;
    }

    String builderJobName = getBuilderJobName(jobDeployment.getDataJobName());

    log.debug("Check if old builder job {} exists", builderJobName);
    if (controlKubernetesService.listJobs().contains(builderJobName)) {
      log.debug("Delete old builder job {}", builderJobName);
      controlKubernetesService.deleteJob(builderJobName);

      // Wait for the old job to be deleted to avoid conflicts
      while (controlKubernetesService.listJobs().contains(builderJobName)) {
        Thread.sleep(1000);
      }
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
    var envs = getBuildParameters(dataJob, jobDeployment);

    log.info(
        "Creating builder job {} for data job version {}",
        builderJobName,
        jobDeployment.getGitCommitSha());
    controlKubernetesService.createJob(
        builderJobName,
        dockerRegistryService.builderImage(),
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
        jobDeployment.getGitCommitSha());

    var condition =
        controlKubernetesService.watchJob(
            builderJobName, BUILDER_TIMEOUT_SECONDS, s -> log.debug("Wait status: {}", s));

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
          builderJobName, dataJob, jobDeployment, condition, logs, sendNotification);
    } else {
      log.info("Builder job {} finished successfully. Will delete it now", builderJobName);
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

  private Map<String, String> getBuildParameters(DataJob dataJob, JobDeployment jobDeployment) {
    String jobName = dataJob.getName();
    String jobVersion = jobDeployment.getGitCommitSha();
    String baseImage = null;
    String pythonVersion = jobDeployment.getPythonVersion();

    // TODO: Remove this part when datajobs.deployment.dataJobBaseImage is deprecated.
    if (deploymentDataJobBaseImage != null) {
      baseImage = deploymentDataJobBaseImage;
    } else if (pythonVersion != null && supportedPythonVersions.isPythonVersionSupported(pythonVersion)) {
      baseImage = supportedPythonVersions.getJobBaseImage(pythonVersion);
    } else {
      baseImage = supportedPythonVersions.getDefaultJobBaseImage();
    }

    return Map.ofEntries(
        entry("JOB_NAME", jobName),
        entry("DATA_JOB_NAME", jobName),
        entry("GIT_COMMIT", jobVersion),
        entry("JOB_GITHASH", jobVersion),
        entry("IMAGE_REGISTRY_PATH", dockerRepositoryUrl),
        entry("BASE_IMAGE", baseImage),
        entry("EXTRA_ARGUMENTS", builderJobExtraArgs),
        entry("GIT_SSL_ENABLED", Boolean.toString(gitDataJobsSslEnabled)));
  }

  private boolean unsupportedRegistryType(String registry) {
    return !registry.equalsIgnoreCase(REGISTRY_TYPE_GENERIC)
        && !registry.equalsIgnoreCase(REGISTRY_TYPE_ECR);
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
