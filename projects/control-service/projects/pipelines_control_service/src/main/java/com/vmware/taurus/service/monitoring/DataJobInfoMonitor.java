/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.model.DataJob;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Objects;

@Slf4j
@Component
public class DataJobInfoMonitor {
   private final DataJobMetrics dataJobMetrics;

   @Autowired
   public DataJobInfoMonitor(DataJobMetrics dataJobMetrics) {
      this.dataJobMetrics = dataJobMetrics;
   }

   /**
    * Creates a gauge to expose information about the specified data job.
    * If a gauge already exists for the job, it is updated if necessary.
    *
    * @param dataJob The data job for which to create or update a gauge.
    */
   public void updateDataJobInfo(final DataJob dataJob) {
      Objects.requireNonNull(dataJob);

      dataJobMetrics.updateInfoGauges(dataJob);
   }

   /**
    * Creates a gauge to expose information about each of the specified data jobs.
    *
    * @param dataJobs The data jobs for which to create or update gauges.
    */
   public void updateDataJobsInfo(final Iterable<DataJob> dataJobs) {
      Objects.requireNonNull(dataJobs);

      dataJobs.forEach(this::updateDataJobInfo);
   }
}
