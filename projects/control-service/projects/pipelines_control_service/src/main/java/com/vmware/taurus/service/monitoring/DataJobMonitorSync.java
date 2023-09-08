/*
 * Copyright 2021-2023 VMware, Inc.
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
public class DataJobMonitorSync {

  private final DataJobMonitor dataJobMonitor;
  private final JobsRepository jobsRepository;

  @Autowired
  public DataJobMonitorSync(DataJobMonitor dataJobMonitor, JobsRepository jobsRepository) {
    this.dataJobMonitor = dataJobMonitor;
    this.jobsRepository = jobsRepository;
  }

  @Scheduled(
      fixedDelayString = "${datajobs.monitoring.sync.interval:5000}",
      initialDelayString = "${datajobs.monitoring.sync.initial.delay:10000}")
  public void updateDataJobStatus() {
    final var dataJobs = jobsRepository.findAll();
    dataJobMonitor.updateDataJobsGauges(dataJobs);
    dataJobMonitor.clearDataJobsGaugesNotIn(dataJobs);
  }
}
