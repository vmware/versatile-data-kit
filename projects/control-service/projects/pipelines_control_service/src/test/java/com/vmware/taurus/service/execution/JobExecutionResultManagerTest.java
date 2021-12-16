/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.OffsetDateTime;

import com.google.gson.JsonObject;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionResult;

import java.time.OffsetDateTime;

public class JobExecutionResultManagerTest {

   @Test
   public void testGetResult_succeededTrueAndNullTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage(null).build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_succeededFalseAndNullTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage(null).build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }


   @Test
   public void testGetResult_succeededNullAndNullTerminationMessage_shouldReturnTerminationStatusNone() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(null)
                  .startTime(OffsetDateTime.now())
                  .podTerminationMessage(null)
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededTrueAndEmptyTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage("").build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_succeededFalseAndEmptyTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage("").build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_succeededNullAndEmptyTerminationMessage_shouldReturnTerminationStatusNone() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(null)
                  .startTime(OffsetDateTime.now())
                  .podTerminationMessage("")
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededTrueAndNotExistingTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage("not-existing-termination-message").build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_succeededFalseAndNotExistingTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage("not-existing-termination-message").build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualTerminationMessage.getExecutionStatus()); // TODO OR platform error
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_succeededNullAndNotExistingTerminationMessage_shouldReturnMessage() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(null)
                  .startTime(OffsetDateTime.now())
                  .podTerminationMessage("not-existing-termination-message")
                  .build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.RUNNING, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals("", actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_jsonTerminationMessage_shouldReturnMessage() {
      ExecutionStatus expectedTerminationStatus = ExecutionStatus.USER_ERROR;
      String vdkVersion = "1.2.3";
      JsonObject expectedTerminationMessage = new JsonObject();
      expectedTerminationMessage.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_STATUS, expectedTerminationStatus.getPodStatus());
      expectedTerminationMessage.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, vdkVersion);

      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution
                  .builder()
                  .succeeded(false)
                  .podTerminationMessage(expectedTerminationMessage.toString())
                  .build();
      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getExecutionStatus());
      Assertions.assertEquals(vdkVersion, actualTerminationMessage.getVdkVersion());
   }

   @Test
   public void testGetResult_stringTerminationMessage_shouldReturnMessage() {
      ExecutionStatus expectedTerminationStatus = ExecutionStatus.USER_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution
                  .builder()
                  .succeeded(false)
                  .podTerminationMessage(expectedTerminationStatus.getPodStatus())
                  .build();

      ExecutionResult actualTerminationMessage = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedTerminationStatus, actualTerminationMessage.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededTrueAndTerminationMessageUserError_shouldReturnTerminationStatusSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.USER_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage(expectedExecutionStatus.getPodStatus()).build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedExecutionStatus, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededFalseAndTerminationMessageUserError_shouldReturnTerminationStatusSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.USER_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage(expectedExecutionStatus.getPodStatus()).build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedExecutionStatus, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededNullAndTerminationMessageUserError_shouldReturnTerminationStatusSuccess() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(null)
                  .startTime(OffsetDateTime.now())
                  .podTerminationMessage(ExecutionStatus.USER_ERROR.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededTrueAndTerminationMessagePlatformError_shouldReturnTerminationStatusSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.PLATFORM_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage(expectedExecutionStatus.getPodStatus()).build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedExecutionStatus, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededFalseAndTerminationMessagePlatformError_shouldReturnTerminationStatusSuccess() {
      ExecutionStatus expectedExecutionStatus = ExecutionStatus.PLATFORM_ERROR;
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage(expectedExecutionStatus.getPodStatus()).build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(expectedExecutionStatus, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededNullAndTerminationMessagePlatformError_shouldReturnTerminationStatusSuccess() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(null)
                  .startTime(OffsetDateTime.now())
                  .podTerminationMessage(ExecutionStatus.PLATFORM_ERROR.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_emptyTerminationMessageAndExecutionStatusSucceeded_shouldReturnTerminationStatusSuccess() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).podTerminationMessage("").build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_emptyTerminationMessageAndExecutionStatusFailed_shouldReturnTerminationStatusPlatformError() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).podTerminationMessage("").build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededNullAndStartTimeNull_shouldReturnExecutionStatusSubmitted() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(null).startTime(null).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.SUBMITTED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededNullAndStartTimeNotNull_shouldReturnExecutionStatusRunning() {
      KubernetesService.JobExecution jobExecution =
              KubernetesService.JobExecution.builder().succeeded(null).startTime(OffsetDateTime.now()).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.RUNNING, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededTrue_shouldReturnExecutionStatusSucceeded() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(true).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionSucceededFalse_shouldReturnExecutionStatusFailed() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder().succeeded(false).build();
      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);

      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionStatusSucceededAndTerminationStatusUserError_shouldReturnExecutionStatusFailed() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .podTerminationMessage(ExecutionStatus.USER_ERROR.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.USER_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_executionStatusSucceededAndTerminationStatusSkipped_shouldReturnExecutionStatusSkipped() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .podTerminationMessage(ExecutionStatus.SKIPPED.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.SKIPPED, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededTrueAndTerminationStatusPlatformError_shouldReturnExecutionStatusPlatformError() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(true)
                  .podTerminationMessage(ExecutionStatus.PLATFORM_ERROR.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   public void testGetResult_succeededFalseAndTerminationStatusPlatformError_shouldReturnExecutionStatusPlatformError() {
      KubernetesService.JobExecution jobExecution =
            KubernetesService.JobExecution.builder()
                  .succeeded(false)
                  .podTerminationMessage(ExecutionStatus.PLATFORM_ERROR.getPodStatus())
                  .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   void testGetResult_terminationMessageNullAndExecutionStatusFailedAndTerminationReasonDeadlineExceeded_shouldReturnTerminationStatusUserError() {
      KubernetesService.JobExecution jobExecution =
              KubernetesService.JobExecution.builder()
                      .podTerminationMessage(null)
                      .succeeded(false)
                      .jobTerminationReason(JobExecutionResultManager.TERMINATION_REASON_DEADLINE_EXCEEDED)
                      .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.USER_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   void testGetResult_terminationMessageNullAndExecutionStatusFailedAndTerminationReasonAny_shouldReturnTerminationStatusUserError() {
      KubernetesService.JobExecution jobExecution =
              KubernetesService.JobExecution.builder()
                      .podTerminationMessage(null)
                      .succeeded(false)
                      .jobTerminationReason("SomeReason")
                      .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualResult.getExecutionStatus());
   }

   @Test
   void testGetResult_terminationMessageNullAndExecutionStatusFailedAndTerminationReasonOutOfMemory_shouldReturnTerminationStatusUserError() {
      KubernetesService.JobExecution jobExecution =
              KubernetesService.JobExecution.builder()
                      .podTerminationMessage(null)
                      .succeeded(false)
                      .jobTerminationReason("Some Reason")
                      .containerTerminationReason(JobExecutionResultManager.TERMINATION_REASON_OUT_OF_MEMORY)
                      .build();

      ExecutionResult actualResult = JobExecutionResultManager.getResult(jobExecution);
      Assertions.assertEquals(ExecutionStatus.USER_ERROR, actualResult.getExecutionStatus());
   }
}
