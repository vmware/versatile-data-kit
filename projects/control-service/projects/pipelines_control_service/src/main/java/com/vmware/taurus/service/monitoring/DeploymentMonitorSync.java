/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Iterator;

@Component
@EnableAsync
public class DeploymentMonitorSync {

  static Logger log = LoggerFactory.getLogger(DeploymentMonitorSync.class);

  @Autowired private final DeploymentMonitor deploymentMonitor;

  @Autowired private final JobsRepository jobsRepository;

  @Autowired
  public DeploymentMonitorSync(DeploymentMonitor deploymentMonitor, JobsRepository jobsRepository) {
    this.deploymentMonitor = deploymentMonitor;
    this.jobsRepository = jobsRepository;
  }

  @Async
  @Scheduled(
      fixedDelayString = "${datajobs.monitoring.sync.interval}",
      initialDelayString = "${datajobs.monitoring.sync.initial.delay}")
  public void updateJobDeploymentStatuses() {
    // TODO: Potentially we can create custom query if this is not optimal.
    Iterator<DataJob> dataJobs = jobsRepository.findAll().iterator();

    if (!dataJobs.hasNext()) {
      log.debug("There are no data jobs");
    } else {
      while (dataJobs.hasNext()) {
        DataJob dataJob = dataJobs.next();
        var status = dataJob.getLatestJobDeploymentStatus();
        if (status != null) {
          if (!status.equals(DeploymentStatus.NONE)) {
            String jobName = dataJob.getName();
            DeploymentStatus latestDeploymentStatus = dataJob.getLatestJobDeploymentStatus();
            deploymentMonitor.updateDataJobStatus(jobName, latestDeploymentStatus);
          } else {
            log.trace("Data job: {} has no deployment process started yet", dataJob.getName());
          }
        } else {
          log.debug("Data job: {} has no status", dataJob.getName());
        }
      }
    }
  }
}
