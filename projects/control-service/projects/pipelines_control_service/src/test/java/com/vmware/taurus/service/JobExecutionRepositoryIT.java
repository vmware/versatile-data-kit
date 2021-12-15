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
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
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
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR);


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
   void testFindFirst5ByDataJobNameOrderByStartTimeDesc_existingDataJobExecutions_shouldReturnValidResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution3 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      DataJobExecution expectedJobExecution4 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR);


      Pageable pageable = PageRequest.of(0, 2, Sort.by(Sort.Order.desc("id")));
      var actualJobExecutions =
            jobExecutionRepository.findDataJobExecutionsByDataJobName(actualDataJob.getName(), pageable);

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution4, actualJobExecutions.get(0));
      Assertions.assertEquals(expectedJobExecution3, actualJobExecutions.get(1));

   }

   @Test
   void testFindDataJobExecutionsByDataJobNameAndStatusIn_nonExistingDataJobExecution_shouldReturnEmptyResult() {
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

   @Test
   void testFindFirstByDataJobNameOrderByStartTimeDesc_withNoExecutions_shouldReturnEmpty() {
      DataJob dataJob = RepositoryUtil.createDataJob(jobsRepository);

      var lastExecution = jobExecutionRepository.findFirstByDataJobNameOrderByStartTimeDesc(dataJob.getName());

      Assertions.assertTrue(lastExecution.isEmpty());
   }

   @Test
   void testFindFirstByDataJobNameOrderByStartTimeDesc_shouldReturnTheLastExecution() {
      DataJob dataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository,
              "execution1", dataJob, ExecutionStatus.SUCCEEDED, "Success",
              OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC),
              OffsetDateTime.of(2000, 1, 1, 1, 0, 0, 0, ZoneOffset.UTC));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository,
              "execution2", dataJob, ExecutionStatus.RUNNING, null,
              OffsetDateTime.of(2000, 1, 1, 4, 0, 0, 0, ZoneOffset.UTC),
              null);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository,
              "execution3", dataJob, ExecutionStatus.PLATFORM_ERROR, "Platform error",
              OffsetDateTime.of(2000, 1, 1, 1, 0, 0, 0, ZoneOffset.UTC),
              OffsetDateTime.of(2000, 1, 1, 3, 0, 0, 0, ZoneOffset.UTC));

      var lastExecution = jobExecutionRepository.findFirstByDataJobNameOrderByStartTimeDesc(dataJob.getName());

      Assertions.assertTrue(lastExecution.isPresent());
      Assertions.assertEquals("execution2", lastExecution.get().getId());
   }
}
