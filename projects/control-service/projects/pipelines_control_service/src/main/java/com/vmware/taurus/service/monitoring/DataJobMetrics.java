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
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import static com.vmware.taurus.service.Utilities.join;

/** This class manages data job monitoring metrics exposed by the service. */
@Slf4j
@Component
public class DataJobMetrics {
    public static final String TAURUS_DATAJOB_INFO_METRIC_NAME = "taurus.datajob.info";
    public static final String TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME = "taurus.datajob.notification.delay";
    public static final String TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME = "taurus.datajob.termination.status";
    public static final String TAURUS_DATAJOB_TERMINATION_STATUS_COUNTER_NAME = "taurus.datajob.termination.status.counter";
    public static final String TAURUS_DATAJOB_WATCH_TASK_INVOCATIONS_COUNTER_NAME = "taurus.datajob.watch.task.invocations.counter";
    public static final String TAG_DATA_JOB = "data_job";
    public static final String TAG_EXECUTION_ID = "execution_id";
    public static final String TAG_TEAM = "team";
    public static final String TAG_STATUS = "status";
    public static final String TAG_EMAIL_NOTIFIED_ON_SUCCESS = "email_notified_on_success";
    public static final String TAG_EMAIL_NOTIFIED_ON_USER_ERROR = "email_notified_on_user_error";
    public static final String TAG_EMAIL_NOTIFIED_ON_PLATFORM_ERROR = "email_notified_on_platform_error";

    public static final Integer GAUGE_METRIC_VALUE = 1;
    public static final int DEFAULT_NOTIFICATION_DELAY_PERIOD_MINUTES = 240;

    private final MeterRegistry meterRegistry;
    private final Counter watchTaskInvocationsCounter;
    private final Map<String, Gauge> infoGauges = new ConcurrentHashMap<>();
    private final Map<String, Gauge> delayGauges = new ConcurrentHashMap<>();
    private final Map<String, Gauge> statusGauges = new ConcurrentHashMap<>();
    private final Map<String, Counter> statusCounters = new ConcurrentHashMap<>();
    private final Map<String, Integer> currentDelays = new ConcurrentHashMap<>();
    private final Map<String, Integer> currentStatuses = new ConcurrentHashMap<>();

    @Autowired
    public DataJobMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;

