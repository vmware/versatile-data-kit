/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.datajobs.DeploymentModelConverter;
import com.vmware.taurus.exception.*;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import com.vmware.taurus.service.repository.JobsRepository;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Objects;
import java.util.Set;

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
  private final JobsRepository jobsRepository;
  private final SupportedPythonVersions supportedPythonVersions;

  /**
   * Updates or creates a Kubernetes CronJob based on the provided configuration.
   * <p>
   * This method takes a CronJob configuration and checks if a CronJob with the same name
   * already exists in the Kubernetes cluster. If the CronJob exists, it will be updated
   * with the new configuration; otherwise, a new CronJob will be created. The method ensures
   * that the CronJob in the cluster matches the desired state specified in the configuration.
   *
   * @param dataJob   The data job to update or create.
   * @param sendNotification if it is true the method will send a notification to the end user.
   * @param dataJobDeploymentNames list of actual data job deployment names returned by Kubernetes.
   */
  public void updateDeployment(
          DataJob dataJob,
          Boolean sendNotification,
          Set<String> dataJobDeploymentNames) {
    DataJobDeployment dataJobDeployment = dataJob.getDataJobDeployment();

    if (dataJobDeployment == null) {
      log.debug("Skipping the data job [job_name={}] deployment due to the missing deployment data", dataJob.getName());
      return;
    }

    JobDeployment jobDeployment = DeploymentModelConverter.toJobDeployment(
            dataJob.getJobConfig().getTeam(), dataJob.getName(), dataJobDeployment);

    try {
      log.info("Starting deployment of job {}", jobDeployment.getDataJobName());
      deploymentProgress.started(dataJob.getJobConfig(), jobDeployment);

      if (jobDeployment.getPythonVersion() == null) {
        jobDeployment.setPythonVersion(supportedPythonVersions.getDefaultPythonVersion());
      }

      String imageName =
              dockerRegistryService.dataJobImage(
                      jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha());
      jobDeployment.setImageName(imageName);

      if (jobImageBuilder.buildImage(imageName, dataJob, jobDeployment, sendNotification)) {
        log.info(
                "Image {} has been built. Will now schedule job {} for execution",
                imageName,
                dataJob.getName());
        jobDeployment.setImageName(imageName);
        if (jobImageDeployer.scheduleJob(
                dataJob, jobDeployment, sendNotification, dataJobDeployment.getLastDeployedBy(), dataJobDeploymentNames)) {
          log.info(
                  String.format(
                          "Successfully updated job: %s with version: %s",
                          jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()));

          saveDeployment(dataJob, jobDeployment);

          deploymentProgress.completed(dataJob, sendNotification);
        }
      }
    } catch (ApiException e) {
      handleException(dataJob, jobDeployment, sendNotification, new KubernetesException("", e));
    } catch (Exception e) {
      handleException(dataJob, jobDeployment, sendNotification, e);
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
        dataJob,
        DeploymentStatus.PLATFORM_ERROR,
        NotificationContent.getPlatformErrorBody(),
        sendNotification);
  }
}
