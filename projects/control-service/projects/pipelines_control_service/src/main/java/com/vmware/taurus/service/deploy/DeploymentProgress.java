/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.monitoring.DeploymentMonitor;
import com.vmware.taurus.service.notification.DataJobNotification;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

/** Track the progress of a deployment. */
@Component
@RequiredArgsConstructor
public class DeploymentProgress {

  private final DataJobNotification dataJobNotification;
  private final DeploymentMonitor deploymentMonitor;

  /**
   * Data Job Deployment has started.
   *
   * @param jobConfig the job configuration
   * @param jobDeployment the job deployment configuration
   */
  @Measurable(includeArg = 1, argName = "deployment")
  void started(JobConfig jobConfig, JobDeployment jobDeployment) {}

  /**
   * Data Job Deployment has started.
   *
   * @param jobConfig the job configuration
   * @param jobDeployment the job deployment configuration
   */
  @Measurable(includeArg = 1, argName = "deployment")
  void started(JobConfig jobConfig, DataJobDeployment jobDeployment) {}

  /**
   * Data Job Deployment has completed successfully.
   *
   * @param dataJob the job
   */
  @Measurable(includeArg = 1, argName = "deployment")
  void completed(DataJob dataJob, boolean sendNotification) {
    deploymentMonitor.recordDeploymentStatus(dataJob.getName(), DeploymentStatus.SUCCESS, dataJob.getDataJobDeployment());
    if (sendNotification) {
      dataJobNotification.notifyJobDeploySuccess(dataJob.getJobConfig());
    }
  }

  /**
   * Data Job Deployment has failed.
   *
   * @param dataJob the job
   * @param status Deployment status - user or platform error
   * @param message the error message that will be sent as notificaiton
   * @param sendNotification if true will sent notification to user
   */
  @Measurable(includeArg = 1, argName = "deployment")
  @Measurable(includeArg = 2, argName = "status")
  @Measurable(includeArg = 3, argName = "message")
  void failed(
          DataJob dataJob,
          DeploymentStatus status,
          String message,
          boolean sendNotification) {
    deploymentMonitor.recordDeploymentStatus(dataJob.getName(), status, dataJob.getDataJobDeployment());
    if (sendNotification) {
      dataJobNotification.notifyJobDeployError(dataJob.getJobConfig(), "Failed to deploy the job.", message);
    }
  }

  /**
   * Data Job Deployment is deleted. On delete for a deployment of a data job we reset its status to
   * 0 (success)
   *
   * @param dataJobName data job name TODO: param to support multiple modes
   */
  @Measurable(includeArg = 0, argName = "job_name")
  public void deleted(String dataJobName) {
    deploymentMonitor.recordDeploymentStatus(dataJobName, DeploymentStatus.SUCCESS, null);
  }

  @Measurable(includeArg = 1, argName = "deployment")
  public void configuration_updated(JobConfig jobConfig, JobDeployment jobDeployment) {}
}
