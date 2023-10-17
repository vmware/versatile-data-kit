/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.controlplane.model.data.DataJobSchedule;
import com.vmware.taurus.service.model.*;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ToModelApiConverter {

  public static JobDeployment toJobDeployment(
      String teamName, String jobName, DataJobDeployment dataJobDeployment) {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(teamName);
    jobDeployment.setDataJobName(jobName);
    jobDeployment.setEnabled(dataJobDeployment.getEnabled());
    jobDeployment.setResources(dataJobDeployment.getResources());
    if (dataJobDeployment.getMode() != null) {
      jobDeployment.setMode(dataJobDeployment.getMode().toString());
    }
    jobDeployment.setGitCommitSha(dataJobDeployment.getJobVersion());
    jobDeployment.setVdkVersion(dataJobDeployment.getVdkVersion());
    if (dataJobDeployment.getPythonVersion() != null) {
      jobDeployment.setPythonVersion(dataJobDeployment.getPythonVersion());
    }
    if (dataJobDeployment.getSchedule() != null) {
      jobDeployment.setSchedule(dataJobDeployment.getSchedule().getScheduleCron());
    }
    return jobDeployment;
  }

  public static DataJob toDataJob(com.vmware.taurus.controlplane.model.data.DataJob modelJob) {
    JobConfig config = new JobConfig();
    config.setJobName(modelJob.getJobName());
    config.setDescription(modelJob.getDescription());
    config.setTeam(modelJob.getTeam());
    DataJobConfig modelConfig = modelJob.getConfig();
    if (modelConfig != null) {
      config.setDbDefaultType(modelConfig.getDbDefaultType());

      if (modelConfig.getSchedule() != null) {
        config.setSchedule(modelConfig.getSchedule().getScheduleCron());
      }
      config.setEnableExecutionNotifications(modelConfig.getEnableExecutionNotifications());
      config.setNotificationDelayPeriodMinutes(modelConfig.getNotificationDelayPeriodMinutes());
      var contacts = modelConfig.getContacts();
      if (contacts != null) {
        config.setNotifiedOnJobSuccess(contacts.getNotifiedOnJobSuccess());
        config.setNotifiedOnJobDeploy(contacts.getNotifiedOnJobDeploy());
        config.setNotifiedOnJobFailurePlatformError(
            contacts.getNotifiedOnJobFailurePlatformError());
        config.setNotifiedOnJobFailureUserError(contacts.getNotifiedOnJobFailureUserError());
      }
      config.setGenerateKeytab(modelConfig.getGenerateKeytab());
    }
    return new DataJob(modelJob.getJobName(), config);
  }

  public static DataJobDeploymentStatus toJobDeploymentStatus(
      ActualDataJobDeployment actualDataJobDeployment, DataJob job) {
    var deploymentStatus = new DataJobDeploymentStatus();
    deploymentStatus.setJobVersion(actualDataJobDeployment.getDeploymentVersionSha());
    deploymentStatus.setPythonVersion(actualDataJobDeployment.getPythonVersion());
    deploymentStatus.setId(actualDataJobDeployment.getDataJobName());
    deploymentStatus.setEnabled(actualDataJobDeployment.getEnabled());
    deploymentStatus.setContacts(getContactsFromJob(job));
    deploymentStatus.setSchedule(
        new DataJobSchedule().scheduleCron(actualDataJobDeployment.getSchedule()));
    deploymentStatus.setResources(getResourcesFromDeployment(actualDataJobDeployment));
    deploymentStatus.setLastDeployedDate(
        actualDataJobDeployment.getLastDeployedDate() == null ? null
            : actualDataJobDeployment.getLastDeployedDate().toString());
    deploymentStatus.setLastDeployedBy(actualDataJobDeployment.getLastDeployedBy());
    return deploymentStatus;
  }

  private static DataJobContacts getContactsFromJob(DataJob job) {
    DataJobContacts contacts = new DataJobContacts();
    if (job.getJobConfig() != null) {
      var config = job.getJobConfig();
      contacts.setNotifiedOnJobDeploy(config.getNotifiedOnJobDeploy());
      contacts.setNotifiedOnJobFailurePlatformError(config.getNotifiedOnJobFailurePlatformError());
      contacts.setNotifiedOnJobSuccess(config.getNotifiedOnJobSuccess());
      contacts.setNotifiedOnJobFailureUserError(config.getNotifiedOnJobFailureUserError());
    }
    return contacts;
  }

  private static DataJobResources getResourcesFromDeployment(ActualDataJobDeployment deployment){
    DataJobResources resources = new DataJobResources();
    var deploymentResources = deployment.getResources();
    if(deploymentResources != null) {
      resources.setCpuRequest(deploymentResources.getCpuRequestCores());
      resources.setCpuLimit(deploymentResources.getCpuLimitCores());
      resources.setMemoryRequest(deploymentResources.getMemoryRequestMi());
      resources.setMemoryLimit(deploymentResources.getMemoryLimitMi());
    }
    return resources;
  }

  public static ExecutionType toExecutionType(DataJobExecution.TypeEnum type) {
    switch (type) {
      case MANUAL:
        return ExecutionType.MANUAL;
      case SCHEDULED:
        return ExecutionType.SCHEDULED;
      default: // no such type
        log.warn("Unexpected type: '" + type + "' in ExecutionType.");
        return null;
    }
  }

  public static ExecutionStatus toExecutionStatus(DataJobExecution.StatusEnum status) {
    switch (status) {
      case SUBMITTED:
        return ExecutionStatus.SUBMITTED;
      case RUNNING:
        return ExecutionStatus.RUNNING;
      case CANCELLED:
        return ExecutionStatus.CANCELLED;
      case SUCCEEDED:
        return ExecutionStatus.SUCCEEDED;
      case SKIPPED:
        return ExecutionStatus.SKIPPED;
      case USER_ERROR:
        return ExecutionStatus.USER_ERROR;
      case PLATFORM_ERROR:
        return ExecutionStatus.PLATFORM_ERROR;
      default: // No such status
        log.warn("Unexpected status: '" + status + "' in ExecutionStatus.");
        return null;
    }
  }
}
