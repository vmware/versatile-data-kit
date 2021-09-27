/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

import com.google.gson.JsonSyntaxException;
import io.kubernetes.client.ApiException;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.exception.DataJobAlreadyRunningException;
import com.vmware.taurus.exception.DataJobDeploymentNotFoundException;
import com.vmware.taurus.exception.DataJobExecutionCannotBeCancelledException;
import com.vmware.taurus.exception.DataJobExecutionNotFoundException;
import com.vmware.taurus.exception.DataJobExecutionStatusNotValidException;
import com.vmware.taurus.exception.DataJobNotFoundException;
import com.vmware.taurus.exception.ExecutionCancellationFailureReason;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.JobEnvVar;


/**
 * Job Execution service.
 * <p>
 * Execution of Data Job is done by starting Kubernetes Job.
 */
@Slf4j
@AllArgsConstructor
@Service
public class JobExecutionService {

   @AllArgsConstructor
   public enum ExecutionType {
      MANUAL("manual"),
      SCHEDULED("scheduled");

      @Getter
      private final String value;
   }

   private JobsService jobsService;

   private JobExecutionRepository jobExecutionRepository;

   private DeploymentService deploymentService;

   private DataJobsKubernetesService dataJobsKubernetesService;

   private OperationContext operationContext;

   public String startDataJobExecution(String teamName, String jobName, String deploymentId, DataJobExecutionRequest jobExecutionRequest) {
      // TODO: deployment ID support
      // TODO: dataJobExecutionRequest args are ignored currently
      var extraJobArguments = jobExecutionRequest.getArgs();
      DataJob dataJob = jobsService.getByNameAndTeam(jobName, teamName).orElseThrow(() -> new DataJobNotFoundException(jobName));

      JobDeploymentStatus jobDeploymentStatus = deploymentService.readDeployment(jobName.toLowerCase())
            .orElseThrow(() -> new DataJobDeploymentNotFoundException(jobName));

      String executionId = getExecutionId(JobImageDeployer.getCronJobName(jobName));

      try {
         if (dataJobsKubernetesService.isRunningJob(jobName)) {
            throw new DataJobAlreadyRunningException(jobName);
         }
         Map<String, String> annotations = new LinkedHashMap<>();

         String opId = operationContext.getOpId();
         annotations.put(JobAnnotation.OP_ID.getValue(), opId);

         String startedBy = StringUtils.isNotBlank(jobExecutionRequest.getStartedBy()) ?
               jobExecutionRequest.getStartedBy() + "/" + operationContext.getUser() :
               operationContext.getUser();
         String startedByBuilt = buildStartedByAnnotationValue(ExecutionType.MANUAL, startedBy);
         annotations.put(JobAnnotation.STARTED_BY.getValue(), startedByBuilt);
         annotations.put(JobAnnotation.EXECUTION_TYPE.getValue(), ExecutionType.MANUAL.getValue());

         Map<String, String> envs = new LinkedHashMap<>();
         envs.put(JobEnvVar.VDK_OP_ID.getValue(), opId);

         // Start K8S Job
         dataJobsKubernetesService.startNewCronJobExecution(jobDeploymentStatus.getCronJobName(), executionId, annotations, envs, extraJobArguments, jobName);

         // Save Data Job execution
         saveDataJobExecution(dataJob, executionId, opId, com.vmware.taurus.service.model.ExecutionType.MANUAL, ExecutionStatus.SUBMITTED, startedByBuilt);

         return executionId;
      } catch (ApiException e) {
         throw new KubernetesException(String.format("Cannot start a Data Job '%s' execution with execution id '%s'", jobName, executionId), e);
      }
   }

