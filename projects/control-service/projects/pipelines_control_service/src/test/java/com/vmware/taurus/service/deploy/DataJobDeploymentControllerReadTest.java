/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.datajobs.DataJobsDeploymentController;
import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {"datajobs.deployment.configuration.persistence.readDataSource=DB"})
public class DataJobDeploymentControllerReadTest {

  @Autowired JobsRepository jobsRepository;
  @Autowired DataJobsDeploymentController dataJobsDeploymentController;
  @Autowired ActualJobDeploymentRepository actualJobDeploymentRepository;

  @WithMockUser
  @Test
  public void testReadJob_expectResponse() {
    var job = createTestJob("test-job", "team");
    createActualJobDeployment(job);
    var retrievedDeployment = dataJobsDeploymentController.deploymentRead("team", "test-job", "");
    Assertions.assertEquals(200, retrievedDeployment.getStatusCodeValue());
    Assertions.assertEquals("test-job", retrievedDeployment.getBody().getId());
  }

  @WithMockUser
  @Test
  public void testReadJob_expectNoResponse() {
    var retrievedDeployment = dataJobsDeploymentController.deploymentRead("team", "test-job", "");
    Assertions.assertEquals(404, retrievedDeployment.getStatusCodeValue());
  }

  @WithMockUser
  @Test
  public void testReadJob_asList_expectResponse() {
    var job = createTestJob("test-job", "team");
    createActualJobDeployment(job);
    var retrievedDeploymentList =
        dataJobsDeploymentController.deploymentList("team", "test-job", "", DataJobMode.RELEASE);
    Assertions.assertEquals(200, retrievedDeploymentList.getStatusCodeValue());
    Assertions.assertEquals("test-job", retrievedDeploymentList.getBody().get(0).getId());
  }

  @WithMockUser
  @Test
  public void testReadJob_asList_expectNoResponse() {
    var retrievedDeploymentList =
        dataJobsDeploymentController.deploymentList("team", "test-job", "", DataJobMode.RELEASE);
    Assertions.assertEquals(404, retrievedDeploymentList.getStatusCodeValue());
  }

  @WithMockUser
  @Test
  public void testReadJobWithNoDeployments_expectEmptyList() {
    createTestJob("test-job", "team");
    var retrievedDeploymentList =
        dataJobsDeploymentController.deploymentList("team", "test-job", "", DataJobMode.RELEASE);
    Assertions.assertTrue(retrievedDeploymentList.getBody().size() == 0);
  }

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
    actualJobDeploymentRepository.deleteAll();
  }

  private DataJob createTestJob(String jobName, String teamName) {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob(teamName, jobName));
    var jobConfig = new JobConfig();
    jobConfig.setTeam(teamName);
    dataJob.setJobConfig(jobConfig);
    jobsRepository.save(dataJob);
    return dataJob;
  }

  private ActualDataJobDeployment createActualJobDeployment(DataJob dataJob) {
    var deployment = new ActualDataJobDeployment();
    deployment.setGitCommitSha("actualSha");
    deployment.setDataJobName(dataJob.getName());
    deployment.setPythonVersion("3.9-secure");
    deployment.setEnabled(true);
    deployment.setLastDeployedBy("user");
    deployment.setSchedule("sched");
    var resources = new DataJobDeploymentResources();
    resources.setMemoryLimitMi(1);
    resources.setMemoryRequestMi(1);
    resources.setCpuLimitCores(1f);
    resources.setCpuRequestCores(1f);
    deployment.setResources(resources);
    actualJobDeploymentRepository.save(deployment);
    return deployment;
  }
}
