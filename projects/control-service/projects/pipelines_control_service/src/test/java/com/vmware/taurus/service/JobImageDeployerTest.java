/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.credentials.JobCredentialsService;
import com.vmware.taurus.service.deploy.*;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.Map;

public class JobImageDeployerTest {

  private JobImageDeployer jobImageDeployer;
  private DataJob dataJob;
  private JobDeployment jobDeployment;

  private JobCredentialsService jobCredentialsService;
  private DataJobsKubernetesService dataJobsKubernetesService;
  private VdkOptionsReader vdkOptionsReader;
  private DataJobDefaultConfigurations dataJobDefaultConfigurations;
  private DeploymentProgress deploymentProgress;
  private KubernetesResources kubernetesResources;
  private JobCommandProvider jobCommandProvider;

  @BeforeEach
  public void setUp() {
    jobCredentialsService = Mockito.mock(JobCredentialsService.class);
    dataJobsKubernetesService = Mockito.mock(DataJobsKubernetesService.class);
    vdkOptionsReader = Mockito.mock(VdkOptionsReader.class);
    dataJobDefaultConfigurations = Mockito.mock(DataJobDefaultConfigurations.class);
    deploymentProgress = Mockito.mock(DeploymentProgress.class);
    kubernetesResources = Mockito.mock(KubernetesResources.class);
    jobCommandProvider = Mockito.mock(JobCommandProvider.class);

    jobImageDeployer =
        new JobImageDeployer(
            jobCredentialsService,
            dataJobsKubernetesService,
            vdkOptionsReader,
            dataJobDefaultConfigurations,
            deploymentProgress,
            kubernetesResources,
            jobCommandProvider);
  }

  @Test
  public void testScheduleLabelsAnnotations() {
    // prepare test class
    dataJob = new DataJob();
    dataJob.setName("TestDataJob");
    dataJob.setJobConfig(new JobConfig());
    dataJob.getJobConfig().setSchedule("schedule string");

    jobDeployment = new JobDeployment();
    jobDeployment.setImageName("TestImageName");
    jobDeployment.setGitCommitSha("testVersionString");
    jobDeployment.setEnabled(false);
    // mock behaviour so we reach tested (private) functionality
    Mockito.when(jobCredentialsService.getJobPrincipalName(Mockito.anyString()))
        .thenReturn("testPrincipalString");
    Mockito.when(vdkOptionsReader.readVdkOptions(Mockito.anyString())).thenReturn(new HashMap<>());
    Mockito.when(dataJobDefaultConfigurations.dataJobLimits())
        .thenReturn(new KubernetesService.Resources("1.2", "200"));
    Mockito.when(dataJobDefaultConfigurations.dataJobRequests())
        .thenReturn(new KubernetesService.Resources("1.5", "250"));
    Mockito.when(kubernetesResources.dataJobInitContainerLimits())
        .thenReturn(new KubernetesService.Resources("1.5", "200"));
    Mockito.when(kubernetesResources.dataJobInitContainerRequests())
        .thenReturn(new KubernetesService.Resources("1.5", "200"));

    var annotationCaptor = ArgumentCaptor.forClass(Map.class);
    var labelCaptor = ArgumentCaptor.forClass(Map.class);
    try {
      // capture labels from method.
      Mockito.doNothing()
          .when(dataJobsKubernetesService)
          .createCronJob(
              Mockito.anyString(),
              Mockito.anyString(),
              Mockito.anyMap(),
              Mockito.anyString(),
              Mockito.anyBoolean(),
              Mockito.anyList(),
              Mockito.any(),
              Mockito.any(),
              Mockito.any(),
              Mockito.any(),
              Mockito.anyList(),
              Mockito.anyMap(),
              Mockito.anyMap(),
              annotationCaptor.capture(),
              labelCaptor.capture(),
              Mockito.anyList());
      // execute public method.
      jobImageDeployer.scheduleJob(dataJob, jobDeployment, false, "lastDeployedBy");
      // verify we called the method only once.
      Mockito.verify(dataJobsKubernetesService)
          .createCronJob(
              Mockito.anyString(),
              Mockito.anyString(),
              Mockito.anyMap(),
              Mockito.anyString(),
              Mockito.anyBoolean(),
              Mockito.anyList(),
              Mockito.any(),
              Mockito.any(),
              Mockito.any(),
              Mockito.any(),
              Mockito.anyList(),
              Mockito.anyMap(),
              Mockito.anyMap(),
              Mockito.anyMap(),
              Mockito.anyMap(),
              Mockito.anyList());
      // extract labels/annotations from call
      var labels = labelCaptor.getValue();
      var annotations = annotationCaptor.getValue();
      // check everything was as expected
      Assertions.assertEquals(3, labels.size(), "Expecting three labels");
      Assertions.assertEquals(6, annotations.size(), "Expecting six annotations");

      var jobName = labels.get(JobLabel.NAME.getValue());
      var jobVersion = labels.get(JobLabel.VERSION.getValue());
      var jobType = labels.get(JobLabel.TYPE.getValue());

      Assertions.assertEquals("TestDataJob", jobName);
      Assertions.assertEquals("testVersionString", jobVersion);
      Assertions.assertEquals("DataJob", jobType);

      var schedule = annotations.get(JobAnnotation.SCHEDULE.getValue());
      var deployedBy = annotations.get(JobAnnotation.DEPLOYED_BY.getValue());
      var deployedDate = annotations.get(JobAnnotation.DEPLOYED_DATE.getValue());
      var startedBy = annotations.get(JobAnnotation.STARTED_BY.getValue());
      var executionType = annotations.get(JobAnnotation.EXECUTION_TYPE.getValue());
      var unscheduled = annotations.get(JobAnnotation.UNSCHEDULED.getValue());

      Assertions.assertEquals("schedule string", schedule);
      Assertions.assertEquals("lastDeployedBy", deployedBy);
      Assertions.assertEquals(
          OffsetDateTime.now().toString().substring(0, 10),
          deployedDate.toString().substring(0, 10),
          "Testing if date is the same, we cannot be precise down to the millisecond.");
      Assertions.assertEquals("scheduled/runtime", startedBy);
      Assertions.assertEquals("scheduled", executionType);
      Assertions.assertEquals("false", unscheduled);

    } catch (ApiException e) {
      e.printStackTrace();
      Assertions.fail(e);
    }
  }
}
