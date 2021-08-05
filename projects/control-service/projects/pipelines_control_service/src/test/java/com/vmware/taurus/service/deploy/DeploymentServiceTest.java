/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import com.vmware.taurus.service.monitoring.DeploymentMonitor;
import com.vmware.taurus.service.notification.DataJobNotification;
import io.kubernetes.client.ApiException;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.MockitoJUnitRunner;

import java.io.IOException;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@RunWith(MockitoJUnitRunner.class)
public class DeploymentServiceTest {

   private static final String OP_ID = "c00b40dcc9904ae6";
   private static final String TEST_JOB_NAME = "test-job-name";
   private static final String TEST_CRONJOB_NAME = TEST_JOB_NAME + "-latest";
   private static final String TEST_JOB_IMAGE_NAME = "test-job-image-name";
   private static final String TEST_JOB_SCHEDULE = "*/5 * * * *";
   private static final String TEST_BUILDER_JOB_NAME = "builder-test-job-name";
   private static final Map<String, String> TEST_VDK_OPTS = Map.of(
           "testOptKey", "testOptVal", "VDK_KEYTAB_PRINCIPAL", "pa__view_test-job-name_taurus");
   private static final String TEST_PRINCIPAL_NAME = "pa__view_test-job-name_taurus";

   @Mock
   private DataJobsKubernetesService kubernetesService;

   @Mock
   private DockerRegistryService dockerRegistryService;

   @Mock
   private DataJobNotification dataJobNotification;

   @Mock
   private JobImageBuilder jobImageBuilder;

   @Mock
   private VdkOptionsReader vdkOptionsReader;

   @Mock
   private DeploymentMonitor deploymentMonitor;

   @Mock
   private DataJobDefaultConfigurations defaultConfigurations;

   @Mock
   private KubernetesResources kubernetesResources;

   @Mock
   private JobCredentialsService jobCredentialsService;

   @InjectMocks
   private DeploymentProgress deploymentProgress;

   @InjectMocks
   private JobImageDeployer jobImageDeployer;

   @InjectMocks
   private DeploymentService deploymentService;

   @InjectMocks
   private OperationContext operationContext;

   private DataJob testDataJob;

   @Before
   public void setUp() {

      // We use lenient here as the mocked methods are indirectly invoked by the JobImageDeployer#updateCronJob
      // and mockito renders them unnecessary mocks and fails the tests. If we remove the lenient tests will
      // throw NullPointerException
      Mockito.lenient().when(kubernetesResources.builderLimits())
              .thenReturn(new KubernetesService.Resources("1000m","1000Mi"));
      Mockito.lenient().when(kubernetesResources.builderRequests())
              .thenReturn(new KubernetesService.Resources("250m","250Mi"));
      Mockito.lenient().when(kubernetesResources.dataJobInitContainerLimits())
              .thenReturn(new KubernetesService.Resources("100m","100Mi"));
      Mockito.lenient().when(kubernetesResources.dataJobInitContainerRequests())
              .thenReturn(new KubernetesService.Resources("100m","100Mi"));

      deploymentService = new DeploymentService(dockerRegistryService,
              deploymentProgress, jobImageBuilder, jobImageDeployer, operationContext);

      Mockito.when(vdkOptionsReader.readVdkOptions(TEST_JOB_NAME)).thenReturn(TEST_VDK_OPTS);
      Mockito.when(jobCredentialsService.getJobPrincipalName(TEST_JOB_NAME)).thenReturn(TEST_PRINCIPAL_NAME);

      when(defaultConfigurations.dataJobRequests())
              .thenReturn(new KubernetesService.Resources("500m", "1G"));
      when(defaultConfigurations.dataJobLimits())
              .thenReturn(new KubernetesService.Resources("2000m", "1G"));

      JobConfig jobConfig = new JobConfig();
      jobConfig.setSchedule(TEST_JOB_SCHEDULE);
      testDataJob = new DataJob();
      testDataJob.setName(TEST_JOB_NAME);
      testDataJob.setJobConfig(jobConfig);
   }

   @Test
   public void updateDeployment_newDeploymentCreated() throws ApiException, IOException, InterruptedException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(true);

