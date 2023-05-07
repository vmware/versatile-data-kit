/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.google.gson.Gson;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import io.kubernetes.client.openapi.ApiException;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.Validate;
import org.springframework.beans.factory.annotation.Value;
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
public class JobImageDeployer {

  // TODO: Out of the image we pick only the python vdk module. Remove when property deprecated
  // It may make sense to just pass the module name as argument instead of an image ???
  @Value("${datajobs.vdk.image}")
  private String vdkImage;

  @Value("${datajobs.docker.registrySecret:}")
  private String dockerRegistrySecret = "";

  @Value("${datajobs.vdk.docker.registrySecret:}")
  private String vdkSdkDockerRegistrySecret = "";

  @Value("${datajobs.deployment.readOnlyRootFilesystem:}")
  private boolean readOnlyRootFilesystem;

  private static final String VOLUME_NAME = "vdk";
  private static final String VOLUME_MOUNT_PATH = "/vdk";
  private static final String EPHEMERAL_VOLUME_NAME = "tmpfs";
  private static final String EPHEMERAL_VOLUME_MOUNT_PATH = "/var/tmp";
  private static final String KEYTAB_PRINCIPAL_ENV = "VDK_KEYTAB_PRINCIPAL";
  private static final String KEYTAB_FOLDER_ENV = "VDK_KEYTAB_FOLDER";
  private static final String KEYTAB_FILENAME_ENV = "VDK_KEYTAB_FILENAME";
  private static final String ATTEMPT_ID = "VDK_ATTEMPT_ID";
  private static final String BASE_CONFIG_FOLDER = "VDK_BASE_CONFIG_FOLDER";

  private final JobCredentialsService jobCredentialsService;
  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final VdkOptionsReader vdkOptionsReader;
  private final DataJobDefaultConfigurations defaultConfigurations;
  private final DeploymentProgress deploymentProgress;
  private final KubernetesResources kubernetesResources;
  private final JobCommandProvider jobCommandProvider;
  private final SupportedPythonVersions supportedPythonVersions;

  public Optional<JobDeploymentStatus> readScheduledJob(String dataJobName) {
    Optional<JobDeploymentStatus> jobDeployment =
        dataJobsKubernetesService.readCronJob(getCronJobName(dataJobName));
    if (jobDeployment.isPresent()) {
      jobDeployment.get().setDataJobName(dataJobName);
    }
    return jobDeployment;
  }

  public List<JobDeploymentStatus> readScheduledJobs() {
    return dataJobsKubernetesService.readJobDeploymentStatuses();
  }

  /**
   * Schedules for execution a data job at kubernetes cluster.
   *
   * @param dataJob the data job being deployed
   * @param jobDeployment the deployment information necessary to exeucte the deployment
   * @param sendNotification to sent or not notification (not it is sent only in case of failure,
   *     caller is responsible for sending on success or in case of an exception)
   * @param lastDeployedBy the name of the user that last deployed the data job
   * @return true if it is successful and false if not.
   */
  public boolean scheduleJob(
      DataJob dataJob,
      JobDeployment jobDeployment,
      Boolean sendNotification,
      String lastDeployedBy) {
    Validate.notNull(jobDeployment, "jobDeployment should not be null");
    Validate.notNull(jobDeployment.getImageName(), "Image name is expected in jobDeployment");
    try {
      return updateCronJobWithNotification(
          dataJob, jobDeployment, sendNotification, lastDeployedBy);
    } catch (ApiException e) {
      throw new KubernetesException("Failed to schedule job", e);
    }
  }

