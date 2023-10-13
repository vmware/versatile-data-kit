/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.kubernetes.client.openapi.ApiException;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultActions;

import java.time.format.DateTimeFormatter;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_WRONG_NAME;
import static org.awaitility.Awaitility.await;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.deployment.configuration.persistence.writeTos=DB",
      "datajobs.deployment.configuration.synchronization.task.enabled=true",
      "datajobs.deployment.configuration.synchronization.task.interval.ms=1000",
      "datajobs.deployment.configuration.synchronization.task.initial.delay.ms=0"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudAsyncIT extends BaseIT {
  private static final Object DEPLOYMENT_ID = "testing";

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

    // Take the job zip as byte array
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    // Execute job upload with no user
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isUnauthorized());

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

    DataJobVersion testDataJobVersion =
        new ObjectMapper().readValue(jobUploadResult.getContentAsString(), DataJobVersion.class);
    Assertions.assertNotNull(testDataJobVersion);

    String testJobVersionSha = testDataJobVersion.getVersionSha();
    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

    // Setup
    String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

    // Execute job upload with wrong team name and user
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_WRONG_NAME, testJobName))
                .with(user("user"))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isNotFound());

    // Execute build and deploy job with no user
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());

    // Execute build and deploy job
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    // Execute build and deploy job with wrong team
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments",
                    TEST_TEAM_WRONG_NAME, testJobName))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());

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

    // Execute get job deployment with no user
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());

    // Execute get job deployment
    MvcResult result =
        mockMvc
            .perform(
                get(String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                    .with(user("user"))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    // Verify response
    DataJobDeploymentStatus jobDeployment =
        mapper.readValue(result.getResponse().getContentAsString(), DataJobDeploymentStatus.class);
    Assertions.assertEquals(testJobVersionSha, jobDeployment.getJobVersion());
    Assertions.assertEquals(true, jobDeployment.getEnabled());
    Assertions.assertEquals(DataJobMode.RELEASE, jobDeployment.getMode());
    Assertions.assertEquals(true, jobDeployment.getEnabled());
    // by default the version is the same as the tag specified by datajobs.vdk.image
    // for integration test this is registry.hub.docker.com/versatiledatakit/quickstart-vdk:release
    Assertions.assertEquals("release", jobDeployment.getVdkVersion());
    Assertions.assertEquals("user", jobDeployment.getLastDeployedBy());
    // just check some valid date is returned. It would be too error-prone/brittle to verify exact
    // time.
    DateTimeFormatter.ISO_OFFSET_DATE_TIME.parse(jobDeployment.getLastDeployedDate());

    // Execute get job deployment with wrong team
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_WRONG_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());

    // Execute disable deployment no user
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .content(getDataJobDeploymentEnableRequestBody(false))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isUnauthorized());

    // Execute disable deployment
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

    // Execute disable deployment with wrong team
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

    // Verify deployment disabled
    waitUntil(() -> {
              Optional<JobDeploymentStatus> cronJobOptional2 = dataJobsKubernetesService.readCronJob(jobDeploymentName);
              Assertions.assertTrue(cronJobOptional2.isPresent());
              JobDeploymentStatus cronJob2 = cronJobOptional2.get();
              return cronJob2.getEnabled();
            });

    // Execute delete deployment with no user
    mockMvc
            .perform(
                    delete(
                            String.format(
                                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isUnauthorized());

    // Execute delete deployment with wrong team
    mockMvc
            .perform(
                    delete(
                            String.format(
                                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                                    TEST_TEAM_WRONG_NAME, testJobName, DEPLOYMENT_ID))
                            .with(user("user"))
                            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isNotFound());

    // Execute delete deployment
    mockMvc
            .perform(
                    delete(
                            String.format(
                                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                            .with(user("user"))
                            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isAccepted());

    Thread.sleep(5 * 1000); // Wait for deployment to be deleted

    // Verify deployment deleted
    waitUntil(() -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isEmpty());
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

  @Test
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

  private void waitUntil(Callable<Boolean> callable) {
    // Wait for the operation to complete, polling every 15 seconds
    // See: https://github.com/awaitility/awaitility/wiki/Usage
    await()
            .atMost(10, TimeUnit.MINUTES)
            .with()
            .pollInterval(15, TimeUnit.SECONDS)
            .until(callable);
  }
}
