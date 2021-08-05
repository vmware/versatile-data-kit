/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobEnvVar;
import io.kubernetes.client.ApiException;
import io.kubernetes.client.apis.BatchV1beta1Api;
import io.kubernetes.client.models.*;
import org.junit.Assert;
import org.junit.Test;
import org.junit.jupiter.api.Assertions;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class KubernetesServiceStartNewCronJobExecutionTest {

   @Test
   public void testStartNewCronJobExecution_nullCronJobDefinition_shouldThrowException() throws ApiException {
      String jobName = "test-job";
      KubernetesService kubernetesService = mockKubernetesService(jobName, null);

      Exception exception = Assertions.assertThrows(ApiException.class, () ->
            kubernetesService.startNewCronJobExecution(jobName, "test-execution-id", Collections.emptyMap(), Collections.emptyMap()));

      Assert.assertEquals(String.format("K8S Cron Job '%s' does not exist or is not properly defined.", jobName), exception.getMessage());
   }

   @Test
   public void testStartNewCronJobExecution_incorrectCronJobDefinition_shouldThrowException() throws ApiException {
      String jobName = "test-job";
      V1beta1CronJob expectedResult = new V1beta1CronJob().spec(new V1beta1CronJobSpec().jobTemplate(new V1beta1JobTemplateSpec().spec(new V1JobSpec())));
      KubernetesService kubernetesService = mockKubernetesService(jobName, expectedResult);

      Exception exception = Assertions.assertThrows(ApiException.class, () ->
            kubernetesService.startNewCronJobExecution(jobName, "dada", Collections.emptyMap(), Collections.emptyMap()));

      Assert.assertEquals(String.format("K8S Cron Job '%s' is not properly defined.", jobName), exception.getMessage());
   }

   @Test
   public void testStartNewCronJobExecution_existingJobContainerEnvs_shouldSetJobContainerEnvs() throws ApiException {
      String jobName = "test-job";
      String executionId = "test-execution-id";
      V1EnvVar vdkOpIdEnv = new V1EnvVar().name(JobEnvVar.VDK_OP_ID.getValue()).value("test-op-id");
      V1EnvVar testEnv = new V1EnvVar().name("test-env-name").value("test-env-value");
      V1beta1CronJob expectedResult = new V1beta1CronJob()
            .spec(new V1beta1CronJobSpec()
                  .jobTemplate(new V1beta1JobTemplateSpec()
                        .spec(new V1JobSpec()
                              .template(new V1PodTemplateSpec()
                                    .spec(new V1PodSpec()
                                          .addContainersItem(new V1Container()
                                                .addEnvItem(testEnv)))))));

      KubernetesService kubernetesService = mockKubernetesService(jobName, expectedResult);
      kubernetesService.startNewCronJobExecution(jobName, executionId, Collections.emptyMap(), Map.of(vdkOpIdEnv.getName(), vdkOpIdEnv.getValue()));

      ArgumentCaptor<String> executionIdArgumentCaptor = ArgumentCaptor.forClass(String.class);
      ArgumentCaptor<V1JobSpec> v1JobSpecArgumentCaptor = ArgumentCaptor.forClass(V1JobSpec.class);

      Mockito.verify(kubernetesService, Mockito.times(1))
            .createNewJob(executionIdArgumentCaptor.capture(),
                  v1JobSpecArgumentCaptor.capture(),
                  Mockito.anyMap(),
                  Mockito.anyMap());

      Assert.assertEquals(executionId, executionIdArgumentCaptor.getValue());

      Optional<List<V1EnvVar>> actualV1EnvVarsOptional = Optional.ofNullable(v1JobSpecArgumentCaptor.getValue())
            .map(v1JobSpec -> v1JobSpec.getTemplate())
            .map(v1PodTemplateSpec -> v1PodTemplateSpec.getSpec())
            .map(v1PodSpec -> v1PodSpec.getContainers())
            .map(v1Containers -> v1Containers.get(0))
            .map(v1Container -> v1Container.getEnv());
      Assert.assertTrue(actualV1EnvVarsOptional.isPresent());

      List<V1EnvVar> actualV1EnvVars = actualV1EnvVarsOptional.get();
      Assert.assertEquals(2, actualV1EnvVars.size());
      Assert.assertTrue(actualV1EnvVars.contains(vdkOpIdEnv));
      Assert.assertTrue(actualV1EnvVars.contains(testEnv));
   }

   @Test
   public void testStartNewCronJobExecution_existingJobLabelsAndJobAnnotations_shouldKeepJobLabelsAndMergeJobAnnotations() throws ApiException {
      String jobName = "test-job";
      String executionId = "test-execution-id";
      V1EnvVar vdkOpIdEnv = new V1EnvVar().name(JobEnvVar.VDK_OP_ID.getValue()).value("test-op-id");
      String expectedAnnotationKey1 = JobAnnotation.SCHEDULE.getValue();
      String expectedAnnotationKey2 = "test-annotation-name";
      Map<String, String> inputAnnotations = Map.of(expectedAnnotationKey2, "test-annotation-value-1");
      Map<String, String> expectedAnnotations = Map.of(expectedAnnotationKey1, "scheduled/runtime", expectedAnnotationKey2, "test-annotation-value-1");

      V1beta1CronJob expectedResult = new V1beta1CronJob()
            .spec(new V1beta1CronJobSpec()
                  .jobTemplate(new V1beta1JobTemplateSpec()
                        .metadata(new V1ObjectMeta()
                              .putAnnotationsItem(expectedAnnotationKey1, expectedAnnotations.get(JobAnnotation.SCHEDULE.getValue()))
                              .putAnnotationsItem(expectedAnnotationKey2, "test-annotation-value-2")
                              .putLabelsItem("test-inline-label-name", "test-inline-label-value"))
                        .spec(new V1JobSpec()
                              .template(new V1PodTemplateSpec()
                                    .spec(new V1PodSpec()
                                          .addContainersItem(new V1Container()))))));

      KubernetesService kubernetesService = mockKubernetesService(jobName, expectedResult);
      kubernetesService.startNewCronJobExecution(jobName, executionId, inputAnnotations, Map.of(vdkOpIdEnv.getName(), vdkOpIdEnv.getValue()));

      ArgumentCaptor<String> executionIdArgumentCaptor = ArgumentCaptor.forClass(String.class);
      ArgumentCaptor<Map> labelsArgumentCaptor = ArgumentCaptor.forClass(Map.class);
      ArgumentCaptor<Map> annotationsArgumentCaptor = ArgumentCaptor.forClass(Map.class);

      Mockito.verify(kubernetesService, Mockito.times(1))
            .createNewJob(executionIdArgumentCaptor.capture(),
                  Mockito.any(),
                  labelsArgumentCaptor.capture(),
                  annotationsArgumentCaptor.capture());

      Assert.assertEquals(executionId, executionIdArgumentCaptor.getValue());
      Assert.assertNotNull(labelsArgumentCaptor.getValue());
      Assert.assertFalse(labelsArgumentCaptor.getValue().isEmpty());
      Assert.assertEquals(expectedResult.getSpec().getJobTemplate().getMetadata().getLabels(), labelsArgumentCaptor.getValue());

      Assert.assertEquals(expectedAnnotations, annotationsArgumentCaptor.getValue());
   }

   private KubernetesService mockKubernetesService(String jobName, V1beta1CronJob result) throws ApiException {
      KubernetesService kubernetesService = Mockito.mock(KubernetesService.class);
      Mockito.doCallRealMethod().when(kubernetesService)
            .startNewCronJobExecution(Mockito.anyString(), Mockito.anyString(), Mockito.anyMap(), Mockito.anyMap());

      BatchV1beta1Api batchV1beta1Api = Mockito.mock(BatchV1beta1Api.class);
      Mockito.when(batchV1beta1Api
            .readNamespacedCronJob(
                  Mockito.eq(jobName),
                  Mockito.isNull(),
                  Mockito.isNull(),
                  Mockito.isNull(),
                  Mockito.isNull()))
            .thenReturn(result);

      Mockito.when(kubernetesService.initBatchV1beta1Api()).thenReturn(batchV1beta1Api);

      return kubernetesService;
   }
}
