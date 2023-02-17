/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobPage;
import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.service.Utilities;
import com.vmware.taurus.service.graphql.GraphQLUtils;
import com.vmware.taurus.service.graphql.model.V2DataJob;
import com.vmware.taurus.service.graphql.model.V2DataJobConfig;
import com.vmware.taurus.service.graphql.model.V2DataJobDeployment;
import com.vmware.taurus.service.graphql.model.V2DataJobSchedule;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.*;
import graphql.ExecutionResult;
import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Objects;

@Slf4j
public class ToApiModelConverter {

  static DataJobSummary toDataJobSummary(DataJob job) {
    DataJobSummary summary = new DataJobSummary();
    summary.setTeam(job.getJobConfig().getTeam());
    summary.setJobName(job.getName());
    summary.setDescription("");
    return summary;
  }

  public static V2DataJob toV2DataJob(DataJob job) {
    V2DataJob v2Job = new V2DataJob();
    v2Job.setJobName(job.getName());
    v2Job.setConfig(toV2JobConfig(job.getJobConfig()));
    //      v2Job.setDeployments(toDeployments(new DataJobDeployment())); TODO
    return v2Job;
  }

  public static com.vmware.taurus.controlplane.model.data.DataJob toDataJob(DataJob dataJob) {
    com.vmware.taurus.controlplane.model.data.DataJob job =
        new com.vmware.taurus.controlplane.model.data.DataJob();
    job.setConfig(toJobConfig(dataJob.getJobConfig()));
    job.setTeam(dataJob.getJobConfig().getTeam());
    job.setDescription(
        dataJob.getJobConfig() == null ? null : dataJob.getJobConfig().getDescription());
    job.setJobName(dataJob.getName());
    return job;
  }

  private static DataJobConfig toJobConfig(JobConfig jobConfig) {
    DataJobConfig dataJobConfig = new DataJobConfig();
    dataJobConfig.setDbDefaultType(jobConfig.getDbDefaultType());
    dataJobConfig.setSchedule(toSchedule(jobConfig.getSchedule()));
    dataJobConfig.setEnableExecutionNotifications(jobConfig.getEnableExecutionNotifications());
    dataJobConfig.setNotificationDelayPeriodMinutes(jobConfig.getNotificationDelayPeriodMinutes());
    dataJobConfig.setContacts(toContacts(jobConfig));
    dataJobConfig.setGenerateKeytab(jobConfig.isGenerateKeytab());
    return dataJobConfig;
  }

  private static V2DataJobConfig toV2JobConfig(JobConfig jobConfig) {
    V2DataJobConfig dataJobConfig = new V2DataJobConfig();
    dataJobConfig.setDescription(jobConfig.getDescription());
    dataJobConfig.setTeam(jobConfig.getTeam());
    dataJobConfig.setDbDefaultType(jobConfig.getDbDefaultType());
    dataJobConfig.setSchedule(toScheduleV2(jobConfig.getSchedule()));
    dataJobConfig.setContacts(toContacts(jobConfig));
    dataJobConfig.setGenerateKeytab(jobConfig.isGenerateKeytab());
    return dataJobConfig;
  }

  private static DataJobContacts toContacts(JobConfig jobConfig) {
    DataJobContacts contacts = new DataJobContacts();
    contacts.setNotifiedOnJobDeploy(jobConfig.getNotifiedOnJobDeploy());
    contacts.setNotifiedOnJobFailurePlatformError(jobConfig.getNotifiedOnJobFailurePlatformError());
    contacts.setNotifiedOnJobFailureUserError(jobConfig.getNotifiedOnJobFailureUserError());
    contacts.setNotifiedOnJobSuccess(jobConfig.getNotifiedOnJobSuccess());
    return contacts;
  }

  private static DataJobSchedule toSchedule(String scheduleCron) {
    DataJobSchedule sched = new DataJobSchedule();
    sched.setScheduleCron(scheduleCron);
    return sched;
  }

