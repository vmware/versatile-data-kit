/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.google.gson.JsonObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionTerminationMessage;
import com.vmware.taurus.service.model.ExecutionTerminationStatus;

public class JobExecutionUtilTest {

   @Test
   public void testGetTerminationMessage_nullTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationMessage actualTerminationMessage = JobExecutionUtil.getTerminationMessage(null, null);

      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetTerminationMessage_emptyTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationMessage actualTerminationMessage = JobExecutionUtil.getTerminationMessage(ExecutionStatus.RUNNING, "");

      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetTerminationMessage_jsonTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationStatus expectedTerminationStatus = ExecutionTerminationStatus.USER_ERROR;
      String vdkVersion = "1.2.3";
      JsonObject expectedTerminationMessage = new JsonObject();
      expectedTerminationMessage.addProperty(JobExecutionUtil.TERMINATION_MESSAGE_ATTRIBUTE_STATUS, expectedTerminationStatus.getString());
      expectedTerminationMessage.addProperty(JobExecutionUtil.TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, vdkVersion);

      ExecutionTerminationMessage actualTerminationMessage = JobExecutionUtil.getTerminationMessage(ExecutionStatus.FAILED, expectedTerminationMessage.toString());

      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals(vdkVersion, actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetTerminationMessage_stringTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationStatus expectedTerminationStatus = ExecutionTerminationStatus.USER_ERROR;
      ExecutionTerminationMessage actualTerminationMessage = JobExecutionUtil.getTerminationMessage(ExecutionStatus.FAILED, expectedTerminationStatus.getString());
      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getTerminationStatus());
   }

   @Test
   public void testGetExecutionStatus_emptyTerminationMessageAndExecutionStatusFinished_shouldReturnTerminationStatusSuccess() {
      ExecutionTerminationStatus actualTerminationStatus = JobExecutionUtil.getTerminationStatus(ExecutionStatus.FINISHED, "");

      Assertions.assertEquals(ExecutionTerminationStatus.SUCCESS, actualTerminationStatus);
   }

   @Test
   public void testGetExecutionStatus_emptyTerminationMessageAndExecutionStatusFailed_shouldReturnTerminationStatusPlatformError() {
      ExecutionTerminationStatus actualTerminationStatus = JobExecutionUtil.getTerminationStatus(ExecutionStatus.FAILED, "");

      Assertions.assertEquals(ExecutionTerminationStatus.PLATFORM_ERROR, actualTerminationStatus);
   }

   @Test
   public void testGetExecutionStatus_emptyTerminationMessageAndExecutionStatusRunning_shouldReturnTerminationStatusNone() {
      ExecutionTerminationStatus actualTerminationStatus = JobExecutionUtil.getTerminationStatus(ExecutionStatus.RUNNING, "");

      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualTerminationStatus);
   }

   @Test
   public void testGetExecutionStatus_terminationMessageSuccessAndExecutionStatusFinished_shouldReturnTerminationStatusSuccess() {
      ExecutionTerminationStatus actualTerminationStatus =
            JobExecutionUtil.getTerminationStatus(ExecutionStatus.FINISHED, ExecutionTerminationStatus.SUCCESS.getString());

      Assertions.assertEquals(ExecutionTerminationStatus.SUCCESS, actualTerminationStatus);
   }

   @Test
   public void testGetExecutionStatus_executionSucceededNull_shouldReturnExecutionStatusRunning() {
      ExecutionStatus actualExecutionStatus = JobExecutionUtil.getExecutionStatus(null);

      Assertions.assertEquals(ExecutionStatus.RUNNING, actualExecutionStatus);
   }

   @Test
   public void testGetExecutionStatus_executionSucceededTrue_shouldReturnExecutionStatusFinished() {
      ExecutionStatus actualExecutionStatus = JobExecutionUtil.getExecutionStatus(true);

      Assertions.assertEquals(ExecutionStatus.FINISHED, actualExecutionStatus);
   }

   @Test
   public void testGetExecutionStatus_executionSucceededFalse_shouldReturnExecutionStatusFailed() {
      ExecutionStatus actualExecutionStatus = JobExecutionUtil.getExecutionStatus(false);

      Assertions.assertEquals(ExecutionStatus.FAILED, actualExecutionStatus);
   }

   @Test
   public void testUpdateExecutionStatusBasedOnTerminationStatus_executionStatusFinishedAndTerminationStatusUserError_shouldReturnExecutionStatusFailed() {
      ExecutionStatus actualExecutionStatus =
            JobExecutionUtil.updateExecutionStatusBasedOnTerminationStatus(ExecutionStatus.FINISHED, ExecutionTerminationStatus.USER_ERROR);

      Assertions.assertEquals(ExecutionStatus.FAILED, actualExecutionStatus);
   }

   @Test
   public void testUpdateExecutionStatusBasedOnTerminationStatus_executionStatusFinishedAndTerminationStatusSkipped_shouldReturnExecutionStatusSkipped() {
      ExecutionStatus actualExecutionStatus =
            JobExecutionUtil.updateExecutionStatusBasedOnTerminationStatus(ExecutionStatus.FINISHED, ExecutionTerminationStatus.SKIPPED);

      Assertions.assertEquals(ExecutionStatus.SKIPPED, actualExecutionStatus);
   }

   @Test
   public void testUpdateExecutionStatusBasedOnTerminationStatus_executionStatusFinishedAndTerminationStatusPlatformError_shouldReturnExecutionStatusFinished() {
      ExecutionStatus actualExecutionStatus =
            JobExecutionUtil.updateExecutionStatusBasedOnTerminationStatus(ExecutionStatus.FINISHED, ExecutionTerminationStatus.PLATFORM_ERROR);

      Assertions.assertEquals(ExecutionStatus.FINISHED, actualExecutionStatus);
   }
}
