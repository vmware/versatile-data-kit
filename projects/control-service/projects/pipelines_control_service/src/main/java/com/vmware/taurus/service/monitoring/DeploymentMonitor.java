/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import io.micrometer.core.instrument.DistributionSummary;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Tags;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class DeploymentMonitor {

  static Logger log = LoggerFactory.getLogger(DeploymentMonitor.class);

  public static String GAUGE_METRIC_NAME = "taurus.deployment.status.gauge";

  public static String SUMMARY_METRIC_NAME = "taurus.deployment.status.summary";

  private final MeterRegistry meterRegistry;

  private final JobsRepository jobsRepository;

  private final ActualJobDeploymentRepository actualJobDeploymentRepository;

  private final Map<String, Integer> currentStatuses = new ConcurrentHashMap<>();

  @Autowired
  public DeploymentMonitor(
      MeterRegistry meterRegistry,
      JobsRepository jobsRepository,
      ActualJobDeploymentRepository actualJobDeploymentRepository) {
    this.meterRegistry = meterRegistry;
    this.jobsRepository = jobsRepository;
    this.actualJobDeploymentRepository = actualJobDeploymentRepository;
  }

  /**
   * Updates the current deployment status of a data job
   *
   * @param dataJob
   * @param deploymentStatus
   */
  public void updateDataJobStatus(String dataJob, DeploymentStatus deploymentStatus) {
    if (!currentStatuses.containsKey(dataJob)) {
      Tags tags = Tags.of("dataJob", dataJob);
      Gauge.builder(GAUGE_METRIC_NAME, currentStatuses, map -> map.getOrDefault(dataJob, 0))
          .tags(tags)
          .register(meterRegistry);
    }
    currentStatuses.put(dataJob, deploymentStatus.getValue());
  }

  /**
   * Records and persists a deployment event of a data job
   *
   * @param dataJobName
   * @param deploymentStatus
   */
  public void recordDeploymentStatus(
      String dataJobName,
      DeploymentStatus deploymentStatus,
      ActualDataJobDeployment actualDataJobDeployment) {
    if (StringUtils.isNotBlank(dataJobName)) {
      boolean jobExists = saveDataJobStatus(dataJobName, deploymentStatus, actualDataJobDeployment);
      if (jobExists || currentStatuses.containsKey(dataJobName)) {
        // TODO: Add tag for data job mode
        DistributionSummary.builder(SUMMARY_METRIC_NAME)
            .tag("dataJob", dataJobName)
            .tag("status", deploymentStatus.toString())
            .register(meterRegistry)
            .record(1);
        updateDataJobStatus(dataJobName, deploymentStatus);
      }
    } else {
      log.warn("Data job name is empty.");
    }
  }

  private boolean saveDataJobStatus(
      final String dataJobName,
      final DeploymentStatus deploymentStatus,
      ActualDataJobDeployment actualDataJobDeployment) {
    if (jobsRepository.updateDataJobLatestJobDeploymentStatusByName(dataJobName, deploymentStatus)
        > 0) {
      switch (deploymentStatus) {
        case SUCCESS:
          if (actualDataJobDeployment != null) {
            actualJobDeploymentRepository.save(actualDataJobDeployment);
          }
      }
      return true;
    }
    log.debug("Data job: {} was deleted or hasn't been created", dataJobName);
    return false;
  }
}
