/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.datajobs.DeploymentModelConverter;
import com.vmware.taurus.exception.*;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import com.vmware.taurus.service.monitoring.DataJobMetrics;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;
import java.util.Optional;

/**
 * CRUD operations for Versatile Data Kit deployments on kubernetes.
 *
 * <p>This class is in a transition from operating against Kubernetes to operating against the
 * database. Currently, only the enabled flag is stored in the database. Eventually, all deployment
 * information will be stored (and retrieved) from a database from a dedicated table.
 */
@Service
@RequiredArgsConstructor
public class DeploymentService {
  private static final Logger log = LoggerFactory.getLogger(DeploymentService.class);

  private final DockerRegistryService dockerRegistryService;
  private final DeploymentProgress deploymentProgress;
  private final JobImageBuilder jobImageBuilder;
  private final JobImageDeployer jobImageDeployer;
  private final OperationContext operationContext;
  private final JobsRepository jobsRepository;
  private final DataJobMetrics dataJobMetrics;
  private final SupportedPythonVersions supportedPythonVersions;

  public Optional<JobDeploymentStatus> readDeployment(String jobName) {
    return jobImageDeployer.readScheduledJob(jobName);
  }

  public List<JobDeploymentStatus> readDeployments() {
    return jobImageDeployer.readScheduledJobs();
  }

  /**
   * Patch existing deployment of a data job. Existing fields are overwritten from non-NULL fields
   * in jobDeployment.
   *
   * @param dataJob the data job details
   * @param jobDeployment JobDeployment that contains ony the changes necessary (all other fields
   *     are null)
   */
  public void patchDeployment(DataJob dataJob, JobDeployment jobDeployment) {

    var deploymentStatus = readDeployment(dataJob.getName());
    if (deploymentStatus.isPresent()) {
      var oldDeployment =
          DeploymentModelConverter.toJobDeployment(
              dataJob.getJobConfig().getTeam(), dataJob.getName(), deploymentStatus.get());
      var mergedDeployment =
          DeploymentModelConverter.mergeDeployments(oldDeployment, jobDeployment);
      validateFieldsCanBePatched(oldDeployment, mergedDeployment);

      // we are setting sendNotification to false since it's not necessary. If something fails we'd
      // return HTTP error
      // as the request is synchronous
      jobImageDeployer.scheduleJob(dataJob, mergedDeployment, false, operationContext.getUser());

      saveDeployment(dataJob, mergedDeployment);

      if (!mergedDeployment.getEnabled()) {
        dataJobMetrics.clearTerminationStatusAndDelayNotifGauges(mergedDeployment.getDataJobName());
      }

      deploymentProgress.configuration_updated(dataJob.getJobConfig(), jobDeployment);
    } else {
      throw new DataJobDeploymentNotFoundException(dataJob.getName());
    }
  }

  /**
   * Changing job/python/vdk versions require rebuilding the data job image which is async operation
   * (happens in background after/while http request finishes) But we'd like to be able to guarantee
   * that patch operation are synchronous (the desired job deployment configuration is applied when
   * the http requests finishes) So we return error if job/python/vdk versions have been changed and
   * require POST request to be completed.
   *
   * @param oldDeployment the old (or existing) deployment of the data job
   * @param mergedDeployment the new (merged with the old one) deployment of the data job
   */
  private void validateFieldsCanBePatched(
      JobDeployment oldDeployment, JobDeployment mergedDeployment) {
    if (mergedDeployment.getGitCommitSha() != null
        && !mergedDeployment.getGitCommitSha().equals(oldDeployment.getGitCommitSha())) {
      throw new ApiConstraintError(
          "job_version",
          "same as the current job version when using PATCH request.",
          mergedDeployment.getGitCommitSha(),
          "Use POST HTTP request to change job version.");
    }

    if (mergedDeployment.getPythonVersion() != null
        && !mergedDeployment.getPythonVersion().equals(oldDeployment.getPythonVersion())) {
      throw new ApiConstraintError(
          "python_version",
          String.format(
              "same as the current python version -- %s -- when using PATCH request.",
              oldDeployment.getPythonVersion()),
          mergedDeployment.getPythonVersion(),
          "Use POST HTTP request to change python version.");
    }

    if (mergedDeployment.getVdkVersion() != null
        && !mergedDeployment.getVdkVersion().equals(oldDeployment.getVdkVersion())) {
      throw new ApiConstraintError(
          "vdk_version",
          String.format(
              "same as the current vdk version -- %s -- when using PATCH request.",
              oldDeployment.getVdkVersion()),
          mergedDeployment.getPythonVersion(),
          "Use POST HTTP request to change vdk version.");
    }
  }

