/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.model.DataJob;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;


@Slf4j
@RequiredArgsConstructor
@Component
public class DataJobExecutionCleanupMonitor {

    public static final String VDK_DATAJOB_EXECUTION_CLEANUP_METRIC_NAME = "vdk.execution.cleanup.task.datajob.status";

    private final MeterRegistry meterRegistry;

    private final Integer GAUGE_SUCCESS_METRIC_VALUE = 0;
    private final Integer GAUGE_FAILURE_METRIC_VALUE = 1;

    private final String TAG_DATA_JOB = "data_job_name";
    private final String TAG_TEAM = "data_job_team";
    private final String TAG_LATEST_DELETED_EXECUTIONS_NUMBER = "latest_datajob_execution_cleanups_number";
    private final String TAG_LATEST_EXECUTION_CLEANUP_STATUS = "latest_datajob_execution_cleanup_status_success";

    private final Map<String, Gauge> cleanupGauges = new ConcurrentHashMap<>();
    private final Map<String, Integer> cleanupStatuses = new ConcurrentHashMap<>();

    /**
     * Creates a gauge for a failed execution cleanup
     * and registers it with the meter registry.
     *
     * @param dataJob
     */
    public void addFailedGauge(final DataJob dataJob) {
        // Set deleted executions to 0 in case of failure.
        addGauge(dataJob, 0, GAUGE_FAILURE_METRIC_VALUE, false);
    }

    /**
     * Creates a gauge for a successful execution cleanup
     * and registers it with the meter registry.
     *
     * @param dataJob
     * @param deletedExecutions
     */
    public void addSuccessfulGauge(final DataJob dataJob, int deletedExecutions) {
        addGauge(dataJob, deletedExecutions, GAUGE_SUCCESS_METRIC_VALUE, true);
    }

    private void addGauge(final DataJob dataJob, int deletedExecutions, int gaugeStatus, boolean isCleanupSuccess) {
        try {

            Objects.requireNonNull(dataJob);
            Objects.requireNonNull(dataJob.getJobConfig());
            Objects.requireNonNull(dataJob.getName());

            var dataJobName = dataJob.getName();
            var oldGauge = cleanupGauges.getOrDefault(dataJobName, null);
            var newTags = createStatusGaugeTags(dataJob, deletedExecutions, isCleanupSuccess);
            // the only way to update a gauge is to delete it and create a new one.
            if (shouldDeleteGaugeBeforeCreation(oldGauge, newTags)) {
                cleanupStatuses.remove(dataJobName);
                removeGauge(dataJobName, cleanupGauges);
            }

            cleanupStatuses.put(dataJobName, gaugeStatus);
            cleanupGauges.put(dataJobName, createStatusGauge(dataJobName, newTags, cleanupStatuses));
        } catch (Exception e) {
            log.warn("Execution cleanup monitoring failed with error: {}", e);
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

    private Tags createStatusGaugeTags(final DataJob dataJob, int successfulCleanups, boolean cleanUpStatus) {
        return Tags.of(
                TAG_DATA_JOB, dataJob.getName(),
                TAG_TEAM, StringUtils.defaultString(dataJob.getJobConfig().getTeam()),
                TAG_LATEST_EXECUTION_CLEANUP_STATUS, Boolean.toString(cleanUpStatus),
                TAG_LATEST_DELETED_EXECUTIONS_NUMBER, Integer.toString(successfulCleanups));
    }

    private Gauge createStatusGauge(final String dataJobName, final Tags tags, final Map<String, Integer> statusMap) {
        var gauge = Gauge.builder(VDK_DATAJOB_EXECUTION_CLEANUP_METRIC_NAME, statusMap,
                        map -> map.getOrDefault(dataJobName, GAUGE_SUCCESS_METRIC_VALUE))
                .tags(tags)
                .description("Cleanup status of data job executions: (0 - Success, 1 - Failure to Delete executions)")
                .register(meterRegistry);
        log.info("The cleanup status gauge for data job {} 's executions was created", dataJobName);
        return gauge;
    }

    private boolean shouldDeleteGaugeBeforeCreation(final Gauge gauge, final Tags newTags) {
        if (gauge == null) {
            return false;
        }

        var existingTags = gauge.getId().getTags();
        return !newTags.stream().allMatch(existingTags::contains);
    }

}
