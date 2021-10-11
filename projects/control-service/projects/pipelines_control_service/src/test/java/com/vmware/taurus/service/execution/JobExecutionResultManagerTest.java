/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.google.gson.JsonObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionResult;
import com.vmware.taurus.service.model.ExecutionTerminationStatus;

public class JobExecutionResultManagerTest {

   @Test
   public void testGetResult_nullTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).terminationMessage(null).build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_emptyTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).terminationMessage("").build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_jsonTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationStatus expectedTerminationStatus = ExecutionTerminationStatus.USER_ERROR;
      String vdkVersion = "1.2.3";
      JsonObject expectedTerminationMessage = new JsonObject();
      expectedTerminationMessage.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_STATUS, expectedTerminationStatus.getString());
      expectedTerminationMessage.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, vdkVersion);

      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution
                  .builder()
                  .succeeded(false)
                  .terminationMessage(expectedTerminationMessage.toString())
                  .build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getTerminationStatus());
      Assertions.assertEquals(vdkVersion, actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_stringTerminationMessage_shouldReturnMessage() {
      ExecutionTerminationStatus expectedTerminationStatus = ExecutionTerminationStatus.USER_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution
                  .builder()
                  .succeeded(false)
                  .terminationMessage(expectedTerminationStatus.getString())
                  .build();

      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getTerminationStatus());
   }

   @Test
   public void testGetResult_emptyTerminationMessage_shouldReturnTerminationStatusNone() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).terminationMessage("").build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionTerminationStatus.NONE, actualResult.getTerminationStatus());
   }

   @Test
   public void testGetResult_terminationMessageSuccess_shouldReturnTerminationStatusSuccess() {
      ExecutionTerminationStatus expectedExecutionTerminationStatus = ExecutionTerminationStatus.SUCCESS;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).terminationMessage(expectedExecutionTerminationStatus.getString()).build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedExecutionTerminationStatus, actualResult.getTerminationStatus());
   }

   @Test
   public void testGetResult_emptyTerminationMessageAndExecutionStatusFinished_shouldReturnTerminationStatusSuccess() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).terminationMessage("").build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionTerminationStatus.SUCCESS, actualResult.getTerminationStatus());
   }

   @Test
   public void testGetResult_emptyTerminationMessageAndExecutionStatusFailed_shouldReturnTerminationStatusPlatformError() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).terminationMessage("").build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionTerminationStatus.PLATFORM_ERROR, actualResult.getTerminationStatus());
   }

   @Test
   public void testGetResult_executionSucceededNull_shouldReturnExecutionStatusRunning() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededTrue_shouldReturnExecutionStatusFinished() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.FINISHED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededFalse_shouldReturnExecutionStatusFailed() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.FAILED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionStatusFinishedAndTerminationStatusUserError_shouldReturnExecutionStatusFailed() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .terminationMessage(ExecutionTerminationStatus.USER_ERROR.getString())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.FAILED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionStatusFinishedAndTerminationStatusSkipped_shouldReturnExecutionStatusSkipped() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .terminationMessage(ExecutionTerminationStatus.SKIPPED.getString())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.SKIPPED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionStatusFinishedAndTerminationStatusPlatformError_shouldReturnExecutionStatusFinished() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .terminationMessage(ExecutionTerminationStatus.PLATFORM_ERROR.getString())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.FINISHED, actualResult.getExecutionStatus());
   }
}
