/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.service.execution.JobExecutionService;
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
import java.util.List;

@SpringBootTest(classes = ServiceApp.class)
@ExtendWith(SpringExtension.class)
public class DataJobExecutionRateCounterTest {

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    JobExecutionService jobExecutionService;

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
        var response = jobExecutionService.countExecutionStatuses(List.of("test-job"), List.of(ExecutionStatus.FAILED, ExecutionStatus.FINISHED));
        Assertions.assertEquals(0, response.get("test-job").getOrDefault(ExecutionStatus.FAILED, 0));
        Assertions.assertEquals(0, response.get("test-job").getOrDefault(ExecutionStatus.FINISHED, 0));
    }

    @Test
    public void testSuccessQuery_oneFailed_expectNoSuccess() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        var response = jobExecutionService.countExecutionStatuses(List.of("test-job"), List.of(ExecutionStatus.FINISHED));
        Assertions.assertEquals(0, response.get("test-job").getOrDefault(ExecutionStatus.FINISHED, 0));
    }

    @Test
    public void testFailureQuery_oneSuccessful_expectNoFailure() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());

        var response = jobExecutionService.countExecutionStatuses(List.of("test-job"), List.of(ExecutionStatus.FAILED));
        Assertions.assertEquals(0, response.get("test-job").getOrDefault(ExecutionStatus.FAILED, 0));
    }

    @Test
    public void testSuccessQuery_twoSuccessful_expectTwoSuccessful() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id2", dataJob,
                ExecutionStatus.FINISHED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id3", dataJob,
                ExecutionStatus.SUBMITTED, "test-msg", OffsetDateTime.now());

        var response = jobExecutionService.countExecutionStatuses(List.of("test-job"), List.of(ExecutionStatus.FINISHED));
        Assertions.assertEquals(2, response.get("test-job").get(ExecutionStatus.FINISHED));
    }

    @Test
    public void testFailureQuery_twoFailed_expectTwoFailed() {
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id2", dataJob,
                ExecutionStatus.FAILED, "test-msg", OffsetDateTime.now());
        RepositoryUtil.createDataJobExecution(jobExecutionRepository, "test-id3", dataJob,
                ExecutionStatus.SUBMITTED, "test-msg", OffsetDateTime.now());

        var response = jobExecutionService.countExecutionStatuses(List.of("test-job"), List.of(ExecutionStatus.FAILED));
        Assertions.assertEquals(2, response.get("test-job").get(ExecutionStatus.FAILED));
    }
}
