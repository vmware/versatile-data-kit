/*
 * Copyright 2021-2023 VMware, Inc.
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
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobExecutionCleanupMonitorTest {

  @Autowired private MeterRegistry meterRegistry;

  @Autowired private DataJobExecutionCleanupMonitor dataJobExecutionCleanupMonitor;

  @Test
  public void testInvocationsCounter() {
    var counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.CLEANUP_JOB_INVOCATIONS_COUNTER_NAME);
    Assertions.assertEquals(0.0, counter.count(), 0.001);
    Assertions.assertEquals(
        "Counts the number of times the cleanup task is called.", counter.getId().getDescription());

    dataJobExecutionCleanupMonitor.countInvocation();

    counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.CLEANUP_JOB_INVOCATIONS_COUNTER_NAME);
    Assertions.assertEquals(1.0, counter.count(), 0.001);

    dataJobExecutionCleanupMonitor.countInvocation();
    dataJobExecutionCleanupMonitor.countInvocation();
    dataJobExecutionCleanupMonitor.countInvocation();
    dataJobExecutionCleanupMonitor.countInvocation();

    counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.CLEANUP_JOB_INVOCATIONS_COUNTER_NAME);
    Assertions.assertEquals(5.0, counter.count(), 0.001);
  }

  @Test
  public void testFailedDeletionsCounter() {
    var counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.FAILED_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(0.0, counter.count(), 0.001);
    Assertions.assertEquals(
        "Counts the total times the data job execution cleanup task was unsuccessful for a data"
            + " job.",
        counter.getId().getDescription());

    dataJobExecutionCleanupMonitor.countFailedDeletion();

    counter = meterRegistry.counter(DataJobExecutionCleanupMonitor.FAILED_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(1.0, counter.count(), 0.001);

    dataJobExecutionCleanupMonitor.countFailedDeletion();
    dataJobExecutionCleanupMonitor.countFailedDeletion();
    dataJobExecutionCleanupMonitor.countFailedDeletion();
    dataJobExecutionCleanupMonitor.countFailedDeletion();

    counter = meterRegistry.counter(DataJobExecutionCleanupMonitor.FAILED_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(5.0, counter.count(), 0.001);
  }

  @Test
  public void testSuccessfulDeletionsCounter() {
    var counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.SUCCESSFUL_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(0.0, counter.count(), 0.001);
    Assertions.assertEquals(
        "Counts the total times the data job execution cleanup task was successful for a data job.",
        counter.getId().getDescription());

    dataJobExecutionCleanupMonitor.countSuccessfulDeletion();

    counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.SUCCESSFUL_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(1.0, counter.count(), 0.001);

    dataJobExecutionCleanupMonitor.countSuccessfulDeletion();
    dataJobExecutionCleanupMonitor.countSuccessfulDeletion();
    dataJobExecutionCleanupMonitor.countSuccessfulDeletion();
    dataJobExecutionCleanupMonitor.countSuccessfulDeletion();

    counter =
        meterRegistry.counter(DataJobExecutionCleanupMonitor.SUCCESSFUL_DELETIONS_COUNTER_NAME);
    Assertions.assertEquals(5.0, counter.count(), 0.001);
  }
}
