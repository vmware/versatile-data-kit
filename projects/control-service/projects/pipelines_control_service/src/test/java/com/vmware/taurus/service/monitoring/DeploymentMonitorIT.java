/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit.jupiter.SpringExtension;

@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DeploymentMonitorIT {

  @Autowired private MeterRegistry meterRegistry;

  @Autowired private JobsRepository jobsRepository;

  @Autowired private DeploymentMonitor deploymentMonitor;

  @Test
  @Order(1)
  public void testRecordDeploymentStatusExistingJob() {
    JobConfig config = new JobConfig();
    config.setSchedule("schedule");
    var entity = new DataJob("data-job", config, DeploymentStatus.NONE);
    jobsRepository.save(entity);

    deploymentMonitor.recordDeploymentStatus("data-job", DeploymentStatus.SUCCESS);

    var gauges = meterRegistry.find(DeploymentMonitor.GAUGE_METRIC_NAME).gauges();
    var summaries = meterRegistry.find(DeploymentMonitor.SUMMARY_METRIC_NAME).summaries();

    Assertions.assertEquals(1, gauges.size());
    Assertions.assertEquals(1, summaries.size());

    DataJob expectedJob = jobsRepository.findById("data-job").get();

    Assertions.assertEquals(expectedJob.getLatestJobDeploymentStatus(), DeploymentStatus.SUCCESS);
  }

  @Test
  @Order(2)
  public void testUpdateDeploymentStatusExistingJob() {

    deploymentMonitor.recordDeploymentStatus("data-job", DeploymentStatus.PLATFORM_ERROR);

    var gauges = meterRegistry.find(DeploymentMonitor.GAUGE_METRIC_NAME).gauges();
    var summaries = meterRegistry.find(DeploymentMonitor.SUMMARY_METRIC_NAME).summaries();

    Assertions.assertEquals(1, gauges.size());
    Assertions.assertEquals(2, summaries.size());

    DataJob expectedJob = jobsRepository.findById("data-job").get();

    Assertions.assertEquals(
        expectedJob.getLatestJobDeploymentStatus(), DeploymentStatus.PLATFORM_ERROR);
  }

  @Test
  @Order(3)
  public void testJobNameNull() {

    deploymentMonitor.recordDeploymentStatus(null, DeploymentStatus.PLATFORM_ERROR);

    var gauges = meterRegistry.find(DeploymentMonitor.GAUGE_METRIC_NAME).gauges();
    var summaries = meterRegistry.find(DeploymentMonitor.SUMMARY_METRIC_NAME).summaries();

    Assertions.assertEquals(1, gauges.size());
    Assertions.assertEquals(2, summaries.size());

    DataJob expectedJob = jobsRepository.findById("data-job").get();

    Assertions.assertEquals(
        DeploymentStatus.PLATFORM_ERROR, expectedJob.getLatestJobDeploymentStatus());
  }

  @Test
  @Order(4)
  public void testJobNameEmpty() {

    deploymentMonitor.recordDeploymentStatus("", DeploymentStatus.PLATFORM_ERROR);

    var gauges = meterRegistry.find(DeploymentMonitor.GAUGE_METRIC_NAME).gauges();
    var summaries = meterRegistry.find(DeploymentMonitor.SUMMARY_METRIC_NAME).summaries();

    Assertions.assertEquals(1, gauges.size());
    Assertions.assertEquals(2, summaries.size());

    DataJob expectedJob = jobsRepository.findById("data-job").get();

    Assertions.assertEquals(
        DeploymentStatus.PLATFORM_ERROR, expectedJob.getLatestJobDeploymentStatus());
  }

  @Test
  @Order(5)
  public void testNonExistingJob() {

    deploymentMonitor.recordDeploymentStatus("data-job-missing", DeploymentStatus.PLATFORM_ERROR);

    var gauges = meterRegistry.find(DeploymentMonitor.GAUGE_METRIC_NAME).gauges();
    var summaries = meterRegistry.find(DeploymentMonitor.SUMMARY_METRIC_NAME).summaries();

    Assertions.assertEquals(1, gauges.size());
    Assertions.assertEquals(2, summaries.size());
  }
}
