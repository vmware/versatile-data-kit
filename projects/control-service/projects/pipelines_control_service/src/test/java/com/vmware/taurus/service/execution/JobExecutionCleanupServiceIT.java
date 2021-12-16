/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.time.OffsetDateTime;
import java.util.List;
import java.util.Random;
import java.util.UUID;

@SpringBootTest(classes = ControlplaneApplication.class)
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
@ExtendWith(SpringExtension.class)
public class JobExecutionCleanupServiceIT {

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    private JobExecutionCleanupService jobExecutionCleanupService;

    @BeforeAll
    public void populateJobsRepository() {
        JobConfig config = new JobConfig();
        config.setSchedule("schedule");

        var jobA = new DataJob("jobA", config);
        var jobB = new DataJob("jobB", config);

        jobsRepository.save(jobA);
        jobsRepository.save(jobB);
    }

    @BeforeEach
    public void cleanJobExecutions() {
        jobExecutionRepository.deleteAll();
    }

    @Test
    public void testOneJobExecutionDeleteNotExpected() {
        addJobExecution("jobA", OffsetDateTime.now(), ExecutionStatus.SUCCEEDED);
        Assertions.assertEquals(1, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(1, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testOneJobExecutionDeleteExpected() {
        addJobExecution("jobA", OffsetDateTime.now().minusDays(14), ExecutionStatus.SUCCEEDED);
        Assertions.assertEquals(1, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(0, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testManyJobExecutionsDeleteExpected() {
        for (int i = 0; i < 101; i++) {
            addJobExecution("jobA", OffsetDateTime.now(), ExecutionStatus.SUCCEEDED);
        }
        Assertions.assertEquals(101, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(100, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testManyJobExecutionsDeleteNotExpected() {
        addExecutions(100, "jobA");
        Assertions.assertEquals(100, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(100, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testJobExecutionOrdering() {
        Random random = new Random();

        for (int i = 0; i < 20; i++) {
            addJobExecution("jobA", OffsetDateTime.now().minusDays(random.nextInt(60)), ExecutionStatus.SUCCEEDED);
        }
        var statuses = List.of(ExecutionStatus.RUNNING, ExecutionStatus.SUBMITTED);
        var jobs = jobExecutionRepository.findByDataJobNameAndStatusNotInOrderByEndTime("jobA", statuses);

        var previous = jobExecutionRepository.findById(jobs.get(0).getId()).get();
        for (int i = 1; i < jobs.size(); i++) {
            var current = jobExecutionRepository.findById(jobs.get(i).getId()).get();
            Assertions.assertTrue(previous.getEndTime().isBefore(current.getEndTime()));
            previous = current;
        }
    }

    @Test
    public void testTwoJobExecutionsDeleteNotExpected() {
        addExecutions(100, "jobA");
        addExecutions(100, "jobB");

        Assertions.assertEquals(200, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(200, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testTwoJobExecutionsDeletesExpected() {
        addExecutions(105, "jobA");
        addExecutions(105, "jobB");

        Assertions.assertEquals(210, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(200, jobExecutionRepository.findAll().size());
    }

    @Test
    public void testMultipleDeletes() {
        addJobExecution("jobA", OffsetDateTime.now().minusDays(14).minusMinutes(1), ExecutionStatus.SUCCEEDED);
        addExecutions(101, "jobB");

        Assertions.assertEquals(101, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobB").size());
        Assertions.assertEquals(1, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(100, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobB").size());
        Assertions.assertEquals(0, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
    }

    @Test
    public void testCutOffDeleteNotExpected() {
        addJobExecution("jobA", OffsetDateTime.now().minusDays(13).minusHours(23).minusMinutes(59), ExecutionStatus.SUCCEEDED);

        Assertions.assertEquals(1, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(1, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
    }

    @Test
    public void testNullEndTimeDeleteNotExpected() {
        addJobExecution("jobA", null, ExecutionStatus.SUCCEEDED);

        Assertions.assertEquals(1, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(1, jobExecutionRepository.findDataJobExecutionsByDataJobName("jobA").size());
    }

    @Test
    public void testDeleteByNumbersAndJobsWithNullEndTimeDeleteExpected() {
        addExecutions(99, "jobA");
        addJobExecution("jobA", null, ExecutionStatus.SUCCEEDED);
        addJobExecution("jobA", null, ExecutionStatus.SUCCEEDED);

        Assertions.assertEquals(101, jobExecutionRepository.findAll().size());
        jobExecutionCleanupService.cleanupExecutions();
        Assertions.assertEquals(100, jobExecutionRepository.findAll().size());
    }

    private void addJobExecution(String jobName, OffsetDateTime time, ExecutionStatus status) {
        var excId = UUID.randomUUID().toString();
        var execution = RepositoryUtil.createDataJobExecution(jobExecutionRepository, excId, jobsRepository.findById(jobName).get(), status);
        execution.setStartTime(time);
        execution.setEndTime(time);
        jobExecutionRepository.save(execution);
    }

    private void addExecutions(int executionsNumber, String jobName) {
        for (int i = 0; i < executionsNumber; i++) {
            addJobExecution(jobName, OffsetDateTime.now(), ExecutionStatus.SUCCEEDED);
        }
    }

}
