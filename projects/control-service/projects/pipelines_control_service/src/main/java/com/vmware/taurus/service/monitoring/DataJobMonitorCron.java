/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.exception.KubernetesException;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobLabel;
import com.vmware.taurus.service.threads.ThreadPoolConf;
import io.kubernetes.client.openapi.ApiException;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.time.Instant;
import java.util.Collections;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
public class DataJobMonitorCron {

  private static final long ONE_MINUTE_MILLIS = TimeUnit.MINUTES.toMillis(1);

  private final Map<String, String> labelsToWatch =
      Collections.singletonMap(JobLabel.TYPE.getValue(), "DataJob");

  private final DataJobsKubernetesService dataJobsKubernetesService;
  private final JobExecutionService jobExecutionService;
  private final DataJobMetrics dataJobMetrics;
  private final DataJobMonitor dataJobMonitor;

  private long lastWatchTime =
      Instant.now().minusMillis(TimeUnit.MINUTES.toMillis(30)).toEpochMilli();

  @Autowired
  public DataJobMonitorCron(
      DataJobsKubernetesService dataJobsKubernetesService,
      JobExecutionService jobExecutionService,
      DataJobMetrics dataJobMetrics,
      DataJobMonitor dataJobMonitor) {
    this.dataJobsKubernetesService = dataJobsKubernetesService;
    this.jobExecutionService = jobExecutionService;
    this.dataJobMetrics = dataJobMetrics;
    this.dataJobMonitor = dataJobMonitor;
    log.info("Data Job Monitor initialized to watch for jobs with labels: {}", labelsToWatch);
  }

  /**
   * This method is annotated with {@link SchedulerLock} to prevent it from being executed
   * simultaneously by more than one instance of the service in a multi-node deployment. This aims
   * to reduce the number of rps to the Kubernetes API as well as to avoid errors due to concurrent
   * database writes.
   *
   * <p>The flow is as follows:
   *
   * <ol>
   *   <li>At any given point only one of the nodes will acquire the lock and execute the method.
   *   <li>A lock will be held for no longer than 10 minutes (as configured in {@link
   *       ThreadPoolConf}), which should be enough for a watch to complete (it currently has 5
   *       minutes timeout).
   *   <li>The other nodes will skip their schedules until after this node completes.
   *   <li>When a termination status of a job is updated by the node holding the lock, the other
   *       nodes will be eventually consistent within 5 seconds (by default) due to the continuous
   *       updates done here: {@link DataJobMonitorSync#updateDataJobStatus}.
   *   <li>Subsequently, when one of the other nodes acquires the lock, it will detect all changes
   *       since its own last run (see {@code lastWatchTime}) and rewrite them. We can potentially
   *       improve on this by sharing the lastWatchTime amongst the nodes.
   * </ol>
   *
   * @see <a href="https://github.com/lukas-krecan/ShedLock">ShedLock</a>
   */
  @Scheduled(
      fixedDelayString = "${datajobs.status.watch.interval:1000}",
      initialDelayString = "${datajobs.status.watch.initial.delay:10000}")
  @SchedulerLock(name = "watchJobs_schedulerLock")
  public void watchJobs() {
    dataJobMetrics.incrementWatchTaskInvocations();
    try {
      dataJobsKubernetesService.watchJobs(
          labelsToWatch,
          s -> {
            log.info(
                "Termination message of Data Job {} with execution {}: {}",
                s.getJobName(),
                s.getExecutionId(),
                s.getMainContainerTerminationMessage());
            dataJobMonitor.recordJobExecutionStatus(s);
          },
          jobExecutionService::syncJobExecutionStatuses,
          lastWatchTime);
      // Move the lastWatchTime one minute into the past to account for events that
      // could have happened after the watch has completed until now
      lastWatchTime = Instant.now().minusMillis(ONE_MINUTE_MILLIS).toEpochMilli();
    } catch (IOException ioe) {
      log.info("Failed to watch jobs. Error was: {}", ioe.toString());
    } catch (ApiException ae) {
      log.info("Failed to watch jobs. Error was: {}", new KubernetesException("", ae).toString());
    }
  }
}