   public void cancelDataJobExecution(String teamName, String jobName, String executionId) {
      log.info("Attempting to cancel data job execution: {}", executionId);

      try {

         if (!jobsService.jobWithTeamExists(jobName, teamName)) {
            log.info("No such data job: {} found for team: {} .", jobName, teamName);
            throw new DataJobExecutionCannotBeCancelledException(executionId, ExecutionCancellationFailureReason.DataJobNotFound);
         }

         var jobExecutionOptional = jobExecutionRepository.findById(executionId);

         if (jobExecutionOptional.isEmpty()) {
            log.info("Execution: {} for data job: {} with team: {} not found!", executionId, teamName, jobName);
            throw new DataJobExecutionCannotBeCancelledException(executionId, ExecutionCancellationFailureReason.DataJobExecutionNotFound);
         }

         var jobExecution = jobExecutionOptional.get();
         var jobStatus = jobExecution.getStatus();
         var acceptedStatusToCancelExecutionSet = Set.of(ExecutionStatus.SUBMITTED, ExecutionStatus.RUNNING);
         if (!acceptedStatusToCancelExecutionSet.contains(jobStatus)) {
            log.info("Trying to cancel execution: {} for data job: {} with team: {} but job has status {}!", executionId, teamName, jobName, jobStatus.toString());
            throw new DataJobExecutionCannotBeCancelledException(executionId, ExecutionCancellationFailureReason.ExecutionNotRunning);
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
         throw new KubernetesException(String.format("Cannot cancel a Data Job '%s' execution with execution id '%s'", jobName, executionId), e);
      }
   }

   public List<DataJobExecution> listJobExecutions(String teamName, String jobName, List<String> apiExecutionStatuses) {
      if (!jobsService.jobWithTeamExists(jobName, teamName)) {
         throw new DataJobNotFoundException(jobName);
      }

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutions;

      if (!CollectionUtils.isEmpty(apiExecutionStatuses)) {
         List<com.vmware.taurus.service.model.ExecutionStatus> modelExecutionStatuses =
               apiExecutionStatuses
                     .stream()
                     .map(apiExecutionStatus -> {
                        try {
                           DataJobExecution.StatusEnum statusEnum = DataJobExecution.StatusEnum.fromValue(apiExecutionStatus);
                           return ToModelApiConverter.toExecutionStatus(statusEnum);
                        } catch (Exception ex) {
                           throw new DataJobExecutionStatusNotValidException(apiExecutionStatus);
                        }
                     })
                     .collect(Collectors.toList());


         dataJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(jobName, modelExecutionStatuses);
      } else {
         dataJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(jobName);
      }

      return dataJobExecutions
            .stream()
            .map(dataJobExecution -> ToApiModelConverter.jobExecutionToConvert(dataJobExecution))
            .collect(Collectors.toList());
   }

   public DataJobExecution readJobExecution(String teamName, String jobName, String executionId) {
      if (!jobsService.jobWithTeamExists(jobName, teamName)) {
         throw new DataJobNotFoundException(jobName);
      }

      return jobExecutionRepository.findById(executionId)
            .map(dataJobExecution -> ToApiModelConverter.jobExecutionToConvert(dataJobExecution))
            .orElseThrow(() -> new DataJobExecutionNotFoundException(executionId));
   }

   public void updateJobExecution(final DataJob dataJob, final KubernetesService.JobExecution jobExecution) {
      if (StringUtils.isBlank(jobExecution.getExecutionId())) {
         log.warn("Could not store Data Job execution due to the missing execution id: {}", jobExecution);
         return;
      }

      final Optional<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionPersistedOptional =
              jobExecutionRepository.findById(jobExecution.getExecutionId());
      final ExecutionStatus status = getJobExecutionStatus(jobExecution);
      //This set contains all the statuses that should not be changed to something else if present in the DB.
      //Using a hash set, because it allows null elements, no NullPointer when contains method called with null.
      var finalStatusSet = new HashSet<>(List.of(ExecutionStatus.CANCELLED, ExecutionStatus.FAILED,
                                                 ExecutionStatus.FINISHED, ExecutionStatus.SKIPPED));

      if (dataJobExecutionPersistedOptional.isPresent() &&
              (dataJobExecutionPersistedOptional.get().getStatus() == status ||
                      finalStatusSet.contains(dataJobExecutionPersistedOptional.get().getStatus()))) {
         return;
      }

      // Optimization:
      // if there is an existing execution in the database and
      // the status has not changed (the new status is equal to the old one)
      // do not update the record
      final com.vmware.taurus.service.model.DataJobExecution.DataJobExecutionBuilder dataJobExecutionBuilder =
              dataJobExecutionPersistedOptional.isPresent() ?
                      dataJobExecutionPersistedOptional.get().toBuilder() :
                      com.vmware.taurus.service.model.DataJobExecution.builder()
                              .id(jobExecution.getExecutionId())
                              .dataJob(dataJob)
                              .type(ExecutionType.MANUAL.getValue().equals(jobExecution.getExecutionType()) ?
                                      com.vmware.taurus.service.model.ExecutionType.MANUAL :
                                      com.vmware.taurus.service.model.ExecutionType.SCHEDULED);

      com.vmware.taurus.service.model.DataJobExecution dataJobExecution = dataJobExecutionBuilder
              .status(status)
              .message(getJobExecutionApiMessage(status, jobExecution))
              .opId(jobExecution.getOpId())
              .startTime(jobExecution.getStartTime())
              .endTime(jobExecution.getEndTime())
              .vdkVersion("") // TODO [miroslavi] VDK version should come from the termination message
              .jobVersion(jobExecution.getJobVersion())
              .jobSchedule(jobExecution.getJobSchedule())
              .resourcesCpuRequest(jobExecution.getResourcesCpuRequest())
              .resourcesCpuLimit(jobExecution.getResourcesCpuLimit())
              .resourcesMemoryRequest(jobExecution.getResourcesMemoryRequest())
              .resourcesMemoryLimit(jobExecution.getResourcesMemoryLimit())
              .lastDeployedDate(jobExecution.getDeployedDate())
              .lastDeployedBy(jobExecution.getDeployedBy())
              .build();
      jobExecutionRepository.save(dataJobExecution);
   }

   /**
    * We need to keep in sync all job executions in the database
    * in case of Control Service downtime or missed Kubernetes Job Event
    * <p>
    * This method synchronizes Data Job Executions in the database
    * with the actual running jobs in Kubernetes.
    * <p>
    * Note: It takes into account the executions that are started concurrently during
    * the synchronization or delayed Kubernetes Job Events by synchronizing
    * only executions that are started before now() - 3 minutes.
    *
    * @param runningJobExecutionIds running job identifiers in Kubernetes
    */
   public void syncJobExecutionStatuses(List<String> runningJobExecutionIds) {
      if (runningJobExecutionIds == null) {
         return;
      }

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsToBeUpdated =
            jobExecutionRepository.findDataJobExecutionsByStatusInAndStartTimeBefore(
                        List.of(ExecutionStatus.RUNNING), OffsetDateTime.now().minusMinutes(3))
                  .stream()
                  .filter(dataJobExecution -> !runningJobExecutionIds.contains(dataJobExecution.getId()))
                  .map(dataJobExecution -> {
                     dataJobExecution.setStatus(ExecutionStatus.FINISHED);
                     dataJobExecution.setMessage("Status is set by VDK Control Service");
                     return dataJobExecution;
                  })
                  .collect(Collectors.toList());

      if (!dataJobExecutionsToBeUpdated.isEmpty()) {
         jobExecutionRepository.saveAll(dataJobExecutionsToBeUpdated);
         dataJobExecutionsToBeUpdated
               .forEach(dataJobExecution -> log.info("Sync Data Job Execution status: {}", dataJobExecution));
      }
   }

   private static String getJobExecutionApiMessage(ExecutionStatus executionStatus, KubernetesService.JobExecution jobExecution) {
      switch (executionStatus) {
         case SKIPPED:
            return "Skipping job execution due to another parallel running execution.";
         default:
            return jobExecution.getTerminationMessage();
      }
   }

   private void saveDataJobExecution(
         DataJob dataJob,
         String executionId,
         String opId,
         com.vmware.taurus.service.model.ExecutionType executionType,
         ExecutionStatus executionStatus,
         String startedBy) {

      com.vmware.taurus.service.model.DataJobExecution dataJobExecution = com.vmware.taurus.service.model.DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .opId(opId)
            .type(executionType)
            .status(executionStatus)
            .startedBy(startedBy)
            .build();

      jobExecutionRepository.save(dataJobExecution);
   }

   private static String getExecutionId(String jobName) {
      return String.format("%s-%s", jobName, Instant.now().getEpochSecond());
   }

   private static String buildStartedByAnnotationValue(ExecutionType executionType, String startedBy) {
      return executionType.getValue() + "/" + startedBy;
   }

   public static ExecutionStatus getJobExecutionStatus(KubernetesService.JobExecution jobExecution) {

      if (isJobExecutionSkipped(jobExecution)) {
         return ExecutionStatus.SKIPPED;
      } else if (isJobExecutionFailed(jobExecution)) {
         return ExecutionStatus.FAILED;
      }

      var jobStatus = jobExecution.getStatus();
      switch (jobStatus) {
         case RUNNING:
            return ExecutionStatus.RUNNING;
         case FAILED:
            return ExecutionStatus.FAILED;
         case FINISHED:
            return ExecutionStatus.FINISHED;
         case SKIPPED:
            return ExecutionStatus.SKIPPED;
         case CANCELLED:
            return ExecutionStatus.CANCELLED;
         default:
            log.warn("Unexpected job status: '" + jobStatus + "' in JobExecutionStatus.Status.");
            return null;
      }
   }

   /**
    * This is a helper method used to determine if a data job execution's status should be changed to SKIPPED.
    *
    * @param jobExecution
    * @return
    */
   private static boolean isJobExecutionSkipped(KubernetesService.JobExecution jobExecution) {
      return jobExecutionEquals(jobExecution, KubernetesService.PodTerminationMessage.SKIPPED);
   }

   /**
    * This is a helper method used to determine if a data job execution's status should be changed to FAILED.
    *
    * @param jobExecution
    * @return
    */
   private static boolean isJobExecutionFailed(KubernetesService.JobExecution jobExecution) {
      return jobExecutionEquals(jobExecution, KubernetesService.PodTerminationMessage.USER_ERROR) ||
            jobExecutionEquals(jobExecution, KubernetesService.PodTerminationMessage.PLATFORM_ERROR);
   }

   private static boolean jobExecutionEquals(KubernetesService.JobExecution jobExecution, KubernetesService.PodTerminationMessage podTerminationMessage) {
      return podTerminationMessage.getValue().equals(StringUtils.trim(jobExecution.getTerminationMessage()));
   }
}
