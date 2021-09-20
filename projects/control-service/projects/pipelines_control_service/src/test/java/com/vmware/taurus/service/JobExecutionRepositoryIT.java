/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

/**
 * Integration tests of the setup of Spring Data repository for data job executions
 */
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionRepositoryIT {

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
   public void testCRUD_shouldSucceed() {
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
   public void testFindDataJobExecutionsByDataJobName_existingDataJobExecution_shouldReturnResult() {
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
   public void testFindDataJobExecutionsByDataJobName_nonExistingDataJobExecution_shouldReturnEmptyResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      var actualJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(actualDataJob.getName());

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertTrue(actualJobExecutions.isEmpty());
   }

   @Test
   public void testFindDataJobExecutionsByDataJobNameAndStatusIn_existingDataJobExecutions_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.FAILED);


      var actualJobExecutions =
            jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(
                  actualDataJob.getName(),
                  List.of(ExecutionStatus.RUNNING, ExecutionStatus.SUBMITTED));

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution1, actualJobExecutions.get(0));
      Assertions.assertEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testFindDataJobExecutionsByDataJobNameAndStatusIn_nonExistingDataJobExecution_shouldReturnEmptyResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      var actualJobExecutions =
            jobExecutionRepository.findDataJobExecutionsByDataJobNameAndStatusIn(actualDataJob.getName(), List.of(ExecutionStatus.RUNNING));

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertTrue(actualJobExecutions.isEmpty());
   }

   @Test
   public void testFindDataJobExecutionsByDataJobName_existingDataJobExecution_shouldReturnResult2() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      String executionId = "test-execution-id";
      ExecutionStatus executionStatus = ExecutionStatus.RUNNING;
      DataJobExecution expectedJobExecution =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, executionId, actualDataJob, executionStatus);

   }
}
