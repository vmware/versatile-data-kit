/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Optional;

/** Integration tests of the setup of Spring Data repository for data job deployments */
@SpringBootTest(classes = ControlplaneApplication.class)
public class ActualJobDeploymentRepositoryIT {

  @Autowired private JobsRepository jobsRepository;

  @Autowired private ActualJobDeploymentRepository jobDeploymentRepository;

  @BeforeEach
  public void setUp() throws Exception {
    jobDeploymentRepository.deleteAll();
  }

  @Test
  public void testCreate_deploymentShouldBeCreated() {
    createDataJobDeployment();
  }

  @Test
  public void testDelete_deploymentShouldBeDeleted() {
    ActualDataJobDeployment expectedDataJobDeployment = createDataJobDeployment();

    var actualDataJobDeployment =
        jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(actualDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, actualDataJobDeployment.get());

    Optional<DataJob> dataJobOptional =
        jobsRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(dataJobOptional.isPresent());

    jobDeploymentRepository.deleteById(expectedDataJobDeployment.getDataJobName());

    Assertions.assertTrue(jobsRepository.findById(expectedDataJobDeployment.getDataJobName()).isPresent());
    var deletedDataJobDeployment =
        jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertFalse(deletedDataJobDeployment.isPresent());
  }

  @Test
  public void testUpdate_deploymentShouldBeUpdated() {
    ActualDataJobDeployment expectedDataJobDeployment = createDataJobDeployment();

    var createdDataJobDeployment =
        jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(createdDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, createdDataJobDeployment.get());

    expectedDataJobDeployment.setGitCommitSha("new-sha");
    jobDeploymentRepository.save(expectedDataJobDeployment);

    var updatedDataJobDeployment =
        jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(updatedDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, updatedDataJobDeployment.get());
  }

  private ActualDataJobDeployment createDataJobDeployment() {
    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

    ActualDataJobDeployment expectedDataJobDeployment = new ActualDataJobDeployment();
    expectedDataJobDeployment.setDataJobName(actualDataJob.getName());
    expectedDataJobDeployment.setDataJob(actualDataJob);
    expectedDataJobDeployment.setPythonVersion("3.9-secure");
    expectedDataJobDeployment.setGitCommitSha("commit");

    DataJobDeploymentResources expectedResources = new DataJobDeploymentResources();
    expectedResources.setCpuLimitCores(1F);
    expectedResources.setCpuRequestCores(1F);
    expectedResources.setMemoryLimitMi(1);
    expectedResources.setMemoryRequestMi(1);
    expectedDataJobDeployment.setResources(expectedResources);

    expectedDataJobDeployment.setLastDeployedDate(OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS));
    expectedDataJobDeployment.setLastDeployedBy("user");
    expectedDataJobDeployment.setEnabled(true);
    expectedDataJobDeployment.setDeploymentVersionSha("sha");

    jobDeploymentRepository.save(expectedDataJobDeployment);

    var createdDataJobDeployment =
        jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(createdDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, createdDataJobDeployment.get());

    return createdDataJobDeployment.get();
  }
}
