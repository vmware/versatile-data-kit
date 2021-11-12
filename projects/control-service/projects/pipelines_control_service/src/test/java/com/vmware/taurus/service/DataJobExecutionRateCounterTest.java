/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.graphql.GraphQLUtils;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.time.OffsetDateTime;

@SpringBootTest(classes = ControlplaneApplication.class)
@ExtendWith(SpringExtension.class)
public class DataJobExecutionRateCounterTest {

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @Autowired
    private JobsRepository jobsRepository;

    private DataJob dataJob;

    @BeforeEach
    public void setup() {
        dataJob = RepositoryUtil.createDataJob(jobsRepository);
    }

    @AfterEach
    public void cleanup() {
        jobsRepository.deleteAll();
        jobExecutionRepository.deleteAll();
    }

    @Test
    public void testSuccessQuery_emptyExecutionsRepo_expectNoSuccess() {
        var response = GraphQLUtils.countSuccessfulExecutions("test-job", jobExecutionRepository);
        Assertions.assertEquals(0, response);
    }

    @Test
    public void testFailureQuery_emptyExecutionsRepo_expectNoFailure() {
        var response = GraphQLUtils.countFailedExecutions("test-job", jobExecutionRepository);
        Assertions.assertEquals(0, response);
    }

    @Test
    public void testSuccessQuery_oneFailed_expectNoSuccess() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        var response = GraphQLUtils.countSuccessfulExecutions("test-job", jobExecutionRepository);

        Assertions.assertEquals(0, response);
    }

    @Test
    public void testFailureQuery_oneSuccessful_expectNoFailure() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());

        var response = GraphQLUtils.countFailedExecutions("test-job", jobExecutionRepository);

        Assertions.assertEquals(0, response);
    }

    @Test
    public void testSuccessQuery_twoSuccessful_expectTwoSuccessful() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id2", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id3", dataJob,
                ExecutionStatus.SUBMITTED, "test-msg", OffsetDateTime.now());

        var response = GraphQLUtils.countSuccessfulExecutions("test-job", jobExecutionRepository);
        Assertions.assertEquals(2, response);
    }

    @Test
    public void testFailureQuery_twoFailed_expectTwoFailed() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id2", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id3", dataJob,
                ExecutionStatus.SUBMITTED, "test-msg", OffsetDateTime.now());

        var response = GraphQLUtils.countFailedExecutions("test-job", jobExecutionRepository);
        Assertions.assertEquals(2, response);
    }

}
