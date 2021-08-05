/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.exception.DataJobExecutionStatusNotValidException;
import com.vmware.taurus.exception.DataJobNotFoundException;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.List;

import static com.vmware.taurus.execution.JobExecutionServiceUtil.assertDataJobExecutionListValid;
import static com.vmware.taurus.execution.JobExecutionServiceUtil.assertDataJobExecutionValid;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceListExecutionsIT {

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    private JobExecutionService jobExecutionService;

    @BeforeEach
    public void cleanDatabase() {
        jobsRepository.deleteAll();
    }

    @Test
    public void testListJobExecutions_nonExistingDataJob_shouldThrowException() {
        Assertions.assertThrows(DataJobNotFoundException.class, () ->
              jobExecutionService.listJobExecutions("test-team","test-job",  null));
    }

    @Test
    public void testReadJobExecution_nonExistingDataJobExecution_shouldReturnEmptyList() {
        DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

        List<DataJobExecution> dataJobExecutions = jobExecutionService.listJobExecutions(
              actualDataJob.getJobConfig().getTeam(),
              actualDataJob.getName(),
              null);
        Assertions.assertTrue(dataJobExecutions.isEmpty());
    }

    @Test
    public void testReadJobExecution_existingDataJobExecutionAndNullStatus_shouldReturnResult() {
        DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
        com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution = RepositoryUtil.createDataJobExecution(
              jobExecutionRepository,
              "test-id",
              actualDataJob,
              ExecutionStatus.RUNNING);

        List<DataJobExecution> actualDataJobExecutions = jobExecutionService.listJobExecutions(
              actualDataJob.getJobConfig().getTeam(),
              actualDataJob.getName(),
              null);

        assertDataJobExecutionListValid(expectedDataJobExecution, actualDataJobExecutions);
    }

    @Test
    public void testListJobExecutions_notValidExecutionStatus_shouldThrowException() {
        RepositoryUtil.createDataJob(jobsRepository);

        Assertions.assertThrows(DataJobExecutionStatusNotValidException.class, () ->
              jobExecutionService.listJobExecutions("test-team","test-job", List.of("not-valid-status")));
    }

    @Test
    public void testReadJobExecution_existingDataJobExecutionAndValidStatuses_shouldReturnResult() {
        DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);
        RepositoryUtil.createDataJobExecution(
              jobExecutionRepository,
              "test-id-1",
              actualDataJob,
              ExecutionStatus.CANCELLED);

        com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution1 = RepositoryUtil.createDataJobExecution(
              jobExecutionRepository,
              "test-id-2",
              actualDataJob,
              ExecutionStatus.RUNNING);

        com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution2 = RepositoryUtil.createDataJobExecution(
              jobExecutionRepository,
              "test-id-3",
              actualDataJob,
              ExecutionStatus.SUBMITTED);

        RepositoryUtil.createDataJobExecution(
              jobExecutionRepository,
              "test-id-4",
              actualDataJob,
              ExecutionStatus.FINISHED);

        List<DataJobExecution> actualDataJobExecutions =
              jobExecutionService.listJobExecutions(
                    actualDataJob.getJobConfig().getTeam(),
                    actualDataJob.getName(),
                    List.of(DataJobExecution.StatusEnum.RUNNING.getValue(), DataJobExecution.StatusEnum.SUBMITTED.getValue()));

        Assertions.assertNotNull(actualDataJobExecutions);
        Assertions.assertEquals(2, actualDataJobExecutions.size());

        assertDataJobExecutionValid(expectedDataJobExecution1,  actualDataJobExecutions.get(0));
        assertDataJobExecutionValid(expectedDataJobExecution2,  actualDataJobExecutions.get(1));
    }
}
