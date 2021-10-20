/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobExecutionCleanupMonitorTest {

    @Autowired
    private MeterRegistry meterRegistry;

    @Autowired
    private DataJobExecutionCleanupMonitor dataJobExecutionCleanupMonitor;

    private DataJob testDataJobOne;
    private DataJob testDataJobTwo;
    private DataJob testDataJobOneClone;

    @BeforeEach
    public void cleanUp() {
        meterRegistry.clear();
        JobConfig config = new JobConfig();
        config.setSchedule("schedule");
        config.setTeam("test-team");
        testDataJobOne = new DataJob("testJobOne", config);
        testDataJobOneClone = new DataJob("testJobOne", config);
        testDataJobTwo = new DataJob("testJobTwo", config);
    }

    @Test
    public void testStatusCreateNewGaugeSuccess() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 2);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();
        // Expecting both gauges to be populated
        Assertions.assertEquals(1, gauges.size());

        var gauge = gauges.stream().findFirst().get();

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.status", gauge.getId().getName());
        Assertions.assertEquals("Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions.)", gauge.getId().getDescription());
        Assertions.assertEquals("testJobOne", gauge.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", gauge.getId().getTag("data_job_team"));
        // Expecting to see status 0 - success
        Assertions.assertEquals(0.0, gauge.value(), 0.001);

    }

    @Test
    public void testStatusCreateNewGaugeFailed() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();
        // Expecting both gauges to be populated
        Assertions.assertEquals(1, gauges.size());

        var gauge = gauges.stream().findFirst().get();

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.status", gauge.getId().getName());
        Assertions.assertEquals("Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions.)", gauge.getId().getDescription());
        Assertions.assertEquals("testJobOne", gauge.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", gauge.getId().getTag("data_job_team"));
        // Expecting to see status 1 - failure
        Assertions.assertEquals(1.0, gauge.value(), 0.001);

    }

    @Test
    public void testDeletionsCreateNewGaugeFailed() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();

        Assertions.assertEquals(1, gauges.size());

        var gauge = gauges.stream().findFirst().get();

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.deletions", gauge.getId().getName());
        Assertions.assertEquals("Deleted executions by the JobExecutionCLeanupService: (number of jobs deleted in last run.)", gauge.getId().getDescription());
        Assertions.assertEquals("testJobOne", gauge.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", gauge.getId().getTag("data_job_team"));
        // Expecting zero deletions.
        Assertions.assertEquals(0.0, gauge.value(), 0.001);

    }

    @Test
    public void testDeletionsCreateNewGaugeSuccess() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 15);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();

        Assertions.assertEquals(1, gauges.size());

        var gauge = gauges.stream().findFirst().get();

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.deletions", gauge.getId().getName());
        Assertions.assertEquals("Deleted executions by the JobExecutionCLeanupService: (number of jobs deleted in last run.)", gauge.getId().getDescription());
        Assertions.assertEquals("testJobOne", gauge.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", gauge.getId().getTag("data_job_team"));
        // Expecting 15 deletions.
        Assertions.assertEquals(15.0, gauge.value(), 0.001);

    }

    @Test
    public void testStatusUpdateExistingGauge() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();
        //Expect one gauge
        Assertions.assertEquals(1, gauges.size());
        var gauge = gauges.stream().findFirst().get();
        //Confirm initial value
        Assertions.assertEquals(1.0, gauge.value(), 0.001);

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 10);
        gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();
        //Confirm one gauge remains after update.
        Assertions.assertEquals(1, gauges.size(), "Expecting one registered meter gauge.");
        gauge = gauges.stream().findFirst().get();
        //Confirm value got updated.
        Assertions.assertEquals(0.0, gauge.value(), 0.001);

    }

    @Test
    public void testDeletionUpdateExistingGauge() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        //Expect one gauge
        Assertions.assertEquals(1, gauges.size());
        var gauge = gauges.stream().findFirst().get();
        //Confirm initial value
        Assertions.assertEquals(0.0, gauge.value(), 0.001);

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 10);
        gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        //Confirm one gauge remains after update.
        Assertions.assertEquals(1, gauges.size(), "Expecting one registered meter gauge.");
        gauge = gauges.stream().findFirst().get();
        //Confirm value got updated.
        Assertions.assertEquals(10.0, gauge.value(), 0.001);

    }

    @Test
    public void testUpdateExistingDeletions() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 5);
        var gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        var gauge = gauges.stream().findFirst().get();
        Assertions.assertEquals(5.0, gauge.value());

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 10);
        gauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size(), 0.001);
        gauge = gauges.stream().findFirst().get();
        Assertions.assertEquals(10.0, gauge.value(), 0.001);

    }

    @Test
    public void testTwoGauges() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 5);
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobTwo);

        var meters = meterRegistry.getMeters();
        Assertions.assertEquals(4, meters.size());

    }

    @Test
    public void testNotUpdatingUnchangedGauge() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 1);

        var deletionGauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        var statusGauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();
        Assertions.assertEquals(1, deletionGauges.size());
        Assertions.assertEquals(1, statusGauges.size());


        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOneClone, 1);
        // Not expecting a change after adding a complete clone of the data job.
        deletionGauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_DELETIONS_METRIC_NAME).gauges();
        statusGauges = meterRegistry.find(DataJobExecutionCleanupMonitor.EXECUTION_STATUS_CLEANUP_METRIC_NAME).gauges();

        Assertions.assertEquals(1, deletionGauges.size());
        Assertions.assertEquals(1, statusGauges.size());

    }

}
