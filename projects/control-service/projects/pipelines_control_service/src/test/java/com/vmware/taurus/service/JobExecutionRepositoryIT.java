/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.List;

/**
 * Integration tests of the setup of Spring Data repository for data job executions
 */
@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
class JobExecutionRepositoryIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionRepository jobExecutionRepository;

   @BeforeEach
   public void setUp() throws Exception {
      jobsRepository.deleteAll();
   }

   /**
    * Tests CRUD operations of job executions
    */
   @Test
   void testCRUD_shouldSucceed() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      String executionId = "test-execution-id";
      ExecutionStatus executionStatus = ExecutionStatus.RUNNING;
      DataJobExecution expectedJobExecution =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, executionId, actualDataJob, executionStatus);

      var actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getId()).get();
      Assertions.assertEquals(expectedJobExecution, actualJobExecution);

      jobsRepository.deleteAll();
      var deletedJobExecution = jobExecutionRepository.findById(expectedJobExecution.getId());
      Assertions.assertFalse(deletedJobExecution.isPresent());
   }

   @Test
   void testFindDataJobExecutionsByDataJobName_existingDataJobExecution_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      String executionId = "test-execution-id";
      ExecutionStatus executionStatus = ExecutionStatus.RUNNING;
      DataJobExecution expectedJobExecution =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, executionId, actualDataJob, executionStatus);

      var actualJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(actualDataJob.getName());

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(1, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution, actualJobExecutions.get(0));
   }

   @Test
   void testFindDataJobExecutionsByDataJobName_nonExistingDataJobExecution_shouldReturnEmptyResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      var actualJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(actualDataJob.getName());

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertTrue(actualJobExecutions.isEmpty());
   }

   @Test
   void testFindFirst5ByDataJobNameOrderByStartTimeDesc_existingDataJobExecutions_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-5", actualDataJob, ExecutionStatus.SUBMITTED);
      DataJobExecution expectedJobExecution6 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-6", actualDataJob, ExecutionStatus.FINISHED);


      var actualJobExecutions =
            jobExecutionRepository.findFirst5ByDataJobNameOrderByStartTimeDesc(actualDataJob.getName());

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(5, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution2, actualJobExecutions.get(4));
      Assertions.assertEquals(expectedJobExecution6, actualJobExecutions.get(0));
   }

   @Test
   void testFindDataJobExecutionsByDataJobNameAndStatusIn_nonExistingDataJobExecution_shouldReturnEmptyResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      var actualJobExecutions =
            jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(actualDataJob.getName(), List.of(ExecutionStatus.RUNNING));

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertTrue(actualJobExecutions.isEmpty());
   }
}
