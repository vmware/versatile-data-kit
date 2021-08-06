/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.KubernetesService.PodTerminationMessage;
import com.vmware.taurus.service.diag.methodintercept.Measurable;
import com.vmware.taurus.service.execution.JobExecutionService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobLabel;
import com.vmware.taurus.service.model.TerminationStatus;
import com.vmware.taurus.service.threads.ThreadPoolConf;
import io.kubernetes.client.ApiException;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import lombok.extern.slf4j.Slf4j;
import net.javacrumbs.shedlock.spring.annotation.SchedulerLock;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Supplier;

@Slf4j
@Component
public class DataJobStatusMonitor {

    public static final String GAUGE_METRIC_NAME = "taurus.datajob.termination.status";
    private static final long ONE_MINUTE_MILLIS = TimeUnit.MINUTES.toMillis(1);

    private final DataJobsKubernetesService dataJobsKubernetesService;
    private final MeterRegistry meterRegistry;
    private final JobsRepository jobsRepository;
    private final JobExecutionService jobExecutionService;
    private final Map<String, String> labelsToWatch = Collections.singletonMap(JobLabel.TYPE.getValue(), "DataJob");
    private final Map<String, Gauge> statusGauges = new ConcurrentHashMap<>();
    private final Map<String, Integer> currentStatuses = new ConcurrentHashMap<>();
    private final ReentrantLock lock = new ReentrantLock(true);
    private long lastWatchTime = 0;

