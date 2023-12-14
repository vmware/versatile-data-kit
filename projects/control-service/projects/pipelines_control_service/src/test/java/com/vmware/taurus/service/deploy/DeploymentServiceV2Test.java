/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest(classes = ControlplaneApplication.class)
public class DeploymentServiceV2Test {

  @Autowired JobsRepository jobsRepository;
  @Autowired DesiredJobDeploymentRepository desiredJobDeploymentRepository;
  @Autowired DeploymentServiceV2 deploymentServiceV2;
  @Autowired ActualJobDeploymentRepository actualJobDeploymentRepository;

  @Test
  public void testUpdateDesiredDeployment_expectNewDeployment() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    JobDeployment jobDeployment = generateTestDeployment();

    deploymentServiceV2.updateDesiredDbDeployment(dataJob, jobDeployment, "user");

    var savedDeployment = desiredJobDeploymentRepository.findById("jobName").get();
    compareSavedDeploymentWithTestDeployment(jobDeployment, savedDeployment, "user");
  }

  @Test
  public void testPatchDesiredDeployment_expectMergedDeployment() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    var initialDeployment = new DesiredDataJobDeployment();
    initialDeployment.setDataJob(dataJob);
    initialDeployment.setDataJobName(dataJob.getName());
    desiredJobDeploymentRepository.save(initialDeployment);
    JobDeployment jobDeployment = generateTestDeployment();
    deploymentServiceV2.patchDesiredDbDeployment(dataJob, jobDeployment, "user");
    var savedDeployment = desiredJobDeploymentRepository.findById("jobName").get();
    compareSavedDeploymentWithTestDeployment(jobDeployment, savedDeployment, "user");
  }

  @Test
  public void testUpdateDeploymentEnabledStatus() {

    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    var initialDeployment = new DesiredDataJobDeployment();
    initialDeployment.setDataJob(dataJob);
    initialDeployment.setDataJobName(dataJob.getName());
    initialDeployment.setEnabled(false);
    desiredJobDeploymentRepository.save(initialDeployment);

    var desiredDeployment = desiredJobDeploymentRepository.findById(dataJob.getName()).get();

    Assertions.assertFalse(desiredDeployment.getEnabled());

    deploymentServiceV2.updateDeploymentEnabledStatus(dataJob.getName(), true);

    desiredDeployment = desiredJobDeploymentRepository.findById(dataJob.getName()).get();

    Assertions.assertTrue(desiredDeployment.getEnabled());
  }

  @Test
  public void testFindAllDesiredDataJobDeployments() {
    Assertions.assertEquals(
        0, deploymentServiceV2.findAllDesiredDataJobDeployments().keySet().size());

    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    var initialDeployment = new DesiredDataJobDeployment();
    initialDeployment.setDataJob(dataJob);
    initialDeployment.setDataJobName(dataJob.getName());
    desiredJobDeploymentRepository.save(initialDeployment);

    Assertions.assertEquals(
        1, deploymentServiceV2.findAllDesiredDataJobDeployments().keySet().size());
  }

  @Test
  public void testFindAllActualDataJobDeployments() {

    Assertions.assertEquals(
        0, deploymentServiceV2.findAllActualDataJobDeployments().keySet().size());
    var deployment = new ActualDataJobDeployment();

    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    deployment.setDataJobName(dataJob.getName());

    jobsRepository.save(dataJob);
    actualJobDeploymentRepository.save(deployment);

    Assertions.assertEquals(
        1, deploymentServiceV2.findAllActualDataJobDeployments().keySet().size());
  }

  @AfterEach
  public void cleanup() {
    desiredJobDeploymentRepository.deleteAll();
    jobsRepository.deleteAll();
    actualJobDeploymentRepository.deleteAll();
  }

  private void compareSavedDeploymentWithTestDeployment(
      JobDeployment testDeployment, DesiredDataJobDeployment savedDeployment, String userDeployer) {
    Assertions.assertEquals(testDeployment.getDataJobName(), savedDeployment.getDataJobName());
    Assertions.assertEquals(DeploymentStatus.NONE, savedDeployment.getStatus());
    Assertions.assertEquals(testDeployment.getEnabled(), savedDeployment.getEnabled());
    Assertions.assertEquals(testDeployment.getGitCommitSha(), savedDeployment.getGitCommitSha());
    Assertions.assertEquals(testDeployment.getPythonVersion(), savedDeployment.getPythonVersion());
    Assertions.assertEquals(testDeployment.getSchedule(), savedDeployment.getSchedule());
    Assertions.assertEquals(
        testDeployment.getResources().getCpuLimit(),
        savedDeployment.getResources().getCpuLimitCores());
    Assertions.assertEquals(
        testDeployment.getResources().getCpuRequest(),
        savedDeployment.getResources().getCpuRequestCores());
    Assertions.assertEquals(
        testDeployment.getResources().getMemoryLimit(),
        savedDeployment.getResources().getMemoryLimitMi());
    Assertions.assertEquals(
        testDeployment.getResources().getMemoryRequest(),
        savedDeployment.getResources().getMemoryRequestMi());
    Assertions.assertEquals(userDeployer, savedDeployment.getLastDeployedBy());
  }

  private JobDeployment generateTestDeployment() {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setSchedule("testSched");
    jobDeployment.setDataJobName("jobName");
    jobDeployment.setDataJobTeam("teamName");
    jobDeployment.setPythonVersion("testPython");
    jobDeployment.setGitCommitSha("testSha");
    jobDeployment.setEnabled(true);
    var resources = new DataJobResources();
    resources.setCpuLimit(1f);
    resources.setCpuRequest(1f);
    resources.setMemoryLimit(1);
    resources.setMemoryRequest(1);
    jobDeployment.setResources(resources);
    return jobDeployment;
  }
}
