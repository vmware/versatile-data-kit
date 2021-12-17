/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.exception.DataJobExecutionCannotBeCancelledException;
import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;
import io.kubernetes.client.ApiException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.HttpStatus;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceCancelExecutionIT {

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @Autowired
    private JobExecutionService jobExecutionService;

    @MockBean
    private DataJobsKubernetesService dataJobsKubernetesService;

    private DataJob testJob;

    @BeforeEach
    public void populateDb() {
        JobConfig config = new JobConfig();
        config.setSchedule("schedule");
        config.setTeam("test-team");
        testJob = new DataJob("testJob", config);

        jobsRepository.save(testJob);
    }

    @AfterEach
    public void cleanDbAfterTests() {
        jobExecutionRepository.deleteAll();
        jobsRepository.deleteAll();
    }

    @Test
    public void testCancelRunningExecution() throws ApiException {

        String jobExecutionId = "test-job-id";
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, jobExecutionId, testJob, ExecutionStatus.RUNNING);
        Mockito.doNothing().when(dataJobsKubernetesService).cancelRunningCronJob(Mockito.anyString(), Mockito.anyString(), Mockito.anyString());

        jobExecutionService.cancelDataJobExecution("test-team", "testJob", jobExecutionId);
        var execution = jobExecutionRepository.findById(jobExecutionId).get();

        Assertions.assertEquals(ExecutionStatus.CANCELLED, execution.getStatus());
        Assertions.assertTrue(jobExecutionRepository.findAll().size() == 1, "Expecting the size of executions to remain 1.");
    }

    @Test
    public void testCancelFinishedExecution() {
        String jobExecutionId = "test-job-id";
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, jobExecutionId, testJob, ExecutionStatus.SUCCEEDED);

        var actualException = Assertions.assertThrows(DataJobExecutionCannotBeCancelledException.class,
                () -> jobExecutionService.cancelDataJobExecution("test-team", "testJob", jobExecutionId));

        var exceptionMessage = actualException.getMessage();
        Assertions.assertTrue(exceptionMessage.contains("Specified data job execution is not in running or submitted state."),
                "Unexpected exception message content.");
        Assertions.assertEquals(HttpStatus.BAD_REQUEST, actualException.getHttpStatus());
    }

    @Test
    public void testCancelNonExistingDataJob() {

        var actualException = Assertions.assertThrows(DataJobExecutionCannotBeCancelledException.class,
                () -> jobExecutionService.cancelDataJobExecution("test-team", "nonExistentDataJob", null));

        var exceptionMessage = actualException.getMessage();
        Assertions.assertTrue(exceptionMessage.contains("Specified Data Job for Team does not exist."),
                "Unexpected exception message content.");
        Assertions.assertEquals(HttpStatus.NOT_FOUND, actualException.getHttpStatus());
    }

    @Test
    public void testCancelNonExistingDataJobExecution() {
        var actualException = Assertions.assertThrows(DataJobExecutionCannotBeCancelledException.class,
                () -> jobExecutionService.cancelDataJobExecution("test-team", "testJob", "nonExistingExecId"));

        var exceptionMessage = actualException.getMessage();
        Assertions.assertTrue(exceptionMessage.contains("Specified data job execution does not exist."),
                "Unexpected exception message content.");
        Assertions.assertEquals(HttpStatus.NOT_FOUND, actualException.getHttpStatus());
    }

    @Test
    public void testCancelExecutionK8SException() throws ApiException {
        String jobExecutionId = "test-job-id";
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, jobExecutionId, testJob, ExecutionStatus.SUBMITTED);

        Mockito.doThrow(new ApiException()).when(dataJobsKubernetesService).cancelRunningCronJob(Mockito.anyString(), Mockito.anyString(), Mockito.anyString());
        var actualException = Assertions.assertThrows(KubernetesException.class,
                () -> jobExecutionService.cancelDataJobExecution("test-team", "testJob", jobExecutionId));

        var exceptionMessage = actualException.getMessage();
        Assertions.assertTrue(exceptionMessage.contains("Cannot cancel a Data Job 'testJob' execution with execution id 'test-job-id'"),
                "Unexpected exception message content.");
    }

    @Test
    public void testExceptionObjectNullTolerant() {
        var exception = new DataJobExecutionCannotBeCancelledException(null, null);
        var message = exception.getMessage();
        var status = exception.getHttpStatus();

        Assertions.assertNotNull(message);
        Assertions.assertNotNull(status);
        Assertions.assertTrue(exception.getMessage().contains("Unknown cause"));
        Assertions.assertEquals(HttpStatus.BAD_REQUEST, status);

    }

}
