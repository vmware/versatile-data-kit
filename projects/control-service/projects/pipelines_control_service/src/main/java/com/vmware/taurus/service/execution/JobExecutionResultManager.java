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

/**
 * This class helps to determine Execution Status
 * as it is difficult to be determined and depend on many components.
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
   private static class PodTerminationMessage {
      private String status;
      private String vdkVersion;
   }

   /**
    * Extracts and determines the execution status and vdk version
    * based on K8S Job status and K8S Pod termination message.
    *
    * @param jobExecution
    *       current job execution
    * @return returns the execution result that contains execution status, termination status and vdk version
    */
   public static ExecutionResult getResult(KubernetesService.JobExecution jobExecution) {
      PodTerminationMessage podTerminationMessage = parsePodTerminationMessage(jobExecution.getPodTerminationMessage());
      ExecutionStatus executionStatus = getExecutionStatus(
            jobExecution.getSucceeded(),
            podTerminationMessage.getStatus(),
            jobExecution.getJobTerminationReason(),
            jobExecution.getContainerTerminationReason(),
            jobExecution.getStartTime());

      return ExecutionResult.builder()
            .executionStatus(executionStatus)
            .vdkVersion(podTerminationMessage.getVdkVersion())
            .build();
   }

   /**
    * Determines the execution status based on K8S Job status as follows:
    * <ul>
    *   <li>If K8S Job succeeded is null (which means there is no K8S Job condition
    *   because the job is already running), then the execution status will be either SUBMITTED or RUNNING</li>
    *   <li>If the K8S Job succeeded is true, then the execution status will be either SUCCEEDED or
    *   the one that comes from K8S Pod termination message (e.g. SUCCESS, USER_ERROR, PLATFORM_ERROR, etc.)</li>
    *   <li>If K8S Job succeeded is false, then the execution status will be either USER_ERROR or PLATFORM_ERROR.
    *   In case of missing termination status due to the missing K8S Pod
    *   it sets an appropriate execution status based on the K8S Job termination reason.</li>
    * </ul>
    *
    * @param executionSucceeded K8s Job status (true - succeeded, false - failed, null - running)
    * @param podTerminationStatus termination status returned from K8S Pod (e.g. "Success", "User error", etc.)
    * @param jobTerminationReason condition reason as reported by K8s Job (e.g. "DeadlineExceeded", "BackoffLimitExceeded", etc.)
    * @param containerTerminationReason termination reason for pod container as returned by K8s pod container (e.g., "OOMKilled", etc.)
    * @param executionStarTime K8S Job execution start time
    * @return if there is no termination message due to the missing K8S Pod
     * returns execution status based on K8S Job status otherwise returns
     * execution status based on the K8S Pod termination status.
    */
   private static ExecutionStatus getExecutionStatus(
         Boolean executionSucceeded,
         String podTerminationStatus,
         String jobTerminationReason,
         String containerTerminationReason,
         OffsetDateTime executionStarTime) {

      ExecutionStatus executionStatus;

      if (executionSucceeded == null) {
         executionStatus = executionStarTime == null ?
               ExecutionStatus.SUBMITTED :
               ExecutionStatus.RUNNING;
      } else if (executionSucceeded && StringUtils.isEmpty(podTerminationStatus)) {
         executionStatus = ExecutionStatus.SUCCEEDED;
      } else if (!executionSucceeded && StringUtils.isEmpty(podTerminationStatus)) {
         executionStatus = inferError(jobTerminationReason, containerTerminationReason);
      } else {
         executionStatus = Arrays.stream(ExecutionStatus.values())
               .filter(status -> status.getPodStatus().equals(podTerminationStatus))
               .findAny()
               .orElse(ExecutionStatus.PLATFORM_ERROR);
      }

      return executionStatus;
   }

   /**
    * Returns execution status based on K8S Job status.
    *
    * @param jobTerminationReason condition reason as reported by K8s Job (e.g. "DeadlineExceeded", "BackoffLimitExceeded", etc.)
    * @param containerTerminationReason termination reason for pod container as reported by K8s Job (e.g., "OOMKilled", etc.)
    * @return returns execution status based on K8S Job status.
    */
   private static ExecutionStatus inferError(String jobTerminationReason, String containerTerminationReason) {
      ExecutionStatus executionStatus;

      if (StringUtils.equalsIgnoreCase(jobTerminationReason, TERMINATION_REASON_DEADLINE_EXCEEDED) ||
            StringUtils.equalsIgnoreCase(containerTerminationReason, TERMINATION_REASON_OUT_OF_MEMORY)) {
         executionStatus = ExecutionStatus.USER_ERROR;
      } else {
         executionStatus = ExecutionStatus.PLATFORM_ERROR;
      }

      return executionStatus;
   }

   /**
    * Extracts attributes from K8S Pod termination message (e.g. status, vdk_version)
    *
    * @param podTerminationMessage
    *       K8S Pod termination message in JSON or Plain Text format
    * @return returns parsed termination message
    */
   private static PodTerminationMessage parsePodTerminationMessage(String podTerminationMessage) {
      String status = "";
      String vdkVersion = "";

      if (!StringUtils.isEmpty(podTerminationMessage)) {
         try {
            Map<String, String> obj = new Gson().fromJson(podTerminationMessage, Map.class);
            status = obj.get(TERMINATION_MESSAGE_ATTRIBUTE_STATUS);
            vdkVersion = obj.getOrDefault(TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, "");
         } catch (com.google.gson.JsonSyntaxException ex) {
            // Fallback to the old plain text format
            status = podTerminationMessage;
         }
      }

      return PodTerminationMessage
            .builder()
            .status(status)
            .vdkVersion(vdkVersion)
            .build();
   }
}
