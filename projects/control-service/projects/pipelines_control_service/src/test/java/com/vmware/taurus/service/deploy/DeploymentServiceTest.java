/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.datajobs.TestUtils;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.monitoring.DeploymentMonitor;
import com.vmware.taurus.service.monitoring.DataJobMetrics;
import com.vmware.taurus.service.notification.DataJobNotification;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
public class DeploymentServiceTest {

  private static final String OP_ID = "c00b40dcc9904ae6";
  private static final String TEST_JOB_NAME = "test-job-name";
  private static final String TEST_CRONJOB_NAME = TEST_JOB_NAME;
  private static final String TEST_JOB_IMAGE_NAME = "test-job-image-name";
  private static final String TEST_JOB_SCHEDULE = "*/5 * * * *";
  private static final String TEST_BUILDER_JOB_NAME = "builder-test-job-name";
  private static final Map<String, String> TEST_VDK_OPTS =
      Map.of("testOptKey", "testOptVal", "VDK_KEYTAB_PRINCIPAL", "pa__view_test-job-name_taurus");
  private static final String TEST_PRINCIPAL_NAME = "pa__view_test-job-name_taurus";

  @Mock private DataJobsKubernetesService kubernetesService;

  @Mock private DockerRegistryService dockerRegistryService;

  @Mock private DataJobMetrics dataJobMetrics;

  @Mock private DataJobNotification dataJobNotification;

  @Mock private JobImageBuilder jobImageBuilder;

  @Mock private VdkOptionsReader vdkOptionsReader;

  @Mock private DeploymentMonitor deploymentMonitor;

  @Mock private DataJobDefaultConfigurations defaultConfigurations;

  @Mock private KubernetesResources kubernetesResources;

  @Mock private JobCredentialsService jobCredentialsService;

  @Spy private JobCommandProvider jobCommandProvider; // We need this to inject it into the deployer

  @InjectMocks private DeploymentProgress deploymentProgress;

  @InjectMocks private JobImageDeployer jobImageDeployer;

  @InjectMocks private DeploymentService deploymentService;

  @InjectMocks private OperationContext operationContext;

  @Mock private JobsRepository jobsRepository;

  private DataJob testDataJob;

  @BeforeEach
  public void setUp() {

    // We use lenient here as the mocked methods are indirectly invoked by the
    // JobImageDeployer#updateCronJob
    // and mockito renders them unnecessary mocks and fails the tests. If we remove the lenient
    // tests will
    // throw NullPointerException
    Mockito.lenient()
        .when(kubernetesResources.builderLimits())
        .thenReturn(new KubernetesService.Resources("1000m", "1000Mi"));
    Mockito.lenient()
        .when(kubernetesResources.builderRequests())
        .thenReturn(new KubernetesService.Resources("250m", "250Mi"));
    Mockito.lenient()
        .when(kubernetesResources.dataJobInitContainerLimits())
        .thenReturn(new KubernetesService.Resources("100m", "100Mi"));
    Mockito.lenient()
        .when(kubernetesResources.dataJobInitContainerRequests())
        .thenReturn(new KubernetesService.Resources("100m", "100Mi"));

    deploymentService =
        new DeploymentService(
            dockerRegistryService,
            deploymentProgress,
            jobImageBuilder,
            jobImageDeployer,
            operationContext,
            jobsRepository,
            dataJobMetrics);

    Mockito.when(vdkOptionsReader.readVdkOptions(TEST_JOB_NAME)).thenReturn(TEST_VDK_OPTS);
    Mockito.when(jobCredentialsService.getJobPrincipalName(TEST_JOB_NAME))
        .thenReturn(TEST_PRINCIPAL_NAME);

    when(defaultConfigurations.dataJobRequests())
        .thenReturn(new KubernetesService.Resources("500m", "1G"));
    when(defaultConfigurations.dataJobLimits())
        .thenReturn(new KubernetesService.Resources("2000m", "1G"));

    JobConfig jobConfig = new JobConfig();
    jobConfig.setTeam(TestUtils.TEST_TEAM_NAME);
    jobConfig.setSchedule(TEST_JOB_SCHEDULE);
    testDataJob = new DataJob();
    testDataJob.setName(TEST_JOB_NAME);
    testDataJob.setJobConfig(jobConfig);

    when(kubernetesService.readCronJob(TEST_CRONJOB_NAME))
        .thenReturn(Optional.of(TestUtils.getJobDeploymentStatus()));
  }

  @Test
  public void updateDeployment_newDeploymentCreated()
      throws ApiException, IOException, InterruptedException {
    JobDeployment jobDeployment = TestUtils.getJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);

