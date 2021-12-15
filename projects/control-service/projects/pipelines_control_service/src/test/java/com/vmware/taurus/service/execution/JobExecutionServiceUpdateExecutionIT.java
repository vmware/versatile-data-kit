/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.Duration;
import java.time.OffsetDateTime;
import java.util.Random;

import com.google.gson.JsonObject;
import org.junit.Assert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionResult;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceUpdateExecutionIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionService jobExecutionService;

   @Autowired
   private JobExecutionRepository jobExecutionRepository;

   @AfterEach
   public void cleanUp() {
      jobsRepository.deleteAll();
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessageUserError_shouldRecordExecutionStatusFailed() {
      String actualTerminationStatus = ExecutionStatus.USER_ERROR.getPodStatus();
      String actualVdkVersion = "1.2.3";
      String actualTerminationMessage = getTerminationMessageJson(actualTerminationStatus, actualVdkVersion);
      Boolean actualExecutionSucceeded = true;
      DataJobExecution.StatusEnum expectedJobExecutionStatus = DataJobExecution.StatusEnum.USER_ERROR;

      // Termination message as Json
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationMessage,
            expectedJobExecutionStatus,
            actualTerminationStatus,
            actualVdkVersion);

      // Termination message as String
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationStatus,
            expectedJobExecutionStatus,
            null,
            "");
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessagePlatformError_shouldRecordExecutionStatusFailed() {
      String actualTerminationStatus = ExecutionStatus.PLATFORM_ERROR.getPodStatus();
      String actualVdkVersion = "1.2.3";
      String actualTerminationMessage = getTerminationMessageJson(actualTerminationStatus, actualVdkVersion);
      Boolean actualExecutionSucceeded = true;
      DataJobExecution.StatusEnum expectedJobExecutionStatus = DataJobExecution.StatusEnum.PLATFORM_ERROR;

      // Termination message as Json
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationMessage,
            expectedJobExecutionStatus,
            actualTerminationStatus,
            actualVdkVersion);

      // Termination message as String
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationStatus,
            expectedJobExecutionStatus,
            null,
            "");
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessageSkipped_shouldRecordExecutionStatusSkipped() {
      String actualTerminationStatus = ExecutionStatus.SKIPPED.getPodStatus();
      String actualVdkVersion = "1.2.3";
      String actualTerminationMessage = getTerminationMessageJson(actualTerminationStatus, actualVdkVersion);
      Boolean actualExecutionSucceeded = true;
      DataJobExecution.StatusEnum expectedJobExecutionStatus = DataJobExecution.StatusEnum.SKIPPED;

      // Termination message as Json
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationMessage,
            expectedJobExecutionStatus,
            "Skipping job execution due to another parallel running execution.",
            actualVdkVersion);

      // Termination message as String
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationStatus,
            expectedJobExecutionStatus,
            "Skipping job execution due to another parallel running execution.",
            "");
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessageSuccess_shouldRecordExecutionStatusFinish() {
      String actualTerminationStatus = ExecutionStatus.SUCCEEDED.getPodStatus();
      String actualVdkVersion = "1.2.3";
      String actualTerminationMessage = getTerminationMessageJson(actualTerminationStatus, actualVdkVersion);
      Boolean actualExecutionSucceeded = true;
      DataJobExecution.StatusEnum expectedJobExecutionStatus = DataJobExecution.StatusEnum.SUCCEEDED;

      // Termination message as Json
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationMessage,
            expectedJobExecutionStatus,
            actualTerminationStatus,
            actualVdkVersion);

      // Termination message as String
      testUpdateJobExecution(
            actualExecutionSucceeded,
            actualTerminationStatus,
            expectedJobExecutionStatus,
            null,
            "");
   }

   @Test
   void testUpdateJobExecution_withoutStartTime_shouldRecordExecutionStartTimeNow() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      KubernetesService.JobExecution expectedJobExecution = createJobExecution(
            actualDataJob,
            null,
            null,
            null,
            null);
      DataJobExecution actualJobExecution = jobExecutionService.readJobExecution(
            actualDataJob.getJobConfig().getTeam(),
            actualDataJob.getName(),
            expectedJobExecution.getExecutionId());

      Assert.assertNotNull(actualJobExecution.getStartTime());
      // Start time should be close to the current time (within 10 seconds) because it is set to the current time when null
      Assert.assertTrue(Duration.between(OffsetDateTime.now(), actualJobExecution.getStartTime()).toMillis() < 10000);
      Assert.assertEquals(DataJobExecution.StatusEnum.SUBMITTED, actualJobExecution.getStatus());
   }

   private KubernetesService.JobExecution createJobExecution(
         DataJob dataJob,
         Boolean succeeded,
         String terminationMessage,
         OffsetDateTime startTime,
         OffsetDateTime endTime) {

      KubernetesService.JobExecution jobExecution = KubernetesService.JobExecution.builder()
            .succeeded(succeeded)
            .opId("test_op_id")
            .executionId("test_execution_id_" + new Random().nextInt())
            .executionType("manual")
            .jobName(dataJob.getName())
            .jobVersion("test_job_version")
            .jobSchedule("test_job_schedule")
            .startTime(startTime)
            .endTime(endTime)
            .resourcesCpuLimit(1f)
            .resourcesCpuRequest(1f)
            .resourcesMemoryLimit(1)
            .resourcesMemoryRequest(1)
            .deployedBy("test_deployed_by")
            .deployedDate(OffsetDateTime.now())
            .podTerminationMessage(terminationMessage)
            .build();
      ExecutionResult executionResult = JobExecutionResultManager.getResult(jobExecution);
      jobExecutionService.updateJobExecution(dataJob, jobExecution, executionResult);

      return jobExecution;
   }

   private void testUpdateJobExecution(
         Boolean actualExecutionSucceeded,
         String actualTerminationMessage,
         DataJobExecution.StatusEnum expectedJobExecutionStatus,
         String expectedJobExecutionMessage,
         String expectedVdkVersion) {

      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      KubernetesService.JobExecution expectedJobExecution = createJobExecution(
            actualDataJob,
            actualExecutionSucceeded,
            actualTerminationMessage,
            OffsetDateTime.now(),
            OffsetDateTime.now());
      DataJobExecution actualJobExecution = jobExecutionService.readJobExecution(
            actualDataJob.getJobConfig().getTeam(),
            actualDataJob.getName(),
            expectedJobExecution.getExecutionId());

      assertDataJobExecutionValid(
            expectedJobExecution,
            expectedJobExecutionStatus,
            expectedJobExecutionMessage != null ?
                  expectedJobExecutionMessage :
                  expectedJobExecution.getPodTerminationMessage(),
            actualJobExecution,
            expectedVdkVersion);
   }

   private void assertDataJobExecutionValid(
         KubernetesService.JobExecution expectedJobExecution,
         DataJobExecution.StatusEnum expectedJobStatus,
         String expectedMessage,
         DataJobExecution actualJobExecution,
         String expectedVdkVersion) {

      Assert.assertEquals(expectedJobExecution.getExecutionId(), actualJobExecution.getId());
      Assert.assertEquals(expectedJobExecution.getExecutionType(), actualJobExecution.getType().toString());
      Assert.assertEquals(expectedJobExecution.getJobName(), actualJobExecution.getJobName());
      Assert.assertEquals(expectedJobExecution.getJobVersion(), actualJobExecution.getDeployment().getJobVersion());
      Assert.assertEquals(expectedMessage, actualJobExecution.getMessage());
      Assert.assertEquals(expectedJobStatus, actualJobExecution.getStatus());
      Assert.assertEquals(expectedJobExecution.getOpId(), actualJobExecution.getOpId());
      Assert.assertEquals(expectedJobExecution.getStartTime(), actualJobExecution.getStartTime());
      Assert.assertEquals(expectedJobExecution.getEndTime(), actualJobExecution.getEndTime());
      Assert.assertEquals(expectedJobExecution.getJobSchedule(), actualJobExecution.getDeployment().getSchedule().getScheduleCron());
      Assert.assertEquals(expectedJobExecution.getResourcesCpuLimit(), actualJobExecution.getDeployment().getResources().getCpuLimit());
      Assert.assertEquals(expectedJobExecution.getResourcesCpuRequest(), actualJobExecution.getDeployment().getResources().getCpuRequest());
      Assert.assertEquals(expectedJobExecution.getResourcesMemoryLimit(), actualJobExecution.getDeployment().getResources().getMemoryLimit());
      Assert.assertEquals(expectedJobExecution.getResourcesMemoryRequest(), actualJobExecution.getDeployment().getResources().getMemoryRequest());
      Assert.assertEquals(expectedJobExecution.getDeployedDate(), actualJobExecution.getDeployment().getDeployedDate());
      Assert.assertEquals(expectedJobExecution.getDeployedBy(), actualJobExecution.getDeployment().getDeployedBy());
      Assert.assertEquals(expectedVdkVersion, actualJobExecution.getDeployment().getVdkVersion());
   }

   @Test
   public void testUpdateJobExecution_DbStatusSubmittedAndUpdateStatusRunning_UpdateExpected() {
      //control test which makes sure the status gets updated if in submitted
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.SUBMITTED, null, ExecutionStatus.RUNNING);
   }

   @Test
   public void testUpdateJobExecution_DbStatusRunningAndUpdateStatusFinished_UpdateExpected() {
      //control test which makes sure the status gets updated if in running
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.RUNNING, true, ExecutionStatus.SUCCEEDED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusSucceededAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in finished
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.SUCCEEDED, null, ExecutionStatus.SUCCEEDED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusCancelledAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in cancelled
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.CANCELLED, null, ExecutionStatus.CANCELLED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusSkippedAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in skipped
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.SKIPPED, null, ExecutionStatus.SKIPPED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusPlatformErrorAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in failed
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.PLATFORM_ERROR, null, ExecutionStatus.PLATFORM_ERROR);
   }

   /**
    * Helper method which tests if a data job execution status changes through the updateJobExecutionMethod when
    * a data job already has an execution status written to the database. Writes a status to a data job
    * execution and then attempts to update it with the provided status. Checks if status matches the expectedStatus
    * param.
    *
    * @param statusPresentInDb the "previous" execution status
    * @param attemptedStatusChange the attempted change execution status
    * @param expectedStatus the expected execution status
    */
   private void testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus statusPresentInDb,
                                                                   Boolean attemptedStatusChange,
                                                                   ExecutionStatus expectedStatus) {
      var actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      var execution = RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", actualDataJob, statusPresentInDb);

      KubernetesService.JobExecution attemptedExecutionUpdate = KubernetesService.JobExecution.builder()
              .succeeded(attemptedStatusChange)
              .opId(execution.getOpId())
              .executionId(execution.getId())
              .executionType("manual")
              .jobName(actualDataJob.getName())
              .jobVersion("test_job_version")
              .jobSchedule("test_job_schedule")
              .startTime(OffsetDateTime.now())
              .endTime(OffsetDateTime.now())
              .resourcesCpuLimit(1f)
              .resourcesCpuRequest(1f)
              .resourcesMemoryLimit(1)
              .resourcesMemoryRequest(1)
              .deployedBy("test_deployed_by")
              .deployedDate(OffsetDateTime.now())
              .podTerminationMessage(expectedStatus.getPodStatus()).build();
      ExecutionResult executionResult = JobExecutionResultManager.getResult(attemptedExecutionUpdate);
      jobExecutionService.updateJobExecution(actualDataJob, attemptedExecutionUpdate, executionResult);
      var actualJobExecution = jobExecutionRepository.findById(attemptedExecutionUpdate.getExecutionId()).get();

      Assertions.assertEquals(expectedStatus, actualJobExecution.getStatus());
   }

   private static String getTerminationMessageJson(String actualTerminationStatus, String vdkVersion) {
      JsonObject actualTerminationMessageJson = new JsonObject();
      actualTerminationMessageJson.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_STATUS, actualTerminationStatus);
      actualTerminationMessageJson.addProperty(JobExecutionResultManager.TERMINATION_MESSAGE_ATTRIBUTE_VDK_VERSION, vdkVersion);

      return actualTerminationMessageJson.toString();
   }
}