    @Autowired
    public DataJobStatusMonitor(
            DataJobsKubernetesService dataJobsKubernetesService,
            MeterRegistry meterRegistry,
            JobsRepository jobsRepository,
            JobExecutionService jobExecutionService) {

        this.dataJobsKubernetesService = dataJobsKubernetesService;
        this.meterRegistry = meterRegistry;
        this.jobsRepository = jobsRepository;
        this.jobExecutionService = jobExecutionService;
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
     *     {@link DataJobStatusMonitorSync#updateDataJobStatus}.</li>
     *     <li>Subsequently, when one of the other nodes acquires the lock, it will detect all changes since
     *     its own last run (see {@code lastWatchTime}) and rewrite them. We can potentially improve on
     *     this by sharing the lastWatchTime amongst the nodes.</li>
     * </ol>
     *
     * @see   <a href="https://github.com/lukas-krecan/ShedLock">ShedLock</a>
     */
    @Scheduled(
            fixedDelayString = "${datajobs.status.watch.interval:1000}",
            initialDelayString = "${datajobs.status.watch.initial.delay:10000}")
    @SchedulerLock(name = "watchJobs_schedulerLock")
    public void watchJobs() {
        try {
            dataJobsKubernetesService.watchJobs(labelsToWatch,
                    s -> {
                        log.info("Termination message of job {} with execution {}: {}",
                                s.getJobName(), s.getExecutionId(), s.getTerminationMessage());
                        recordJobExecutionStatus(s);
                    }, lastWatchTime);
            // Move the lastWatchTime one minute into the past to account for events that
            // could have happened after the watch has completed until now
            lastWatchTime = System.currentTimeMillis() - ONE_MINUTE_MILLIS;
        } catch (IOException | ApiException e) {
            log.info("Failed to watch jobs. Error was: {}", e.getMessage());
        }
    }

    public static TerminationStatus getTerminationStatus(String terminationMessage) {
        if (PodTerminationMessage.SUCCESS.getValue().equals(terminationMessage)) {
            return TerminationStatus.SUCCESS;
        }
        if (PodTerminationMessage.PLATFORM_ERROR.getValue().equals(terminationMessage)) {
            return TerminationStatus.PLATFORM_ERROR;
        }
        if (PodTerminationMessage.USER_ERROR.getValue().equals(terminationMessage)) {
            return TerminationStatus.USER_ERROR;
        }
        if (PodTerminationMessage.SKIPPED.getValue().equals(terminationMessage)){
            return TerminationStatus.SKIPPED;
        }
        return TerminationStatus.NONE;
    }

    /**
     * Creates a gauge to expose execution status about the specified data job.
     * If a gauge already exists for the job, it is updated if needed.
     * <p>
     * This method is synchronized.
     *
     * @param dataJobSupplier A supplier of the data job for which to create or update a gauge.
     */
    public void updateDataJobTerminationStatus(final Supplier<DataJob> dataJobSupplier) {
        updateDataJobsTerminationStatus(() -> {
            final var dataJob = Objects.requireNonNullElse(dataJobSupplier, () -> null).get();
            return dataJob == null ? Collections.emptyList() : Collections.singletonList(dataJob);
        });
    }

    /**
     * Creates a gauge to expose termination status for each of the specified data jobs.
     * If a gauge already exists for any of the jobs, it is updated if needed.
     * <p>
     * This method is synchronized.
     *
     * @param dataJobsSupplier A supplier of the data jobs for which to create or update gauges.
     * @return true if the supplier produced at least one job; otherwise, false.
     */
    public boolean updateDataJobsTerminationStatus(final Supplier<Iterable<DataJob>> dataJobsSupplier) {
        lock.lock();
        try {
            var dataJobs = Objects.requireNonNullElse(dataJobsSupplier, Collections::emptyList).get().iterator();
            if (!dataJobs.hasNext()) {
                return false;
            }

            dataJobs.forEachRemaining(dataJob -> {
                if (dataJob.getLatestJobTerminationStatus() == null ||
                        StringUtils.isEmpty(dataJob.getLatestJobExecutionId())) {
                    return;
                }

                var dataJobName = dataJob.getName();
                var gauge = statusGauges.getOrDefault(dataJobName, null);
                var newTags = createGaugeTags(dataJob);
                if (isChanged(gauge, newTags)) {
                    log.info("The last termination status of data job {} has changed", dataJobName);
                    removeGauge(dataJobName);
                }

                if (!statusGauges.containsKey(dataJobName)) {
                    gauge = createGauge(dataJobName, newTags);
                    statusGauges.put(dataJobName, gauge);
                    log.info("The termination status gauge for data job {} was created", dataJobName);
                }
                currentStatuses.put(dataJobName, dataJob.getLatestJobTerminationStatus().getValue());
            });

            return true;
        } finally {
            lock.unlock();
        }
    }

    /**
     * Record Data Job execution status. It will record when a job has started, finished, failed or skipped.
     * @param jobStatus - the job status of the job. The same information is send as telemetry by Measureable annotation.
     */
    @Measurable(includeArg = 0, argName = "execution_status")
    void recordJobExecutionStatus(KubernetesService.JobExecution jobStatus) {
        log.debug("Storing Data Job execution status: {}", jobStatus);
        String dataJobName = jobStatus.getJobName();
        String executionId = jobStatus.getExecutionId();
        var terminationStatus = getTerminationStatus(jobStatus.getTerminationMessage());

        if (StringUtils.isBlank(dataJobName)) {
            log.warn("Data job name is empty");
            return;
        }

        Optional<DataJob> dataJobOptional = jobsRepository.findById(dataJobName);
        if (dataJobOptional.isEmpty()) {
            log.debug("Data job {} was deleted or hasn't been created", dataJobName);
            return;
        }

        var dataJob = dataJobOptional.get();
        updateDataJobTerminationStatus(() -> saveTerminationStatus(dataJob, executionId, terminationStatus));

        jobExecutionService.updateJobExecution(dataJob, jobStatus);
    }

    private boolean isChanged(final Gauge gauge, final Tags newTags) {
        if (gauge == null) {
            return false;
        }

        var existingTags = gauge.getId().getTags();
        return !newTags.stream().allMatch(existingTags::contains);
    }

    /**
     * Creates and registers a termination status gauge for the data job with the specified name,
     *
     * @param dataJobName The name of the data job for which to create gauge.
     * @param tags        The labels of the new gauge.
     */
    private Gauge createGauge(final String dataJobName, final Tags tags) {
        return Gauge.builder(GAUGE_METRIC_NAME, currentStatuses,
                map -> map.getOrDefault(dataJobName, TerminationStatus.NONE.getValue()))
                .tags(tags)
                .description("Termination status of data job executions (0 - Success, 1 - Platform error, 3 - User error)")
                .register(meterRegistry);
    }

    private Tags createGaugeTags(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);
        return Tags.of(
                "data_job", dataJob.getName(),
                "execution_id", dataJob.getLatestJobExecutionId());
    }

    private void removeGauge(final String dataJobName) {
        if (StringUtils.isNotBlank(dataJobName)) {
            var gauge = statusGauges.getOrDefault(dataJobName, null);
            if (gauge != null) {
                meterRegistry.remove(gauge);
                statusGauges.remove(dataJobName);
                log.info("The termination status gauge for data job {} was removed", dataJobName);
            }
        } else {
            log.warn("Data job name is empty");
        }
    }

    /**
     * Updates the latest termination status of the data job with the specified name (if it exists)
     * in the jobs repository.
     *
     * @param dataJob           the data job to be updated
     * @param executionId       The execution identifier.
     * @param terminationStatus The termination status of the job.
     * @return The updated data job, or null, if no job with this name does not exist.
     */
    private DataJob saveTerminationStatus(DataJob dataJob, String executionId, TerminationStatus terminationStatus) {
        if (dataJob.getLatestJobTerminationStatus() == terminationStatus &&
                StringUtils.equals(dataJob.getLatestJobExecutionId(), executionId)) {
            return dataJob;
        }

        dataJob.setLatestJobTerminationStatus(terminationStatus);
        dataJob.setLatestJobExecutionId(executionId);

        return jobsRepository.save(dataJob);
    }
}
