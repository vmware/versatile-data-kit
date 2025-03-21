/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.datajobs.DeploymentModelConverter;
import com.vmware.taurus.exception.DataJobDeploymentNotFoundException;
import com.vmware.taurus.exception.ErrorMessage;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.notification.NotificationContent;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import io.kubernetes.client.openapi.ApiException;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

/**
 * CRUD operations for Versatile Data Kit deployments on kubernetes.
 *
 * <p>This class is in a transition from operating against Kubernetes to operating against the
 * database. Currently, only the enabled flag is stored in the database. Eventually, all deployment
 * information will be stored (and retrieved) from a database from a dedicated table.
 */
@Service
@RequiredArgsConstructor
public class DeploymentServiceV2 {

  private static final Logger log = LoggerFactory.getLogger(DeploymentServiceV2.class);

  private final DockerRegistryService dockerRegistryService;
  private final DeploymentProgress deploymentProgress;
  private final JobImageBuilder jobImageBuilder;
  private final JobImageDeployerV2 jobImageDeployer;
  private final SupportedPythonVersions supportedPythonVersions;
  private final DesiredJobDeploymentRepository desiredJobDeploymentRepository;
  private final ActualJobDeploymentRepository actualJobDeploymentRepository;
  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final JobsRepository jobsRepository;

  /**
   * This method updates an existing job deployment in the database. Only fields present in the job
   * deployment are updated, other fields are not overridden.
   *
   * @param dataJob the data job to which the deployment is associated
   * @param jobDeployment the deployment to patch with
   */
  public void patchDesiredDbDeployment(
      DataJob dataJob, JobDeployment jobDeployment, String userDeployer) {
    populateDeploymentForBackwardCompatibility(dataJob, jobDeployment);
    desiredJobDeploymentRepository
        .findById(dataJob.getName())
        .ifPresentOrElse(
            oldDeployment -> {
              var mergedDeployment =
                  DeploymentModelConverter.mergeDeployments(
                      oldDeployment, jobDeployment, userDeployer);
              saveNewDesiredDeployment(mergedDeployment, dataJob);
            },
            () -> {
              throw new DataJobDeploymentNotFoundException(dataJob.getName());
            });
  }

  /**
   * Create or update a deployment in the database. If the deployment already exists, behaves like
   * patch
   *
   * @param dataJob The data job to which the deployment is associated.
   * @param jobDeployment the new deployment.
   * @param userDeployer the user.
   */
  public void updateDesiredDbDeployment(
      DataJob dataJob, JobDeployment jobDeployment, String userDeployer) {
    populateDeploymentForBackwardCompatibility(dataJob, jobDeployment);
    desiredJobDeploymentRepository
        .findById(dataJob.getName())
        .ifPresentOrElse(
            oldDeployment -> patchDesiredDbDeployment(dataJob, jobDeployment, userDeployer),
            () -> {
              var newDeployment =
                  DeploymentModelConverter.toJobDeployment(userDeployer, jobDeployment);
              saveNewDesiredDeployment(newDeployment, dataJob);
            });
  }

  private void saveNewDesiredDeployment(DesiredDataJobDeployment deployment, DataJob dataJob) {
    deployment.setStatus(DeploymentStatus.NONE);
    deployment.setDataJob(dataJob);
    deployment.setUserInitiated(true);
    desiredJobDeploymentRepository.save(deployment);
  }

  /**
   * Updates or creates a Kubernetes CronJob based on the provided configuration.
   *
   * <p>This method takes a CronJob configuration and checks if a CronJob with the same name already
   * exists in the Kubernetes cluster. If the CronJob exists, it will be updated with the new
   * configuration; otherwise, a new CronJob will be created. The method ensures that the CronJob in
   * the cluster matches the desired state specified in the configuration.
   *
   * @param dataJob the data job to be deployed.
   * @param desiredJobDeployment the desired data job deployment to be deployed.
   * @param actualJobDeployment the actual data job deployment has been deployed.
   * @param isJobDeploymentPresentInKubernetes if it is true the data job deployment is present in
   *     Kubernetes.
   */
  @Measurable(includeArg = 0, argName = "data_job")
  public void updateDeployment(
      DataJob dataJob,
      DesiredDataJobDeployment desiredJobDeployment,
      ActualDataJobDeployment actualJobDeployment,
      boolean isJobDeploymentPresentInKubernetes) {
    if (desiredJobDeployment == null) {
      log.warn(
          "Skipping the data job [job_name={}] deployment due to the missing deployment data",
          dataJob.getName());
      return;
    }

    if (DeploymentStatus.USER_ERROR.equals(desiredJobDeployment.getStatus())
        || DeploymentStatus.PLATFORM_ERROR.equals(desiredJobDeployment.getStatus())) {
      log.trace(
          "Skipping the data job [job_name={}] deployment due to the previously failed deployment"
              + " [status={}]",
          dataJob.getName(),
          desiredJobDeployment.getStatus());
      return;
    }

    // Sends notification only when the deployment is initiated by the user.
    boolean sendNotification = Boolean.TRUE.equals(desiredJobDeployment.getUserInitiated());

    try {
      log.trace("Starting deployment of job {}", desiredJobDeployment.getDataJobName());
      deploymentProgress.started(dataJob.getJobConfig(), desiredJobDeployment);

      if (desiredJobDeployment.getPythonVersion() == null) {
        desiredJobDeployment.setPythonVersion(supportedPythonVersions.getDefaultPythonVersion());
      }

      String imageName =
          dockerRegistryService.dataJobImage(
              desiredJobDeployment.getDataJobName(), desiredJobDeployment.getGitCommitSha());

      // If a previously enabled job is being disabled, we don't want to build the image.
      if ((Boolean.FALSE.equals(desiredJobDeployment.getEnabled())
              && Boolean.TRUE.equals(actualJobDeployment.getEnabled()))
          || jobImageBuilder.buildImage(
              imageName, dataJob, desiredJobDeployment, actualJobDeployment, sendNotification)) {
        ActualDataJobDeployment actualJobDeploymentResult =
            jobImageDeployer.scheduleJob(
                dataJob,
                desiredJobDeployment,
                actualJobDeployment,
                sendNotification,
                isJobDeploymentPresentInKubernetes,
                imageName);

        if (actualJobDeploymentResult != null) {
          log.info(
              String.format(
                  "Successfully updated job: %s with version: %s",
                  desiredJobDeployment.getDataJobName(), desiredJobDeployment.getGitCommitSha()));

          deploymentProgress.completed(dataJob, actualJobDeploymentResult, sendNotification);
        }
      }
    } catch (ApiException e) {
      handleException(
          dataJob, desiredJobDeployment, sendNotification, new KubernetesException("", e));
    } catch (Exception e) {
      handleException(dataJob, desiredJobDeployment, sendNotification, e);
    }
  }

