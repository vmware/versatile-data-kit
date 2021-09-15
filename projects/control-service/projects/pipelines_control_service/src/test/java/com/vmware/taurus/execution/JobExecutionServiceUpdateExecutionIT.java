/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.execution;

import java.time.OffsetDateTime;

import org.junit.Assert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.model.DataJob;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceUpdateExecutionIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionService jobExecutionService;

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
}
