/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.datajobs.ToModelApiConverter;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJobDeploymentResources;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import java.time.OffsetDateTime;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.test.mock.mockito.SpyBean;
import org.springframework.test.context.TestPropertySource;

@SpringBootTest(classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {
      "datajobs.deployment.configuration.persistence.writeTos=DB",
      "datajobs.deployment.configuration.persistence.readDataSource=DB",
      "datajobs.deployment.configuration.synchronization.task.enabled:true"
    })
public class DataJobsSynchronizerWriteTest {

  @SpyBean DeploymentServiceV2 deploymentServiceV2;
  @SpyBean JobImageBuilder jobImageBuilder;
  @MockBean JobImageDeployerV2 jobImageDeployer;
  @MockBean ControlKubernetesService controlKubernetesService;
  @Autowired JobsRepository jobsRepository;
  @Autowired DesiredJobDeploymentRepository desiredJobDeploymentRepository;
  @Autowired DataJobsSynchronizer dataJobsSynchronizer;
  @Autowired ActualJobDeploymentRepository actualJobDeploymentRepository;

  @BeforeEach
  public void setup() throws Exception {
    Mockito.doReturn(Set.of("jobName"))
        .when(deploymentServiceV2)
        .findAllActualDeploymentNamesFromKubernetes();
    Mockito.doReturn(true)
        .when(jobImageBuilder)
        .buildImage(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any());
    Mockito.doReturn(getTestDeployment())
        .when(jobImageDeployer)
        .scheduleJob(
            Mockito.any(),
            Mockito.any(),
            Mockito.any(),
            Mockito.anyBoolean(),
            Mockito.anyBoolean(),
            Mockito.anyString());
  }

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  @Test
  public void testUpdateDesiredDeployment_expectNewDeployment() {
    var dataJob = ToModelApiConverter.toDataJob(TestUtils.getDataJob("teamName", "jobName"));
    jobsRepository.save(dataJob);
    JobDeployment jobDeployment = generateTestDeployment();
    deploymentServiceV2.updateDesiredDbDeployment(dataJob, jobDeployment, "user");

    Assertions.assertEquals(0, actualJobDeploymentRepository.findAll().size());

    dataJobsSynchronizer.synchronizeDataJobs();

    var actualDataJobDeployment = actualJobDeploymentRepository.findById(dataJob.getName()).get();

    Assertions.assertEquals(
        jobDeployment.getDataJobName(), actualDataJobDeployment.getDataJobName());
    Assertions.assertEquals(
        jobDeployment.getGitCommitSha(), actualDataJobDeployment.getGitCommitSha());
    Assertions.assertEquals(
        jobDeployment.getPythonVersion(), actualDataJobDeployment.getPythonVersion());
    Assertions.assertEquals("user", actualDataJobDeployment.getLastDeployedBy());
  }

  @Test
  public void testUpdateDesiredDeployment_expectNoDeployment() {
    Mockito.doReturn(Set.of())
        .when(deploymentServiceV2)
        .findAllActualDeploymentNamesFromKubernetes();

    Assertions.assertEquals(0, actualJobDeploymentRepository.findAll().size());

    dataJobsSynchronizer.synchronizeDataJobs();

    Assertions.assertEquals(0, actualJobDeploymentRepository.findAll().size());
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

  private ActualDataJobDeployment getTestDeployment() {
    var testDeployment = new ActualDataJobDeployment();
    var testJob = generateTestDeployment();
    testDeployment.setDataJobName(testJob.getDataJobName());
    testDeployment.setDeploymentVersionSha(testJob.getGitCommitSha());
    testDeployment.setPythonVersion(testJob.getPythonVersion());
    testDeployment.setGitCommitSha(testJob.getGitCommitSha());
    testDeployment.setLastDeployedDate(OffsetDateTime.now());
    testDeployment.setResources(new DataJobDeploymentResources());
    testDeployment.setLastDeployedBy("user");
    return testDeployment;
  }
}
