/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@Slf4j
public class DataJobSynchronizerMonitor {

  public static final String DATAJOBS_SUCCESSFUL_SYNCHRONIZER_INVOCATIONS_COUNTER =
      "vdk.deploy.datajob.synchronizer.successful.invocations.counter";
  public static final String DATAJOBS_FAILED_SYNCHRONIZER_INVOCATIONS_COUNTER =
      "vdk.deploy.datajob.synchronizer.failed.invocations.counter";

  private final MeterRegistry meterRegistry;
  private final Counter successfulInvocationsCounter;
  private final Counter failedInvocationsCounter;

  @Autowired(required = true)
  public DataJobSynchronizerMonitor(MeterRegistry meterRegistry) {
    this.meterRegistry = meterRegistry;

    successfulInvocationsCounter =
        Counter.builder(DATAJOBS_SUCCESSFUL_SYNCHRONIZER_INVOCATIONS_COUNTER)
            .description(
                "Counts the number of times the synchronizeDataJobs() method is called and completes.")
            .register(this.meterRegistry);

    failedInvocationsCounter =
        Counter.builder(DATAJOBS_FAILED_SYNCHRONIZER_INVOCATIONS_COUNTER)
            .description(
                "Counts the number of times the synchronizeDataJobs() method failed to finish.")
            .register(this.meterRegistry);
  }

  /**
   * Counts the number of times the DataJobSynchronizer's synchronize method was invoked and
   * completed.
   */
  public void countSuccessfulSynchronizerInvocation() {
    incrementCounter(successfulInvocationsCounter);
  }

  /**
   * Counts the number of failed data job deployment synchronizations invocations by the
   * DataJobsSynchronizer due to K8S issues.
   */
  public void countSynchronizerFailures() {
    incrementCounter(failedInvocationsCounter);
  }

  private void incrementCounter(Counter counter) {
    try {
      counter.increment();
    } catch (Exception e) {
      log.warn("Error while trying to increment counter.", e);
    }
  }
}