  /**
   * Deploys data jobs on kubernetes as cron jobs. Creates a new deployment if none is present for
   * the data job. Updates an existing deployment if it already exists (behaves same as patch). This
   * method is will be executed in a separate thread (it is async).
   *
   * @param dataJob The data job
   * @param jobDeployment Deployment configuration
   * @param sendNotification
   * @param lastDeployedBy name of the user that last updated the data job
   * @param opId Operation ID of the client request
   * @see org.springframework.scheduling.annotation.Async
   */
  @Async
  @Measurable(includeArg = 0, argName = "data_job")
  public void updateDeployment(
      DataJob dataJob,
      JobDeployment jobDeployment,
      Boolean sendNotification,
      String lastDeployedBy,
      String opId) {
    // TODO: Consider introducing a generalised mechanism to propagate Operation Context properties
    // to all ASYNC calls.
    // Add the opId value propagated from the operation context to a thread's local operation
    // context.
    operationContext.setId(opId);

    try {
      log.info("Starting deployment of job {}", jobDeployment.getDataJobName());
      deploymentProgress.started(dataJob.getJobConfig(), jobDeployment);

      var deploymentStatus = readDeployment(dataJob.getName());
      if (deploymentStatus.isPresent()) {
        var oldDeployment =
            DeploymentModelConverter.toJobDeployment(
                dataJob.getJobConfig().getTeam(), dataJob.getName(), deploymentStatus.get());
        setPythonVersionIfNull(oldDeployment, jobDeployment);
        jobDeployment = DeploymentModelConverter.mergeDeployments(oldDeployment, jobDeployment);
      }

      if (jobDeployment.getPythonVersion() == null) {
        jobDeployment.setPythonVersion(supportedPythonVersions.getDefaultPythonVersion());
      }

      String imageName =
          dockerRegistryService.dataJobImage(
              jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha());

      if (jobImageBuilder.buildImage(imageName, dataJob, jobDeployment, sendNotification)) {
        log.info(
            "Image {} has been built. Will now schedule job {} for execution",
            imageName,
            dataJob.getName());
        jobDeployment.setImageName(imageName);
        if (jobImageDeployer.scheduleJob(
            dataJob, jobDeployment, sendNotification, lastDeployedBy)) {
          log.info(
              String.format(
                  "Successfully updated job: %s with version: %s",
                  jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()));

          saveDeployment(dataJob, jobDeployment);

          deploymentProgress.completed(dataJob.getJobConfig(), jobDeployment, sendNotification);
        }
      }
    } catch (ApiException e) {
      handleException(dataJob, jobDeployment, sendNotification, new KubernetesException("", e));
    } catch (Exception e) {
      handleException(dataJob, jobDeployment, sendNotification, e);
    } catch (Throwable e) {
      handleException(dataJob, jobDeployment, sendNotification, e);
      throw e;
    }
  }

  private void saveDeployment(DataJob dataJob, JobDeployment jobDeployment) {
    // Currently, store only 'enabled' in the database
    if (!Objects.equals(dataJob.getEnabled(), jobDeployment.getEnabled())) {
      dataJob.setEnabled(jobDeployment.getEnabled());
      jobsRepository.save(dataJob);
      log.info(
          "The deployment of the data job {} has been {}",
          dataJob.getName(),
          Boolean.TRUE.equals(dataJob.getEnabled()) ? "ENABLED" : "DISABLED");
    }
  }

  /**
   * As pythonVersion is optional, we need to check if it is passed. And if it is, we need to
   * validate that the python version is supported by the Control Service. If it is not, we need to
   * fail the operation, as we don't have sufficient information for the user's intent to deploy the
   * data job.
   *
   * @param pythonVersion The python version to be used for the data job deployment.
   */
  public void validatePythonVersionIsSupported(String pythonVersion) {
    if (pythonVersion != null && !supportedPythonVersions.isPythonVersionSupported(pythonVersion)) {
      throw new UnsupportedPythonVersionException(
          pythonVersion, supportedPythonVersions.getSupportedPythonVersions());
    }
  }

  private void handleException(
      DataJob dataJob, JobDeployment jobDeployment, Boolean sendNotification, Throwable e) {
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
        dataJob.getJobConfig(),
        jobDeployment,
        DeploymentStatus.PLATFORM_ERROR,
        NotificationContent.getPlatformErrorBody(),
        sendNotification);
  }

  public void deleteDeployment(String dataJobName) {
    if (this.deploymentExistsOrInProgress(dataJobName)) {
      jobImageBuilder.cancelBuildingJob(dataJobName);
      jobImageDeployer.unScheduleJob(dataJobName);
      jobsRepository.updateDataJobEnabledByName(dataJobName, false);
    }
    deploymentProgress.deleted(dataJobName);
  }

  private boolean deploymentExistsOrInProgress(String dataJobName) {
    return jobImageBuilder.isBuildingJobInProgress(dataJobName)
        || readDeployment(dataJobName).isPresent();
  }

  private void setPythonVersionIfNull(JobDeployment oldDeployment, JobDeployment newDeployment) {
    if (oldDeployment.getPythonVersion() == null && newDeployment.getPythonVersion() == null) {
      newDeployment.setPythonVersion(supportedPythonVersions.getDefaultPythonVersion());
    }
  }
}
