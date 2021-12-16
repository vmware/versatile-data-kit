/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.graphql.model.DataJobExecutionFilter;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.OffsetDateTime;
import java.util.List;

@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionFilterSpecIT {

   @Autowired
   private JobsRepository jobsRepository;

   @Autowired
   private JobExecutionRepository jobExecutionRepository;

   @BeforeEach
   public void setUp() throws Exception {
      jobsRepository.deleteAll();
   }

   @Test
   public void testJobExecutionFilterSpec_filerByStatusIn_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED);
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING);
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED);
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR);

      DataJobExecutionFilter filter = DataJobExecutionFilter.builder()
            .statusIn(List.of(ExecutionStatus.RUNNING, ExecutionStatus.SUBMITTED))
            .build();
      JobExecutionFilterSpec jobExecutionFilterSpec = new JobExecutionFilterSpec(filter);
      var actualJobExecutions = jobExecutionRepository.findAll(jobExecutionFilterSpec);

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution1, actualJobExecutions.get(0));
      Assertions.assertEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testJobExecutionFilterSpec_filerByStartTimeGte_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1));
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR, now.minusMinutes(2));

      DataJobExecutionFilter filter = DataJobExecutionFilter.builder()
            .startTimeGte(now.minusMinutes(1))
            .build();
      JobExecutionFilterSpec jobExecutionFilterSpec = new JobExecutionFilterSpec(filter);
      var actualJobExecutions = jobExecutionRepository.findAll(jobExecutionFilterSpec);

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution1, actualJobExecutions.get(0));
      Assertions.assertEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testJobExecutionFilterSpec_filerByEndTimeGte_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2), now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1), now.minusMinutes(1));
      DataJobExecution expectedJobExecution2 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR, now.minusMinutes(2), now.minusMinutes(2));

      DataJobExecutionFilter filter = DataJobExecutionFilter.builder()
            .endTimeGte(now.minusMinutes(1))
            .build();
      JobExecutionFilterSpec jobExecutionFilterSpec = new JobExecutionFilterSpec(filter);
      var actualJobExecutions = jobExecutionRepository.findAll(jobExecutionFilterSpec);

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(2, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution1, actualJobExecutions.get(0));
      Assertions.assertEquals(expectedJobExecution2, actualJobExecutions.get(1));
   }

   @Test
   public void testJobExecutionFilterSpec_filerByAllFields_shouldReturnResult() {
      DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
      OffsetDateTime now = OffsetDateTime.now();

      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-1", actualDataJob, ExecutionStatus.CANCELLED, now.minusMinutes(2), now.minusMinutes(2));
      DataJobExecution expectedJobExecution1 =
            RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-2", actualDataJob, ExecutionStatus.RUNNING, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-3", actualDataJob, ExecutionStatus.SUBMITTED, now.minusMinutes(1), now.minusMinutes(1));
      RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-execution-id-4", actualDataJob, ExecutionStatus.PLATFORM_ERROR, now.minusMinutes(2), now.minusMinutes(2));

      DataJobExecutionFilter filter = DataJobExecutionFilter.builder()
            .startTimeGte(now.minusMinutes(1))
            .endTimeGte(now.minusMinutes(1))
            .statusIn(List.of(ExecutionStatus.RUNNING))
            .build();
      JobExecutionFilterSpec jobExecutionFilterSpec = new JobExecutionFilterSpec(filter);
      var actualJobExecutions = jobExecutionRepository.findAll(jobExecutionFilterSpec);

      Assertions.assertNotNull(actualJobExecutions);
      Assertions.assertEquals(1, actualJobExecutions.size());
      Assertions.assertEquals(expectedJobExecution1, actualJobExecutions.get(0));
   }
}
