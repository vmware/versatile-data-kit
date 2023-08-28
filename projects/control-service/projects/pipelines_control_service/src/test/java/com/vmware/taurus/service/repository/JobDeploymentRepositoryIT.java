/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.repository;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeployment;
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
public class JobDeploymentRepositoryIT {

  @Autowired private JobsRepository jobsRepository;

  @Autowired private JobDeploymentRepository jobDeploymentRepository;

  @BeforeEach
  public void setUp() throws Exception {
    jobsRepository.deleteAll();
  }

  @Test
  public void testCreate_deploymentShouldBeCreated() {
    createDataJobDeployment();
  }

  @Test
  public void testDelete_deploymentShouldBeDeleted() {
    DataJobDeployment expectedDataJobDeployment = createDataJobDeployment();

    var actualDataJobDeployment = jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(actualDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, actualDataJobDeployment.get());

    Optional<DataJob> dataJobOptional = jobsRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(dataJobOptional.isPresent());

    DataJob dataJob = dataJobOptional.get();
    dataJob.setDataJobDeployment(null);
    jobsRepository.save(dataJob);

    var deletedDataJobDeployment = jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertFalse(deletedDataJobDeployment.isPresent());
  }

  @Test
  public void testUpdate_deploymentShouldBeUpdated() {
    DataJobDeployment expectedDataJobDeployment = createDataJobDeployment();

    var createdDataJobDeployment = jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(createdDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, createdDataJobDeployment.get());

    expectedDataJobDeployment.setGitCommitSha("new-sha");
    jobDeploymentRepository.save(expectedDataJobDeployment);

    var updatedDataJobDeployment = jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(updatedDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, updatedDataJobDeployment.get());
  }

  private DataJobDeployment createDataJobDeployment() {
    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

    DataJobDeployment expectedDataJobDeployment = new DataJobDeployment(actualDataJob.getName(), actualDataJob, "sha", "3.9-secure", "commit", 1F, 1F, 1, 1, OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS), "user", true);
    actualDataJob.setDataJobDeployment(expectedDataJobDeployment);
    jobsRepository.save(actualDataJob);

    var createdDataJobDeployment = jobDeploymentRepository.findById(expectedDataJobDeployment.getDataJobName());
    Assertions.assertTrue(createdDataJobDeployment.isPresent());
    Assertions.assertEquals(expectedDataJobDeployment, createdDataJobDeployment.get());

    return createdDataJobDeployment.get();
  }
}
