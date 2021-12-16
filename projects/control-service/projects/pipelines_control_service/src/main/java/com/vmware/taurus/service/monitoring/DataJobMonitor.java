/*
 * Copyright 2021 VMware, Inc.
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
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionResult;
import com.vmware.taurus.service.model.JobLabel;
import com.vmware.taurus.service.threads.ThreadPoolConf;
import io.kubernetes.client.ApiException;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import javax.transaction.Transactional;
import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Slf4j
@Component
public class DataJobMonitor {

    private static final long ONE_MINUTE_MILLIS = TimeUnit.MINUTES.toMillis(1);

    private final Map<String, String> labelsToWatch = Collections.singletonMap(JobLabel.TYPE.getValue(), "DataJob");

    private final JobsRepository jobsRepository;
    private final DataJobsKubernetesService dataJobsKubernetesService;
    private final JobsService jobsService;
    private final JobExecutionService jobExecutionService;
    private final DataJobMetrics dataJobMetrics;

    private long lastWatchTime = 0;

    @Autowired
    public DataJobMonitor(
            JobsRepository jobsRepository,
            DataJobsKubernetesService dataJobsKubernetesService,
            JobsService jobsService,
            JobExecutionService jobExecutionService,
            DataJobMetrics dataJobMetrics) {
        this.dataJobsKubernetesService = dataJobsKubernetesService;
        this.jobsRepository = jobsRepository;
        this.jobsService = jobsService;
        this.jobExecutionService = jobExecutionService;
        this.dataJobMetrics = dataJobMetrics;
    }

    /**
     * This method is annotated with {@link SchedulerLock} to prevent it from being executed simultaneously
     * by more than one instance of the service in a multi-node deployment. This aims to reduce the number
     * of rps to the Kubernetes API as well as to avoid errors due to concurrent database writes.
     * <p>
     * The flow is as follows:
     * <ol>
     *     <li>At any given point only one of the nodes will acquire the lock and execute the method.</li>
     *     <li>A lock will be held for no longer than 10 minutes (as configured in {@link ThreadPoolConf}),
     *     which should be enough for a watch to complete (it currently has 5 minutes timeout).</li>
     *     <li>The other nodes will skip their schedules until after this node completes.</li>
     *     <li>When a termination status of a job is updated by the node holding the lock, the other nodes will
     *     be eventually consistent within 5 seconds (by default) due to the continuous updates done here:
     *     {@link DataJobMonitorSync#updateDataJobStatus}.</li>
     *     <li>Subsequently, when one of the other nodes acquires the lock, it will detect all changes since
     *     its own last run (see {@code lastWatchTime}) and rewrite them. We can potentially improve on
     *     this by sharing the lastWatchTime amongst the nodes.</li>
     * </ol>
     *
     * @see <a href="https://github.com/lukas-krecan/ShedLock">ShedLock</a>
     */
    @Scheduled(
            fixedDelayString = "${datajobs.status.watch.interval:1000}",
            initialDelayString = "${datajobs.status.watch.initial.delay:10000}")
    @SchedulerLock(name = "watchJobs_schedulerLock")
    public void watchJobs() {
        try {
            dataJobsKubernetesService.watchJobs(
                    labelsToWatch,
                    s -> {
                        log.info("Termination message of Data Job {} with execution {}: {}",
                                s.getJobName(), s.getExecutionId(), s.getPodTerminationMessage());
                        recordJobExecutionStatus(s);
                    },
                    runningJobExecutionIds -> {
                        jobExecutionService.syncJobExecutionStatuses(runningJobExecutionIds);
                    },
                    lastWatchTime);
            // Move the lastWatchTime one minute into the past to account for events that
            // could have happened after the watch has completed until now
            lastWatchTime = System.currentTimeMillis() - ONE_MINUTE_MILLIS;
        } catch (IOException | ApiException e) {
            log.info("Failed to watch jobs. Error was: {}", e.getMessage());
        }
    }


    /**
     * Creates gauges that expose configuration information and termination status for the specified data jobs.
     * If the gauges already exist for a particular data job, they are updated if necessary.
     *
     * @param dataJobs The data jobs for which to create or update gauges.
     */
    public void updateDataJobsGauges(final Iterable<DataJob> dataJobs) {
        Objects.requireNonNull(dataJobs);

        dataJobs.forEach(job -> {
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
        var jobs = Streams.stream(dataJobs)
                .map(DataJob::getName)
                .collect(Collectors.toSet());
        dataJobMetrics.clearGaugesNotIn(jobs);
    }

    /**
     * Creates a gauge that exposes termination status for the specified data job.
     * If a gauge already exists for the data job, it is updated if necessary.
     *
     * @param dataJob The data job for which to create or update a gauge.
     */
    void updateDataJobTerminationStatusGauge(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        if (dataJob.getLatestJobTerminationStatus() == null ||
                StringUtils.isEmpty(dataJob.getLatestJobExecutionId())) {
            return;
        }

        dataJobMetrics.updateTerminationStatusGauge(dataJob);
    }

    /**
     * Creates gauges that expose configuration information for the specified data job.
     * If the gauges already exist for the data job, they are updated if necessary.
     *
     * @param dataJob The data job for which to create or update the gauges.
     */
    void updateDataJobInfoGauges(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        dataJobMetrics.updateInfoGauges(dataJob);
    }

    /**
     * Record Data Job execution status. It will record when a job has started, finished, failed or skipped.
     *
     * @param jobStatus - the job status of the job. The same information is sent as telemetry by Measureable annotation.
     */
    @Measurable(includeArg = 0, argName = "execution_status")
    @Transactional
    void recordJobExecutionStatus(KubernetesService.JobExecution jobStatus) {
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
        jobExecutionService.updateJobExecution(dataJob, jobStatus, executionResult)
                .ifPresent(jobsService::updateLastExecution);

        // Update the termination status from the last execution
        jobExecutionService.getLastExecution(dataJobName)
                .ifPresent(e -> {
                    if (jobsService.updateTerminationStatus(e)) {
                        jobsRepository.findById(dataJobName).ifPresent(this::updateDataJobTerminationStatusGauge);
                    }
                });
    }
}
