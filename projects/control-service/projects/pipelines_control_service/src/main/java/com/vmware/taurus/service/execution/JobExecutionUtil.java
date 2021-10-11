/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.Instant;
import java.util.Arrays;
import java.util.Map;

import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionTerminationMessage;
import com.vmware.taurus.service.model.ExecutionTerminationStatus;

@Slf4j
public class JobExecutionUtil {

   static final String TERMINATION_MESSAGE_ATTRIBUTE_STATUS = "status";
   static final String TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION = "vdk_version";

   public static ExecutionTerminationMessage getTerminationMessage(ExecutionStatus executionStatus, String terminationMessage) {
      String vdkVersion = "";
      String terminationStatus = "";

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

      return ExecutionTerminationMessage.builder()
            .terminationStatus(getTerminationStatus(executionStatus, terminationStatus))
            .vdkVersion(vdkVersion)
            .build();
   }

   public static ExecutionStatus getExecutionStatus(Boolean executionSucceeded) {
      ExecutionStatus executionStatus;

      if (executionSucceeded == null) {
         executionStatus = ExecutionStatus.RUNNING;
      } else if (executionSucceeded) {
         executionStatus = ExecutionStatus.FINISHED;
      } else {
         executionStatus = ExecutionStatus.FAILED;
      }

      return executionStatus;
   }

   static ExecutionTerminationStatus getTerminationStatus(ExecutionStatus executionStatus, String terminationMessage) {
      ExecutionTerminationStatus terminationStatus = ExecutionTerminationStatus.NONE;

      // if there is no termination message due to the missing K8S Pod
      // the method sets an appropriate termination status based on the execution status
      if (StringUtils.isEmpty(terminationMessage) && ExecutionStatus.FINISHED.equals(executionStatus)) {
         terminationStatus = ExecutionTerminationStatus.SUCCESS;
      } else if (StringUtils.isEmpty(terminationMessage) && ExecutionStatus.FAILED.equals(executionStatus)) {
         terminationStatus = ExecutionTerminationStatus.PLATFORM_ERROR;
      } else {
         terminationStatus = Arrays.stream(ExecutionTerminationStatus.values())
               .filter(status -> status.getString().equals(terminationMessage))
               .findAny()
               .orElse(terminationStatus);
      }

      return terminationStatus;
   }

   static ExecutionStatus updateExecutionStatusBasedOnTerminationStatus(ExecutionStatus executionStatus, ExecutionTerminationStatus terminationStatus) {
      if (isJobExecutionSkipped(terminationStatus)) {
         executionStatus = ExecutionStatus.SKIPPED;
      } else if (isJobExecutionFailed(terminationStatus)) {
         executionStatus = ExecutionStatus.FAILED;
      }

      return executionStatus;
   }

   static String getExecutionId(String jobName) {
      return String.format("%s-%s", jobName, Instant.now().getEpochSecond());
   }

   /**
    * This is a helper method used to determine if a data job execution's status should be changed to SKIPPED.
    *
    * @param terminationStatus
    * @return
    */
   private static boolean isJobExecutionSkipped(ExecutionTerminationStatus terminationStatus) {
      return ExecutionTerminationStatus.SKIPPED.equals(terminationStatus);
   }

   /**
    * This is a helper method used to determine if a data job execution's status should be changed to FAILED.
    *
    * @param terminationStatus
    * @return
    */
   private static boolean isJobExecutionFailed(ExecutionTerminationStatus terminationStatus) {
      return ExecutionTerminationStatus.USER_ERROR.equals(terminationStatus);
   }
}
