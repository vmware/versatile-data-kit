/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.AWSCredentialsService;
import com.vmware.taurus.service.credentials.AWSCredentialsService.AWSCredentialsDTO;
import com.vmware.taurus.service.kubernetes.ControlKubernetesService;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DesiredDataJobDeployment;
import com.vmware.taurus.service.model.JobConfig;
import io.kubernetes.client.openapi.ApiException;
import java.io.IOException;
import java.util.Collections;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

@ExtendWith(MockitoExtension.class)
public class JobImageBuilderTest {
  private static final String TEST_JOB_NAME = "test-job-name";
  private static final String TEST_IMAGE_NAME = "test-image-name";
  private static final String TEST_BUILDER_IMAGE_NAME = "builder-test-job-name";
  private static final String TEST_BUILDER_LOGS = "test-logs";
  private static final String TEST_JOB_SCHEDULE = "*/5 * * * *";
  private static final String TEST_DB_DEFAULT_TYPE = "IMPALA";
  private static final String TEST_BUILDER_JOB_NAME = "builder-test-job-name";

  @Mock private ControlKubernetesService kubernetesService;

  @Mock private DockerRegistryService dockerRegistryService;

  @Mock private DeploymentNotificationHelper notificationHelper;

  @Mock private KubernetesResources kubernetesResources;

  @Mock private AWSCredentialsService awsCredentialsService;

  @Mock private SupportedPythonVersions supportedPythonVersions;

  @InjectMocks private JobImageBuilder jobImageBuilder;

  private DataJob testDataJob;

  @BeforeEach
  public void setUp() {
    ReflectionTestUtils.setField(jobImageBuilder, "dockerRepositoryUrl", "test-docker-repository");
    ReflectionTestUtils.setField(jobImageBuilder, "gitDataJobsBranch", "branch");
    ReflectionTestUtils.setField(jobImageBuilder, "registryType", "generic");
    ReflectionTestUtils.setField(jobImageBuilder, "builderJobExtraArgs", "");

    when(awsCredentialsService.createTemporaryCredentials())
        .thenReturn(new AWSCredentialsDTO("test", "test", "test", "test"));

    JobConfig jobConfig = new JobConfig();
    jobConfig.setDbDefaultType(TEST_DB_DEFAULT_TYPE);
    jobConfig.setSchedule(TEST_JOB_SCHEDULE);
    jobConfig.setTeam("test-team");
    testDataJob = new DataJob();
    testDataJob.setName(TEST_JOB_NAME);
    testDataJob.setJobConfig(jobConfig);
  }

  @Test
  public void buildImage_notExist_success() throws InterruptedException, ApiException, IOException {
    when(kubernetesService.listJobs()).thenReturn(Collections.emptySet());
    var builderJobResult =
        new KubernetesService.JobStatusCondition(true, "type", "test-reason", "test-message", 0);
    when(kubernetesService.watchJob(any(), anyInt(), any())).thenReturn(builderJobResult);
    when(supportedPythonVersions.getJobBaseImage(any())).thenReturn("python:3.7-slim");
    when(supportedPythonVersions.getBuilderImage(any())).thenReturn(TEST_BUILDER_IMAGE_NAME);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.7");

    var result = jobImageBuilder.buildImage("test-image", testDataJob, jobDeployment, null, true);

    verify(kubernetesService)
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());

