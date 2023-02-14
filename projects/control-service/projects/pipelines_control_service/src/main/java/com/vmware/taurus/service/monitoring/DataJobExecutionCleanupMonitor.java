/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class DataJobExecutionCleanupMonitor {

  public static final String SUCCESSFUL_DELETIONS_COUNTER_NAME =
      "vdk.execution.cleanup.task.datajob.successful.deletions.counter";
  public static final String FAILED_DELETIONS_COUNTER_NAME =
      "vdk.execution.cleanup.task.datajob.failed.deletions.counter";
  public static final String CLEANUP_JOB_INVOCATIONS_COUNTER_NAME =
      "vdk.execution.cleanup.task.datajob.invocations.counter";

  private final MeterRegistry meterRegistry;
  private final Counter invocationsCounter;
  private final Counter failedDeletionsCounter;
  private final Counter successfulDeletionsCounter;

  @Autowired(required = true)
  public DataJobExecutionCleanupMonitor(MeterRegistry meterRegistry) {
    this.meterRegistry = meterRegistry;

    invocationsCounter =
        Counter.builder(CLEANUP_JOB_INVOCATIONS_COUNTER_NAME)
            .description("Counts the number of times the cleanup task is called.")
            .register(this.meterRegistry);

    failedDeletionsCounter =
        Counter.builder(FAILED_DELETIONS_COUNTER_NAME)
            .description(
                "Counts the total times the data job execution cleanup task was unsuccessful for a"
                    + " data job.")
            .register(this.meterRegistry);

    successfulDeletionsCounter =
        Counter.builder(SUCCESSFUL_DELETIONS_COUNTER_NAME)
            .description(
                "Counts the total times the data job execution cleanup task was successful for a"
                    + " data job.")
            .register(this.meterRegistry);
  }

  /**
   * Counts the number of times the JobExecutionCleanupService's cleanup data job execution method
   * was invoked.
   */
  public void countInvocation() {
    incrementCounter(invocationsCounter);
  }

  /** Counts the number of failed data job execution deletions by the JobExecutionCleanupService */
  public void countFailedDeletion() {
    incrementCounter(failedDeletionsCounter);
  }

  /**
   * Counts the number of successful data job execution deletions by the JobExecutionCleanupService.
   */
  public void countSuccessfulDeletion() {
    incrementCounter(successfulDeletionsCounter);
  }

  private void incrementCounter(Counter counter) {
    try {
      counter.increment();
    } catch (Exception e) {
      log.warn("Error while trying to increment counter.", e);
    }
  }
}