  private static V2DataJobSchedule toScheduleV2(String scheduleCron) {
    V2DataJobSchedule schedule = new V2DataJobSchedule();
    schedule.setScheduleCron(scheduleCron);
    // next run is calculated only if requested
    return schedule;
  }

  public static DataJobDeploymentStatus toDataJobDeploymentStatus(
      JobDeploymentStatus jobDeploymentStatus) {
    // TODO: Set other properties when the model is changed
    DataJobDeploymentStatus deployment = new DataJobDeploymentStatus();
    deployment.setEnabled(jobDeploymentStatus.getEnabled());
    deployment.setResources(jobDeploymentStatus.getResources());
    deployment.setMode(DataJobMode.fromValue(jobDeploymentStatus.getMode()));
    deployment.setJobVersion(jobDeploymentStatus.getGitCommitSha());
    deployment.setLastDeployedBy(jobDeploymentStatus.getLastDeployedBy());
    deployment.setLastDeployedDate(jobDeploymentStatus.getLastDeployedDate());
    deployment.setVdkVersion(jobDeploymentStatus.getVdkVersion());

    return deployment;
  }

  public static DataJobQueryResponse toDataJobPage(ExecutionResult executionResult) {
    // TODO allow introspecting GraphQL schema as part of TAUR-1432
    var dataJobQueryResponse = new DataJobQueryResponse();
    if (executionResult == null) {
      return dataJobQueryResponse;
    }

    dataJobQueryResponse.setErrors(
        new ArrayList<>(Utilities.removeGraphQLErrorsStackTrace(executionResult.getErrors())));

    LinkedHashMap<String, LinkedHashMap<String, Object>> executionResultData =
        executionResult.getData();
    if (executionResultData == null) {
      return dataJobQueryResponse;
    }

    String executionResultDataKey =
        GraphQLUtils.QUERIES.stream()
            .filter(query -> executionResultData.containsKey(query))
            .findFirst()
            .orElse(null);
    LinkedHashMap<String, Object> nestedExecutionResultData =
        executionResultData.get(executionResultDataKey);
    if (nestedExecutionResultData == null) {
      return dataJobQueryResponse;
    }
    var dataJobPage = new DataJobPage();
    dataJobPage.setTotalPages(
        nestedExecutionResultData.get("totalPages") == null
            ? 0
            : (Integer) nestedExecutionResultData.get("totalPages"));
    dataJobPage.setTotalItems(
        nestedExecutionResultData.get("totalItems") == null
            ? 0
            : (Integer) nestedExecutionResultData.get("totalItems"));
    dataJobPage.setContent((List<Object>) nestedExecutionResultData.get("content"));

    dataJobQueryResponse.setData(dataJobPage);

    return dataJobQueryResponse;
  }

  public static V2DataJobDeployment toV2DataJobDeployment(
      JobDeploymentStatus jobDeploymentStatus, DataJob sourceDataJob) {
    Objects.requireNonNull(jobDeploymentStatus);
    Objects.requireNonNull(sourceDataJob);

    var v2DataJobDeployment = new V2DataJobDeployment();

    v2DataJobDeployment.setId(jobDeploymentStatus.getCronJobName());
    v2DataJobDeployment.setEnabled(jobDeploymentStatus.getEnabled());
    v2DataJobDeployment.setJobVersion(jobDeploymentStatus.getGitCommitSha());
    v2DataJobDeployment.setMode(DataJobMode.fromValue(jobDeploymentStatus.getMode()));
    v2DataJobDeployment.setResources(jobDeploymentStatus.getResources());
    v2DataJobDeployment.setLastDeployedBy(jobDeploymentStatus.getLastDeployedBy());
    v2DataJobDeployment.setLastDeployedDate(jobDeploymentStatus.getLastDeployedDate());
    // TODO: Get these from the job deployment when they are available there
    v2DataJobDeployment.setLastExecutionStatus(
        convertStatusEnum(sourceDataJob.getLastExecutionStatus()));
    v2DataJobDeployment.setLastExecutionTime(sourceDataJob.getLastExecutionEndTime());
    v2DataJobDeployment.setLastExecutionDuration(sourceDataJob.getLastExecutionDuration());

    // TODO finish mapping implementation in TAUR-1535
    v2DataJobDeployment.setContacts(new DataJobContacts());
    v2DataJobDeployment.setSchedule(new V2DataJobSchedule());
    v2DataJobDeployment.setVdkVersion(jobDeploymentStatus.getVdkVersion());
    v2DataJobDeployment.setExecutions(new ArrayList<>());

    return v2DataJobDeployment;
  }

