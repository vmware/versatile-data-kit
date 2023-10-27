/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = ControlplaneApplication.class)
public class DataJobSynchronizerMonitorTest {

  @Autowired DataJobSynchronizerMonitor dataJobSynchronizerMonitor;

  @Autowired private MeterRegistry meterRegistry;

  @Test
  public void testIncrementSuccessfulInvocations() {
    var counter =
        meterRegistry.counter(
            DataJobSynchronizerMonitor.DATAJOBS_SUCCESSFUL_SYNCHRONIZER_INVOCATIONS_COUNTER);
    Assertions.assertEquals(0.0, counter.count(), 0.001);
    dataJobSynchronizerMonitor.countSuccessfulSynchronizerInvocation();

    Assertions.assertEquals(1, counter.count(), 0.001);
  }

  @Test
  public void testIncrementFailedInvocations() {
    var counter =
        meterRegistry.counter(
            DataJobSynchronizerMonitor.DATAJOBS_FAILED_SYNCHRONIZER_INVOCATIONS_COUNTER);
    Assertions.assertEquals(0.0, counter.count(), 0.001);
    dataJobSynchronizerMonitor.countSynchronizerFailures();

    Assertions.assertEquals(1, counter.count(), 0.001);
  }
}
