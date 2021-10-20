/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobExecutionCleanupMonitorCounterTest {
    @Autowired
    private MeterRegistry meterRegistry;

    @Autowired
    private DataJobExecutionCleanupMonitor dataJobExecutionCleanupMonitor;

    @Test
    public void testInvocationsCounter() {
        var counter = meterRegistry.counter(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_INVOCATIONS_COUNTER_NAME);
        Assertions.assertEquals(0.0, counter.count(), 0.001);
        Assertions.assertEquals("Counts the number of times the cleanup task is called.", counter.getId().getDescription());

        dataJobExecutionCleanupMonitor.countInvocation();

        counter = meterRegistry.counter(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_INVOCATIONS_COUNTER_NAME);
        Assertions.assertEquals(1.0, counter.count(), 0.001);

        dataJobExecutionCleanupMonitor.countInvocation();
        dataJobExecutionCleanupMonitor.countInvocation();
        dataJobExecutionCleanupMonitor.countInvocation();
        dataJobExecutionCleanupMonitor.countInvocation();

        counter = meterRegistry.counter(DataJobExecutionCleanupMonitor.EXECUTION_CLEANUP_INVOCATIONS_COUNTER_NAME);
        Assertions.assertEquals(5.0, counter.count(), 0.001);

    }

}
