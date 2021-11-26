/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.OffsetDateTime;
import java.util.Arrays;
import java.util.Map;

import com.google.gson.Gson;
import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.ExecutionResult;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionTerminationStatus;

/**
 * This class helps to determine Execution Status and Termination Status
 * as they are difficult to determine and depend on many components.
 * It extracts, determines and combines the data as {@link ExecutionResult}.
 */
@Slf4j
public class JobExecutionResultManager {

   static final String TERMINATION_MESSAGE_ATTRIBUTE_STATUS = "status";
   static final String TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION = "vdk_version";
   static final String TERMINATION_REASON_DEADLINE_EXCEEDED = "DeadlineExceeded";
   static final String TERMINATION_REASON_OUT_OF_MEMORY = "OOMKilled";

   @Data
   @Builder
   private static class TerminationMessage {
      private String terminationStatus;
      private String vdkVersion;
   }

   /**
    * Extracts and determines the execution status, termination status and vdk version
    * based on K8S Job status and K8S Pod termination message.
    *
    * @param jobExecution current job execution
    * @return returns the execution result that contains execution status, termination status and vdk version
    */
   public static ExecutionResult getResult(KubernetesService.JobExecution jobExecution) {
      TerminationMessage terminationMessage = parseTerminationMessage(jobExecution.getTerminationMessage());
      ExecutionStatus executionStatus = getExecutionStatus(jobExecution.getSucceeded(), jobExecution.getStartTime());
      ExecutionTerminationStatus terminationStatus = getTerminationStatus(terminationMessage.getTerminationStatus());

      terminationStatus = updateTerminationStatusBasedOnExecutionStatus(
              terminationStatus, executionStatus, terminationMessage.getTerminationStatus(), jobExecution.getJobTerminationReason(), jobExecution.getContainerTerminationReason());
      executionStatus = updateExecutionStatusBasedOnTerminationStatus(executionStatus, terminationStatus);

      return ExecutionResult.builder()
            .executionStatus(executionStatus)
            .terminationStatus(terminationStatus)
            .vdkVersion(terminationMessage.getVdkVersion())
            .build();
   }

   /**
    * Determines the execution status based on K8S Job status as follows:
    * <ul>
    *   <li>If K8S Job succeeded is null (which means there is no K8S Job condition
    *   because the job has still not finished), then the execution status will be either RUNNING,
    *   if the K8S Job has start time, or SUBMITTED, if the K8S Job does not have start time,
    *   i.e. it was created but the execution has not started yet.</li>
    *   <li>If the K8S Job succeeded is true, then the execution status will be FINISHED</li>
    *   <li>If K8S Job succeeded is false, then the execution status will be FAILED</li>
    * </ul>
    *
    * @param executionSucceeded
    * @param startTime
    * @return
    */
   private static ExecutionStatus getExecutionStatus(Boolean executionSucceeded, OffsetDateTime startTime) {
      ExecutionStatus executionStatus;

      if (executionSucceeded == null) {
         if (startTime == null) {
            executionStatus = ExecutionStatus.SUBMITTED;
         } else {
            executionStatus = ExecutionStatus.RUNNING;
         }
      } else if (executionSucceeded) {
         executionStatus = ExecutionStatus.FINISHED;
      } else {
         executionStatus = ExecutionStatus.FAILED;
      }

      return executionStatus;
   }

   /**
    * Determines the job execution termination status based on
    * the K8S Pod termination message (e.g. SUCCESS, USER_ERROR, PLATFORM_ERROR, etc.)
    *
    * @param podTerminationMessage termination message returned by K8S Pod (e.g. "Success", "User error", etc.)
    * @return if there is a K8S Pod termination message returns appropriate termination status otherwise returns NONE
    */
   private static ExecutionTerminationStatus getTerminationStatus(String podTerminationMessage) {
      return Arrays.stream(ExecutionTerminationStatus.values())
            .filter(status -> status.getString().equals(podTerminationMessage))
            .findAny()
            .orElse(ExecutionTerminationStatus.NONE);
   }

