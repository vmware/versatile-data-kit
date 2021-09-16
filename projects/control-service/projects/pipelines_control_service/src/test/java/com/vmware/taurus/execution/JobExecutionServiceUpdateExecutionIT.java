/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.Assert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.time.OffsetDateTime;

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
      testUpdateJobExecution(
            KubernetesService.JobExecution.Status.FINISHED,
            KubernetesService.PodTerminationMessage.USER_ERROR,
            DataJobExecution.StatusEnum.FAILED);
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessagePlatformError_shouldRecordExecutionStatusFailed() {
      testUpdateJobExecution(
            KubernetesService.JobExecution.Status.FINISHED,
            KubernetesService.PodTerminationMessage.PLATFORM_ERROR,
            DataJobExecution.StatusEnum.FAILED);
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessageSkipped_shouldRecordExecutionStatusSkipped() {
      testUpdateJobExecution(
            KubernetesService.JobExecution.Status.FINISHED,
            KubernetesService.PodTerminationMessage.SKIPPED,
            DataJobExecution.StatusEnum.SKIPPED,
            "Skipping job execution due to another parallel running execution.");
   }

   @Test
   public void testUpdateJobExecution_statusFinishedAndTerminationMessageSuccess_shouldRecordExecutionStatusFinish() {
      testUpdateJobExecution(
            KubernetesService.JobExecution.Status.FINISHED,
            KubernetesService.PodTerminationMessage.SUCCESS,
            DataJobExecution.StatusEnum.FINISHED);
   }

   private void testUpdateJobExecution(
         KubernetesService.JobExecution.Status actualExecutionStatus,
         KubernetesService.PodTerminationMessage actualTerminationMessage,
         DataJobExecution.StatusEnum expectedJobExecutionStatus) {

      testUpdateJobExecution(actualExecutionStatus, actualTerminationMessage, expectedJobExecutionStatus, null);
   }

   private void testUpdateJobExecution(
         KubernetesService.JobExecution.Status actualExecutionStatus,
         KubernetesService.PodTerminationMessage actualTerminationMessage,
         DataJobExecution.StatusEnum expectedJobExecutionStatus,
         String expectedJobExecutionMessage) {

      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      KubernetesService.JobExecution expectedJobExecution = KubernetesService.JobExecution.builder()
            .status(actualExecutionStatus)
            .opId("test_op_id")
            .executionId("test_execution_id")
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
            .terminationMessage(actualTerminationMessage.getValue()).build();
      jobExecutionService.updateJobExecution(actualDataJob, expectedJobExecution);

      DataJobExecution actualJobExecution = jobExecutionService.readJobExecution(
            actualDataJob.getJobConfig().getTeam(),
            actualDataJob.getName(),
            expectedJobExecution.getExecutionId());

      expectedJobExecutionMessage = expectedJobExecutionMessage != null ? expectedJobExecutionMessage : expectedJobExecution.getTerminationMessage();
      assertDataJobExecutionValid(expectedJobExecution, expectedJobExecutionStatus, expectedJobExecutionMessage, actualJobExecution);
   }

   private void assertDataJobExecutionValid(
         KubernetesService.JobExecution expectedJobExecution,
         DataJobExecution.StatusEnum expectedJobStatus,
         String expectedMessage,
         DataJobExecution actualJobExecution) {

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
   }

   @Test
   public void testUpdateJobExecution_DbStatusSubmittedAndUpdateStatusRunning_UpdateExpected() {
      //control test which makes sure the status gets updated if in submitted
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.SUBMITTED, KubernetesService.JobExecution.Status.RUNNING, ExecutionStatus.RUNNING);
   }

   @Test
   public void testUpdateJobExecution_DbStatusRunningAndUpdateStatusFinished_UpdateExpected() {
      //control test which makes sure the status gets updated if in running
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.RUNNING, KubernetesService.JobExecution.Status.FINISHED, ExecutionStatus.FINISHED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusFinishedAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in finished
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.FINISHED, KubernetesService.JobExecution.Status.RUNNING, ExecutionStatus.FINISHED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusCancelledAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in cancelled
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.CANCELLED, KubernetesService.JobExecution.Status.RUNNING, ExecutionStatus.CANCELLED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusSkippedAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in skipped
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.SKIPPED, KubernetesService.JobExecution.Status.RUNNING, ExecutionStatus.SKIPPED);
   }

   @Test
   public void testUpdateJobExecution_DbStatusFailedAndUpdateStatusRunning_NoUpdateExpected() {
      //test which makes sure the status doesn't get updated if in failed
      testUpdateJobExecutionWithPreviousStatusInDatabase(ExecutionStatus.FAILED, KubernetesService.JobExecution.Status.RUNNING, ExecutionStatus.FAILED);
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
                                                                   KubernetesService.JobExecution.Status attemptedStatusChange,
                                                                   ExecutionStatus expectedStatus) {
      var actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      var execution = RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", actualDataJob, statusPresentInDb);

      KubernetesService.JobExecution attemptedExecutionUpdate = KubernetesService.JobExecution.builder()
              .status(attemptedStatusChange)
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
              .terminationMessage("TestMessage").build();

      jobExecutionService.updateJobExecution(actualDataJob, attemptedExecutionUpdate);
      var actualJobExecution = jobExecutionRepository.findById(attemptedExecutionUpdate.getExecutionId()).get();

      Assertions.assertEquals(expectedStatus, actualJobExecution.getStatus());
   }

}
