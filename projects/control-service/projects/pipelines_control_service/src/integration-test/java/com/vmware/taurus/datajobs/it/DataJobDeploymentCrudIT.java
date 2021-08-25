/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.controlplane.model.data.DataJobMode;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.IOUtils;
import org.junit.After;
import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.junit.platform.commons.util.StringUtils;
import org.junit.runner.RunWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MvcResult;

import java.util.Optional;
import java.util.UUID;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

// TODO: move to junit 5
@RunWith(SpringRunner.class)
@Import({DataJobDeploymentCrudIT.TaskExecutorConfig.class})
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudIT extends BaseIT {

   // TODO: those are manually added to repo - it's good idea to be automated
   private static final String TEST_JOB_NAME = "integration-test-" + UUID.randomUUID().toString().substring(0, 8);
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

   @Before
   public void setup() throws Exception {
      String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

      // Execute create job
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME)).with(user("user"))
            .content(dataJobRequestBody)
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isCreated())
            .andExpect(header().string(HttpHeaders.LOCATION,
                  lambdaMatcher(s -> s.endsWith(String.format("/data-jobs/for-team/%s/jobs/%s",
                          TEST_TEAM_NAME,
                          TEST_JOB_NAME)))));
   }

   @Test
   public void testDataJobDeploymentCrud() throws Exception {

      // Take the job zip as byte array
      byte[] jobZipBinary = IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("simple_job.zip"));

      // Execute job upload with no user
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
            TEST_TEAM_NAME,
            TEST_JOB_NAME))
            .content(jobZipBinary)
            .contentType(MediaType.APPLICATION_OCTET_STREAM))
            .andExpect(status().isUnauthorized());

      // Execute job upload with proper user
      MvcResult jobUploadResult = mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
            TEST_TEAM_NAME,
            TEST_JOB_NAME))
            .with(user("user"))
            .content(jobZipBinary)
            .contentType(MediaType.APPLICATION_OCTET_STREAM))
            .andExpect(status().isOk())
            .andReturn();

      DataJobVersion testDataJobVersion = new ObjectMapper()
            .readValue(jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
      Assert.assertNotNull(testDataJobVersion);

      String testJobVersionSha = testDataJobVersion.getVersionSha();
      Assert.assertFalse(StringUtils.isBlank(testJobVersionSha));

      // Setup
      String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

      // Execute job upload with wrong team name and user
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
            TEST_TEAM_WRONG_NAME,
            TEST_JOB_NAME))
            .with(user("user"))
            .content(jobZipBinary)
            .contentType(MediaType.APPLICATION_OCTET_STREAM))
            .andExpect(status().isNotFound());

      // Execute build and deploy job with no user
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
              .content(dataJobDeploymentRequestBody)
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isUnauthorized());

      // Execute build and deploy job
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
              .with(user("user"))
              .content(dataJobDeploymentRequestBody)
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isAccepted());

      // Execute build and deploy job with wrong team
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_WRONG_NAME, TEST_JOB_NAME))
              .with(user("user"))
              .content(dataJobDeploymentRequestBody)
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isNotFound());

      String jobDeploymentName = JobImageDeployer.getCronJobName(TEST_JOB_NAME);
      // Verify job deployment created
      Optional<JobDeploymentStatus> cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
      Assert.assertTrue(cronJobOptional.isPresent());
      JobDeploymentStatus cronJob = cronJobOptional.get();
      Assert.assertEquals(testJobVersionSha, cronJob.getGitCommitSha());
      Assert.assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
      Assert.assertEquals(true, cronJob.getEnabled());
      Assert.assertTrue(cronJob.getImageName().endsWith(testJobVersionSha));
      Assert.assertEquals("user", cronJob.getLastDeployedBy());

      // Execute get job deployment with no user
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isUnauthorized());

      // Execute get job deployment
      MvcResult result = mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andReturn();

      // Execute get job deployment with wrong team
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_WRONG_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isNotFound());

      // Verify response
      DataJobDeploymentStatus jobDeployment = mapper.readValue(result.getResponse().getContentAsString(),
              DataJobDeploymentStatus.class);
      Assert.assertEquals(testJobVersionSha, jobDeployment.getJobVersion());
      Assert.assertEquals(DataJobMode.RELEASE, jobDeployment.getMode());
      Assert.assertEquals(true, jobDeployment.getEnabled());

      // Execute disable deployment no user
      mockMvc.perform(patch(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .content(getDataJobDeploymentEnableRequestBody(false))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isUnauthorized());

      // Execute disable deployment
      mockMvc.perform(patch(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .content(getDataJobDeploymentEnableRequestBody(false))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isAccepted());

      // Execute disable deployment with wrong team
      mockMvc.perform(patch(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_WRONG_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .content(getDataJobDeploymentEnableRequestBody(false))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isNotFound());

      // Verify deployment disabled
      cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
      Assert.assertTrue(cronJobOptional.isPresent());
      cronJob = cronJobOptional.get();
      Assert.assertEquals(false, cronJob.getEnabled());

      // Execute delete deployment with no user
      mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isUnauthorized());

      // Execute delete deployment with wrong team
      mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_WRONG_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isNotFound());

      // Execute delete deployment
      mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
              TEST_TEAM_NAME,
              TEST_JOB_NAME,
              DEPLOYMENT_ID))
              .with(user("user"))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isAccepted());

      Thread.sleep(5 * 1000); // Wait for deployment to be deleted

      // Verify deployment deleted
      cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
      Assert.assertTrue(cronJobOptional.isEmpty());
   }

   @After
   public void cleanUp() throws Exception {
      mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
            TEST_TEAM_NAME,
            TEST_JOB_NAME))
            .with(user("user")))
            .andExpect(status().isOk());
   }


   @Test
   public void testDataJobDeleteSource() throws Exception {
      byte[] jobZipBinary = IOUtils.toByteArray(
              getClass().getClassLoader().getResourceAsStream("simple_job.zip"));

      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
              TEST_TEAM_NAME,
              TEST_JOB_NAME))
              .with(user("user"))
              .content(jobZipBinary)
              .contentType(MediaType.APPLICATION_OCTET_STREAM))
              .andExpect(status().isOk());
   }
}