   /**
    * Updates job execution termination status based on job execution status.
    * In case of missing termination status due to the missing K8S Pod
    * it sets an appropriate termination status based on the execution status.
    *
    * @param terminationStatus termination status based on the K8S Pod termination status
    * @param executionStatus execution status based on K8S Job status
    * @param terminationStatusString termination status returned from K8S Pod (e.g. "Success", "User error", etc.)
    * @param jobTerminationReason condition reason as reported by K8s Job (e.g. "DeadlineExceeded", "BackoffLimitExceeded", etc.)
    * @param containerTerminationReason termination reason for pod container as reported by K8s Job (e.g., "OOMKilled", etc.)
    * @return if there is no termination message due to the missing K8S Pod
    * returns termination status based on execution status otherwise returns
    * termination status based on the K8S Pod termination status
    */
   private static ExecutionTerminationStatus updateTerminationStatusBasedOnExecutionStatus(
         ExecutionTerminationStatus terminationStatus,
         ExecutionStatus executionStatus,
         String terminationStatusString,
         String jobTerminationReason,
         String containerTerminationReason) {

      if (StringUtils.isEmpty(terminationStatusString) && ExecutionStatus.FINISHED.equals(executionStatus)) {
         terminationStatus = ExecutionTerminationStatus.SUCCESS;
      } else if (StringUtils.isEmpty(terminationStatusString) && ExecutionStatus.FAILED.equals(executionStatus)) {
         if (StringUtils.equalsIgnoreCase(jobTerminationReason, TERMINATION_REASON_DEADLINE_EXCEEDED) ||
                 StringUtils.equalsIgnoreCase(containerTerminationReason, TERMINATION_REASON_OUT_OF_MEMORY)) {
            terminationStatus = ExecutionTerminationStatus.USER_ERROR;
         } else {
            terminationStatus = ExecutionTerminationStatus.PLATFORM_ERROR;
         }
      }

      return terminationStatus;
   }

   /**
    * Updates the execution status based on termination status,
    * since we have some corner cases such as successfully completed K8S Job
    * but the K8S Pod termination status is "User error".
    *
    * @param executionStatus the execution status based on K8S Job status
    * @param terminationStatus the termination status (e.g. SUCCESS, USER_ERROR, PLATFORM_ERROR, etc.)
    * @return returns updated execution status
    */
   private static ExecutionStatus updateExecutionStatusBasedOnTerminationStatus(ExecutionStatus executionStatus, ExecutionTerminationStatus terminationStatus) {
      if (ExecutionTerminationStatus.SKIPPED.equals(terminationStatus)) {
         executionStatus = ExecutionStatus.SKIPPED;
      } else if (ExecutionTerminationStatus.USER_ERROR.equals(terminationStatus)) {
         executionStatus = ExecutionStatus.FAILED;
      }

      return executionStatus;
   }

   /**
    * Extracts attributes from K8S Pod termination message (e.g. status, vdk_version)
    *
    * @param terminationMessage K8S Pod termination message in JSON or Plain Text format
    * @return returns parsed termination message
    */
   private static TerminationMessage parseTerminationMessage(String terminationMessage) {
      String terminationStatus = "";
      String vdkVersion = "";

      if (!StringUtils.isEmpty(terminationMessage)) {
         try {
            Map<String, String> obj = new Gson().fromJson(terminationMessage, Map.class);
            terminationStatus = obj.get(TERMINATION_MESSAGE_ATTRIBUTE_STATUS);
            vdkVersion = obj.getOrDefault(TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, "");
         } catch (com.google.gson.JsonSyntaxException ex) {
            // Fallback to the old plain text format
            terminationStatus = terminationMessage;
         }
      }

      return TerminationMessage
            .builder()
            .terminationStatus(terminationStatus)
            .vdkVersion(vdkVersion)
            .build();
   }
}