  public void deleteDesiredDeployment(String dataJobName) {
    if (desiredJobDeploymentRepository.existsById(dataJobName)) {
      desiredJobDeploymentRepository.deleteById(dataJobName);
    }
  }

  public void deleteActualDeployment(String dataJobName) {
    if (this.deploymentExistsOrInProgress(dataJobName)) {
      jobImageBuilder.cancelBuildingJob(dataJobName);
      jobImageDeployer.unScheduleJob(dataJobName);
      jobsRepository.updateDataJobEnabledByName(dataJobName, false);
    }

    actualJobDeploymentRepository.deleteById(dataJobName);
    deploymentProgress.deleted(dataJobName);
  }

  public Optional<ActualDataJobDeployment> readDeployment(String dataJobName) {
    return actualJobDeploymentRepository.findById(dataJobName);
  }

  public void updateDeploymentEnabledStatus(String dataJobName, Boolean enabledStatus) {
    desiredJobDeploymentRepository.updateDesiredDataJobDeploymentEnabledByDataJobName(
        dataJobName, enabledStatus);
  }

  public Map<String, DesiredDataJobDeployment> findAllDesiredDataJobDeployments() {
    return desiredJobDeploymentRepository.findAll().stream()
        .collect(Collectors.toMap(DesiredDataJobDeployment::getDataJobName, Function.identity()));
  }

  public Map<String, ActualDataJobDeployment> findAllActualDataJobDeployments() {
    return actualJobDeploymentRepository.findAll().stream()
        .collect(Collectors.toMap(ActualDataJobDeployment::getDataJobName, Function.identity()));
  }

  public Set<String> findAllActualDeploymentNamesFromKubernetes() throws KubernetesException {
    try {
      return dataJobsKubernetesService.listCronJobs();
    } catch (ApiException e) {
      throw new KubernetesException("Cannot load cron jobs", e);
    }
  }

  private void handleException(
      DataJob dataJob,
      DesiredDataJobDeployment jobDeployment,
      Boolean sendNotification,
      Throwable e) {
    ErrorMessage message =
        new ErrorMessage(
            String.format(
                "An error occurred while trying to deploy job: %s with version: %s",
                jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()),
            "See exception message below for possible reason.",
            "Most likely the deployment has failed. It is possible that deployment may have"
                + " succeeded (or failed with User error) but there was communication issue. Since"
                + " we do not know we assume that it was platform error and SRE team need to"
                + " investigate. End user deploying the job would get notification for deploy"
                + " failure due to platform error",
            "End user may verify which version is currently deployed and re-try if necessary. "
                + "SRE team may investigate by looking at the logs or in kubernetes.");
    log.error(message.toString(), e);
    deploymentProgress.failed(
        dataJob,
        DeploymentStatus.PLATFORM_ERROR,
        NotificationContent.getPlatformErrorBody(),
        sendNotification);
  }

  private boolean deploymentExistsOrInProgress(String dataJobName) {
    return jobImageBuilder.isBuildingJobInProgress(dataJobName)
        || readDeployment(dataJobName).isPresent();
  }

  /**
   * Populates the deployment's fields with legacy data to ensure backward compatibility. This
   * method is used to maintain compatibility with older versions of the deployment process.
   */
  private void populateDeploymentForBackwardCompatibility(
      DataJob dataJob, JobDeployment jobDeployment) {
    setDeploymentSchedule(dataJob, jobDeployment);
    setDeploymentEnabled(jobDeployment);
  }

  /**
   * Sets the deployment schedule if it is not passed to the API for backward compatibility, as the
   * schedule is still passed as part of the data job.
   *
   * @param dataJob the data job to which the deployment is associated
   * @param jobDeployment the deployment to patch with
   */
  private void setDeploymentSchedule(DataJob dataJob, JobDeployment jobDeployment) {
    if (jobDeployment.getSchedule() == null) {
      String schedule =
          Optional.ofNullable(dataJob)
              .map(DataJob::getJobConfig)
              .map(JobConfig::getSchedule)
              .orElse(null);
      jobDeployment.setSchedule(schedule);
    }
  }

  /**
   * Sets the deployment enabled flag to true if it is not passed to the API for backward
   * compatibility.
   *
   * @param jobDeployment the deployment to patch with
   */
  private void setDeploymentEnabled(JobDeployment jobDeployment) {
    jobDeployment.setEnabled(jobDeployment.getEnabled() == null || jobDeployment.getEnabled());
  }
}
