/*
 * Copyright 2023-2025 Broadcom
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
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
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
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.ResultActions;

import java.time.format.DateTimeFormatter;
import java.util.Optional;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.hamcrest.Matchers.is;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Import({TestJobImageBuilderDynamicVdkImageIT.TaskExecutorConfig.class})
@TestPropertySource(
    properties = {
      "datajobs.deployment.supportedPythonVersions={3.8: {vdkImage:"
          + " 'registry.hub.docker.com/versatiledatakit/quickstart-vdk:pre-release', baseImage:"
          + " 'versatiledatakit/data-job-base-python-3.8:latest', builderImage:"
          + " 'ghcr.io/versatile-data-kit-dev/versatiledatakit/job-builder:1.3.3'}, 3.9: {vdkImage:"
          + " 'ghcr.io/versatile-data-kit-dev/versatiledatakit/quickstart-vdk:release', baseImage:"
          + " 'ghcr.io/versatile-data-kit-dev/versatiledatakit/data-job-base-python-3.9:latest',"
          + " builderImage: 'ghcr.io/versatile-data-kit-dev/versatiledatakit/job-builder:1.3.3'}}",
      "datajobs.deployment.defaultPythonVersion=3.9",
      "datajobs.builder.image="
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class TestJobImageBuilderDynamicVdkImageIT extends BaseIT {
  private static final Object DEPLOYMENT_ID = "testing";

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
  public void testDataJobDeploymentDynamicVdkVersion() throws Exception {

    // Take the job zip as byte array
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    // Execute job upload
    ResultActions resultAction =
        mockMvc.perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM));

    if (resultAction.andReturn().getResponse().getStatus() != 200) {
      throw new Exception(
          "status is "
              + resultAction.andReturn().getResponse().getStatus()
              + "\nbody is "
              + resultAction.andReturn().getResponse().getContentAsString());
    }
    MvcResult jobUploadResult = resultAction.andExpect(status().isOk()).andReturn();

    DataJobVersion testDataJobVersion =
        new ObjectMapper()
            .readValue(jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
    Assertions.assertNotNull(testDataJobVersion);

    String testJobVersionSha = testDataJobVersion.getVersionSha();
    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

    // Setup
    String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

    // Execute build and deploy job
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    String jobDeploymentName = JobImageDeployer.getCronJobName(testJobName);
    // Verify job deployment created
    Optional<JobDeploymentStatus> cronJobOptional =
        dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isPresent());
    JobDeploymentStatus cronJob = cronJobOptional.get();
    Assertions.assertEquals(testJobVersionSha, cronJob.getGitCommitSha());
    Assertions.assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
    Assertions.assertEquals(true, cronJob.getEnabled());
    Assertions.assertTrue(cronJob.getImageName().endsWith(testJobVersionSha));
    Assertions.assertEquals("user", cronJob.getLastDeployedBy());

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

    // Verify deployment disabled
    cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isPresent());
    cronJob = cronJobOptional.get();
    Assertions.assertEquals(false, cronJob.getEnabled());

    // Execute set vdk version for deployment
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentVdkVersionRequestBody("new_vdk_version_tag"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    // verify vdk version is changed
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.vdk_version", is("new_vdk_version_tag")));

    // Execute change python version and set corresponding vdk version for deployment
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, testJobName))
                .with(user("user"))
                .content(getDataJobDeploymentRequestBody(testJobVersionSha, "3.8"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    jobDeploymentName = JobImageDeployer.getCronJobName(testJobName);
    // Verify job deployment updated properly
    cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isPresent());
    cronJob = cronJobOptional.get();
    Assertions.assertEquals(testJobVersionSha, cronJob.getGitCommitSha());
    Assertions.assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
    Assertions.assertEquals(false, cronJob.getEnabled());
    Assertions.assertTrue(cronJob.getImageName().endsWith(testJobVersionSha));
    Assertions.assertEquals("user", cronJob.getLastDeployedBy());
    Assertions.assertTrue(cronJob.getVdkVersion().endsWith("pre-release"));
    Assertions.assertEquals("3.8", cronJob.getPythonVersion());

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
    cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isEmpty());
  }

  @AfterEach
  public void cleanUp() throws Exception {
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, testJobName))
                .with(user("user")))
        .andExpect(status().isOk());
  }
}
