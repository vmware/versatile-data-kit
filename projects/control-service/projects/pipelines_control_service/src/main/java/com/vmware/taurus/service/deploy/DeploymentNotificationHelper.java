/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.exception.ErrorMessage;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.notification.NotificationContent;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class DeploymentNotificationHelper {
  private static final Logger log = LoggerFactory.getLogger(DeploymentNotificationHelper.class);

  private final DeploymentProgress deploymentProgress;

  public void verifyBuilderResult(
      String builderJobName,
      DataJob dataJob,
      JobDeployment jobDeployment,
      KubernetesService.JobStatusCondition condition,
      String logs,
      Boolean sendNotification) {

    if (condition.isSuccess()) {
      log.info("Builder job {} finished successfully", builderJobName);
    } else {
      log.info("Something went wrong when building job image. Job condition: {}", condition);
      String userErrorMessage = getUserErrorMessage(logs, jobDeployment);
      if (StringUtils.isNotBlank(userErrorMessage)) {
        log.info(
            String.format(
                "An error occurred while processing the requirements file for job: %s with version:"
                    + " %s",
                jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()));

        deploymentProgress.failed(
            dataJob,
            DeploymentStatus.USER_ERROR,
            userErrorMessage,
            sendNotification);
      } else {
        if (logs.contains("error resolving source context: reference not found")) {
          log.error(
              "Job Builder image failed to clone the git repository: "
                  + "double check the git configuration including git url, credentials and branch."
                  + "If this not not the root cause. See next error message");
        }

        ErrorMessage message =
            new ErrorMessage(
                String.format(
                    "Could not build an image for job: %s with version: %s",
                    jobDeployment.getDataJobName(), jobDeployment.getGitCommitSha()),
                "Unexpected error occurred.",
                "The new/updated job was not deployed. The job will run its latest successfully"
                    + " deployed version (if any) as scheduled.  Data Job Owner will get"
                    + " notification if enabled.",
                "Investigate. See the failed builder job if it is still present in kubernetes. "
                    + "Or see captured logs from the job here:\n"
                    + logs);
        log.warn(message.toString());
        deploymentProgress.failed(
            dataJob,
            DeploymentStatus.PLATFORM_ERROR,
            NotificationContent.getPlatformErrorBody(),
            sendNotification);
      }
    }
  }

  private String getUserErrorMessage(String logs, JobDeployment jobDeployment) {
    String requirementsError = getRequirementsError(logs);
    if (StringUtils.isNotBlank(requirementsError)) {
      return NotificationContent.getErrorBody(
          "Tried to deploy a data job",
          "There has been an error while processing your requirements file: " + requirementsError,
          "Your new/updated job was not deployed. Your job will run its latest successfully"
              + " deployed version (if any) as scheduled.",
          "Please fix the requirements file");
    }
    String notFoundError = getDataJobNotFoundError(logs, jobDeployment);
    if (StringUtils.isNotBlank(notFoundError)) {
      return notFoundError;
    }

    return null;
  }

  private String getDataJobNotFoundError(String logs, JobDeployment jobDeployment) {
    String error = null;

    if (StringUtils.isNotBlank(logs)
        && (logs.contains(">data-job-not-found<")
            || logs.contains("failed to get files used from context"))) {
      error =
          NotificationContent.getErrorBody(
              "Tried to deploy a data job and failed.",
              "The data job source code cannot be found. Tried to deploy with git commit: "
                  + jobDeployment.getGitCommitSha(),
              "Your new/updated job was not deployed. Your job will run its latest successfully"
                  + " deployed version (if any) as scheduled.",
              "Make sure you push the job in the git repository and during deployment have"
                  + " specified the correct commit hash.");
    }
    return error;
  }

  // Currently, the only way to differentiate between infra and user error
  // when building a data job is by parsing the logs of the builder job.
  private String getRequirementsError(String logs) {
    String requirements_error = null;

    if (StringUtils.isNotBlank(logs) && logs.contains(">requirements_failed<")) {
      String[] error_list = logs.split(">requirements_failed<");

      if (error_list.length > 3) {
        requirements_error = error_list[error_list.length - 2];
      }
    }
    return requirements_error;
  }
}
