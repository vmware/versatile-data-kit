/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.repository.JobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.upload.GitWrapper;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.security.test.context.support.WithMockUser;

@SpringBootTest(
    classes = ControlplaneApplication.class)
public class DataJobsControllerDeploymentIT {

  @Autowired
  JobDeploymentRepository jobDeploymentRepository;
  @Autowired
  DataJobsController dataJobsController;
  @Autowired
  JobsRepository jobsRepository;

  @MockBean
  JobCredentialsService jobCredentialsService;
  @MockBean
  DeploymentService deploymentService;
  @MockBean
  GitWrapper gitWrapper;

  private final String TEST_JOB_NAME = "foo-job";
  private final String TEST_TEAM_NAME = "bar-team";

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  @Test
  @WithMockUser
  public void testWriteToDB_fromDataJobCreate() {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);
    dataJobsController.dataJobCreate(TEST_TEAM_NAME,
        job, TEST_JOB_NAME);
    var deploymentEntity = jobDeploymentRepository.findById(TEST_JOB_NAME);
    Assertions.assertEquals(TEST_JOB_NAME, deploymentEntity.get().getDataJobName());
  }

  @Test
  @WithMockUser
  public void testDelete_fromDataJobDelete() {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);
    dataJobsController.dataJobCreate(TEST_TEAM_NAME,
        job, TEST_JOB_NAME);
    dataJobsController.dataJobDelete(TEST_TEAM_NAME, TEST_JOB_NAME);
    Assertions.assertTrue(jobDeploymentRepository.findAll().size() == 0);
  }

  @Test
  @WithMockUser
  public void testUpdate_fromUpdateTeam() {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);
    dataJobsController.dataJobCreate(TEST_TEAM_NAME,
        job, TEST_JOB_NAME);

    var updatedDelpoyment = jobsRepository.findById(TEST_JOB_NAME).get().getDataJobDeployment();
    updatedDelpoyment.setGitCommitSha("TEST");
    jobDeploymentRepository.save(updatedDelpoyment);

    dataJobsController.dataJobTeamUpdate(TEST_TEAM_NAME, "new-team", TEST_JOB_NAME);
    var retrievedDeployment = jobDeploymentRepository.findById(TEST_JOB_NAME).get();
    Assertions.assertEquals("TEST", retrievedDeployment.getGitCommitSha());

  }

  @Test
  @WithMockUser
  public void testUpdate_formDataJobUpdate() {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);
    dataJobsController.dataJobCreate(TEST_TEAM_NAME,
        job, TEST_JOB_NAME);

    var updatedJob = jobsRepository.findById(TEST_JOB_NAME).get();
    updatedJob.setLatestJobDeploymentStatus(DeploymentStatus.PLATFORM_ERROR);
    jobsRepository.save(updatedJob);

    var updatedDelpoyment = updatedJob.getDataJobDeployment();
    updatedDelpoyment.setGitCommitSha("TEST");
    jobDeploymentRepository.save(updatedDelpoyment);

    dataJobsController.dataJobUpdate(TEST_TEAM_NAME, TEST_JOB_NAME, ToApiModelConverter.toDataJob(updatedJob));

    var retrievedDeployment = jobDeploymentRepository.findById(TEST_JOB_NAME).get();
    Assertions.assertEquals("TEST", retrievedDeployment.getGitCommitSha());

  }

}
