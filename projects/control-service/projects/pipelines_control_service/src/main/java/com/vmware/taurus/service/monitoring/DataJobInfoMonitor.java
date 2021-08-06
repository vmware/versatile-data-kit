/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.model.DataJob;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.function.Supplier;

import static com.vmware.taurus.service.Utilities.join;

@Slf4j
@Component
public class DataJobInfoMonitor {

   public static final String TAURUS_DATAJOB_INFO_METRIC_NAME = "taurus.datajob.info";
   public static final String TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME = "taurus.datajob.notification.delay";
   public static final Integer GAUGE_METRIC_VALUE = 1;
   public static final int DEFAULT_NOTIFICATION_DELAY_PERIOD_MINUTES = 240;

   private final MeterRegistry meterRegistry;

   private final Map<String, Gauge> infoGauges = new ConcurrentHashMap<>();
   private final ReentrantLock lock = new ReentrantLock(true);
   private final Map<String, Integer> currentDelays = new ConcurrentHashMap<>();

   @Autowired
   public DataJobInfoMonitor(MeterRegistry meterRegistry) {
      this.meterRegistry = meterRegistry;
   }

   /**
    * Creates a gauge to expose information about the specified data job.
    * If a gauge already exists for the job, it is updated if necessary.
    * <p>
    * This method is synchronized.
    *
    * @param dataJobSupplier A supplier of the data job for which to create or update a gauge.
    * @return true if the supplier produced a job; otherwise, false.
    */
   public boolean updateDataJobInfo(final Supplier<DataJob> dataJobSupplier) {
      return updateDataJobsInfo(() -> {
         final var dataJob = Objects.requireNonNullElse(dataJobSupplier, () -> null).get();
         return dataJob == null ? Collections.emptyList() : Collections.singletonList(dataJob);
      });
   }

   /**
    * Creates a gauge to expose information about each of the specified data jobs.
    * If a gauge already exists for any of the jobs, it is updated if necessary.
    * <p>
    * This method is synchronized.
    *
    * @param dataJobsSupplier A supplier of the data jobs for which to create or update gauges.
    * @return true if the supplier produced at least one job; otherwise, false.
    */
   public boolean updateDataJobsInfo(final Supplier<Iterable<DataJob>> dataJobsSupplier) {
      lock.lock();
      try {
         var dataJobs = Objects.requireNonNullElse(dataJobsSupplier, Collections::emptyList).get().iterator();
         if (!dataJobs.hasNext()) {
            return false;
         }

         dataJobs.forEachRemaining(dataJob -> {
            if (dataJob == null) {
               log.warn("The data job is null");
               return;
            }

            var dataJobName = dataJob.getName();
            if (dataJob.getJobConfig() == null) {
               log.debug("The data job {} does not have configuration", dataJobName);
               return;
            }

            var gauge = infoGauges.getOrDefault(dataJobName, null);
            var newTags = createGaugeTags(dataJob);
            if (isChanged(gauge, newTags)) {
               log.info("The configuration of data job {} has changed", dataJobName);
               removeGauge(dataJobName);
            }

            if (!infoGauges.containsKey(dataJobName)) {
               gauge = createInfoGauge(newTags);
               infoGauges.put(dataJobName, gauge);
               log.info("The info gauge for data job {} was created", dataJobName);
            }

            if (!currentDelays.containsKey(dataJobName)) {
               createNotificationDelayGauge(dataJobName);
               log.info("The notification delay gauge for data job {} was created", dataJobName);
            }
            currentDelays.put(dataJobName,
                    Optional.ofNullable(dataJob.getJobConfig().getNotificationDelayPeriodMinutes()).orElse(DEFAULT_NOTIFICATION_DELAY_PERIOD_MINUTES));
         });

         return true;
      } finally {
         lock.unlock();
      }
   }

   /**
    * Removes the gauge associated with the specified data job.
    * <p>
    * This method is synchronized.
    *
    * @param dataJobNameSupplier A supplier of the name of the data job whose gauge is to be removed.
    */
   public void removeDataJobInfo(final Supplier<String> dataJobNameSupplier) {
      lock.lock();
      try {
         final var jobName = Objects.requireNonNullElse(dataJobNameSupplier, () -> null).get();
         removeGauge(jobName);
      } finally {
         lock.unlock();
      }
   }

   private void removeGauge(final String dataJobName) {
      if (StringUtils.isNotBlank(dataJobName)) {
         var gauge = infoGauges.getOrDefault(dataJobName, null);
         if (gauge != null) {
            meterRegistry.remove(gauge);
            infoGauges.remove(dataJobName);
            log.info("The info gauge for data job {} was removed", dataJobName);
         }
      } else {
         log.warn("Data job name is empty");
      }
   }

   private boolean isChanged(final Gauge gauge, final Tags newTags) {
      if (gauge == null) {
         return false;
      }

      var existingTags = gauge.getId().getTags();
      return !newTags.stream().allMatch(existingTags::contains);
   }

   private Gauge createInfoGauge(final Tags tags) {
      return Gauge.builder(TAURUS_DATAJOB_INFO_METRIC_NAME, GAUGE_METRIC_VALUE, value -> value)
            .tags(tags)
            .description("Info about data jobs")
            .register(meterRegistry);
   }

   private void createNotificationDelayGauge(final String dataJobName) {
      Gauge.builder(TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME, currentDelays,
              map -> map.getOrDefault(dataJobName, 0))
              .tags(Tags.of("data_job", dataJobName))
              .description("The time (in minutes) a job execution is allowed to be delayed from its schedule before an alert is triggered")
              .register(meterRegistry);
   }

   private Tags createGaugeTags(final DataJob dataJob) {
      Objects.requireNonNull(dataJob);
      var jobConfig = dataJob.getJobConfig();
      boolean enableExecutionNotifications = jobConfig.getEnableExecutionNotifications() == null ||
              jobConfig.getEnableExecutionNotifications();
      return Tags.of(
            "data_job", dataJob.getName(),
            "team", StringUtils.defaultString(jobConfig.getTeam()),
            "email_notified_on_success", enableExecutionNotifications ?
                      join(jobConfig.getNotifiedOnJobSuccess()) : "",
            "email_notified_on_user_error", enableExecutionNotifications ?
                      join(jobConfig.getNotifiedOnJobFailureUserError()) : "",
            "email_notified_on_platform_error", enableExecutionNotifications ?
                      join(jobConfig.getNotifiedOnJobFailurePlatformError()) : "");
   }
}
