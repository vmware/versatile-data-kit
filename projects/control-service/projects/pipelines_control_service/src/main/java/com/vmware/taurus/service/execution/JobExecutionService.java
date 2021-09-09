/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.google.gson.JsonSyntaxException;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
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
import io.kubernetes.client.ApiException;
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
         dataJobsKubernetesService.startNewCronJobExecution(jobDeploymentStatus.getCronJobName(), executionId, annotations, envs);

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

   public void updateJobExecution(DataJob dataJob, KubernetesService.JobExecution jobExecution) {
      if (StringUtils.isBlank(jobExecution.getExecutionId())) {
         log.warn("Could not store Data Job execution due to the missing execution id: {}", jobExecution);
      }

      Optional<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionPersistedOptional =
            jobExecutionRepository.findById(jobExecution.getExecutionId());
      com.vmware.taurus.service.model.DataJobExecution.DataJobExecutionBuilder dataJobExecutionBuilder;
      ExecutionStatus status = getJobExecutionStatus(jobExecution);
      // Optimization:
      // if there is an existing execution in the database and
      // the status has not changed (the new status is equal to the old one)
      // do not update the record
      if (dataJobExecutionPersistedOptional.isPresent() && status != null && status.equals(dataJobExecutionPersistedOptional.get().getStatus())) {
         return;
      } else if (dataJobExecutionPersistedOptional.isPresent()) {
         dataJobExecutionBuilder = dataJobExecutionPersistedOptional.get().toBuilder();
      } else {
         com.vmware.taurus.service.model.ExecutionType executionType =
               ExecutionType.MANUAL.getValue().equals(jobExecution.getExecutionType()) ?
                     com.vmware.taurus.service.model.ExecutionType.MANUAL :
                     com.vmware.taurus.service.model.ExecutionType.SCHEDULED;
         dataJobExecutionBuilder = com.vmware.taurus.service.model.DataJobExecution.builder()
               .id(jobExecution.getExecutionId())
               .dataJob(dataJob)
               .type(executionType);
      }

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
      return String.format("%s-%s-%s", jobName, Instant.now().toEpochMilli(), UUID.randomUUID().toString().substring(0, 5));
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