  private boolean updateCronJobWithNotification(
      DataJob dataJob, JobDeployment jobDeployment, Boolean sendNotification, String lastDeployedBy)
      throws ApiException {
    try {
      log.info("Update cron job for data job {}", dataJob.getName());
      updateCronJob(dataJob, jobDeployment, lastDeployedBy);
    } catch (ApiException apiException) {
      if (apiException.getCode() == 422) {
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
          deploymentProgress.failed(
              dataJob.getJobConfig(),
              jobDeployment,
              DeploymentStatus.USER_ERROR,
              msg,
              sendNotification);
          return false;
        } catch (Exception ignored) {
          log.debug("Failed to parse ApiException body, re-throwing it.: ", ignored);
        }
      }
      throw apiException;
    }
    return true;
  }

  /**
   * Remove a Data Job from Kubernetes cluster.
   *
   * @param dataJobName the job name
   */
  public void unScheduleJob(@NonNull String dataJobName) {
    String cronJobName = getCronJobName(dataJobName);
    try {
      if (dataJobsKubernetesService.listCronJobs().contains(cronJobName)) {
        dataJobsKubernetesService.deleteCronJob(cronJobName);
      }
    } catch (ApiException e) {
      // TODO: technically if code is 4xx, k8s errors are more of Bug exception ...
      throw new KubernetesException("Failed to un-schedule job", e);
    }
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
  private void updateCronJob(DataJob dataJob, JobDeployment jobDeployment, String lastDeployedBy)
      throws ApiException {
    log.debug("Deploy cron job for data job {}", dataJob);

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

    var principalName = jobCredentialsService.getJobPrincipalName(jobName);
    var vdkEnvs = vdkOptionsReader.readVdkOptions(jobName);

    var jobContainerEnvVars = new HashMap<String, String>();

    String keytabFolder = "/credentials";
    String jobKeytabKubernetesSecretName =
        JobCredentialsService.getJobKeytabKubernetesSecretName(jobName);
    var secretVolume =
        KubernetesService.volume(jobKeytabKubernetesSecretName, jobKeytabKubernetesSecretName);
    var secretVolumeMount =
        KubernetesService.volumeMount(jobKeytabKubernetesSecretName, keytabFolder, true);

    jobContainerEnvVars.put(KEYTAB_PRINCIPAL_ENV, principalName);
    jobContainerEnvVars.put(KEYTAB_FOLDER_ENV, keytabFolder);
    jobContainerEnvVars.put(KEYTAB_FILENAME_ENV, JobCredentialsService.K8S_KEYTAB_KEY_IN_SECRET);
    jobContainerEnvVars.put(ATTEMPT_ID, "$metadata.name");
    jobContainerEnvVars.put(BASE_CONFIG_FOLDER, EPHEMERAL_VOLUME_MOUNT_PATH);
    jobContainerEnvVars.putAll(getSystemDefaults());
    jobContainerEnvVars.putAll(vdkEnvs);
    jobContainerEnvVars.putAll(jobConfigBasedEnvVars(dataJob.getJobConfig()));

    var jobCommand = jobCommandProvider.getJobCommand(jobName);

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
            "Always",
            defaultConfigurations.dataJobRequests(),
            defaultConfigurations.dataJobLimits(),
            null,
            jobCommand);
    var vdkCommand =
        List.of(
            "/bin/bash",
            "-c",
            "cp -r $(python -c \"from distutils.sysconfig import get_python_lib;"
                + " print(get_python_lib())\") /vdk/. && cp /usr/local/bin/vdk /vdk/.");
    var jobVdkImage = getJobVdkImage(jobDeployment);
    var jobInitContainer =
        KubernetesService.container(
            "vdk",
            jobVdkImage,
            false,
            readOnlyRootFilesystem,
            Map.of(),
            List.of(),
            List.of(volumeMount, secretVolumeMount, ephemeralVolumeMount),
            "Always",
            kubernetesResources.dataJobInitContainerRequests(),
            kubernetesResources.dataJobInitContainerLimits(),
            null,
            vdkCommand);
    // TODO: changing imagePullPolicy to IfNotPresent might be necessary optimization when running
    // thousands of jobs.
    // At the moment Always is chosen because it's possible to have a change in image that is not
    // detected.

    Map<String, String> jobDeploymentAnnotations = new HashMap<>();
    var jobLabels = getJobLabels(dataJob, jobDeployment);
    var jobAnnotations =
        getJobAnnotations(dataJob, lastDeployedBy, jobDeployment.getPythonVersion());

    String cronJobName = getCronJobName(jobName);
    boolean enabled = jobDeployment.getEnabled() == null || jobDeployment.getEnabled();
    if (dataJobsKubernetesService.listCronJobs().contains(cronJobName)) {
      dataJobsKubernetesService.updateCronJob(
          cronJobName,
          jobDeployment.getImageName(),
          schedule,
          enabled,
          jobContainer,
          jobInitContainer,
          Arrays.asList(volume, secretVolume, ephemeralVolume),
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          List.of(dockerRegistrySecret, vdkSdkDockerRegistrySecret));
    } else {
      dataJobsKubernetesService.createCronJob(
          cronJobName,
          jobDeployment.getImageName(),
          schedule,
          enabled,
          jobContainer,
          jobInitContainer,
          Arrays.asList(volume, secretVolume, ephemeralVolume),
          jobDeploymentAnnotations,
          jobAnnotations,
          jobLabels,
          List.of(dockerRegistrySecret, vdkSdkDockerRegistrySecret));
    }
  }

  private String getJobVdkImage(JobDeployment jobDeployment) {
    // TODO: Refactor when vdkImage is deprecated.
    if (!supportedPythonVersions.getSupportedPythonVersions().isEmpty()
        && supportedPythonVersions.isPythonVersionSupported(jobDeployment.getPythonVersion())) {
      return supportedPythonVersions.getVdkImage(jobDeployment.getPythonVersion());
    } else {
      if (StringUtils.isNotBlank(jobDeployment.getVdkVersion())
          && StringUtils.isNotBlank(vdkImage)) {
        return DockerImageName.updateImageWithTag(vdkImage, jobDeployment.getVdkVersion());
      } else {
        return vdkImage;
      }
    }
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

  // Public for integration testing purposes
  public static String getCronJobName(String jobName) {
    return jobName;
  }
}