      when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit")).thenReturn(TEST_JOB_IMAGE_NAME);
      when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true)).thenReturn(true);

      deploymentService.updateDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

      verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
      verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
      verify(kubernetesService).createCronJob(eq(TEST_CRONJOB_NAME), eq(TEST_JOB_IMAGE_NAME), any(),
            eq(TEST_JOB_SCHEDULE), eq(true), any(), any(), any(),
              any(),
              any(), any(), any(), any(), any(), any());
      verify(deploymentMonitor).recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.SUCCESS);
      verify(dataJobNotification).notifyJobDeploySuccess(testDataJob.getJobConfig());
   }

   @Test
   public void updateDeployment_existingDeploymentUpdated() throws ApiException, IOException, InterruptedException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(true);

      when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit")).thenReturn(TEST_JOB_IMAGE_NAME);
      when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true)).thenReturn(true);
      when(kubernetesService.listCronJobs()).thenReturn(Set.of(TEST_CRONJOB_NAME));

      deploymentService.updateDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

      verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
      verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
      verify(kubernetesService).updateCronJob(eq(TEST_CRONJOB_NAME), eq(TEST_JOB_IMAGE_NAME), any(),
            eq(TEST_JOB_SCHEDULE), eq(true), any(), any(), any(), any(), any(), any(), any(), any(), any(), any());
      verify(deploymentMonitor).recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.SUCCESS);
      verify(dataJobNotification).notifyJobDeploySuccess(testDataJob.getJobConfig());
   }


   @Test
   public void updateDeployment_failedToBuildImage_deploymentSkipped() throws ApiException, IOException, InterruptedException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(true);

      when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit")).thenReturn(TEST_JOB_IMAGE_NAME);
      when(jobImageBuilder.buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true)).thenReturn(false);

      deploymentService.updateDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

      verify(dockerRegistryService).dataJobImage(TEST_JOB_NAME, "test-commit");
      verify(jobImageBuilder).buildImage(TEST_JOB_IMAGE_NAME, testDataJob, jobDeployment, true);
      verify(kubernetesService, never()).updateCronJob(anyString(), anyString(), any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
      verify(kubernetesService, never()).createCronJob(anyString(), anyString(), any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
      verify(dataJobNotification, never()).notifyJobDeploySuccess(testDataJob.getJobConfig());
      // The builder class is responsible for sending metrics and notifications on failed build.
      verify(deploymentMonitor, never()).recordDeploymentStatus(any(), any());
      verify(dataJobNotification, never()).notifyJobDeployError(eq(testDataJob.getJobConfig()), any(), any());
   }

   @Test
   public void updateDeployment_exceptionOccurred_errorNotificationSent() throws ApiException {
      when(dockerRegistryService.dataJobImage(TEST_JOB_NAME, "test-commit"))
            .thenThrow(new RuntimeException("test-exception"));

      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(true);

      deploymentService.updateDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME, OP_ID);

      verify(kubernetesService, never()).updateCronJob(anyString(), anyString(),  any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
      verify(kubernetesService, never()).createCronJob(anyString(), anyString(),  any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
      verify(deploymentMonitor).recordDeploymentStatus(jobDeployment.getDataJobName(), DeploymentStatus.PLATFORM_ERROR);
      verify(dataJobNotification).notifyJobDeployError(eq(testDataJob.getJobConfig()), any(), any());
   }

   @Test
   public void enableDeployment() throws ApiException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setImageName(TEST_JOB_IMAGE_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(false);

      deploymentService.enableDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME);

      verify(kubernetesService).createCronJob(eq(TEST_CRONJOB_NAME), eq(TEST_JOB_IMAGE_NAME), any(),
            eq(TEST_JOB_SCHEDULE), eq(true), any(), any(), any(), any(), any(), any(), any(), any(), any(), any());
   }

   @Test
   public void enableDeployment_deploymentDisabled() throws ApiException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setDataJobName(TEST_JOB_NAME);
      jobDeployment.setImageName(TEST_JOB_IMAGE_NAME);
      jobDeployment.setGitCommitSha("test-commit");
      jobDeployment.setEnabled(true);

      deploymentService.enableDeployment(testDataJob, jobDeployment, false, TEST_PRINCIPAL_NAME);

      verify(kubernetesService).createCronJob(eq(TEST_CRONJOB_NAME), eq(TEST_JOB_IMAGE_NAME), any(),
            eq(TEST_JOB_SCHEDULE), eq(false), any(), any(), any(), any(), any(), any(), any(), any(), any(), any());
   }

   @Test
   public void enableDeployment_sameEnabledStatus_updateSkipped() throws ApiException {
      JobDeployment jobDeployment = new JobDeployment();
      jobDeployment.setEnabled(true);

      deploymentService.enableDeployment(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME);

      verify(kubernetesService, never()).updateCronJob(any(), any(), any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
      verify(kubernetesService, never()).createCronJob(any(), any(), any(), anyString(), anyBoolean(),
              any(), any(), any(), any(), any(), any(), any());
   }

   @Test
   public void deleteDeployment() throws ApiException {

      when(kubernetesService
            .listCronJobs())
            .thenReturn(Set.of(TEST_CRONJOB_NAME));
      when(kubernetesService.readCronJob(TEST_CRONJOB_NAME)).thenReturn(Optional.of(new JobDeploymentStatus()));

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
