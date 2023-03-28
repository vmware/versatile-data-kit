/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.google.gson.JsonSyntaxException;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionLogs;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.exception.*;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import io.kubernetes.client.openapi.ApiException;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Job Execution service.
 *
 * <p>Execution of Data Job is done by starting Kubernetes Job.
 */
@Slf4j
@AllArgsConstructor
@Service
public class JobExecutionService {

  @AllArgsConstructor
  public enum ExecutionType {
    MANUAL("manual"), // "manual" executions are ones ran through the `vdk execute --start` command and
    // the startedBy value of the execution request must always be 'vdk-control-cli'
    SCHEDULED("scheduled");

    @Getter private final String value;
  }

  private JobsService jobsService;

  private JobExecutionRepository jobExecutionRepository;

  private DeploymentService deploymentService;

  private DataJobsKubernetesService dataJobsKubernetesService;

  private JobExecutionLogsUrlBuilder jobExecutionLogsUrlBuilder;

  private OperationContext operationContext;

  public String startDataJobExecution(
      String teamName,
      String jobName,
      String deploymentId,
      DataJobExecutionRequest jobExecutionRequest) {
    // TODO: deployment ID support
    // TODO: dataJobExecutionRequest args are ignored currently
    var extraJobArguments = jobExecutionRequest.getArgs();
    DataJob dataJob =
        jobsService
            .getByNameAndTeam(jobName, teamName)
            .orElseThrow(() -> new DataJobNotFoundException(jobName));

    JobDeploymentStatus jobDeploymentStatus =
        deploymentService
            .readDeployment(jobName.toLowerCase())
            .orElseThrow(() -> new DataJobDeploymentNotFoundException(jobName));

    String executionId = getExecutionId(JobImageDeployer.getCronJobName(jobName));

    try {
      if (dataJobsKubernetesService.isRunningJob(jobName)) {
        throw new DataJobAlreadyRunningException(jobName);
      }
      Map<String, String> annotations = new LinkedHashMap<>();

      String opId = operationContext.getOpId();
      annotations.put(JobAnnotation.OP_ID.getValue(), opId);

      String startedBy =
          StringUtils.isNotBlank(jobExecutionRequest.getStartedBy())
              ? jobExecutionRequest.getStartedBy() + "/" + operationContext.getUser()
              : operationContext.getUser();
      annotations.put(JobAnnotation.STARTED_BY.getValue(), startedBy);
      annotations.put(
          JobAnnotation.EXECUTION_TYPE.getValue(),
              (jobExecutionRequest.getStartedBy().contains("vdk-control-cli") ||
                      jobExecutionRequest.getStartedBy().contains("manual"))
              ? ExecutionType.MANUAL.getValue()
              : ExecutionType.SCHEDULED.getValue());


      Map<String, String> envs = new LinkedHashMap<>();
      envs.put(JobEnvVar.VDK_OP_ID.getValue(), opId);

      // Save Data Job execution
      saveDataJobExecution(
          dataJob,
          executionId,
          opId,
          com.vmware.taurus.service.model.ExecutionType.MANUAL,
          ExecutionStatus.SUBMITTED,
          startedBy,
          OffsetDateTime.now());
      try {
        // Start K8S Job
        dataJobsKubernetesService.startNewCronJobExecution(
            jobDeploymentStatus.getCronJobName(),
            executionId,
            annotations,
            envs,
            extraJobArguments,
            jobName);
      } catch (Exception e) {
        // rollback data job execution
        jobExecutionRepository.deleteDataJobExecutionByIdAndDataJobAndStatusAndType(
            executionId,
            dataJob,
            ExecutionStatus.SUBMITTED,
            com.vmware.taurus.service.model.ExecutionType.MANUAL);
        throw e;
      }

      return executionId;
    } catch (ApiException e) {
      throw new KubernetesException(
          String.format(
              "Cannot start a Data Job '%s' execution with execution id '%s'",
              jobName, executionId),
          e);
    }
  }

