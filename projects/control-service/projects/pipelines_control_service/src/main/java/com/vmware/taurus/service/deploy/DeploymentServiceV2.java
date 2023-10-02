/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.exception.*;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.notification.NotificationContent;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import io.kubernetes.client.openapi.ApiException;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

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
   * @param sendNotification if it is true the method will send a notification to the end user.
   */
  @Measurable(includeArg = 0, argName = "data_job")
  public void updateDeployment(
      DataJob dataJob,
      DesiredDataJobDeployment desiredJobDeployment,
      ActualDataJobDeployment actualJobDeployment,
      boolean isJobDeploymentPresentInKubernetes,
      Boolean sendNotification) {
    if (desiredJobDeployment == null) {
      log.warn(
          "Skipping the data job [job_name={}] deployment due to the missing deployment data",
          dataJob.getName());
      return;
    }

    if (DeploymentStatus.USER_ERROR.equals(desiredJobDeployment.getStatus()) ||
            DeploymentStatus.PLATFORM_ERROR.equals(desiredJobDeployment.getStatus())) {
      log.debug(
          "Skipping the data job [job_name={}] deployment due to the previously failed deployment [status={}]",
          dataJob.getName(),
          desiredJobDeployment.getStatus());
      return;
    }

    try {
      log.info("Starting deployment of job {}", desiredJobDeployment.getDataJobName());
      deploymentProgress.started(dataJob.getJobConfig(), desiredJobDeployment);

      if (desiredJobDeployment.getPythonVersion() == null) {
        desiredJobDeployment.setPythonVersion(supportedPythonVersions.getDefaultPythonVersion());
      }

      String imageName =
          dockerRegistryService.dataJobImage(
              desiredJobDeployment.getDataJobName(), desiredJobDeployment.getGitCommitSha());

      if (jobImageBuilder.buildImage(imageName, dataJob, desiredJobDeployment, sendNotification)) {
        log.info(
            "Image {} has been built. Will now schedule job {} for execution",
            imageName,
            dataJob.getName());

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

  public Set<String> findAllActualDeploymentNamesFromKubernetes() throws ApiException {
    return dataJobsKubernetesService.listCronJobs();
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
}
