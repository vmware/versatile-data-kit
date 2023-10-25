/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;

@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.deployment.configuration.persistence.writeTos=DB",
      "datajobs.deployment.configuration.synchronization.task.enabled=true",
      "datajobs.deployment.configuration.synchronization.task.interval.ms=1000",
      "datajobs.deployment.configuration.synchronization.task.initial.delay.ms=0"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudAsyncIT extends BaseDataJobDeploymentCrudIT {

  @Autowired private DesiredJobDeploymentRepository desiredJobDeploymentRepository;
  @Autowired private ActualJobDeploymentRepository actualJobDeploymentRepository;

  @Override
  protected void beforeDeploymentDeletion() {
    var desiredDataJobDeployment = desiredJobDeploymentRepository.findById(testJobName);
    var actualDataJobDeployment = actualJobDeploymentRepository.findById(testJobName);

    checkDesiredDeployment(desiredDataJobDeployment);
    checkActualDeployment(actualDataJobDeployment);
  }

  @Override
  protected void afterDeploymentDeletion() {
    var desiredDataJobDeployment = desiredJobDeploymentRepository.findById(testJobName);
    var actualDataJobDeployment = actualJobDeploymentRepository.findById(testJobName);

    checkDesiredDeploymentDeleted(desiredDataJobDeployment);
    checkActualDeploymentDeleted(actualDataJobDeployment);
  }

  private void checkDesiredDeployment(Optional<DesiredDataJobDeployment> desiredDataJobDeployment) {
    Assertions.assertTrue(desiredDataJobDeployment.isPresent());
    var deployment = desiredDataJobDeployment.get();
    Assertions.assertEquals(DeploymentStatus.SUCCESS, deployment.getStatus());
    Assertions.assertEquals(TEST_JOB_SCHEDULE, deployment.getSchedule());
    Assertions.assertEquals("test-team", deployment.getDataJob().getJobConfig().getTeam());
    Assertions.assertFalse(deployment.getEnabled());
    Assertions.assertEquals(testJobName, deployment.getDataJobName());
    Assertions.assertFalse(deployment.getUserInitiated());
    Assertions.assertEquals("user", deployment.getLastDeployedBy());
    Assertions.assertNotNull(deployment.getGitCommitSha());
    Assertions.assertEquals("3.9", deployment.getPythonVersion());
  }

  private void checkActualDeployment(Optional<ActualDataJobDeployment> actualDataJobDeployment) {
    Assertions.assertTrue(actualDataJobDeployment.isPresent());
    var deployment = actualDataJobDeployment.get();
    Assertions.assertEquals("user", deployment.getLastDeployedBy());
    Assertions.assertEquals(testJobName, deployment.getDataJobName());
    Assertions.assertNotNull(deployment.getLastDeployedDate());
    Assertions.assertFalse(deployment.getEnabled());
    Assertions.assertEquals(testJobName, deployment.getDataJobName());
    Assertions.assertEquals(TEST_JOB_SCHEDULE, deployment.getSchedule());
    Assertions.assertEquals("3.9", deployment.getPythonVersion());
  }

  private void checkDesiredDeploymentDeleted(
      Optional<DesiredDataJobDeployment> desiredDataJobDeployment) {
    Assertions.assertFalse(desiredDataJobDeployment.isPresent());
  }

  private void checkActualDeploymentDeleted(
      Optional<ActualDataJobDeployment> actualDataJobDeployment) {
    Assertions.assertFalse(actualDataJobDeployment.isPresent());
  }
}