  public void cancelDataJobExecution(String teamName, String jobName, String executionId) {
    log.info("Attempting to cancel data job execution: {}", executionId);

    try {

      if (!jobsService.jobWithTeamExists(jobName, teamName)) {
        log.info("No such data job: {} found for team: {} .", jobName, teamName);
        throw new DataJobExecutionCannotBeCancelledException(
            executionId, ExecutionCancellationFailureReason.DataJobNotFound);
      }

      var jobExecutionOptional =
          jobExecutionRepository.findDataJobExecutionByIdAndTeamAndName(
              executionId, jobName, teamName);

      if (jobExecutionOptional.isEmpty()) {
        log.info(
            "Execution: {} for data job: {} with team: {} not found!",
            executionId,
            jobName,
            teamName);
        throw new DataJobExecutionCannotBeCancelledException(
            executionId, ExecutionCancellationFailureReason.DataJobExecutionNotFound);
      }

      var jobExecution = jobExecutionOptional.get();
      var jobStatus = jobExecution.getStatus();
      var acceptedStatusToCancelExecutionSet =
          Set.of(ExecutionStatus.SUBMITTED, ExecutionStatus.RUNNING);
      if (!acceptedStatusToCancelExecutionSet.contains(jobStatus)) {
        log.info(
            "Trying to cancel execution: {} for data job: {} with team: {} but job has status {}!",
            executionId,
            jobName,
            teamName,
            jobStatus.toString());
        throw new DataJobExecutionCannotBeCancelledException(
            executionId, ExecutionCancellationFailureReason.ExecutionNotRunning);
      }

      dataJobsKubernetesService.cancelRunningCronJob(teamName, jobName, executionId);
      log.info("Deleted execution in K8S.");
      jobExecution.setEndTime(OffsetDateTime.now());
      jobExecution.setStatus(ExecutionStatus.CANCELLED);
      jobExecution.setMessage("Job execution cancelled by user.");
      log.info("Writing cancelled status in database.");
      jobExecutionRepository.save(jobExecution);
      log.info("Cancelled data job execution {} successfully.", executionId);

    } catch (ApiException | JsonSyntaxException e) {
      throw new KubernetesException(
          String.format(
              "Cannot cancel a Data Job '%s' execution with execution id '%s'",
              jobName, executionId),
          e);
    }
  }

  public List<DataJobExecution> listJobExecutions(
      String teamName, String jobName, List<String> apiExecutionStatuses) {
    if (!jobsService.jobWithTeamExists(jobName, teamName)) {
      throw new DataJobNotFoundException(jobName);
    }

    List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutions;

    if (!CollectionUtils.isEmpty(apiExecutionStatuses)) {
      List<com.vmware.taurus.service.model.ExecutionStatus> modelExecutionStatuses =
          apiExecutionStatuses.stream()
              .map(
                  apiExecutionStatus -> {
                    try {
                      DataJobExecution.StatusEnum statusEnum =
                          DataJobExecution.StatusEnum.fromValue(apiExecutionStatus);
                      return ToModelApiConverter.toExecutionStatus(statusEnum);
                    } catch (Exception ex) {
                      throw new DataJobExecutionStatusNotValidException(apiExecutionStatus);
                    }
                  })
              .collect(Collectors.toList());

      dataJobExecutions =
          jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(
              jobName, modelExecutionStatuses);

      // The VDK Skip plugin relies heavily on running execution status.
      // In some cases, the execution status in the database may be outdated due to delay.
      // As a result the next job execution will be skipped. In order to avoid such cases
      // we must return only running jobs in Kubernetes when a filter (status=RUNNING) is passed to
      // the API.
      try {
        if (modelExecutionStatuses.contains(ExecutionStatus.RUNNING)
            && !dataJobsKubernetesService.isRunningJob(jobName)) {
          dataJobExecutions.removeIf(
              dataJobExecution -> ExecutionStatus.RUNNING.equals(dataJobExecution.getStatus()));
        }
      } catch (ApiException e) {
        log.warn("Error while filtering RUNNING job executions.", e);
      }
    } else {
      dataJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(jobName);
    }

    return dataJobExecutions.stream()
        .map(dataJobExecution -> convertToModel(dataJobExecution))
        .collect(Collectors.toList());
  }

  public DataJobExecution readJobExecution(String teamName, String jobName, String executionId) {
    if (!jobsService.jobWithTeamExists(jobName, teamName)) {
      throw new DataJobNotFoundException(jobName);
    }

    return jobExecutionRepository
        .findById(executionId)
        .map(dataJobExecution -> convertToModel(dataJobExecution))
        .orElseThrow(() -> new DataJobExecutionNotFoundException(executionId));
  }

