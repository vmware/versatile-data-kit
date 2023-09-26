/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.google.gson.Gson;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.Validate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

import java.time.OffsetDateTime;
import java.util.*;

/**
 * Takes care of deploying a Data Job in Kubernetes and scheduling it to run. Currently this is
 * deployed as CronJob. For more details see #updateCronJob doc.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class JobImageDeployerV2 {

  @Value("${datajobs.docker.registrySecret:}")
  private String dockerRegistrySecret = "";

  @Value("${datajobs.vdk.docker.registrySecret:}")
  private String vdkSdkDockerRegistrySecret = "";

  @Value("${datajobs.deployment.readOnlyRootFilesystem:}")
  private boolean readOnlyRootFilesystem;

  @Value("${datajobs.deployment.jobImagePullPolicy:IfNotPresent}")
  private String jobImagePullPolicy;

  private static final String VOLUME_NAME = "vdk";
  private static final String VOLUME_MOUNT_PATH = "/vdk";
  private static final String EPHEMERAL_VOLUME_NAME = "tmpfs";
  private static final String EPHEMERAL_VOLUME_MOUNT_PATH = "/var/tmp";
  private static final String KEYTAB_PRINCIPAL_ENV = "VDK_KEYTAB_PRINCIPAL";
  private static final String KEYTAB_FOLDER_ENV = "VDK_KEYTAB_FOLDER";
  private static final String KEYTAB_FILENAME_ENV = "VDK_KEYTAB_FILENAME";
  private static final String ATTEMPT_ID = "VDK_ATTEMPT_ID";
  private static final String BASE_CONFIG_FOLDER = "VDK_BASE_CONFIG_FOLDER";
  private static final String VDK_TEMPORARY_WRITE_DIRECTORY = "VDK_TEMPORARY_WRITE_DIRECTORY";
  private static final String TEMPORARY_WRITE_DIRECTORY_PATH = EPHEMERAL_VOLUME_MOUNT_PATH;
  private static final String KEYTAB_FOLDER = "/credentials";

  private final JobCredentialsService jobCredentialsService;
  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final VdkOptionsReader vdkOptionsReader;
  private final DataJobDefaultConfigurations defaultConfigurations;
  private final DeploymentProgress deploymentProgress;
  private final KubernetesResources kubernetesResources;
  private final JobCommandProvider jobCommandProvider;
  private final SupportedPythonVersions supportedPythonVersions;

  /**
   * Schedules for execution a data job at kubernetes cluster.
   *
   * @param dataJob the data job to be updated or created.
   * @param jobDeployment the deployment information necessary to execute the deployment.
   * @param sendNotification if it is true the method will send a notification to the end user.
   * @param lastDeployedBy the name of the user that last deployed the data job
   * @param dataJobDeploymentNames list of actual data job deployment names returned by Kubernetes.
   * @return true if it is successful and false if not.
   */
  public boolean scheduleJob(
      DataJob dataJob,
      JobDeployment jobDeployment,
      Boolean sendNotification,
      String lastDeployedBy,
      Set<String> dataJobDeploymentNames) {
    Validate.notNull(jobDeployment, "jobDeployment should not be null");
    Validate.notNull(jobDeployment.getImageName(), "Image name is expected in jobDeployment");
    log.info("Update cron job for data job {}", dataJob.getName());

    try {
      updateCronJob(dataJob, jobDeployment, lastDeployedBy, dataJobDeploymentNames);
      return true;
    } catch (ApiException e) {
      return catchApiException(dataJob, sendNotification, e);
    }
  }

  private boolean catchApiException(
      DataJob dataJob, Boolean sendNotification, ApiException apiException) {
    if (apiException.getCode() == HttpStatus.UNPROCESSABLE_ENTITY.value()) {
      try {
        Gson gson = new Gson();
        String msg =
            NotificationContent.getErrorBody(
                "Tried to deploy a data job",
                "There has been an error in the configuration of your data job.",
                "Your new/updated job was not deployed. Your job will run its latest successfully"
                    + " deployed version (if any) as scheduled.",
                "Please fix the job's configuration");
        Map<Object, Object> error = gson.fromJson(apiException.getResponseBody(), HashMap.class);
        if (error != null) {
          log.error(
              "Failed to schedule job due to Kubernetes client error (422). Generally input"
                  + " validation should be done earlier. If this exception happens, most likely"
                  + " we need to do some better input validation at client library. We are"
                  + " assuming all k8s client error when creating cron job can be only customer"
                  + " misconfiguration sending notification and reporting as user error",
              apiException);
          msg =
              NotificationContent.getErrorBody(
                  "Tried to deploy a data job",
                  "There has been an error in the configuration of your data job : "
                      + error.get("message"),
                  "Your new/updated job was not deployed. Your job will run its latest"
                      + " successfully deployed version (if any) as scheduled.",
                  "Please fix the job's configuration");
          log.error(msg);
        }
        deploymentProgress.failed(dataJob, DeploymentStatus.USER_ERROR, msg, sendNotification);
        return false;
      } catch (Exception ignored) {
        log.debug("Failed to parse ApiException body: ", ignored);
      }
    }

    throw new KubernetesException("Failed to schedule job", apiException);
  }

  // Public for integration testing purposes
  public static String getCronJobName(String jobName) {
    return jobName;
  }

  private Map<String, String> getSystemDefaults() {
    Map<String, String> systemDefaults = new LinkedHashMap<>();

    systemDefaults.put("LOG_CONFIG", "CLOUD");
    systemDefaults.put("MONITORING_ENABLED", String.valueOf(true));
    return systemDefaults;
  }

  /**
   * Creates data job as CronJob against the Kubernetes API:
   *
   * <p>The implementation includes vdk as initContainer. The main container stores the job with its
   * dependencies and shared emptyDir volume between the two containers.
   *
   * <p>Requires image with pip installed vdk so it can be found in the site-packages directory of
   * the vdk container. This is in order for the initContainer (vdk) primitive to copy it from there
   * into the shared folder to be used by the container which runs the job.
   *
   * @param dataJob The data job
   * @param jobDeployment Deployment configuration
   */
  private void updateCronJob(
      DataJob dataJob,
      JobDeployment jobDeployment,
      String lastDeployedBy,
      Set<String> dataJobDeploymentNames)
      throws ApiException {
    log.debug("Deploy cron job for data job {}", dataJob);

    String jobName = dataJob.getName();
    String dataJobDeploymentName = getCronJobName(jobName);
    KubernetesService.CronJob cronJob =
        getCronJob(dataJobDeploymentName, dataJob, jobDeployment, lastDeployedBy);

    // TODO [miroslavi] store sha in annotation???
    String cronJobSha =
        dataJobsKubernetesService.getCronJobSha512(cronJob, JobAnnotation.DEPLOYED_DATE);

    if (dataJobDeploymentNames.contains(dataJobDeploymentName)) {
      if (!cronJobSha.equals(dataJob.getDataJobDeployment().getDeploymentVersionSha())) {
        dataJobsKubernetesService.updateCronJob(cronJob);
      }
    } else {
      dataJobsKubernetesService.createCronJob(cronJob);
    }

    dataJob.getDataJobDeployment().setDeploymentVersionSha(cronJobSha);
  }

  /**
   * Returns the environment variables set to vdk that are based on job configuration. Those are
   * automatically injected during cloud runs
   */
  private static HashMap<String, String> jobConfigBasedEnvVars(JobConfig config) {
    HashMap<String, String> envVars = new LinkedHashMap<>();
    if (StringUtils.isNotBlank(config.getDbDefaultType())) {
      envVars.put("VDK_DB_DEFAULT_TYPE", config.getDbDefaultType());
    }
    if (StringUtils.isNotBlank(config.getTeam())) {
      envVars.put("VDK_JOB_TEAM", config.getTeam());
    }
    if (config.getEnableExecutionNotifications() != null) {
      envVars.put(
          "VDK_ENABLE_EXECUTION_NOTIFICATIONS",
          config.getEnableExecutionNotifications().toString());
    }
    if (config.getNotifiedOnJobSuccess() != null) {
      envVars.put(
          "VDK_NOTIFIED_ON_JOB_SUCCESS", String.join(",", config.getNotifiedOnJobSuccess()));
    }
    if (config.getNotifiedOnJobFailurePlatformError() != null) {
      envVars.put(
          "VDK_NOTIFIED_ON_JOB_FAILURE_PLATFORM_ERROR",
          String.join(",", config.getNotifiedOnJobFailurePlatformError()));
    }
    if (config.getNotifiedOnJobFailureUserError() != null) {
      envVars.put(
          "VDK_NOTIFIED_ON_JOB_FAILURE_USER_ERROR",
          String.join(",", config.getNotifiedOnJobFailureUserError()));
    }
    if (config.getNotifiedOnJobDeploy() != null) {
      envVars.put("VDK_NOTIFIED_ON_JOB_DEPLOY", String.join(",", config.getNotifiedOnJobDeploy()));
    }
    return envVars;
  }

  private Map<String, String> getJobLabels(DataJob dataJob, JobDeployment jobDeployment) {
    Map<String, String> jobPodLabels = new HashMap<>();
    // This label provides means during watching to select only Kubernetes jobs which represent data
    // jobs.
    // See DataJobStatusMonitor.watchJobs for how the label is used
    jobPodLabels.put(JobLabel.TYPE.getValue(), "DataJob");
    jobPodLabels.put(JobLabel.NAME.getValue(), dataJob.getName());
    jobPodLabels.put(JobLabel.VERSION.getValue(), jobDeployment.getGitCommitSha());

    return jobPodLabels;
  }

  private Map<String, String> getJobAnnotations(
      DataJob dataJob, String deployedBy, String pythonVersion) {
    Map<String, String> jobPodAnnotations = new HashMap<>();
    jobPodAnnotations.put(JobAnnotation.SCHEDULE.getValue(), dataJob.getJobConfig().getSchedule());
    jobPodAnnotations.put(JobAnnotation.EXECUTION_TYPE.getValue(), "scheduled");
    jobPodAnnotations.put(JobAnnotation.DEPLOYED_BY.getValue(), deployedBy);
    jobPodAnnotations.put(JobAnnotation.DEPLOYED_DATE.getValue(), OffsetDateTime.now().toString());
    jobPodAnnotations.put(
        JobAnnotation.STARTED_BY.getValue(), "scheduled/runtime"); // TODO are those valid?
    jobPodAnnotations.put(
        JobAnnotation.UNSCHEDULED.getValue(),
        (StringUtils.isEmpty(dataJob.getJobConfig().getSchedule()) ? "true" : "false"));
    jobPodAnnotations.put(JobAnnotation.PYTHON_VERSION.getValue(), pythonVersion);
    return jobPodAnnotations;
  }

  private Map<String, String> getJobContainerEnvVars(String jobName, JobConfig jobConfig) {
    String principalName = jobCredentialsService.getJobPrincipalName(jobName);
    Map<String, String> vdkEnvs = vdkOptionsReader.readVdkOptions(jobName);

    Map<String, String> jobContainerEnvVars = new HashMap<>();
    jobContainerEnvVars.put(KEYTAB_PRINCIPAL_ENV, principalName);
    jobContainerEnvVars.put(KEYTAB_FOLDER_ENV, KEYTAB_FOLDER);
    jobContainerEnvVars.put(KEYTAB_FILENAME_ENV, JobCredentialsService.K8S_KEYTAB_KEY_IN_SECRET);
    jobContainerEnvVars.put(ATTEMPT_ID, "$metadata.name");
    jobContainerEnvVars.put(BASE_CONFIG_FOLDER, EPHEMERAL_VOLUME_MOUNT_PATH);
    jobContainerEnvVars.put(VDK_TEMPORARY_WRITE_DIRECTORY, TEMPORARY_WRITE_DIRECTORY_PATH);
    jobContainerEnvVars.putAll(getSystemDefaults());
    jobContainerEnvVars.putAll(vdkEnvs);
    jobContainerEnvVars.putAll(jobConfigBasedEnvVars(jobConfig));

    return jobContainerEnvVars;
  }

  // TODO migrate to new Data Job deployment
  private KubernetesService.CronJob getCronJob(
      String dataJobDeploymentName,
      DataJob dataJob,
      JobDeployment jobDeployment,
      String lastDeployedBy) {
    // Schedule defaults to Feb 30 (i.e. never) if no schedule has been given.
    String schedule =
        StringUtils.isEmpty(dataJob.getJobConfig().getSchedule())
            ? "0 0 30 2 *"
            : dataJob.getJobConfig().getSchedule();

    var jobName = dataJob.getName();
    var volume = KubernetesService.volume(VOLUME_NAME);
    var volumeMount = KubernetesService.volumeMount(VOLUME_NAME, VOLUME_MOUNT_PATH, false);
    var ephemeralVolume = KubernetesService.volume(EPHEMERAL_VOLUME_NAME);
    var ephemeralVolumeMount =
        KubernetesService.volumeMount(EPHEMERAL_VOLUME_NAME, EPHEMERAL_VOLUME_MOUNT_PATH, false);
    var jobContainerEnvVars = getJobContainerEnvVars(jobName, dataJob.getJobConfig());

    String jobKeytabKubernetesSecretName =
        JobCredentialsService.getJobKeytabKubernetesSecretName(jobName);
    var secretVolume =
        KubernetesService.volume(jobKeytabKubernetesSecretName, jobKeytabKubernetesSecretName);
    var secretVolumeMount =
        KubernetesService.volumeMount(jobKeytabKubernetesSecretName, KEYTAB_FOLDER, true);

    var jobCommand = jobCommandProvider.getJobCommand(jobName);
    DataJobResources resources = jobDeployment.getResources();
    String cpuRequest =
        resources.getCpuRequest() != null && resources.getCpuRequest() > 0
            ? String.valueOf(resources.getCpuRequest())
            : defaultConfigurations.dataJobRequests().getCpu();
    String cpuLimit =
        resources.getCpuLimit() != null && resources.getCpuLimit() > 0
            ? String.valueOf(resources.getCpuLimit())
            : defaultConfigurations.dataJobLimits().getCpu();
    String memoryRequest =
        resources.getMemoryRequest() != null && resources.getMemoryRequest() > 0
            ? resources.getMemoryRequest() + "Mi"
            : defaultConfigurations.dataJobRequests().getMemory();
    String memoryLimit =
        resources.getMemoryLimit() != null && resources.getMemoryLimit() > 0
            ? resources.getMemoryLimit() + "Mi"
            : defaultConfigurations.dataJobLimits().getMemory();

    // The job name is used as the container name. This is something that we rely on later,
    // when watching for pod modifications in DataJobStatusMonitor.watchPods
    var jobContainer =
        KubernetesService.container(
            jobName,
            jobDeployment.getImageName(),
            false,
            readOnlyRootFilesystem,
            jobContainerEnvVars,
            List.of(),
            List.of(volumeMount, secretVolumeMount, ephemeralVolumeMount),
            jobImagePullPolicy,
            new KubernetesService.Resources(cpuRequest, memoryRequest),
            new KubernetesService.Resources(cpuLimit, memoryLimit),
            null,
            jobCommand);
    var vdkCommand =
        List.of(
            "/bin/bash",
            "-c",
            "cp -r $(python -c \"from distutils.sysconfig import get_python_lib;"
                + " print(get_python_lib())\") /vdk/. && cp /usr/local/bin/vdk /vdk/.");
    var jobVdkImage = supportedPythonVersions.getVdkImage(jobDeployment.getPythonVersion());
    var jobInitContainer =
        KubernetesService.container(
            "vdk",
            jobVdkImage,
            false,
            readOnlyRootFilesystem,
            Map.of(),
            List.of(),
            List.of(volumeMount, secretVolumeMount, ephemeralVolumeMount),
            jobImagePullPolicy,
            kubernetesResources.dataJobInitContainerRequests(),
            kubernetesResources.dataJobInitContainerLimits(),
            null,
            vdkCommand);

    var jobLabels = getJobLabels(dataJob, jobDeployment);
    var jobAnnotations =
        getJobAnnotations(dataJob, lastDeployedBy, jobDeployment.getPythonVersion());
    boolean enabled =
        (dataJob.getEnabled() == null || dataJob.getEnabled()) && jobDeployment.getEnabled();

    return KubernetesService.CronJob.builder()
        .name(dataJobDeploymentName)
        .image(jobDeployment.getImageName())
        .schedule(schedule)
        .enable(enabled)
        .jobContainer(jobContainer)
        .initContainer(jobInitContainer)
        .volumes(Arrays.asList(volume, secretVolume, ephemeralVolume))
        .jobAnnotations(jobAnnotations)
        .jobLabels(jobLabels)
        .imagePullSecret(List.of(dockerRegistrySecret, vdkSdkDockerRegistrySecret))
        .build();
  }
}
