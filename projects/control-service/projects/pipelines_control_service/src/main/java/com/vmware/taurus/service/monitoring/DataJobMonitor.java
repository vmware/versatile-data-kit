/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.google.common.collect.Streams;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.execution.JobExecutionResultManager;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionResult;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.transaction.Transactional;
import java.io.IOException;
import java.time.Instant;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Slf4j
@Component
public class DataJobMonitor {

  private final JobsRepository jobsRepository;
  private final JobsService jobsService;
  private final JobExecutionService jobExecutionService;
  private final DataJobMetrics dataJobMetrics;

  private long lastWatchTime =
      Instant.now().minusMillis(TimeUnit.MINUTES.toMillis(30)).toEpochMilli();

  @Autowired
  public DataJobMonitor(
      JobsRepository jobsRepository,
      JobsService jobsService,
      JobExecutionService jobExecutionService,
      DataJobMetrics dataJobMetrics) {
    this.jobsRepository = jobsRepository;
    this.jobsService = jobsService;
    this.jobExecutionService = jobExecutionService;
    this.dataJobMetrics = dataJobMetrics;
  }


  /**
   * Creates gauges that expose configuration information and termination status for the specified
   * data jobs. If the gauges already exist for a particular data job, they are updated if
   * necessary.
   *
   * @param dataJobs The data jobs for which to create or update gauges.
   */
  public void updateDataJobsGauges(final Iterable<DataJob> dataJobs) {
    Objects.requireNonNull(dataJobs);

    dataJobs.forEach(
        job -> {
          updateDataJobInfoGauges(job);
          updateDataJobTerminationStatusGauge(job);
        });
  }

  /**
   * Deletes the gauges for all data jobs that are not present in the specified iterable.
   *
   * @param dataJobs The data jobs for which to keep gauges.
   */
  public void clearDataJobsGaugesNotIn(final Iterable<DataJob> dataJobs) {
    var jobs = Streams.stream(dataJobs).map(DataJob::getName).collect(Collectors.toSet());
    dataJobMetrics.clearGaugesNotIn(jobs);
  }

  /**
   * Creates a gauge that exposes termination status for the specified data job. If a gauge already
   * exists for the data job, it is updated if necessary.
   *
   * @param dataJob The data job for which to create or update a gauge.
   */
  void updateDataJobTerminationStatusGauge(final DataJob dataJob) {
    Objects.requireNonNull(dataJob);

    if (dataJob.getLatestJobTerminationStatus() == null
        || StringUtils.isEmpty(dataJob.getLatestJobExecutionId())) {
      return;
    }

    dataJobMetrics.updateTerminationStatusGauge(dataJob);
  }

  /**
   * Creates gauges that expose configuration information for the specified data job. If the gauges
   * already exist for the data job, they are updated if necessary.
   *
   * @param dataJob The data job for which to create or update the gauges.
   */
  void updateDataJobInfoGauges(final DataJob dataJob) {
    Objects.requireNonNull(dataJob);

    dataJobMetrics.updateInfoGauges(dataJob);
  }

  /**
   * Record Data Job execution status. It will record when a job has started, finished, failed or
   * skipped.
   *
   * @param jobStatus - the job status of the job. The same information is sent as telemetry by
   *     Measureable annotation.
   */
  @Measurable(includeArg = 0, argName = "execution_status")
  @Transactional
  public void recordJobExecutionStatus(KubernetesService.JobExecution jobStatus) {
    log.debug("Storing Data Job execution status: {}", jobStatus);
    String dataJobName = jobStatus.getJobName();
    ExecutionResult executionResult = JobExecutionResultManager.getResult(jobStatus);

    if (StringUtils.isBlank(dataJobName)) {
      log.warn("Data job name is empty");
      return;
    }

    Optional<DataJob> dataJobOptional = jobsRepository.findById(dataJobName);
    if (dataJobOptional.isEmpty()) {
      log.debug("Data job {} was deleted or hasn't been created", dataJobName);
      return;
    }

    final DataJob dataJob = dataJobOptional.get();

    // Update the job execution and the last execution state
    Optional<DataJobExecution> dataJobExecution = jobExecutionService
            .updateJobExecution(dataJob, jobStatus, executionResult);
    dataJobExecution
        .ifPresent(jobsService::updateLastExecution);

    // Update the termination status from the last execution
    dataJobExecution
        .ifPresent(
            e -> {
              if (jobsService.updateTerminationStatus(e)) {
                jobsRepository
                    .findById(dataJobName)
                    .ifPresent(this::updateDataJobTerminationStatusGauge);
              }
            });
  }
}