    verify(kubernetesService).deleteJob(TEST_BUILDER_JOB_NAME);
    Assertions.assertTrue(result);
  }

  @Test
  public void buildImage_builderRunning_oldBuilderDeleted()
      throws InterruptedException, ApiException, IOException {
    when(dockerRegistryService.dataJobImageExists(eq(TEST_IMAGE_NAME), Mockito.any()))
        .thenReturn(false);
    when(kubernetesService.listJobs())
        .thenReturn(Set.of(TEST_BUILDER_IMAGE_NAME), Collections.emptySet());
    var builderJobResult =
        new KubernetesService.JobStatusCondition(true, "type", "test-reason", "test-message", 0);
    when(kubernetesService.watchJob(any(), anyInt(), any())).thenReturn(builderJobResult);
    when(supportedPythonVersions.getJobBaseImage(any())).thenReturn("python:3.7-slim");
    when(supportedPythonVersions.getBuilderImage(any())).thenReturn(TEST_BUILDER_IMAGE_NAME);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.7");

    var result =
        jobImageBuilder.buildImage(TEST_IMAGE_NAME, testDataJob, jobDeployment, null, true);

    verify(kubernetesService, times(2)).deleteJob(TEST_BUILDER_IMAGE_NAME);
    verify(kubernetesService)
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());
    Assertions.assertTrue(result);
  }

  @Test
  public void buildImage_imageExists_buildSkipped()
      throws InterruptedException, ApiException, IOException {
    when(dockerRegistryService.dataJobImageExists(eq(TEST_IMAGE_NAME), Mockito.any()))
        .thenReturn(true);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.7");

    var result =
        jobImageBuilder.buildImage(TEST_IMAGE_NAME, testDataJob, jobDeployment, null, true);

    verify(kubernetesService, never())
        .createJob(
            anyString(),
            anyString(),
            anyBoolean(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            anyString(),
            anyString());
    verify(notificationHelper, never())
        .verifyBuilderResult(anyString(), any(), any(), any(), anyString(), anyBoolean());
    Assertions.assertTrue(result);
  }

  @Test
  public void buildImage_jobFailed_failure()
      throws InterruptedException, ApiException, IOException {
    when(kubernetesService.listJobs()).thenReturn(Collections.emptySet());
    var builderJobResult =
        new KubernetesService.JobStatusCondition(false, "type", "test-reason", "test-message", 0);
    when(kubernetesService.watchJob(any(), anyInt(), any())).thenReturn(builderJobResult);
    when(kubernetesService.getPodLogs(TEST_BUILDER_JOB_NAME)).thenReturn(TEST_BUILDER_LOGS);
    when(supportedPythonVersions.getJobBaseImage(any())).thenReturn("python:3.7-slim");
    when(supportedPythonVersions.getBuilderImage(any())).thenReturn(TEST_BUILDER_IMAGE_NAME);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.7");

    var result = jobImageBuilder.buildImage("test-image", testDataJob, jobDeployment, null, true);

    verify(kubernetesService)
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());

    // verify(kubernetesService).deleteJob(TEST_BUILDER_JOB_NAME); // not called in case of an error
    verify(notificationHelper)
        .verifyBuilderResult(
            TEST_BUILDER_JOB_NAME,
            testDataJob,
            jobDeployment,
            builderJobResult,
            TEST_BUILDER_LOGS,
            true);
    Assertions.assertFalse(result);
  }

  @Test
  public void
      buildImage_deploymentDataJobBaseImageNullAndSupportedPythonVersions_shouldCreateCronjobUsingSupportedPythonVersions()
          throws InterruptedException, ApiException, IOException {
    when(kubernetesService.listJobs()).thenReturn(Collections.emptySet());
    var builderJobResult =
        new KubernetesService.JobStatusCondition(true, "type", "test-reason", "test-message", 0);
    when(kubernetesService.watchJob(any(), anyInt(), any())).thenReturn(builderJobResult);
    when(supportedPythonVersions.getJobBaseImage("3.11")).thenReturn("test-base-image");
    when(supportedPythonVersions.getBuilderImage(any())).thenReturn(TEST_BUILDER_IMAGE_NAME);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.11");

    ArgumentCaptor<Map<String, String>> captor = ArgumentCaptor.forClass(Map.class);

    var result = jobImageBuilder.buildImage("test-image", testDataJob, jobDeployment, null, true);

    verify(kubernetesService)
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            captor.capture(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());

    Map<String, String> capturedEnvs = captor.getValue();
    Assertions.assertEquals("test-base-image", capturedEnvs.get("BASE_IMAGE"));

    verify(kubernetesService).deleteJob(TEST_BUILDER_JOB_NAME);
    Assertions.assertTrue(result);
  }

  @Test
  public void buildImage_PythonVersionNull_shouldNotCreateCronjob()
      throws InterruptedException, ApiException, IOException {

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);

    var result = jobImageBuilder.buildImage("test-image", testDataJob, jobDeployment, null, true);

    verify(supportedPythonVersions, never()).isPythonVersionSupported("3.11");
    verify(supportedPythonVersions, never()).getJobBaseImage("3.11");

    verify(kubernetesService, never())
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());

    Assertions.assertFalse(result);
  }

  @Test
  public void buildImage_imageExistsAndEqualPythonVersions_shouldSkipBuild()
      throws InterruptedException, ApiException, IOException {
    when(dockerRegistryService.dataJobImageExists(eq(TEST_IMAGE_NAME), Mockito.any()))
        .thenReturn(true);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.7");

    ActualDataJobDeployment actualDataJobDeployment = new ActualDataJobDeployment();
    actualDataJobDeployment.setPythonVersion("3.7");

    var result =
        jobImageBuilder.buildImage(
            TEST_IMAGE_NAME, testDataJob, jobDeployment, actualDataJobDeployment, true);

    verify(kubernetesService, never())
        .createJob(
            anyString(),
            anyString(),
            anyBoolean(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            anyString(),
            anyString());
    verify(notificationHelper, never())
        .verifyBuilderResult(anyString(), any(), any(), any(), anyString(), anyBoolean());
    Assertions.assertTrue(result);
  }

  @Test
  public void buildImage_imageExistsAndDifferentPythonVersions_shouldSucceed()
      throws InterruptedException, ApiException, IOException {
    when(kubernetesService.listJobs()).thenReturn(Collections.emptySet());
    var builderJobResult =
        new KubernetesService.JobStatusCondition(true, "type", "test-reason", "test-message", 0);
    when(kubernetesService.watchJob(any(), anyInt(), any())).thenReturn(builderJobResult);
    when(supportedPythonVersions.getJobBaseImage(any())).thenReturn("python:3.7-slim");
    when(supportedPythonVersions.getBuilderImage(any())).thenReturn(TEST_BUILDER_IMAGE_NAME);

    DesiredDataJobDeployment jobDeployment = new DesiredDataJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setPythonVersion("3.8");

    ActualDataJobDeployment actualDataJobDeployment = new ActualDataJobDeployment();
    actualDataJobDeployment.setPythonVersion("3.7");

    var result =
        jobImageBuilder.buildImage(
            TEST_IMAGE_NAME, testDataJob, jobDeployment, actualDataJobDeployment, true);

    verify(kubernetesService)
        .createJob(
            eq(TEST_BUILDER_JOB_NAME),
            eq(TEST_BUILDER_IMAGE_NAME),
            eq(false),
            eq(false),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyLong(),
            anyLong(),
            anyLong(),
            any(),
            any());

    verify(kubernetesService).deleteJob(TEST_BUILDER_JOB_NAME);
    Assertions.assertTrue(result);
  }

  private static Map<String, Map<String, String>> generateSupportedPythonVersionsConf() {
    return Map.of(
        "3.10", Map.of("baseImage", "python:3.10-slim", "vdkImage", "test_vdk_image_3.10"),
        "3.11", Map.of("baseImage", "python:3.11-slim", "vdkImage", "test_vdk_image_3.11"));
  }
}
