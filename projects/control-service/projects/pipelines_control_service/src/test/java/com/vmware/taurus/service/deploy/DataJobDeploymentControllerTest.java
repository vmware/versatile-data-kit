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
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeployment;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.repository.JobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.test.context.support.WithMockUser;

@SpringBootTest(classes = ControlplaneApplication.class)
public class DataJobDeploymentControllerTest {

  @Autowired JobDeploymentRepository jobDeploymentRepository;
  @Autowired JobsRepository jobsRepository;
  @Autowired DataJobsDeploymentController dataJobsDeploymentController;

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
    var deployment = getJobDeployment(dataJob);
    dataJob.setDataJobDeployment(deployment);
    Assertions.assertEquals("commit", deployment.getGitCommitSha());
    jobsRepository.save(dataJob);
    var newDeployment = TestUtils.getDataJobDeployment("deploymentId", "jobVersion");
    dataJobsDeploymentController.deploymentPatch("teamName", "jobName", "id", newDeployment);
    var patchedJob = jobsRepository.findById("jobName").get();
    Assertions.assertEquals("jobVersion", patchedJob.getDataJobDeployment().getGitCommitSha());
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

    var updatedJob = jobsRepository.findById(dataJob.getName()).get();
    Assertions.assertEquals("jobVersion", updatedJob.getDataJobDeployment().getGitCommitSha());
  }

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  private DataJobDeployment getJobDeployment(DataJob dataJob) {
    var deployment =
        new DataJobDeployment(
            dataJob.getName(),
            dataJob,
            "sha",
            "3.9-secure",
            "commit",
            1F,
            1F,
            1,
            1,
            OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS),
            "user",
            true);
    return deployment;
  }
}
