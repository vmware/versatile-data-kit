/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.model.JobDeployment;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.models.V1Container;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
public class JobImageDeployerTest {

  private static final String TEST_JOB_NAME = "test-job-name";
  private static final String TEST_CRONJOB_NAME = TEST_JOB_NAME;
  private static final String TEST_JOB_IMAGE_NAME = "test-job-image-name";
  private static final String TEST_JOB_SCHEDULE = "*/5 * * * *";
  private static final String TEST_BUILDER_JOB_NAME = "builder-test-job-name";
  private static final Map<String, String> TEST_VDK_OPTS =
      Map.of("testOptKey", "testOptVal", "VDK_KEYTAB_PRINCIPAL", "pa__view_test-job-name_taurus");
  private static final String TEST_PRINCIPAL_NAME = "pa__view_test-job-name_taurus";

  @Mock private DataJobsKubernetesService kubernetesService;

  @Mock private VdkOptionsReader vdkOptionsReader;

  @Mock private DeploymentProgress deploymentProgress;

  @Mock private DataJobDefaultConfigurations defaultConfigurations;

  @Mock private JobCredentialsService jobCredentialsService;

  @Mock private KubernetesResources kubernetesResources;

  @Spy private JobCommandProvider jobCommandProvider; // We need this to inject it into the deployer

  @InjectMocks private JobImageDeployer jobImageDeployer;

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

    Mockito.when(vdkOptionsReader.readVdkOptions(TEST_JOB_NAME)).thenReturn(TEST_VDK_OPTS);
    Mockito.when(jobCredentialsService.getJobPrincipalName(TEST_JOB_NAME))
        .thenReturn(TEST_PRINCIPAL_NAME);

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
  public void test_scheduleJobMonitoring() throws ApiException, IOException, InterruptedException {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setImageName("image");

    when(kubernetesService.listCronJobs()).thenReturn(Set.of(TEST_CRONJOB_NAME));
    doThrow(
            new ApiException(
                "foo",
                422,
                Collections.emptyMap(),
                "{\"kind\":\"Status\",\"apiVersion\":\"v1\",\"metadata\":{},\"status\":\"Failure\",\"message\":\"CronJob.batch"
                    + " \\\"foo\\\" is invalid: spec.schedule: Invalid value: \\\"a * * * *\\\":"
                    + " Failed to parse int from a: strconv.Atoi: parsing \\\"a\\\": invalid"
                    + " syntax\",\"reason\":"
                    + "\"Invalid\",\"details\":{\"name\":\"foo\",\"group\":\"batch\",\"kind\":\"CronJob\",\"causes\":[{\"reason\":\"FieldValueInvalid\",\"message\":\"Invalid"
                    + " value: \\\"a * * * *\\\": Failed to parse int from a: strconv.Atoi: parsing"
                    + " \\\"a\\\": invalid syntax\",\"field\":\"spec.schedule\"}]},\"code\":422}"))
        .when(kubernetesService)
        .updateCronJob(
            anyString(),
            anyString(),
            anyMap(),
            anyString(),
            anyBoolean(),
            anyList(),
            any(KubernetesService.Resources.class),
            any(KubernetesService.Resources.class),
            any(V1Container.class),
            any(V1Container.class),
            any(List.class),
            anyMap(),
            anyMap(),
            anyMap(),
            anyMap(),
            anyList());

    jobImageDeployer.scheduleJob(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME);
    verify(deploymentProgress)
        .failed(any(), any(), eq(DeploymentStatus.USER_ERROR), anyString(), anyBoolean());
  }

  /** Test that the job container name is the same as the data job name. */
  @Test
  public void testJobContainerName() throws ApiException {
    var jobDeployment = new JobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setImageName("image");

    jobImageDeployer.scheduleJob(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME);

    ArgumentCaptor<V1Container> containerCaptor = ArgumentCaptor.forClass(V1Container.class);
    verify(kubernetesService)
        .createCronJob(
            anyString(),
            anyString(),
            anyMap(),
            anyString(),
            anyBoolean(),
            anyList(),
            any(KubernetesService.Resources.class),
            any(KubernetesService.Resources.class),
            containerCaptor.capture(),
            any(V1Container.class),
            anyList(),
            anyMap(),
            anyMap(),
            anyMap(),
            anyMap(),
            anyList());
    var jobContainer = containerCaptor.getValue();
    Assertions.assertEquals(testDataJob.getName(), jobContainer.getName());
  }

  @Test
  public void testJobNoSchedule() throws ApiException {
    JobConfig jobConfig = new JobConfig();
    jobConfig.setSchedule("");
    testDataJob = new DataJob();
    testDataJob.setName(TEST_JOB_NAME);
    testDataJob.setJobConfig(jobConfig);

    var jobDeployment = new JobDeployment();
    jobDeployment.setDataJobName(TEST_JOB_NAME);
    jobDeployment.setGitCommitSha("test-commit");
    jobDeployment.setEnabled(true);
    jobDeployment.setImageName("image");

    jobImageDeployer.scheduleJob(testDataJob, jobDeployment, true, TEST_PRINCIPAL_NAME);

    ArgumentCaptor<String> scheduleCaptor = ArgumentCaptor.forClass(String.class);
    verify(kubernetesService)
        .createCronJob(
            anyString(),
            anyString(),
            anyMap(),
            scheduleCaptor.capture(),
            anyBoolean(),
            anyList(),
            any(KubernetesService.Resources.class),
            any(KubernetesService.Resources.class),
            any(V1Container.class),
            any(V1Container.class),
            anyList(),
            anyMap(),
            anyMap(),
            anyMap(),
            anyMap(),
            anyList());
    Assertions.assertEquals("0 0 30 2 *", scheduleCaptor.getValue());
    Assertions.assertEquals("", testDataJob.getJobConfig().getSchedule());
  }
}
