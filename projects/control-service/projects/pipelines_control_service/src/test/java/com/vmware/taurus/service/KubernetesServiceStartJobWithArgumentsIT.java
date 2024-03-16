/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.deploy.JobCommandProvider;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.models.V1CronJob;
import io.kubernetes.client.openapi.models.V1JobSpec;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;

public class KubernetesServiceStartJobWithArgumentsIT {

  private KubernetesService kubernetesService;

  @BeforeEach
  public void getMockKubernetesServiceForVdkRunExtraArgsTests() throws Exception {
    BatchV1Api mockBatchV1 = Mockito.mock(BatchV1Api.class);

    kubernetesService =
        new DataJobsKubernetesService(
            "default", new ApiClient(), mockBatchV1, new JobCommandProvider());
    V1CronJob internalCronjobTemplate = getValidCronJobForVdkRunExtraArgsTests();

    kubernetesService =
        Mockito.spy(
            new DataJobsKubernetesService(
                "default", new ApiClient(), mockBatchV1, new JobCommandProvider()));
    Mockito.doNothing()
        .when(kubernetesService)
        .createNewJob(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any());

    Mockito.when(mockBatchV1.readNamespacedCronJob(any(), any(), any()))
        .thenReturn(internalCronjobTemplate);
  }

  @Test
  public void testStartCronJobWithExtraArgumentForVdkRun() {

    try {
      ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
      Map<String, Object> extraArgs = Map.of("argument1", "value1");
      kubernetesService.startNewCronJobExecution(
          "test-job", "test-id", new HashMap<>(), new HashMap<>(), extraArgs, "test-job");
      Mockito.verify(kubernetesService)
          .createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
      var capturedSpec = specCaptor.getValue();
      var capturedCommand =
          capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
      // check if command arg starts correctly
      Assertions.assertEquals(
          "export PYTHONPATH=$(python -c \"from distutils.sysconfig import get_python_lib;"
              + " print(get_python_lib())\"):/vdk/site-packages/ && /vdk/vdk run ./test-job"
              + " --arguments '{\"argument1\":\"value1\"}'",
          capturedCommand);

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  @Test
  public void testStartCronJobWithExtraArgumentsForVdkRun() {

    try {
      ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
      Map<String, Object> extraArgs = Map.of("argument1", "value1", "argument2", "value2");
      kubernetesService.startNewCronJobExecution(
          "test-job", "test-id", new HashMap<>(), new HashMap<>(), extraArgs, "test-job");
      Mockito.verify(kubernetesService)
          .createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
      var capturedSpec = specCaptor.getValue();
      var capturedCommand =
          capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
      // check if command arg starts correctly
      Assertions.assertTrue(
          capturedCommand.startsWith(
              "export PYTHONPATH=$(python -c \"from distutils.sysconfig import get_python_lib;"
                  + " print(get_python_lib())\"):/vdk/site-packages/ && /vdk/vdk run ./test-job"
                  + " --arguments '{"),
          "Vdk run command string invalid.");
      // extra arguments passed as a map, print order might be different.
      Assertions.assertTrue(
          capturedCommand.contains("\"argument2\":\"value2\""), "Second argument not present.");
      Assertions.assertTrue(
          capturedCommand.contains("\"argument1\":\"value1\""), "First argument not present.");

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  @Test
  public void testStartCronJobWithNullArgumentsForVdkRun() {

    try {
      ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
      kubernetesService.startNewCronJobExecution(
          "test-job", "test-id", new HashMap<>(), new HashMap<>(), null, "test-job");

      Mockito.verify(kubernetesService)
          .createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
      var capturedSpec = specCaptor.getValue();
      var capturedCommand =
          capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
      // check if command arg hasn't changed.
      Assertions.assertEquals(
          "export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/"
              + "site-packages/ && /vdk/vdk run ./test-job",
          capturedCommand);

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  @Test
  public void testStartCronJobWithEmptyArgumentsForVdkRun() {

    try {
      ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
      kubernetesService.startNewCronJobExecution(
          "test-job", "test-id", new HashMap<>(), new HashMap<>(), Map.of(), "test-job");

      Mockito.verify(kubernetesService)
          .createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
      var capturedSpec = specCaptor.getValue();
      var capturedCommand =
          capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
      // check if command arg hasn't changed.
      Assertions.assertEquals(
          "export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/"
              + "site-packages/ && /vdk/vdk run ./test-job",
          capturedCommand);

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  private V1CronJob getValidCronJobForVdkRunExtraArgsTests() throws Exception {
    KubernetesService service =
        new DataJobsKubernetesService(
            "default", new ApiClient(), new BatchV1Api(), new JobCommandProvider());
    // V1betaCronJob initializing snippet copied from tests above, using reflection
    Method loadInternalV1CronjobTemplate =
        KubernetesService.class.getDeclaredMethod("loadInternalV1CronjobTemplate");
    if (loadInternalV1CronjobTemplate == null) {
      Assertions.fail("The method 'loadInternalV1CronjobTemplate' does not exist.");
    }
    loadInternalV1CronjobTemplate.setAccessible(true);
    V1CronJob internalCronjobTemplate = (V1CronJob) loadInternalV1CronjobTemplate.invoke(service);
    var container =
        internalCronjobTemplate
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getContainers()
            .get(0);

    var newCommand = new ArrayList<>(container.getCommand());
    newCommand.set(
        2,
        "export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/site-packages/ && /vdk/vdk"
            + " run ./test-job");
    container.setCommand(newCommand);
    return internalCronjobTemplate;
  }
}
