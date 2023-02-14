/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.exception.DataJobExecutionNotFoundException;
import com.vmware.taurus.exception.DataJobNotFoundException;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceReadExecutionIT {

  @Autowired private JobExecutionRepository jobExecutionRepository;

  @Autowired private JobsRepository jobsRepository;

  @Autowired private JobExecutionService jobExecutionService;

  @BeforeEach
  public void cleanDatabase() {
    jobsRepository.deleteAll();
  }

  @Test
  public void testReadJobExecution_existingDataJobExecution_shouldReturnExecution() {
    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
    com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution =
        RepositoryUtil.createDataJobExecution(
            jobExecutionRepository, "test-id", actualDataJob, ExecutionStatus.RUNNING);

    var actualDataJobExecution =
        jobExecutionService.readJobExecution(
            actualDataJob.getJobConfig().getTeam(),
            actualDataJob.getName(),
            expectedDataJobExecution.getId());

    JobExecutionServiceUtil.assertDataJobExecutionValid(
        expectedDataJobExecution, actualDataJobExecution);
  }

  @Test
  public void testReadJobExecution_nonExistingDataJob_shouldThrowException() {
    Assertions.assertThrows(
        DataJobNotFoundException.class,
        () -> jobExecutionService.readJobExecution("test-team", "test-job", "test-execution-id"));
  }

  @Test
  public void testReadJobExecution_nonExistingDataJobExecution_shouldThrowException() {
    DataJob dataJob = RepositoryUtil.createDataJob(jobsRepository);

    Assertions.assertThrows(
        DataJobExecutionNotFoundException.class,
        () ->
            jobExecutionService.readJobExecution(
                dataJob.getJobConfig().getTeam(), dataJob.getName(), "test-id"));
  }
}
