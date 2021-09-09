/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.JobsRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class DataJobInfoMonitorSync {

   private final DataJobInfoMonitor dataJobInfoMonitor;

   private final JobsRepository jobsRepository;

   @Autowired
   public DataJobInfoMonitorSync(DataJobInfoMonitor dataJobInfoMonitor, JobsRepository jobsRepository) {
      this.dataJobInfoMonitor = dataJobInfoMonitor;
      this.jobsRepository = jobsRepository;
   }

   @Scheduled(
         fixedDelayString = "${datajobs.monitoring.sync.interval}",
         initialDelayString = "${datajobs.monitoring.sync.initial.delay}")
   public void updateDataJobInfo() {
      if (!dataJobInfoMonitor.updateDataJobsInfo(jobsRepository::findAll)) {
         log.debug("There are no data jobs");
      }
   }
}
