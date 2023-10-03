/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.DataJobsDeploymentController;
import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.exception.DataJobDeploymentNotFoundException;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.test.context.support.WithMockUser;

@SpringBootTest(classes = ControlplaneApplication.class)
public class DataJobDeploymentControllerTest {

  @Autowired JobsRepository jobsRepository;
  @Autowired DataJobsDeploymentController dataJobsDeploymentController;
  @Autowired DesiredJobDeploymentRepository desiredJobDeploymentRepository;
  @Autowired ActualJobDeploymentRepository actualJobDeploymentRepository;

  @MockBean DeploymentService deploymentService;

  @Test
  @WithMockUser
  public void testDeploymentPatch_noExistingDeployment_expectError() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    var deployment = TestUtils.getDataJobDeployment(null, null);

    Assertions.assertThrows(
        DataJobDeploymentNotFoundException.class,
        () ->
            dataJobsDeploymentController.deploymentPatch(
                "teamName", "jobName", "deploymentId", deployment));
  }

  @Test
  @WithMockUser
  public void testDeploymentPatch_expectDeploymentMerge() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    var existingDeployment = getActualJobDeployment(dataJob);
    actualJobDeploymentRepository.save(existingDeployment);

    var newDeployment = TestUtils.getDataJobDeployment("deploymentId", "jobVersion");
    dataJobsDeploymentController.deploymentPatch("teamName", "jobName", "id", newDeployment);
    var patchedJob = desiredJobDeploymentRepository.findById("jobName").get();
    Assertions.assertEquals("jobVersion", patchedJob.getGitCommitSha());
  }

  @Test
  @WithMockUser
  public void testDeploymentUpdate_noDeployment_expectDeployment() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "job-name"));
    var jobConfig = new JobConfig();
    jobConfig.setTeam("teamName");
    dataJob.setJobConfig(jobConfig);
    jobsRepository.save(dataJob);
    var deployment = TestUtils.getDataJobDeployment("deploymentId", "jobVersion");
    dataJobsDeploymentController.deploymentUpdate("teamName", "job-name", true, deployment);
    var updatedJob = desiredJobDeploymentRepository.findById(dataJob.getName()).get();
    Assertions.assertEquals("jobVersion", updatedJob.getGitCommitSha());
  }

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  private ActualDataJobDeployment getActualJobDeployment(DataJob dataJob) {
    var deployment = new ActualDataJobDeployment();
    deployment.setGitCommitSha("actualSha");
    deployment.setDataJob(dataJob);
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
    return deployment;
  }
}
