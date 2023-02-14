/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeployment;
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
   * Data Job Deployment has completed successfully.
   *
   * @param jobConfig the job configuration
   * @param jobDeployment the job deployment configuration
   */
  @Measurable(includeArg = 1, argName = "deployment")
  void completed(JobConfig jobConfig, JobDeployment jobDeployment, boolean sendNotification) {
    deploymentMonitor.recordDeploymentStatus(
        jobDeployment.getDataJobName(), DeploymentStatus.SUCCESS);
    if (sendNotification) {
      dataJobNotification.notifyJobDeploySuccess(jobConfig);
    }
  }

  /**
   * Data Job Deployment has failed.
   *
   * @param jobConfig the job configuration
   * @param jobDeployment the job deployment configuration
   * @param status Deployment status - user or platform error
   * @param message the error message that will be sent as notificaiton
   * @param sendNotification if true will sent notification to user
   */
  @Measurable(includeArg = 1, argName = "deployment")
  @Measurable(includeArg = 2, argName = "status")
  @Measurable(includeArg = 3, argName = "message")
  void failed(
      JobConfig jobConfig,
      JobDeployment jobDeployment,
      DeploymentStatus status,
      String message,
      boolean sendNotification) {
    deploymentMonitor.recordDeploymentStatus(jobDeployment.getDataJobName(), status);
    if (sendNotification) {
      dataJobNotification.notifyJobDeployError(jobConfig, "Failed to deploy the job.", message);
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
    deploymentMonitor.recordDeploymentStatus(dataJobName, DeploymentStatus.SUCCESS);
  }

  @Measurable(includeArg = 1, argName = "deployment")
  public void configuration_updated(JobConfig jobConfig, JobDeployment jobDeployment) {}
}
