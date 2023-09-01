/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobDeployment;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.repository.JobsRepository;
import io.kubernetes.client.openapi.ApiException;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.ResultActions;

import java.util.Collections;
import java.util.Optional;
import java.util.Set;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Import({DataJobDeploymentCrudITV2.TaskExecutorConfig.class})
@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudITV2 extends BaseIT {

  @Autowired private JobsRepository jobsRepository;

  @Autowired private DataJobsSynchronizer dataJobsSynchronizer;

  @Autowired private DeploymentService deploymentService;

  @TestConfiguration
  static class TaskExecutorConfig {

    @Bean
    @Primary
    public TaskExecutor taskExecutor() {
      // Deployment methods are non-blocking (Async) which makes them harder to test.
      // Making them sync for the purposes of this test.
      return new SyncTaskExecutor();
    }
  }

  @BeforeEach
  public void setup() throws Exception {
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, testJobName);

    // Execute create job
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated())
        .andExpect(
            header()
                .string(
                    HttpHeaders.LOCATION,
                    lambdaMatcher(
                        s ->
                            s.endsWith(
                                String.format(
                                    "/data-jobs/for-team/%s/jobs/%s",
                                    TEST_TEAM_NAME, testJobName)))));
  }

  @Test
  public void testDataJobDeploymentCrud() throws Exception {
    DataJobVersion testDataJobVersion = uploadDataJob();
    Assertions.assertNotNull(testDataJobVersion);

    String testJobVersionSha = testDataJobVersion.getVersionSha();
    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

    DataJob dataJob = createDataJobDeployment(testJobVersionSha);

    Optional<JobDeploymentStatus> jobDeploymentStatusOptional = deploymentService.readDeployment(testJobName);
    Assertions.assertFalse(jobDeploymentStatusOptional.isPresent());

    // Deploys data job for the very first time
    Set<String> dataJobDeploymentNames = Set.of(JobImageDeployer.getCronJobName(testJobName));
    dataJobsSynchronizer.synchronizeDataJob(dataJob, Collections.emptySet());
    String lastDeployedDateInitial = verifyDeploymentStatus(false);
    Assertions.assertNotNull(lastDeployedDateInitial);

    // Tries to redeploy job without any changes
    dataJobsSynchronizer.synchronizeDataJob(dataJob, dataJobDeploymentNames);
    String lastDeployedDateShouldNotBeChanged = verifyDeploymentStatus(false);
    Assertions.assertEquals(lastDeployedDateInitial, lastDeployedDateShouldNotBeChanged);

    // Tries to redeploy job with changes
    dataJob = updateDataJobDeployment();
    dataJobsSynchronizer.synchronizeDataJob(dataJob, dataJobDeploymentNames);
    String lastDeployedDateShouldBeChanged = verifyDeploymentStatus(true);
    Assertions.assertNotEquals(lastDeployedDateInitial, lastDeployedDateShouldBeChanged);
  }

  private String verifyDeploymentStatus(boolean enabled) {
    Optional<JobDeploymentStatus> deploymentStatusOptional = deploymentService.readDeployment(testJobName);
    Assertions.assertTrue(deploymentStatusOptional.isPresent());
    Assertions.assertEquals(enabled, deploymentStatusOptional.get().getEnabled());

    return deploymentStatusOptional.get().getLastDeployedDate();
  }

  @AfterEach
  public void cleanUp() throws Exception {
    ResultActions perform =
            mockMvc.perform(
                    delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, testJobName))
                            .with(user(TEST_USERNAME))
                            .contentType(MediaType.APPLICATION_JSON));
    if (perform.andReturn().getResponse().getStatus() != 200) {
      throw new Exception(
              "status is "
                      + perform.andReturn().getResponse().getStatus()
                      + "\nbody is"
                      + perform.andReturn().getResponse().getContentAsString());
    }

    // Finally, delete the K8s jobs to avoid them messing up subsequent runs of the same test
    dataJobsKubernetesService.listJobs().stream()
            .filter(jobName -> jobName.startsWith(testJobName))
            .forEach(
                    s -> {
                      try {
                        dataJobsKubernetesService.deleteJob(s);
                      } catch (ApiException e) {
                        e.printStackTrace();
                      }
                    });
  }

  private DataJobVersion uploadDataJob() throws Exception {
    // Take the job zip as byte array
    byte[] jobZipBinary =
            IOUtils.toByteArray(
                    getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    // Execute job upload with proper user
    var jobUploadResult =
            mockMvc
                    .perform(
                            post(String.format(
                                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                                    .with(user("user"))
                                    .content(jobZipBinary)
                                    .contentType(MediaType.APPLICATION_OCTET_STREAM))
                    .andReturn()
                    .getResponse();

    if (jobUploadResult.getStatus() != 200) {
      throw new Exception(
              "status is "
                      + jobUploadResult.getStatus()
                      + "\nbody is "
                      + jobUploadResult.getContentAsString());
    }

    return new ObjectMapper().readValue(jobUploadResult.getContentAsString(), DataJobVersion.class);
  }

  private DataJob createDataJobDeployment(String testJobVersionSha) {
    Optional<DataJob> dataJobOptional = jobsRepository.findById(testJobName);

    DataJob dataJob = dataJobOptional.get();
    DataJobDeployment dataJobDeployment = new DataJobDeployment();
    dataJobDeployment.setEnabled(false);
    dataJobDeployment.setDataJobName(dataJob.getName());
    dataJobDeployment.setGitCommitSha(testJobVersionSha);
    dataJobDeployment.setDataJob(dataJob);
    dataJob.setDataJobDeployment(dataJobDeployment);

    return jobsRepository.save(dataJob);
  }

  private DataJob updateDataJobDeployment() {
    Optional<DataJob> dataJobOptional = jobsRepository.findById(testJobName);
    Assertions.assertTrue(dataJobOptional.isPresent());

    DataJob dataJob = dataJobOptional.get();
    dataJob.getDataJobDeployment().setEnabled(true);
    dataJob.setEnabled(true);
    return jobsRepository.save(dataJob);
  }
}
