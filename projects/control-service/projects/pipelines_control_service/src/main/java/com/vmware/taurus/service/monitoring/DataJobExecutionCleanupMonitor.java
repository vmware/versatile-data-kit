/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.model.DataJob;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;


@Slf4j
@Component
public class DataJobExecutionCleanupMonitor {

    public static final String EXECUTION_STATUS_CLEANUP_METRIC_NAME = "vdk.execution.cleanup.task.datajob.status";
    public static final String EXECUTION_CLEANUP_DELETIONS_METRIC_NAME = "vdk.execution.cleanup.task.datajob.deletions";
    public static final String EXECUTION_CLEANUP_INVOCATIONS_COUNTER_NAME = "vdk.execution.cleanup.task.datajob.invocations";

    private final String STATUS_GAUGE_DESCRIPTION = "Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions.)";
    private final String DELETIONS_GAUGE_DESCRIPTION = "Deleted executions by the JobExecutionCLeanupService: (number of jobs deleted in last run.)";

    private final MeterRegistry meterRegistry;

    private final Integer GAUGE_SUCCESS_METRIC_VALUE = 0;
    private final Integer GAUGE_FAILURE_METRIC_VALUE = 1;

    private final String TAG_DATA_JOB = "data_job_name";
    private final String TAG_TEAM = "data_job_team";

    private final Map<String, Gauge> cleanupStatusGauges = new ConcurrentHashMap<>();
    private final Map<String, Integer> cleanupStatuses = new ConcurrentHashMap<>();

    private final Map<String, Gauge> cleanupNumberGauges = new ConcurrentHashMap<>();
    private final Map<String, Integer> deletedExecutionsNumbers = new ConcurrentHashMap<>();
    private final Counter invocationsCounter;

    @Autowired(required = true)
    public DataJobExecutionCleanupMonitor(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        invocationsCounter = Counter.builder(EXECUTION_CLEANUP_INVOCATIONS_COUNTER_NAME)
                .description("Counts the number of times the cleanup task is called.")
                .register(this.meterRegistry);
    }

    /**
     * Creates a gauge for a failed execution cleanup
     * and registers it with the meter registry.
     *
     * @param dataJob
     */
    public void addFailedGauge(final DataJob dataJob) {
        // Set deleted executions to 0 in case of failure.
        addGauge(dataJob, 0, GAUGE_FAILURE_METRIC_VALUE);
    }

    /**
     * Creates a gauge for a successful execution cleanup
     * and registers it with the meter registry.
     *
     * @param dataJob
     * @param deletedExecutions
     */
    public void addSuccessfulGauge(final DataJob dataJob, int deletedExecutions) {
        addGauge(dataJob, deletedExecutions, GAUGE_SUCCESS_METRIC_VALUE);
    }

    public void countInvocation() {
        try {
            invocationsCounter.increment();
        } catch (Exception e) {
            log.warn("Error while trying to increment invocation counter.", e);
        }
    }

    private void addGauge(final DataJob dataJob, int deletedExecutions, int gaugeStatus) {
        try {

            Objects.requireNonNull(dataJob);
            Objects.requireNonNull(dataJob.getJobConfig());
            Objects.requireNonNull(dataJob.getName());

            var dataJobName = dataJob.getName();
            var oldStatusGauge = cleanupStatusGauges.getOrDefault(dataJobName, null);
            var oldDeletionsGauge = cleanupNumberGauges.getOrDefault(dataJobName, null);
            var newTags = createStatusGaugeTags(dataJob);
            // the only way to update a gauge is to delete it and create a new one.
            removeGaugeIfNecessary(oldStatusGauge, newTags, dataJobName, cleanupStatuses, cleanupStatusGauges);
            removeGaugeIfNecessary(oldDeletionsGauge, newTags, dataJobName, deletedExecutionsNumbers, cleanupNumberGauges);

            deletedExecutionsNumbers.put(dataJobName, deletedExecutions);
            cleanupStatuses.put(dataJobName, gaugeStatus);

            cleanupNumberGauges.put(dataJobName, createGauge(dataJobName, newTags, deletedExecutionsNumbers,
                    EXECUTION_CLEANUP_DELETIONS_METRIC_NAME, DELETIONS_GAUGE_DESCRIPTION));

            cleanupStatusGauges.put(dataJobName, createGauge(dataJobName, newTags, cleanupStatuses,
                    EXECUTION_STATUS_CLEANUP_METRIC_NAME, STATUS_GAUGE_DESCRIPTION));

        } catch (Exception e) {
            log.warn("Execution cleanup monitoring failed with error: {}", e);
        }
    }

    private void removeGaugeIfNecessary(Gauge oldStatusGauge, Tags newTags, String dataJobName,
                                        Map<String, Integer> valueMapToCleanp, Map<String, Gauge> gaugeMapToCleanup) {

        if (MonitoringUtil.isGaugeChanged(oldStatusGauge, newTags)) {
            valueMapToCleanp.remove(dataJobName);
            removeGauge(dataJobName, gaugeMapToCleanup);
        }
    }

    private void removeGauge(String dataJobName, final Map<String, Gauge> gauges) {
        if (StringUtils.isNotBlank(dataJobName)) {
            var gauge = gauges.getOrDefault(dataJobName, null);
            if (gauge != null) {
                meterRegistry.remove(gauge);
                gauges.remove(dataJobName);
                log.info("Removed job: {}", dataJobName);
            } else {
                log.info("Job {} cannot be removed: gauge not found", dataJobName);
            }
        } else {
            log.warn("Job name is empty");
        }
    }

    private Tags createStatusGaugeTags(final DataJob dataJob) {
        return Tags.of(
                TAG_DATA_JOB, dataJob.getName(),
                TAG_TEAM, StringUtils.defaultString(dataJob.getJobConfig().getTeam()));
    }

    private Gauge createGauge(final String dataJobName, final Tags tags,
                              final Map<String, Integer> statusMap, final String gaugeName,
                              final String description) {

        var gauge = Gauge.builder(gaugeName, statusMap,
                        map -> map.getOrDefault(dataJobName, 0))
                .tags(tags)
                .description(description)
                .register(meterRegistry);
        log.info("The cleanup status gauge for data job {} 's executions was created", dataJobName);
        return gauge;

    }

}