  /**
   * Updates job execution in database. It does NOT update job execution when the execution status
   * has not changed or if the status is not in the correct order (e.g. from FINISHED to RUNNING).
   */
  public Optional<com.vmware.taurus.service.model.DataJobExecution> updateJobExecution(
      final DataJob dataJob,
      final KubernetesService.JobExecution jobExecution,
      ExecutionResult executionResult) {

    if (StringUtils.isBlank(jobExecution.getExecutionId())) {
      log.warn(
          "Could not store Data Job execution due to the missing execution id: {}", jobExecution);
      return Optional.empty();
    }

    final Optional<com.vmware.taurus.service.model.DataJobExecution>
        dataJobExecutionPersistedOptional =
            jobExecutionRepository.findById(jobExecution.getExecutionId());

    // This set contains all the statuses that should not be changed to something else if present in
    // the DB.
    // All the elements in this list should therefore be a final status. Meaning non retryable
    // statuses.
    // Using a hash set, because it allows null elements, no NullPointer when contains method called
    // with null.
    var finalStatusSet =
        new HashSet<>(
            List.of(ExecutionStatus.CANCELLED, ExecutionStatus.SUCCEEDED, ExecutionStatus.SKIPPED));
    ExecutionStatus executionStatus = executionResult.getExecutionStatus();

    // Optimization:
    // if there is an existing execution in the database and
    // the status has not changed (the new status is equal to the old one)
    // do not update the record. Does not update record if previous status is
    // in the list above.
    if (dataJobExecutionPersistedOptional.isPresent()
        && (dataJobExecutionPersistedOptional.get().getStatus()
                == executionResult.getExecutionStatus()
            || finalStatusSet.contains(dataJobExecutionPersistedOptional.get().getStatus()))) {
      log.debug(
          "The job execution will NOT be updated due to the incorrect status. "
              + "Execution status to be updated {}. New execution status {}",
          dataJobExecutionPersistedOptional.get().getStatus(),
          executionResult.getExecutionStatus());
      return Optional.empty();
    }

    final com.vmware.taurus.service.model.DataJobExecution.DataJobExecutionBuilder
        dataJobExecutionBuilder =
            dataJobExecutionPersistedOptional.isPresent()
                ? dataJobExecutionPersistedOptional.get().toBuilder()
                : com.vmware.taurus.service.model.DataJobExecution.builder()
                    .id(jobExecution.getExecutionId())
                    .dataJob(dataJob)
                    .startTime(
                        jobExecution.getStartTime() != null
                            ? jobExecution.getStartTime()
                            : OffsetDateTime.now())
                    .type(
                        ExecutionType.MANUAL.getValue().equals(jobExecution.getExecutionType())
                            ? com.vmware.taurus.service.model.ExecutionType.MANUAL
                            : com.vmware.taurus.service.model.ExecutionType.SCHEDULED);

    com.vmware.taurus.service.model.DataJobExecution dataJobExecution =
        dataJobExecutionBuilder
            .status(executionStatus)
            .message(
                getJobExecutionApiMessage(
                    executionStatus, jobExecution.getMainContainerTerminationReason()))
            .opId(jobExecution.getOpId())
            .endTime(jobExecution.getEndTime())
            .vdkVersion(executionResult.getVdkVersion())
            .jobVersion(jobExecution.getJobVersion())
            .jobPythonVersion(jobExecution.getJobPythonVersion())
            .jobSchedule(jobExecution.getJobSchedule())
            .resourcesCpuRequest(jobExecution.getResourcesCpuRequest())
            .resourcesCpuLimit(jobExecution.getResourcesCpuLimit())
            .resourcesMemoryRequest(jobExecution.getResourcesMemoryRequest())
            .resourcesMemoryLimit(jobExecution.getResourcesMemoryLimit())
            .lastDeployedDate(jobExecution.getDeployedDate())
            .lastDeployedBy(jobExecution.getDeployedBy())
            .build();
    return Optional.of(jobExecutionRepository.save(dataJobExecution));
  }

  /**
   * Returns the last execution of the data job with the specified name, or an empty optional if
   * there are no executions. The last execution is considered the one with the most recent start
   * time.
   *
   * @param dataJobName The name of the data job whose last execution to return.
   * @return The last execution of the data job if any, otherwise, {@link Optional#empty()}.
   */
  public Optional<com.vmware.taurus.service.model.DataJobExecution> getLastExecution(
      String dataJobName) {
    return jobExecutionRepository.findFirstByDataJobNameOrderByStartTimeDesc(dataJobName);
  }

  /**
   * We need to keep in sync all job executions in the database in case of Control Service downtime
   * or missed Kubernetes Job Event
   *
   * <p>This method synchronizes Data Job Executions in the database with the actual running jobs in
   * Kubernetes.
   *
   * <p>Note: It takes into account the executions that are started concurrently during the
   * synchronization or delayed Kubernetes Job Events by synchronizing only executions that are
   * started before now() - 3 minutes.
   *
   * @param runningJobExecutionIds running job identifiers in Kubernetes
   */
  public void syncJobExecutionStatuses(List<String> runningJobExecutionIds) {
    if (runningJobExecutionIds == null) {
      return;
    }
    var runningJobStatus = List.of(ExecutionStatus.SUBMITTED, ExecutionStatus.RUNNING);
    List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsToBeUpdated =
        jobExecutionRepository
            .findDataJobExecutionsByStatusInAndStartTimeBefore(
                runningJobStatus, OffsetDateTime.now().minusMinutes(3))
            .stream()
            .filter(dataJobExecution -> !runningJobExecutionIds.contains(dataJobExecution.getId()))
            .collect(Collectors.toList());

    if (!dataJobExecutionsToBeUpdated.isEmpty()) {
      var jobsToUpdate =
          dataJobExecutionsToBeUpdated.stream().map(e -> e.getId()).collect(Collectors.toList());
      jobExecutionRepository.updateExecutionStatusWhereOldStatusInAndExecutionIdIn(
          ExecutionStatus.SUCCEEDED,
          OffsetDateTime.now(),
          "Status is set by VDK Control Service",
          runningJobStatus,
          jobsToUpdate);
      dataJobExecutionsToBeUpdated.forEach(
          dataJobExecution -> log.info("Sync Data Job Execution status: {}", dataJobExecution));
    }
  }