        watchTaskInvocationsCounter = Counter.builder(TAURUS_DATAJOB_WATCH_TASK_INVOCATIONS_COUNTER_NAME)
                .description("Counts the number of times the data jobs watching task is called.")
                .register(this.meterRegistry);
    }

    /**
     * Increments the counter used to track the number of times the {@link DataJobMonitor#watchJobs} method was invoked.
     */
    public void incrementWatchTaskInvocations() {
        try {
            watchTaskInvocationsCounter.increment();
        } catch (Exception e) {
            log.warn("Error while trying to increment counter.", e);
        }
    }

    /**
     * Creates a "taurus.datajob.info" and a "taurus.datajob.notification.delay" gauge for the specified data job
     * if they do not exist. If a gauge already exists, but it has different tags, the existing gauge is deleted
     * and a new one is created. If the data job does not have a configuration, no gauges are created.
     *
     * @param dataJob The data job for which to update the gauges.
     */
    public void updateInfoGauges(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        updateInfoGauge(dataJob);
        updateNotificationDelayGauge(dataJob);
    }

    /**
     * Creates a "taurus.datajob.info" gauge for the specified data job if one does not exist.
     * If a gauge already exists, but it has different tags, the existing gauge is deleted and a new one is created.
     * If the data job does not have a configuration, no gauge is created.
     *
     * @param dataJob The data job for which to update the gauge.
     */
    private void updateInfoGauge(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        try {
            var dataJobName = dataJob.getName();
            if (dataJob.getJobConfig() == null) {
                log.debug("The data job {} does not have configuration", dataJobName);
                return;
            }

            var gauge = infoGauges.getOrDefault(dataJobName, null);
            var newTags = createInfoGaugeTags(dataJob);
            if (isGaugeChanged(gauge, newTags)) {
                log.info("The configuration of data job {} has changed", dataJobName);
                removeInfoGauge(dataJobName);
            }

            infoGauges.computeIfAbsent(dataJobName, name -> createInfoGauge(name, newTags));
        } catch (Exception e) {
            log.warn("An exception occurred while updating the info gauge of data job {}", dataJob.getName(), e);
        }
    }

    /**
     * Creates a "taurus.datajob.notification.delay" gauge for the specified data job if one does not exist.
     * If a gauge already exists, its value is updated.
     * If the data job does not have a configuration, no gauge is created.
     *
     * @param dataJob The data job for which to update the gauge.
     */
    private void updateNotificationDelayGauge(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        try {
            var dataJobName = dataJob.getName();
            if (dataJob.getJobConfig() == null) {
                log.debug("The data job {} does not have configuration", dataJobName);
                return;
            }

            currentDelays.put(dataJobName,
                    Optional.ofNullable(dataJob.getJobConfig().getNotificationDelayPeriodMinutes()).orElse(DEFAULT_NOTIFICATION_DELAY_PERIOD_MINUTES));
            delayGauges.computeIfAbsent(dataJobName, this::createNotificationDelayGauge);
        } catch (Exception e) {
            log.warn("An exception occurred while updating the notification delay gauge of data job {}", dataJob.getName(), e);
        }
    }

    /**
     * Creates a "taurus.datajob.termination.status" gauge for the specified data job if one does not exist.
     * If a gauge already exists, its value is updated.
     *
     * @param dataJob The data job for which to update the gauge.
     */
    public void updateTerminationStatusGauge(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        try {
            var dataJobName = dataJob.getName();
            var gauge = statusGauges.getOrDefault(dataJobName, null);
            var newTags = createStatusGaugeTags(dataJob);
            if (isGaugeChanged(gauge, newTags)) {
                log.info("The last termination status of data job {} has changed", dataJobName);
                removeTerminationStatusGauge(dataJobName);
            }

            Integer previousTerminationStatus = currentStatuses.get(dataJobName);
            Integer newTerminationStatus = dataJob.getLatestJobTerminationStatus().getAlertValue();
            currentStatuses.put(dataJobName, newTerminationStatus);
            statusGauges.computeIfAbsent(dataJobName, name -> createTerminationStatusGauge(name, newTags));
            if (!Objects.equals(previousTerminationStatus, newTerminationStatus)) {
                log.debug("The termination status gauge value for data job {} with execution {} was changed from {} to {}",
                        dataJobName, dataJob.getLatestJobExecutionId(), previousTerminationStatus, newTerminationStatus);
            }
        } catch (Exception e) {
            log.warn("An exception occurred while updating the termination status gauge of data job {}", dataJob.getName(), e);
        }
    }

    /**
     * Creates a "taurus.datajob.termination.status.counter" counter for the specified
     * data job and execution status, if one does not exist. If a counter already
     * exists, its value is incremented.
     *
     * @param dataJob The data job for which to increment the counter.
     * */
    public void incrementTerminationStatusCounter(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        try {
            var dataJobName = dataJob.getName();
            var dataJobStatus = dataJob.getLatestJobTerminationStatus().getAlertValue().toString();
            var jobStatusKey = dataJobName + "__" + dataJobStatus;
            var counter = statusCounters.getOrDefault(jobStatusKey, null);
            var tags = createStatusCounterTags(dataJob);

            if (counter == null) {
                statusCounters.computeIfAbsent(jobStatusKey, name -> createTerminationStatusCounter(dataJobName, tags, dataJobStatus));
            } else {
                counter.increment();
            }
        } catch (Exception e) {
            log.warn("An exception occurred while incrementing the termination status counter of data job {} and status {}", dataJob.getName(), dataJob.getLatestJobTerminationStatus().getAlertValue().toString());
        }
    }

    /**
     * Removes all gauges associated with the specified data job.
     *
     * @param dataJobName The name of the data job for which to clear all gauges.
     */
    public void clearGauges(final String dataJobName) {
        removeInfoGauge(dataJobName);
      }

      infoGauges.computeIfAbsent(dataJobName, name -> createInfoGauge(name, newTags));
    } catch (Exception e) {
      log.warn(
          "An exception occurred while updating the info gauge of data job {}",
          dataJob.getName(),
          e);
    }

    /**
     * Removes all counters associated with the specified data job.
     *
     * @param dataJobName The name of the data job for which to clear all counters.
     */
    public void clearCounters(final String dataJobName) {
        removeTerminationStatusCounters(dataJobName);
    }

    /**
     * Removes all gauges associated with data jobs that are not present in the specified iterable.
     *
     * @param dataJobNames The names of the data jobs which will still have gauges.
     */
    public void clearGaugesNotIn(final Set<String> dataJobNames) {
        var absentEntries = filterByKeyNotIn(infoGauges, dataJobNames);
        absentEntries.forEach(e -> removeInfoGauge(e.getKey()));

        absentEntries = filterByKeyNotIn(delayGauges, dataJobNames);
        absentEntries.forEach(e -> removeNotificationDelayGauge(e.getKey()));

        absentEntries = filterByKeyNotIn(statusGauges, dataJobNames);
        absentEntries.forEach(e -> removeTerminationStatusGauge(e.getKey()));
    }

    /**
     * Returns a list consisting of the entries of the specified map, that do not have their keys in the specified set.
     *
     * @param from The map to filter.
     * @param set A set containing keys for the elements that should <b>NOT</b> be returned.
     * @return A list of all Map.Entry objects with keys inside {@code set}.
     */
    private <K> List<Map.Entry<K, ?>> filterByKeyNotIn(final Map<K, ?> from, final Set<K> set) {
        return from.entrySet().stream()
                .filter(e -> !set.contains(e.getKey()))
                .collect(Collectors.toList());
    }

    private Gauge createInfoGauge(final String dataJobName, final Tags tags) {
        var gauge = Gauge.builder(TAURUS_DATAJOB_INFO_METRIC_NAME, GAUGE_METRIC_VALUE, value -> value)
                .tags(tags)
                .description("Info about data jobs")
                .register(meterRegistry);
        log.info("The info gauge for data job {} was created", dataJobName);
        return gauge;
    }
  }

  /**
   * Creates a "taurus.datajob.termination.status" gauge for the specified data job if one does not
   * exist. If a gauge already exists, its value is updated.
   *
   * @param dataJob The data job for which to update the gauge.
   */
  public void updateTerminationStatusGauge(final DataJob dataJob) {
    Objects.requireNonNull(dataJob);

    try {
      var dataJobName = dataJob.getName();
      var gauge = statusGauges.getOrDefault(dataJobName, null);
      var newTags = createStatusGaugeTags(dataJob);
      if (isGaugeChanged(gauge, newTags)) {
        log.info("The last termination status of data job {} has changed", dataJobName);
        removeTerminationStatusGauge(dataJobName);
      }

      Integer previousTerminationStatus = currentStatuses.get(dataJobName);
      Integer newTerminationStatus = dataJob.getLatestJobTerminationStatus().getAlertValue();
      currentStatuses.put(dataJobName, newTerminationStatus);
      statusGauges.computeIfAbsent(
          dataJobName, name -> createTerminationStatusGauge(name, newTags));
      if (!Objects.equals(previousTerminationStatus, newTerminationStatus)) {
        log.debug(
            "The termination status gauge value for data job {} with execution {} was changed from"
                + " {} to {}",
            dataJobName,
            dataJob.getLatestJobExecutionId(),
            previousTerminationStatus,
            newTerminationStatus);
      }
    } catch (Exception e) {
      log.warn(
          "An exception occurred while updating the termination status gauge of data job {}",
          dataJob.getName(),
          e);
    }
  }

  /**
   * Removes all gauges associated with the specified data job.
   *
   * @param dataJobName The name of the data job for which to clear all gauges.
   */
  public void clearGauges(final String dataJobName) {
    removeInfoGauge(dataJobName);
    removeNotificationDelayGauge(dataJobName);
    removeTerminationStatusGauge(dataJobName);
  }

  /**
   * Removes all gauges associated with data jobs that are not present in the specified iterable.
   *
   * @param dataJobNames The names of the data jobs which will still have gauges.
   */
  public void clearGaugesNotIn(final Set<String> dataJobNames) {
    var absentEntries = filterByKeyNotIn(infoGauges, dataJobNames);
    absentEntries.forEach(e -> removeInfoGauge(e.getKey()));

    absentEntries = filterByKeyNotIn(delayGauges, dataJobNames);
    absentEntries.forEach(e -> removeNotificationDelayGauge(e.getKey()));

    absentEntries = filterByKeyNotIn(statusGauges, dataJobNames);
    absentEntries.forEach(e -> removeTerminationStatusGauge(e.getKey()));
  }

  /**
   * Returns a list consisting of the entries of the specified map, that do not have their keys in
   * the specified set.
   *
   * @param from The map to filter.
   * @param set A set containing keys for the elements that should <b>NOT</b> be returned.
   * @return A list of all Map.Entry objects with keys inside {@code set}.
   */
  private <K> List<Map.Entry<K, ?>> filterByKeyNotIn(final Map<K, ?> from, final Set<K> set) {
    return from.entrySet().stream()
        .filter(e -> !set.contains(e.getKey()))
        .collect(Collectors.toList());
  }

  private Gauge createInfoGauge(final String dataJobName, final Tags tags) {
    var gauge =
        Gauge.builder(TAURUS_DATAJOB_INFO_METRIC_NAME, GAUGE_METRIC_VALUE, value -> value)
            .tags(tags)
            .description("Info about data jobs")
            .register(meterRegistry);
    log.info("The info gauge for data job {} was created", dataJobName);
    return gauge;
  }

  private void removeInfoGauge(final String dataJobName) {
    try {
      if (StringUtils.isNotBlank(dataJobName)) {
        var gauge = infoGauges.getOrDefault(dataJobName, null);
        if (gauge != null) {
          meterRegistry.remove(gauge);
          infoGauges.remove(dataJobName);
          log.info("The info gauge for data job {} was removed", dataJobName);
        } else {
          log.info(
              "The info gauge for data job {} cannot be removed: gauge not found", dataJobName);
        }
      } else {
        log.warn("The info gauge cannot be removed: data job name is empty");
      }
    } catch (Exception e) {
      log.warn(
          "An exception occurred while removing the info gauge of data job {}", dataJobName, e);
    }
  }

  private Gauge createNotificationDelayGauge(final String dataJobName) {
    var gauge =
        Gauge.builder(
                TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME,
                currentDelays,
                map -> map.getOrDefault(dataJobName, 0))
            .tags(Tags.of(TAG_DATA_JOB, dataJobName))
            .description(
                "The time (in minutes) a job execution is allowed to be delayed from its schedule"
                    + " before an alert is triggered")
            .register(meterRegistry);
    log.info("The notification delay gauge for data job {} was created", dataJobName);
    return gauge;
  }

  private void removeNotificationDelayGauge(final String dataJobName) {
    try {
      if (StringUtils.isNotBlank(dataJobName)) {
        var gauge = delayGauges.getOrDefault(dataJobName, null);
        if (gauge != null) {
          meterRegistry.remove(gauge);
          delayGauges.remove(dataJobName);
          currentDelays.remove(dataJobName);
          log.info("The notification delay gauge for data job {} was removed", dataJobName);
        } else {
          log.info(
              "The notification delay gauge for data job {} cannot be removed: gauge not found",
              dataJobName);
        }
      } else {
        log.warn("The notification delay gauge cannot be removed: data job name is empty");
      }
    } catch (Exception e) {
      log.warn(
          "An exception occurred while removing the notification delay gauge of data job {}",
          dataJobName,
          e);
    }

    private Counter createTerminationStatusCounter(final String dataJobName, final Tags tags, final String status) {
        var counter = Counter.builder(TAURUS_DATAJOB_TERMINATION_STATUS_COUNTER_NAME)
                .description("Counts the number of specific statuses per job")
                .tags(tags)
                .register(meterRegistry);
        counter.increment();
        log.info("Counter for data job {} and status {} was created.", dataJobName, status);
        return counter;
    }

    /**
     * Removes all termination status counters associated with a data job.
     * Status counters for each data job are stored in the statusCounters
     * hash map, in the form:
     *    `<data-job-name>__<execution-status> : <counter-object>`
     * and we need to iterate over the hash map, in order to find all instances
     * that need to be removed.
     *
     * @param dataJobName the name of the data job
     * */
    private void removeTerminationStatusCounters(final String dataJobName) {
        try {
            if (StringUtils.isNotBlank(dataJobName)) {
                Set<String> toBeDeleted = new HashSet<>();
                String filter = dataJobName + "__";

                for (Map.Entry<String, Counter> pair : statusCounters.entrySet()) {
                    if (pair.getKey().contains(filter)) {
                        toBeDeleted.add(pair.getKey());
                    }
                }

                if (!toBeDeleted.isEmpty()) {
                    for (String key : toBeDeleted) {
                        var counter = statusCounters.getOrDefault(key, null);
                        meterRegistry.remove(counter);
                        statusCounters.remove(key);
                    }
                } else {
                    log.info("No termination status counters found for data job: {}", dataJobName);
                }
            } else {
                log.warn("The termination status counters cannot be removed: data job name is empty.");
            }
        } catch (Exception e) {
            log.warn("An exception occurred while removing a termination status counter of data job {}", dataJobName);
        }
    }

    private boolean isGaugeChanged(final Gauge gauge, final Tags newTags) {
        if (gauge == null) {
            return false;
        }
      } else {
        log.warn("The termination status gauge cannot be removed: data job name is empty");
      }
    } catch (Exception e) {
      log.warn(
          "An exception occurred while removing the termination status gauge of data job {}",
          dataJobName,
          e);
    }
  }

  private boolean isGaugeChanged(final Gauge gauge, final Tags newTags) {
    if (gauge == null) {
      return false;
    }

    private Tags createStatusGaugeTags(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        return Tags.of(
                TAG_DATA_JOB, dataJob.getName(),
                TAG_EXECUTION_ID, dataJob.getLatestJobExecutionId());
    }

    private Tags createStatusCounterTags(final DataJob dataJob) {
        Objects.requireNonNull(dataJob);

        return Tags.of(
                TAG_DATA_JOB, dataJob.getName(),
                TAG_TEAM, Objects.requireNonNullElse(dataJob.getJobConfig().getTeam(), "none"),
                TAG_STATUS, dataJob.getLatestJobTerminationStatus().getAlertValue().toString()
        );
    }
}
