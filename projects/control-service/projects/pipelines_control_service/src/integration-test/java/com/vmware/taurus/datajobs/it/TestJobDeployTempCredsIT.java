/*
 * Copyright 2023-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.awaitility.Awaitility.await;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.amazonaws.services.ecr.AmazonECR;
import com.amazonaws.services.ecr.AmazonECRClientBuilder;
import com.amazonaws.services.ecr.model.DeleteRepositoryRequest;
import com.amazonaws.services.ecr.model.DescribeImagesRequest;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.deploy.DockerRegistryService;
import com.vmware.taurus.service.deploy.EcrRegistryInterface;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
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

@Import({TestJobDeployTempCredsIT.TaskExecutorConfig.class})
@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.aws.assumeIAMRole=true",
      "datajobs.aws.RoleArn=arn:aws:iam::320807031117:role/svc.ecr-integration-test",
      "datajobs.docker.registryType=ecr",
      "datajobs.aws.region=us-west-2",
      "DOCKER_REGISTRY_URL = 320807031117.dkr.ecr.us-west-2.amazonaws.com/sc/dp"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class TestJobDeployTempCredsIT extends BaseIT {

  private static final String TEST_JOB_NAME =
      JobExecutionUtil.generateJobName(TestJobDeployTempCredsIT.class.getSimpleName());

  @Autowired DockerRegistryService dockerRegistryService;

  @Autowired AWSCredentialsService awsCredentialsService;

  @Autowired EcrRegistryInterface ecrRegistryInterface;

  @Value("${datajobs.docker.repositoryUrl}")
  private String dockerRepositoryUrl;

  @Value("datajobs.aws.serviceAccountAccessKeyId")
  private String iamServiceAccountAccessKeyId;

  @Value("datajobs.aws.serviceAccountSecretAccessKey")
  private String iamUserServiceAccountSecretAccessKey;

  private AWSCredentialsService.AWSCredentialsDTO credentialsDTO;
  private AmazonECR ecrClient;
  private String repositoryName;

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
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

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
                                    TEST_TEAM_NAME, TEST_JOB_NAME)))));
    // Check authentication credentials are filled properly before continuing test.
    Assertions.assertFalse(iamServiceAccountAccessKeyId.isBlank());
    Assertions.assertFalse(iamUserServiceAccountSecretAccessKey.isBlank());

    this.repositoryName = dockerRepositoryUrl + "/" + TEST_JOB_NAME;
    this.credentialsDTO = awsCredentialsService.createTemporaryCredentials();
    this.ecrClient =
        AmazonECRClientBuilder.standard()
            .withCredentials(ecrRegistryInterface.createStaticCredentialsProvider(credentialsDTO))
            .withRegion(credentialsDTO.region())
            .build();
  }

  @Test
  public void testDeployment() throws Exception {
    // Take the job zip as byte array
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    // Execute job upload with proper user
    MvcResult jobUploadResult =
        mockMvc
            .perform(
                post(String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                    .with(user("user"))
                    .content(jobZipBinary)
                    .contentType(MediaType.APPLICATION_OCTET_STREAM))
            .andExpect(status().isOk())
            .andReturn();

    DataJobVersion testDataJobVersion =
        new ObjectMapper()
            .readValue(jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
    Assertions.assertNotNull(testDataJobVersion);

    String testJobVersionSha = testDataJobVersion.getVersionSha();

    var jobUri = dockerRegistryService.dataJobImage(TEST_JOB_NAME, testJobVersionSha);

    Assertions.assertFalse(dockerRegistryService.dataJobImageExists(jobUri, credentialsDTO));

    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

    // Setup
    String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

    // Execute build and deploy job
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    await()
        .atMost(10, TimeUnit.MINUTES)
        .with()
        .pollInterval(30, TimeUnit.SECONDS)
        .untilAsserted(
            () ->
                Assertions.assertTrue(
                    dockerRegistryService.dataJobImageExists(jobUri, credentialsDTO)));

    String jobDeploymentName = JobImageDeployer.getCronJobName(TEST_JOB_NAME);

    // Verify job deployment created
    Optional<JobDeploymentStatus> cronJobOptional =
        dataJobsKubernetesService.readCronJob(jobDeploymentName);
    Assertions.assertTrue(cronJobOptional.isPresent());

    // Re-deploy job
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());

    // Make sure same image still exists. Wait 1 minute for update method to finish before checking.
    await()
        .atMost(3, TimeUnit.MINUTES)
        .pollDelay(Duration.ofMinutes(1))
        .pollInterval(30, TimeUnit.SECONDS)
        .untilAsserted(
            () ->
                Assertions.assertTrue(
                    dockerRegistryService.dataJobImageExists(jobUri, credentialsDTO)));

    // Making sure only one image present, even though job was redeployed.
    DescribeImagesRequest countImagesRequest =
        new DescribeImagesRequest()
            .withRepositoryName(ecrRegistryInterface.extractImageRepositoryTag(repositoryName));
    var response = ecrClient.describeImages(countImagesRequest).getImageDetails();
    Assertions.assertEquals(1, response.size(), "Expecting only one image");
  }

  @AfterEach
  public void deleteImage() {

    // delete repository and images
    DeleteRepositoryRequest request =
        new DeleteRepositoryRequest()
            .withRepositoryName(ecrRegistryInterface.extractImageRepositoryTag(repositoryName))
            .withForce(true); // Set force to true to delete the repository even if it's not empty.

    ecrClient.deleteRepository(request);
  }

  @AfterEach
  public void deleteDataJob() throws Exception {
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user")))
        .andExpect(status().isOk());
  }
}