  public DataJobExecutionLogs getJobExecutionLogs(
      String teamName, String jobName, String executionId, Integer tailLines) {
    // we use readJobExecution to check that execution exists
    var execution = readJobExecution(teamName, jobName, executionId);

    // if execution.getLogsUrl()
    // TODO: should we return redirect link ? Or we can let users (e.g CLI) to decide which to use
    // themselves
    // for example CLI may decide to use logsUrl if it is not empty otherwise it would use Execution
    // Logging API

    // TODO: we need to consider how to throttle memory and api requests ...
    //  Maybe cache file on disk? Or limit concurrent logging api requests? or limit max lines
    //  caching logs on disk may help reduce requests toward Kubernetes API as well
    //  (for example: use logs from disk and max 1 req per minute toward API)

    if (tailLines != null && tailLines <= 0) {
      tailLines = null;
    }

    try {
      var logs = dataJobsKubernetesService.getJobLogs(executionId, tailLines);
      DataJobExecutionLogs executionLogs = new DataJobExecutionLogs();
      executionLogs.setLogs(logs.orElseGet(() -> ""));
      return executionLogs;
    } catch (Exception e) {
      var msg =
          String.format(
              "Failed to get logs for job execution %s (job: %s, team: %s)",
              executionId, jobName, teamName);
      throw new KubernetesException(msg, e);
    }
  }

  /**
   * This method returns a per job name mapping containing statuses count for a given data job and
   * status list. The method is not guaranteed to return a mapping if a data job does not have
   * executions with a provided status or if one of the provided ExecutionStatuses is not present in
   * the database, thus it is advisable to use Map::getOrDefault to prevent null pointer exceptions
   * when retrieving both mappings.
   *
   * @param dataJobs The data jobs to count statuses of.
   * @param statuses The statuses to count.
   * @return Map which maps a data job name to a Map<ExecutionStatus, Integer>
   */
  public Map<String, Map<ExecutionStatus, Integer>> countExecutionStatuses(
      List<String> dataJobs, List<ExecutionStatus> statuses) {

    Map<String, Map<ExecutionStatus, Integer>> returnValue = new HashMap<>();
    var statusCount = jobExecutionRepository.countDataJobExecutionStatuses(statuses, dataJobs);

    // Populate count mappings.
    for (var statusesCount : statusCount) {

      if (!returnValue.containsKey(statusesCount.getJobName())) {
        returnValue.put(statusesCount.getJobName(), new HashMap<>());
      }

      returnValue
          .get(statusesCount.getJobName())
          .put(statusesCount.getStatus(), statusesCount.getStatusCount());
    }

    return returnValue;
  }

  private static String getJobExecutionApiMessage(
      ExecutionStatus executionStatus, String containerTerminationMessage) {
    switch (executionStatus) {
      case SKIPPED:
        return "Skipping job execution due to another parallel running execution.";
      case USER_ERROR:
        if (StringUtils.equalsIgnoreCase(
            containerTerminationMessage,
            JobExecutionResultManager.TERMINATION_REASON_OUT_OF_MEMORY)) {
          return "Out of memory error on the K8S pod. Please optimize your data job.";
        }
        return executionStatus.getPodStatus();
      default:
        return executionStatus.getPodStatus();
    }
  }

  private static String getExecutionId(String jobName) {
    return String.format("%s-%s", jobName, Instant.now().getEpochSecond());
  }

  private void saveDataJobExecution(
      DataJob dataJob,
      String executionId,
      String opId,
      com.vmware.taurus.service.model.ExecutionType executionType,
      ExecutionStatus executionStatus,
      String startedBy,
      OffsetDateTime startTime) {

    com.vmware.taurus.service.model.DataJobExecution dataJobExecution =
        com.vmware.taurus.service.model.DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .opId(opId)
            .type(executionType)
            .status(executionStatus)
            .startedBy(startedBy)
            .startTime(startTime)
            .build();
    jobExecutionRepository.save(dataJobExecution);
  }

  private DataJobExecution convertToModel(
      com.vmware.taurus.service.model.DataJobExecution dataJobExecution) {
    return ToApiModelConverter.jobExecutionToConvert(
        dataJobExecution, jobExecutionLogsUrlBuilder.build(dataJobExecution));
  }
}