    when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit"))
        .thenReturn(TEST_JOB_IMAGE_NAME);
    when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true))
        .thenReturn(true);

    deploymentService.updateDeployment(
        testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

    verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
    verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
    verify(kubernetesService)
        .createCronJob(
            eq(TEST_CRONJOB_NAME),
            eq(TEST_JOB_IMAGE_NAME),
            any(),
            eq(TEST_JOB_SCHEDULE),
            eq(true),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyList());
    verify(deploymentMonitor)
        .recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.SUCCESS);
    verify(dataJobNotification).notifyJobDeploySuccess(testDataJob.getJobConfig());

    var dataJobCaptor = ArgumentCaptor.forClass(DataJob.class);
    verify(jobsRepository).save(dataJobCaptor.capture());
    assertEquals(true, dataJobCaptor.getValue().getEnabled());
  }

  @Test
  public void updateDeployment_existingDeploymentUpdated()
      throws ApiException, IOException, InterruptedException {
    JobDeployment jobDeployment = TestUtils.getJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    testDataJob.setEnabled(true);

    when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit"))
        .thenReturn(TEST_JOB_IMAGE_NAME);
    when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true))
        .thenReturn(true);
    when(kubernetesService.listCronJobs()).thenReturn(Set.of(TEST_CRONJOB_NAME));

    deploymentService.updateDeployment(
        testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

    verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
    verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
    verify(kubernetesService)
        .updateCronJob(
            eq(TEST_CRONJOB_NAME),
            eq(TEST_JOB_IMAGE_NAME),
            any(),
            eq(TEST_JOB_SCHEDULE),
            eq(true),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyList());
    verify(deploymentMonitor)
        .recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.SUCCESS);
    verify(dataJobNotification).notifyJobDeploySuccess(testDataJob.getJobConfig());

    verify(jobsRepository, never()).save(any());
  }

  @Test
  public void updateDeployment_failedToBuildImage_deploymentSkipped()
      throws ApiException, IOException, InterruptedException {
    JobDeployment jobDeployment = TestUtils.getJobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);

    when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit"))
        .thenReturn(TEST_JOB_IMAGE_NAME);
    when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true))
        .thenReturn(false);

    deploymentService.updateDeployment(
        testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

    verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
    verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
    verify(kubernetesService, never())
        .updateCronJob(
            anyString(),
            anyString(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(kubernetesService, never())
        .createCronJob(
            anyString(),
            anyString(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(dataJobNotification, never()).notifyJobDeploySuccess(testDataJob.getJobConfig());
    // The builder class is responsible for sending metrics and notifications on failed build.
    verify(deploymentMonitor, never()).recordDeploymentStatus(any(), any());
    verify(dataJobNotification, never())
        .notifyJobDeployError(eq(testDataJob.getJobConfig()), any(), any());
  }

  @Test
  public void updateDeployment_exceptionOccurred_errorNotificationSent() throws ApiException {
    when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit"))
        .thenThrow(new RuntimeException("test-exception"));

    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);

    deploymentService.updateDeployment(
        testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

    verify(kubernetesService, never())
        .updateCronJob(
            anyString(),
            anyString(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(kubernetesService, never())
        .createCronJob(
            anyString(),
            anyString(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(deploymentMonitor)
        .recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.PLATFORM_ERROR);
    verify(dataJobNotification).notifyJobDeployError(eq(testDataJob.getJobConfig()), any(), any());
  }

  @Test
  public void patchDeployment() throws ApiException {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(testDataJob.getJobConfig().getTeam());
    jobDeployment.setDataJobName(testDataJob.getName());
    jobDeployment.setEnabled(true);

    deploymentService.patchDeployment(testDataJob, jobDeployment);

    verify(kubernetesService)
        .createCronJob(
            eq(TEST_CRONJOB_NAME),
            eq(TEST_JOB_IMAGE_NAME),
            any(),
            eq(TEST_JOB_SCHEDULE),
            eq(true),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            anyList());

    var dataJobCaptor = ArgumentCaptor.forClass(DataJob.class);
    verify(jobsRepository).save(dataJobCaptor.capture());
    assertEquals(true, dataJobCaptor.getValue().getEnabled());
  }

  @Test
  public void patchDeployment_deploymentEnabled_shouldNotClearTerminationStatus()
      throws ApiException {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(testDataJob.getJobConfig().getTeam());
    jobDeployment.setDataJobName(testDataJob.getName());
    jobDeployment.setEnabled(true);

    deploymentService.patchDeployment(testDataJob, jobDeployment);

    verify(dataJobMetrics, times(0))
        .clearTerminationStatusAndDelayNotifGauges(testDataJob.getName());
  }

  @Test
  public void patchDeployment_deploymentDisabled_shouldClearTerminationStatus()
      throws ApiException {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(testDataJob.getJobConfig().getTeam());
    jobDeployment.setDataJobName(testDataJob.getName());
    jobDeployment.setEnabled(false);

    deploymentService.patchDeployment(testDataJob, jobDeployment);

    verify(dataJobMetrics, times(1))
        .clearTerminationStatusAndDelayNotifGauges(testDataJob.getName());
  }

  @Test
  public void enableDeployment_sameEnabledStatus_updateSkipped() throws ApiException {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(testDataJob.getJobConfig().getTeam());
    jobDeployment.setDataJobName(testDataJob.getName());
    jobDeployment.setEnabled(true);

    deploymentService.patchDeployment(testDataJob, jobDeployment);

    verify(kubernetesService, never())
        .updateCronJob(
            any(),
            any(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
    verify(kubernetesService, never())
        .createCronJob(
            any(),
            any(),
            any(),
            anyString(),
            anyBoolean(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any(),
            any());
  }

  @Test
  public void deleteDeployment() throws ApiException {

    when(kubernetesService.listCronJobs()).thenReturn(Set.of(TEST_CRONJOB_NAME));
    when(kubernetesService.readCronJob(TEST_CRONJOB_NAME))
        .thenReturn(Optional.of(new JobDeploymentStatus()));

    deploymentService.deleteDeployment(TEST_JOB_NAME);

    verify(jobImageBuilder).cancelBuildingJob(TEST_JOB_NAME);
    verify(kubernetesService).deleteCronJob(any());
  }

  @Test
  public void deleteDeployment_notFound_skipped() throws ApiException {
    when(kubernetesService.readCronJob(TEST_CRONJOB_NAME)).thenReturn(Optional.empty());

    deploymentService.deleteDeployment(TEST_JOB_NAME);

    verify(kubernetesService, never()).deleteJob(any());
    verify(kubernetesService, never()).deleteCronJob(any());
    verify(deploymentMonitor).recordDeploymentStatus(any(), eq(DeploymentStatus.SUCCESS));
  }
}
