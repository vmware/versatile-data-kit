/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
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
    public void testCreateNewSuccessGauge() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 1);
        var meters = meterRegistry.getMeters();

        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");

        var meter = meters.get(0);

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.status", meter.getId().getName());
        Assertions.assertEquals("Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions)", meter.getId().getDescription());
        Assertions.assertEquals("testJobOne", meter.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", meter.getId().getTag("data_job_team"));
        Assertions.assertEquals("1", meter.getId().getTag("latest_datajob_execution_cleanups_number"));
        Assertions.assertEquals("true", meter.getId().getTag("latest_datajob_execution_cleanup_status_success"));

    }

    @Test
    public void testCreateNewFailureGauge() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var meters = meterRegistry.getMeters();

        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");

        var meter = meters.get(0);

        Assertions.assertEquals("vdk.execution.cleanup.task.datajob.status", meter.getId().getName());
        Assertions.assertEquals("Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions)", meter.getId().getDescription());
        Assertions.assertEquals("testJobOne", meter.getId().getTag("data_job_name"));
        Assertions.assertEquals("test-team", meter.getId().getTag("data_job_team"));
        Assertions.assertEquals("0", meter.getId().getTag("latest_datajob_execution_cleanups_number"));
        Assertions.assertEquals("false", meter.getId().getTag("latest_datajob_execution_cleanup_status_success"));
    }

    @Test
    public void testUpdateExistingStatus() {
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobOne);
        var meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");
        var meter = meters.get(0);
        Assertions.assertEquals("false", meter.getId().getTag("latest_datajob_execution_cleanup_status_success"));

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 10);
        meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");
        meter = meters.get(0);
        Assertions.assertEquals("true", meter.getId().getTag("latest_datajob_execution_cleanup_status_success"));

    }

    @Test
    public void testUpdateExistingDeletions() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 5);
        var meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");
        var meter = meters.get(0);
        Assertions.assertEquals("true", meter.getId().getTag("latest_datajob_execution_cleanup_status_success"));
        Assertions.assertEquals("5", meter.getId().getTag("latest_datajob_execution_cleanups_number"));

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 10);
        meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");
        meter = meters.get(0);
        Assertions.assertEquals("10", meter.getId().getTag("latest_datajob_execution_cleanups_number"));

    }

    @Test
    public void testTwoGauges() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 5);
        dataJobExecutionCleanupMonitor.addFailedGauge(testDataJobTwo);

        var meters = meterRegistry.getMeters();
        Assertions.assertEquals(2, meters.size(), "Expecting two registered meter gauges.");

    }

    @Test
    public void testNotUpdatingUnchangedGauge() {
        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOne, 1);

        var meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");

        dataJobExecutionCleanupMonitor.addSuccessfulGauge(testDataJobOneClone, 1);
        // Not expecting a change after adding a complete clone of the data job.
        meters = meterRegistry.getMeters();
        Assertions.assertEquals(1, meters.size(), "Expecting one registered meter gauge.");

    }

}
