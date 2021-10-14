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
public class DataJobStatusMonitorSync {

    private final DataJobStatusMonitor dataJobStatusMonitor;
    private final JobsRepository jobsRepository;

    @Autowired
    public DataJobStatusMonitorSync(DataJobStatusMonitor dataJobStatusMonitor, JobsRepository jobsRepository) {
        this.dataJobStatusMonitor = dataJobStatusMonitor;
        this.jobsRepository = jobsRepository;
    }

    @Scheduled(
            fixedDelayString = "${datajobs.monitoring.sync.interval:5000}",
            initialDelayString = "${datajobs.monitoring.sync.initial.delay:10000}")
    public void updateDataJobStatus() {
        dataJobStatusMonitor.updateDataJobsTerminationStatus(jobsRepository.findAll());
    }
}
