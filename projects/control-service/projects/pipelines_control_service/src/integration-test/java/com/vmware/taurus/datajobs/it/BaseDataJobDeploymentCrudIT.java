/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_WRONG_NAME;
import static org.awaitility.Awaitility.await;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.patch;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.controlplane.model.data.DataJobSchedule;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.kubernetes.client.openapi.ApiException;
import java.time.format.DateTimeFormatter;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultActions;

public abstract class BaseDataJobDeploymentCrudIT extends BaseIT {
  protected static final Object DEPLOYMENT_ID = "testing";

  protected abstract void beforeDeploymentDeletion() throws Exception;

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
  @Order(1)
  public void uploadJobWithNoUser() throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                .content(getJobZipArray())
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isUnauthorized());
  }

  @Test
  @Order(2)
  public void uploadJobWithWrongTeamAndUser() throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_WRONG_NAME, testJobName))
                .with(user("user"))
                .content(getJobZipArray())
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isNotFound());
  }

  @Test
  @Order(3)
  public void testDataJobDeploymentCrudOperations() throws Exception {

    var testDataJobVersion = uploadJobWithProperUser();
    var testJobVersionSha = getTestJobVersionSha(testDataJobVersion);
    var dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha, "3.9");
    String jobDeploymentName = JobImageDeployer.getCronJobName(testJobName);

    buildAndDeployJobWithNoUser(dataJobDeploymentRequestBody);

    buildAndDeployJob(dataJobDeploymentRequestBody);

    buildAndDeployJobWrongTeam(dataJobDeploymentRequestBody);

    buildAndDeployJobWithResources(testJobVersionSha);

    verifyJobDeploymentResponse(testJobVersionSha);

    executeJobDeploymentWithNoUser();

    executeGetJobDeploymentWithWrongTeam();

    executeDisableDeploymentNoUser();

    executeDisableDeployment();

    executeDisableDeploymentWrongTeam();

    verifyDeploymentDisabled(jobDeploymentName);

    verifyDeploymentFieldsAfterDisable(testJobVersionSha);

    beforeDeploymentDeletion();

    deleteDeploymentNoUser();

    deleteDeploymentWrongTeam();

    executeDeleteDeployment(jobDeploymentName);
  }

  @Test
  @Order(4)
  public void testDataJobDeleteSource() throws Exception {
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isOk());
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

  private byte[] getJobZipArray() throws Exception {
    return IOUtils.toByteArray(
        getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));
  }

  private DataJobVersion uploadJobWithProperUser() throws Exception {
    var jobUploadResult =
        mockMvc
            .perform(
                post(String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                    .with(user("user"))
                    .content(getJobZipArray())
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

    DataJobVersion testDataJobVersion =
        new ObjectMapper().readValue(jobUploadResult.getContentAsString(), DataJobVersion.class);
    Assertions.assertNotNull(testDataJobVersion);
    return testDataJobVersion;
  }

  private String getTestJobVersionSha(DataJobVersion testDataJobVersion) {
    String testJobVersionSha = testDataJobVersion.getVersionSha();
    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));
    return testJobVersionSha;
  }

  private void buildAndDeployJobWithNoUser(String dataJobDeploymentRequestBody) throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());
  }

  private void buildAndDeployJob(String dataJobDeploymentRequestBody) throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());
  }

  private void buildAndDeployJobWrongTeam(String dataJobDeploymentRequestBody) throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments",
                    TEST_TEAM_WRONG_NAME, testJobName))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }

  private void buildAndDeployJobWithResources(String testJobVersionSha) throws Exception {
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(getDataJobDeploymentRequestBodyWithJobResources(testJobVersionSha))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isBadRequest());

    String jobDeploymentName = JobImageDeployer.getCronJobName(testJobName);
    // Verify job deployment created
    waitUntil(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isPresent());

    Optional<JobDeploymentStatus> cronJobOptional =
        dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isPresent());
    JobDeploymentStatus cronJob = cronJobOptional.get();
    Assertions.assertEquals(testJobVersionSha, cronJob.getGitCommitSha());
    Assertions.assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
    Assertions.assertEquals(true, cronJob.getEnabled());
    Assertions.assertTrue(cronJob.getImageName().endsWith(testJobVersionSha));
    Assertions.assertEquals("user", cronJob.getLastDeployedBy());
  }

  private void executeJobDeploymentWithNoUser() throws Exception {
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());
  }

  private MvcResult getJobDeployment() throws Exception {
    return mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andReturn();
  }

  private void executeGetJobDeploymentWithWrongTeam() throws Exception {
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_WRONG_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }

  private void executeDisableDeploymentNoUser() throws Exception {
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .content(getDataJobDeploymentEnableRequestBody(false))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());
  }

  private void executeDisableDeployment() throws Exception {
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentEnableRequestBody(false))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());
  }

  private void executeDisableDeploymentWrongTeam() throws Exception {
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_WRONG_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentEnableRequestBody(false))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }

  private void verifyDeploymentDisabled(String jobDeploymentName) {
    waitUntil(
        () -> {
          Optional<JobDeploymentStatus> deploymentOptional =
              dataJobsKubernetesService.readCronJob(jobDeploymentName);
          Assertions.assertTrue(deploymentOptional.isPresent());
          JobDeploymentStatus deployment = deploymentOptional.get();
          return !deployment.getEnabled();
        });
  }

  private void verifyDeploymentFieldsAfterDisable(String testJobVersionSha) throws Exception {
    var result = getJobDeployment();
    DataJobDeploymentStatus jobDeployment =
        mapper.readValue(result.getResponse().getContentAsString(), DataJobDeploymentStatus.class);

    Assertions.assertEquals(testJobVersionSha, jobDeployment.getJobVersion());
    Assertions.assertFalse(jobDeployment.getEnabled());
    Assertions.assertEquals(DataJobMode.RELEASE, jobDeployment.getMode());
    Assertions.assertEquals("user", jobDeployment.getLastDeployedBy());
    DateTimeFormatter.ISO_OFFSET_DATE_TIME.parse(jobDeployment.getLastDeployedDate());
  }

  private void deleteDeploymentNoUser() throws Exception {
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());
  }

  private void deleteDeploymentWrongTeam() throws Exception {
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_WRONG_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }

  private void executeDeleteDeployment(String jobDeploymentName) throws Exception {
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    // Verify deployment deleted
    waitUntil(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isEmpty());
  }

  private void verifyJobDeploymentResponse(String testJobVersionSha) throws Exception {
    var result = getJobDeployment();
    DataJobDeploymentStatus jobDeployment =
        mapper.readValue(result.getResponse().getContentAsString(), DataJobDeploymentStatus.class);
    Assertions.assertEquals(testJobVersionSha, jobDeployment.getJobVersion());
    Assertions.assertTrue(jobDeployment.getEnabled());
    Assertions.assertEquals(DataJobMode.RELEASE, jobDeployment.getMode());
    Assertions.assertEquals("3.9", jobDeployment.getPythonVersion());
    // by default the version is the same as the tag specified by datajobs.vdk.image
    // for integration test this is registry.hub.docker.com/versatiledatakit/quickstart-vdk:release
    Assertions.assertEquals("user", jobDeployment.getLastDeployedBy());
    // just check some valid date is returned. It would be too error-prone/brittle to verify exact
    // time.
    DateTimeFormatter.ISO_OFFSET_DATE_TIME.parse(jobDeployment.getLastDeployedDate());
  }

  private String getDataJobDeploymentRequestBodyWithJobResources(String jobVersionSha)
      throws JsonProcessingException {
    var jobDeployment = new DataJobDeployment();
    jobDeployment.setJobVersion(jobVersionSha);
    jobDeployment.setMode(DataJobMode.RELEASE);
    DataJobResources dataJobResources = new DataJobResources();
    dataJobResources.setCpuRequest(100F);
    dataJobResources.setCpuLimit(1000F);
    dataJobResources.setMemoryRequest(500);
    dataJobResources.setMemoryLimit(1000);
    jobDeployment.setResources(dataJobResources);
    jobDeployment.setSchedule(new DataJobSchedule());
    jobDeployment.setId(TEST_JOB_DEPLOYMENT_ID);

    return mapper.writeValueAsString(jobDeployment);
  }

  private void waitUntil(Callable<Boolean> callable) {
    // Wait for the operation to complete, polling every 15 seconds
    // See: https://github.com/awaitility/awaitility/wiki/Usage
    await().atMost(10, TimeUnit.MINUTES).with().pollInterval(15, TimeUnit.SECONDS).until(callable);
  }
}
