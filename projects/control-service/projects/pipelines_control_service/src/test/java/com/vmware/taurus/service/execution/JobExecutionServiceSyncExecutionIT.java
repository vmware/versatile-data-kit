/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;

import org.junit.Assert;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceSyncExecutionIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionRepository jobExecutionRepository;

   @Autowired
   private JobExecutionService jobExecutionService;

   @AfterEach
   public void cleanUp() {
      jobsRepository.deleteAll();
   }

   @Test
   public void testSyncJobExecutionStatuses_fourRunningExecutionsWithStartTimeBefore5min_shouldSyncTwoExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsBeforeSync.size());
      jobExecutionService.syncJobExecutionStatuses(List.of(expectedJobExecution1.getId(), expectedJobExecution3.getId()));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(2, dataJobExecutionsAfterSync.size());
      Assert.assertEquals(expectedJobExecution1.getId(), dataJobExecutionsAfterSync.get(0).getId());
      Assert.assertEquals(expectedJobExecution3.getId(), dataJobExecutionsAfterSync.get(1).getId());
   }

   @Test
   public void testSyncJobExecutionStatuses_twoRunningExecutionsWithStartTimeBefore2minAndTwoWithStartTimeBefore5min_shouldSyncOneExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(2));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(2));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsBeforeSync.size());
      jobExecutionService.syncJobExecutionStatuses(List.of(expectedJobExecution1.getId(), expectedJobExecution3.getId()));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(3, dataJobExecutionsAfterSync.size());
      Assert.assertEquals(expectedJobExecution1.getId(), dataJobExecutionsAfterSync.get(0).getId());
      Assert.assertEquals(expectedJobExecution2.getId(), dataJobExecutionsAfterSync.get(1).getId());
      Assert.assertEquals(expectedJobExecution3.getId(), dataJobExecutionsAfterSync.get(2).getId());
   }

   @Test
   public void testSyncJobExecutionStatuses_fourRunningExecutionsWithStartTimeBefore5min_shouldSyncFourExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsBeforeSync.size());
      jobExecutionService.syncJobExecutionStatuses(Collections.emptyList());

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(0, dataJobExecutionsAfterSync.size());
   }

   @Test
   public void testSyncJobExecutionStatuses_fourRunningExecutionsWithStartTimeBefore5min_shouldNotSyncAnyExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution4 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsBeforeSync.size());
      jobExecutionService.syncJobExecutionStatuses(List.of(
            expectedJobExecution1.getId(),
            expectedJobExecution2.getId(),
            expectedJobExecution3.getId(),
            expectedJobExecution4.getId()));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsAfterSync.size());
   }

   @Test
   public void testSyncJobExecutionStatuses_fourRunningExecutionsWithStartTimeBefore5minAndNullRunningExecutionsIds_shouldNotSyncAnyExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.SUBMITTED, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsBeforeSync.size());
      jobExecutionService.syncJobExecutionStatuses(null);

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(4, dataJobExecutionsAfterSync.size());
   }

   @Test
   public void testSyncJobExecutionStatuses_twoRunningExecutionsWithStartTimeBefore5minAndTwoFinishedExecutionsWithStartTimeBefore5min_shouldSyncOneExecutions() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.SUCCEEDED, OffsetDateTime.now().minusMinutes(5));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.SUCCEEDED, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));
      com.vmware.taurus.service.model.DataJobExecution expectedJobExecution4 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.RUNNING, OffsetDateTime.now().minusMinutes(5));

      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsBeforeSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(2, dataJobExecutionsBeforeSync.size());
      Assert.assertEquals(expectedJobExecution3.getId(), dataJobExecutionsBeforeSync.get(0).getId());
      Assert.assertEquals(expectedJobExecution4.getId(), dataJobExecutionsBeforeSync.get(1).getId());

      jobExecutionService.syncJobExecutionStatuses(List.of(expectedJobExecution1.getId(), expectedJobExecution3.getId()));
      List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutionsAfterSync = findRunningDataJobExecutions(actualDataJob.getName());

      Assert.assertEquals(1, dataJobExecutionsAfterSync.size());
      Assert.assertEquals(expectedJobExecution3.getId(), dataJobExecutionsAfterSync.get(0).getId());

      DataJobExecution actualFinishedExecution = jobExecutionRepository.findById(expectedJobExecution4.getId()).get();
      Assert.assertEquals("Status is set by VDK Control Service", actualFinishedExecution.getMessage());
      Assert.assertNotNull(actualFinishedExecution.getEndTime());
   }

   private List<com.vmware.taurus.service.model.DataJobExecution> findRunningDataJobExecutions(String dataJobName) {
      return jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(dataJobName, List.of(ExecutionStatus.SUBMITTED, ExecutionStatus.RUNNING));
   }
}