  public static DataJobExecution jobExecutionToConvert(
      com.vmware.taurus.service.model.DataJobExecution jobExecutionToConvert, String logsUrl) {
    return new DataJobExecution()
        .id(jobExecutionToConvert.getId())
        .jobName(jobExecutionToConvert.getDataJob().getName())
        .type(convertTypeEnum(jobExecutionToConvert.getType()))
        .status(convertStatusEnum(jobExecutionToConvert.getStatus()))
        .message(jobExecutionToConvert.getMessage())
        .opId(jobExecutionToConvert.getOpId())
        .startTime(jobExecutionToConvert.getStartTime())
        .endTime(jobExecutionToConvert.getEndTime())
        .startedBy(jobExecutionToConvert.getStartedBy())
        .logsUrl(logsUrl)
        .deployment(
            new DataJobDeployment()
                .vdkVersion(jobExecutionToConvert.getVdkVersion())
                .jobVersion(jobExecutionToConvert.getJobVersion())
                .schedule(
                    new DataJobSchedule().scheduleCron(jobExecutionToConvert.getJobSchedule()))
                .resources(getJobResources(jobExecutionToConvert))
                .deployedBy(jobExecutionToConvert.getLastDeployedBy())
                .deployedDate(jobExecutionToConvert.getLastDeployedDate())
                // TODO [miroslavi] get the following properties from the database once we introduce
                // the deployments
                .id(DataJobMode.RELEASE.getValue())
                .mode(DataJobMode.RELEASE)
                .enabled(true));
  }

  // Public for testing purposes
  public static DataJobExecution.TypeEnum convertTypeEnum(ExecutionType type) {
    switch (type) {
      case MANUAL:
        return DataJobExecution.TypeEnum.MANUAL;
      case SCHEDULED:
        return DataJobExecution.TypeEnum.SCHEDULED;
      default: // no such type
        log.warn("Unexpected type: '" + type + "' in TypeEnum.");
        return null;
    }
  }

  // Public for testing purposes
  public static DataJobExecution.StatusEnum convertStatusEnum(ExecutionStatus status) {
    if (status == null) {
      return null;
    }
    switch (status) {
      case SUBMITTED:
        return DataJobExecution.StatusEnum.SUBMITTED;
      case RUNNING:
        return DataJobExecution.StatusEnum.RUNNING;
      case CANCELLED:
        return DataJobExecution.StatusEnum.CANCELLED;
      case SUCCEEDED:
        return DataJobExecution.StatusEnum.SUCCEEDED;
      case SKIPPED:
        return DataJobExecution.StatusEnum.SKIPPED;
      case USER_ERROR:
        return DataJobExecution.StatusEnum.USER_ERROR;
      case PLATFORM_ERROR:
        return DataJobExecution.StatusEnum.PLATFORM_ERROR;
      default: // No such case
        log.warn("Unexpected status: '" + status + "' in StatusEnum.");
        return null;
    }
  }

  private static DataJobResources getJobResources(
      com.vmware.taurus.service.model.DataJobExecution job) {
    DataJobResources dataJobResources = new DataJobResources();
    dataJobResources.setCpuLimit(job.getResourcesCpuLimit());
    dataJobResources.setCpuRequest(job.getResourcesCpuRequest());
    dataJobResources.setMemoryLimit(job.getResourcesMemoryLimit());
    dataJobResources.setMemoryRequest(job.getResourcesMemoryRequest());

    return dataJobResources;
  }
}
