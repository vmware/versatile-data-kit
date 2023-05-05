/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import com.vmware.taurus.service.model.JobLabel;
import io.kubernetes.client.custom.Quantity;
import io.kubernetes.client.openapi.models.*;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.springframework.test.util.ReflectionTestUtils;

import java.lang.reflect.Method;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class KubernetesServiceTest {

  @Test
  public void testCreateVDKContainer() {

    var vdkCommand =
        List.of(
            "/bin/bash",
            "-c",
            "cp -r /usr/local/lib/python3.7/site-packages /vdk/. && cp /usr/local/bin/vdk /vdk/.");

    var volumeMount = KubernetesService.volumeMount("vdk-volume", "/vdk", false);

    var expectedVDKContainer =
        new V1ContainerBuilder()
            .withName("vdk")
            .withImage("vdk:latest")
            .withVolumeMounts(
                new V1VolumeMount().name("vdk-volume").mountPath("/vdk").readOnly(false))
            .withImagePullPolicy("Always")
            .withSecurityContext(
                new V1SecurityContextBuilder()
                    .withPrivileged(false)
                    .withReadOnlyRootFilesystem(false)
                    .build())
            .withCommand(vdkCommand)
            .withArgs(List.of())
            .withEnvFrom(
                new V1EnvFromSource()
                    .secretRef(new V1SecretEnvSource().name("builder-secrets").optional(true)))
            .withEnv(List.of())
            .withResources(
                new V1ResourceRequirementsBuilder()
                    .withRequests(Map.of("cpu", new Quantity("500m"), "memory", new Quantity("1G")))
                    .withLimits(Map.of("cpu", new Quantity("2000m"), "memory", new Quantity("1G")))
                    .build())
            .build();

    var actualVDKContainer =
        KubernetesService.container(
            "vdk",
            "vdk:latest",
            false,
            false,
            Map.of(),
            List.of(),
            List.of(volumeMount),
            "Always",
            new KubernetesService.Resources("500m", "1G"),
            new KubernetesService.Resources("2000m", "1G"),
            null,
            vdkCommand);

    Assertions.assertEquals(expectedVDKContainer, actualVDKContainer);
  }

  @Test
  public void testGetJobExecutionStatus_emptyJob_shouldReturnEmptyJobExecutionStatus() {
    V1Job v1Job = new V1Job();
    var mock = Mockito.mock(KubernetesService.class);
    Mockito.when(mock.getK8sSupportsV1CronJob()).thenReturn(false);
    Mockito.when(mock.getTerminationStatus(v1Job))
        .thenReturn(ImmutablePair.of(Optional.empty(), Optional.empty()));
    Mockito.when(mock.getJobExecutionStatus(v1Job, null)).thenCallRealMethod();
    Optional<KubernetesService.JobExecution> actualJobExecutionStatusOptional =
        mock.getJobExecutionStatus(v1Job, null);

    Assertions.assertTrue(actualJobExecutionStatusOptional.isPresent());

    KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
    Assertions.assertNull(actualJobExecution.getExecutionId());
    Assertions.assertNull(actualJobExecution.getJobName());
    Assertions.assertNull(actualJobExecution.getJobVersion());
    Assertions.assertNull(actualJobExecution.getJobPythonVersion());
    Assertions.assertNull(actualJobExecution.getDeployedDate());
    Assertions.assertNull(actualJobExecution.getExecutionType());
    Assertions.assertNull(actualJobExecution.getOpId());
    Assertions.assertNull(actualJobExecution.getResourcesCpuRequest());
    Assertions.assertNull(actualJobExecution.getResourcesCpuLimit());
    Assertions.assertNull(actualJobExecution.getResourcesMemoryRequest());
    Assertions.assertNull(actualJobExecution.getResourcesMemoryLimit());
    Assertions.assertNull(actualJobExecution.getStartTime());
    Assertions.assertNull(actualJobExecution.getEndTime());
    Assertions.assertNull(actualJobExecution.getSucceeded());
  }

  @Test
  public void testGetJobExecutionStatus_notEmptyJob_shouldReturnNotEmptyJobExecutionStatus() {
    String dataJobName = "test-data-job";
    String kubernetesJobName = "test-job";
    String jobVersion = "1234";
    String jobPythonVersion = "3.11";
    String deployedDate = "2021-06-15T08:04:33.534787Z";
    String deployedBy = "test-user";
    String executionType = "manual";
    String opId = "test-op-id";
    String cpuRequest = "1";
    String cpuLimit = "2";
    Integer memoryRequest = 500;
    Integer memoryLimit = 1000;
    OffsetDateTime startTime = OffsetDateTime.now();
    OffsetDateTime endTime = OffsetDateTime.now();
    Integer succeeded = 1;

    V1Job expectedJob =
        new V1Job()
            .metadata(
                new V1ObjectMeta()
                    .name(kubernetesJobName)
                    .putLabelsItem(JobLabel.VERSION.getValue(), jobVersion)
                    .putLabelsItem(JobLabel.NAME.getValue(), dataJobName)
                    .putAnnotationsItem(JobAnnotation.DEPLOYED_DATE.getValue(), deployedDate)
                    .putAnnotationsItem(JobAnnotation.DEPLOYED_BY.getValue(), deployedBy)
                    .putAnnotationsItem(JobAnnotation.EXECUTION_TYPE.getValue(), executionType)
                    .putAnnotationsItem(JobAnnotation.OP_ID.getValue(), opId)
                    .putAnnotationsItem(JobAnnotation.PYTHON_VERSION.getValue(), jobPythonVersion))
            .spec(
                new V1JobSpec()
                    .template(
                        new V1PodTemplateSpec()
                            .spec(
                                new V1PodSpec()
                                    .addContainersItem(
                                        new V1Container()
                                            .name(dataJobName)
                                            .resources(
                                                new V1ResourceRequirements()
                                                    .putRequestsItem(
                                                        "cpu", new Quantity(cpuRequest))
                                                    .putRequestsItem(
                                                        "memory",
                                                        new Quantity(
                                                            Integer.toString(
                                                                memoryRequest * 1000 * 1000)))
                                                    .putLimitsItem("cpu", new Quantity(cpuLimit))
                                                    .putLimitsItem(
                                                        "memory",
                                                        new Quantity(
                                                            Integer.toString(
                                                                memoryLimit * 1000 * 1000))))))))
            .status(
                new V1JobStatus()
                    .startTime(startTime)
                    .completionTime(endTime)
                    .succeeded(succeeded));
    KubernetesService.JobStatusCondition condition =
        new KubernetesService.JobStatusCondition(
            true, "type", "reason", "message", endTime.toInstant().toEpochMilli());

    KubernetesService mock = Mockito.mock(KubernetesService.class);
    Mockito.when(mock.getK8sSupportsV1CronJob()).thenReturn(false);
    Mockito.when(mock.getTerminationStatus(expectedJob))
        .thenReturn(
            ImmutablePair.of(
                Optional.ofNullable(new V1ContainerStateTerminated().reason("test")),
                Optional.ofNullable(new V1ContainerStateTerminated().reason("test"))));
    Mockito.when(mock.getJobExecutionStatus(expectedJob, condition)).thenCallRealMethod();
    Optional<KubernetesService.JobExecution> actualJobExecutionStatusOptional =
        mock.getJobExecutionStatus(expectedJob, condition);

    Assertions.assertTrue(actualJobExecutionStatusOptional.isPresent());

    KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
    Assertions.assertEquals(kubernetesJobName, actualJobExecution.getExecutionId());
    Assertions.assertEquals(dataJobName, actualJobExecution.getJobName());
    Assertions.assertEquals(jobVersion, actualJobExecution.getJobVersion());
    Assertions.assertEquals(jobPythonVersion, actualJobExecution.getJobPythonVersion());
    Assertions.assertEquals(
        OffsetDateTime.parse(deployedDate), actualJobExecution.getDeployedDate());
    Assertions.assertEquals(executionType, actualJobExecution.getExecutionType());
    Assertions.assertEquals(opId, actualJobExecution.getOpId());
    Assertions.assertEquals(Float.valueOf(cpuRequest), actualJobExecution.getResourcesCpuRequest());
    Assertions.assertEquals(Float.valueOf(cpuLimit), actualJobExecution.getResourcesCpuLimit());
    Assertions.assertEquals(memoryRequest, actualJobExecution.getResourcesMemoryRequest());
    Assertions.assertEquals(memoryLimit, actualJobExecution.getResourcesMemoryLimit());
    Assertions.assertEquals(
        OffsetDateTime.ofInstant(
            Instant.ofEpochMilli(startTime.toInstant().toEpochMilli()), ZoneOffset.UTC),
        actualJobExecution.getStartTime());
    Assertions.assertEquals(
        OffsetDateTime.ofInstant(
            Instant.ofEpochMilli(endTime.toInstant().toEpochMilli()), ZoneOffset.UTC),
        actualJobExecution.getEndTime());
    Assertions.assertTrue(actualJobExecution.getSucceeded());
  }

  // Note that we are testing private functionality and mocking the surrounding methods
  // won't do us any good. Better approach is to rely on integration tests where we can
  // check the final outcome directly in the K8s environment.
  @Test
  public void testCreateV1beta1CronJobFromInternalResource() {
    KubernetesService service = new DataJobsKubernetesService("default", "someConfig", false);
    try {
      // Step 1 - load and check the internal cronjob template.
      service.afterPropertiesSet();
      // At this point we know that the cronjob template is loaded successfully.

      // Step 2 - check whether an empty V1beta1CronJob object is properly populated
      //          with corresponding entries from the internal cronjob template.
      // First we load the internal cronjob template.
      Method loadInternalV1beta1CronjobTemplate =
          KubernetesService.class.getDeclaredMethod("loadInternalV1beta1CronjobTemplate");
      if (loadInternalV1beta1CronjobTemplate == null) {
        Assertions.fail("The method 'loadInternalV1beta1CronjobTemplate' does not exist.");
      }
      loadInternalV1beta1CronjobTemplate.setAccessible(true);
      V1beta1CronJob internalCronjobTemplate =
          (V1beta1CronJob) loadInternalV1beta1CronjobTemplate.invoke(service);
      // Prepare the 'v1beta1checkForMissingEntries' method.
      Method checkForMissingEntries =
          KubernetesService.class.getDeclaredMethod(
              "v1beta1checkForMissingEntries", V1beta1CronJob.class);
      if (checkForMissingEntries == null) {
        Assertions.fail("The method 'v1beta1checkForMissingEntries' does not exist.");
      }
      checkForMissingEntries.setAccessible(true);
      V1beta1CronJob emptyCronjobToBeFixed =
          new V1beta1CronJob(); // Worst case scenario to test - empty cronjob.
      checkForMissingEntries.invoke(service, emptyCronjobToBeFixed);
      // We can't rely on equality check on root metadata/spec level, because if the internal
      // template
      // has missing elements, the equality check will miss them. Instead, we will check the most
      // important elements one by one.
      Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata().getAnnotations());
      Assertions.assertEquals(
          internalCronjobTemplate.getMetadata().getAnnotations(),
          emptyCronjobToBeFixed.getMetadata().getAnnotations());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata());
      Assertions.assertEquals(
          internalCronjobTemplate
              .getSpec()
              .getJobTemplate()
              .getSpec()
              .getTemplate()
              .getMetadata()
              .getLabels(),
          emptyCronjobToBeFixed
              .getSpec()
              .getJobTemplate()
              .getSpec()
              .getTemplate()
              .getMetadata()
              .getLabels());

      Assertions.assertNotNull(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
      // Step 3 - create and check the actual cronjob.
      Method[] methods = KubernetesService.class.getDeclaredMethods();
      // This is much easier than describing the whole method signature.
      Optional<Method> method =
          Arrays.stream(methods)
              .filter(m -> m.getName().equals("v1beta1CronJobFromTemplate"))
              .findFirst();
      if (method.isEmpty()) {
        Assertions.fail("The method 'v1beta1cronJobFromTemplate' does not exist.");
      }
      method.get().setAccessible(true);
      V1beta1CronJob cronjob =
          (V1beta1CronJob)
              method
                  .get()
                  .invoke(
                      service,
                      "test-job-name",
                      "test-job-schedule",
                      true,
                      null,
                      null,
                      null,
                      Collections.EMPTY_MAP,
                      Collections.EMPTY_MAP,
                      Collections.EMPTY_MAP,
                      List.of(""));
      Assertions.assertEquals("test-job-name", cronjob.getMetadata().getName());
      Assertions.assertEquals("test-job-schedule", cronjob.getSpec().getSchedule());
      Assertions.assertEquals(true, cronjob.getSpec().getSuspend());
      Assertions.assertEquals(
          Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getLabels());
      Assertions.assertEquals(
          Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations());

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  @Test
  public void testCreateV1CronJobFromInternalResource() {
    KubernetesService service = new DataJobsKubernetesService("default", "someConfig", false);
    try {
      // Step 1 - load and check the internal cronjob template.
      service.afterPropertiesSet();
      // At this point we know that the cronjob template is loaded successfully.

      // Step 2 - check whether an empty V1CronJob object is properly populated
      //          with corresponding entries from the internal cronjob template.
      // First we load the internal cronjob template.
      Method loadInternalV1CronjobTemplate =
          KubernetesService.class.getDeclaredMethod("loadInternalV1CronjobTemplate");
      if (loadInternalV1CronjobTemplate == null) {
        Assertions.fail("The method 'loadInternalV1CronjobTemplate' does not exist.");
      }
      loadInternalV1CronjobTemplate.setAccessible(true);
      V1CronJob internalCronjobTemplate = (V1CronJob) loadInternalV1CronjobTemplate.invoke(service);
      // Prepare the 'v1checkForMissingEntries' method.
      Method checkForMissingEntries =
          KubernetesService.class.getDeclaredMethod("v1checkForMissingEntries", V1CronJob.class);
      if (checkForMissingEntries == null) {
        Assertions.fail("The method 'v1checkForMissingEntries' does not exist.");
      }
      checkForMissingEntries.setAccessible(true);
      V1CronJob emptyCronjobToBeFixed =
          new V1CronJob(); // Worst case scenario to test - empty cronjob.
      checkForMissingEntries.invoke(service, emptyCronjobToBeFixed);
      // We can't rely on equality check on root metadata/spec level, because if the internal
      // template
      // has missing elements, the equality check will miss them. Instead, we will check the most
      // important elements one by one.
      Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata().getAnnotations());
      Assertions.assertEquals(
          internalCronjobTemplate.getMetadata().getAnnotations(),
          emptyCronjobToBeFixed.getMetadata().getAnnotations());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate());
      Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
      Assertions.assertNotNull(
          emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata());
      Assertions.assertEquals(
          internalCronjobTemplate
              .getSpec()
              .getJobTemplate()
              .getSpec()
              .getTemplate()
              .getMetadata()
              .getLabels(),
          emptyCronjobToBeFixed
              .getSpec()
              .getJobTemplate()
              .getSpec()
              .getTemplate()
              .getMetadata()
              .getLabels());

      Assertions.assertNotNull(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
      // Step 3 - create and check the actual cronjob.
      Method[] methods = KubernetesService.class.getDeclaredMethods();
      // This is much easier than describing the whole method signature.
      Optional<Method> method =
          Arrays.stream(methods)
              .filter(m -> m.getName().equals("v1CronJobFromTemplate"))
              .findFirst();
      if (method.isEmpty()) {
        Assertions.fail("The method 'v1cronJobFromTemplate' does not exist.");
      }
      method.get().setAccessible(true);
      V1CronJob cronjob =
          (V1CronJob)
              method
                  .get()
                  .invoke(
                      service,
                      "test-job-name",
                      "test-job-schedule",
                      true,
                      null,
                      null,
                      null,
                      Collections.EMPTY_MAP,
                      Collections.EMPTY_MAP,
                      Collections.EMPTY_MAP,
                      List.of(""));
      Assertions.assertEquals("test-job-name", cronjob.getMetadata().getName());
      Assertions.assertEquals("test-job-schedule", cronjob.getSpec().getSchedule());
      Assertions.assertEquals(true, cronjob.getSpec().getSuspend());
      Assertions.assertEquals(
          Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getLabels());
      Assertions.assertEquals(
          Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations());

    } catch (Exception e) {
      e.printStackTrace();
      Assertions.fail(e.getMessage());
    }
  }

  @Test
  public void testReadJobDeploymentStatuses() {
    KubernetesService mock = Mockito.mock(KubernetesService.class);
    List<JobDeploymentStatus> v1TestList = new ArrayList<>();
    List<JobDeploymentStatus> v1BetaTestList = new ArrayList<>();

    JobDeploymentStatus v1BetaDeploymentStatus = new JobDeploymentStatus();
    v1BetaDeploymentStatus.setEnabled(false);
    v1BetaDeploymentStatus.setDataJobName("v1betaTestJob");
    v1BetaDeploymentStatus.setCronJobName("v1betaTestJob");
    v1BetaTestList.add(v1BetaDeploymentStatus);

    JobDeploymentStatus v1DeploymentStatus = new JobDeploymentStatus();
    v1DeploymentStatus.setEnabled(false);
    v1DeploymentStatus.setDataJobName("v1TestJob");
    v1DeploymentStatus.setCronJobName("v1TestJob");
    v1TestList.add(v1DeploymentStatus);

    var mergedTestLists =
        Stream.concat(v1TestList.stream(), v1BetaTestList.stream()).collect(Collectors.toList());

    Mockito.when(mock.getK8sSupportsV1CronJob()).thenReturn(true);
    Mockito.when(mock.readV1CronJobDeploymentStatuses()).thenReturn(v1TestList);
    Mockito.when(mock.readV1beta1CronJobDeploymentStatuses()).thenReturn(v1BetaTestList);
    Mockito.when(mock.readJobDeploymentStatuses()).thenCallRealMethod();
    List<JobDeploymentStatus> resultStatuses = mock.readJobDeploymentStatuses();

    Assertions.assertEquals(mergedTestLists, resultStatuses);
  }

  @Test
  public void testReadCronJob_readV1CronJobShouldReturnStatus() {
    String testCronjobName = "testCronjob";
    KubernetesService mock = Mockito.mock(KubernetesService.class);

    JobDeploymentStatus testDeploymentStatus = new JobDeploymentStatus();
    testDeploymentStatus.setEnabled(false);
    testDeploymentStatus.setDataJobName(testCronjobName);
    testDeploymentStatus.setCronJobName(testCronjobName);
    Mockito.when(mock.readCronJob(testCronjobName)).thenCallRealMethod();

    Mockito.when(mock.readV1beta1CronJob(testCronjobName)).thenReturn(Optional.empty());
    Mockito.when(mock.readV1CronJob(testCronjobName)).thenReturn(Optional.of(testDeploymentStatus));

    Assertions.assertNotNull(mock.readCronJob(testCronjobName));
    Assertions.assertEquals(
        testCronjobName, mock.readCronJob(testCronjobName).get().getCronJobName());
    verify(mock, times(2)).readV1beta1CronJob(testCronjobName);
    verify(mock, times(2)).readV1CronJob(testCronjobName);
  }

  @Test
  public void testReadCronJob_readV1beta1CronJobShouldReturnStatus() {
    String testCronjobName = "testCronjob";
    KubernetesService mock = Mockito.mock(KubernetesService.class);

    JobDeploymentStatus testDeploymentStatus = new JobDeploymentStatus();
    testDeploymentStatus.setEnabled(false);
    testDeploymentStatus.setDataJobName(testCronjobName);
    testDeploymentStatus.setCronJobName(testCronjobName);
    Mockito.when(mock.readCronJob(testCronjobName)).thenCallRealMethod();

    Mockito.when(mock.readV1beta1CronJob(testCronjobName))
        .thenReturn(Optional.of(testDeploymentStatus));
    Mockito.when(mock.readV1CronJob(testCronjobName)).thenReturn(Optional.empty());

    Assertions.assertNotNull(mock.readCronJob(testCronjobName));
    Assertions.assertEquals(
        testCronjobName, mock.readCronJob(testCronjobName).get().getCronJobName());
    verify(mock, times(2)).readV1beta1CronJob(testCronjobName);
    verify(mock, times(0)).readV1CronJob(testCronjobName);
  }

  @Test
  public void testQuantityToMbConversionMegabytes() throws Exception {
    var hundredMb = "100M";
    testQuantityToMbConversion(100, hundredMb);

    var thousandMb = "1000M";
    testQuantityToMbConversion(1000, thousandMb);
    // this should be enough for overflow errors on the method to manifest.
    var tenThousandMb = "10000M";
    testQuantityToMbConversion(10000, tenThousandMb);

    var hundredThousandMb = "100000M";
    testQuantityToMbConversion(100000, hundredThousandMb);
  }

  @Test
  public void testQuantityConversionGigabytes() throws Exception {
    var oneG = "1G";
    testQuantityToMbConversion(1000, oneG);

    var twoG = "2G";
    testQuantityToMbConversion(2000, twoG);
    // this should be enough for overflow errors on the method to manifest.
    var threeG = "3G";
    testQuantityToMbConversion(3000, threeG);

    var fourG = "4G";
    testQuantityToMbConversion(4000, fourG);

    var sixtyFourG = "64G";
    testQuantityToMbConversion(64000, sixtyFourG);
  }

  @Test
  public void testV1beta1CronJobFromTemplate_emptyImagePullSecretsList() {
    var mock = mockCronJobFromTemplate();
    V1beta1CronJob v1beta1CronJob =
        mock.v1beta1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyList());

    Assertions.assertNull(
        v1beta1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets());
  }

  @Test
  public void testV1CronJobFromTemplate_emptyImagePullSecretsList() {
    var mock = mockCronJobFromTemplate();
    V1CronJob v1CronJob =
        mock.v1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyList());

    Assertions.assertNull(
        v1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets());
  }

  @Test
  public void testV1beta1CronJobFromTemplate_imagePullSecretsListWithEmptyValues() {
    var mock = mockCronJobFromTemplate();
    V1beta1CronJob v1beta1CronJob =
        mock.v1beta1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            List.of("", ""));

    Assertions.assertNull(
        v1beta1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets());
  }

  @Test
  public void testV1CronJobFromTemplate_imagePullSecretsListWithEmptyValues() {
    var mock = mockCronJobFromTemplate();
    V1CronJob v1CronJob =
        mock.v1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            List.of("", ""));

    Assertions.assertNull(
        v1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets());
  }

  @Test
  public void
      testV1beta1CronJobFromTemplate_imagePullSecretsListWithOneNonEmptyValueAndOneEmptyValue() {
    var mock = mockCronJobFromTemplate();
    String secretName = "test_secret_name";
    V1beta1CronJob v1beta1CronJob =
        mock.v1beta1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            List.of("", secretName));

    List<V1LocalObjectReference> actualImagePullSecrets =
        v1beta1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets();

    Assertions.assertNotNull(actualImagePullSecrets);
    Assertions.assertEquals(1, actualImagePullSecrets.size());
    Assertions.assertEquals(secretName, actualImagePullSecrets.get(0).getName());
  }

  @Test
  public void testV1CronJobFromTemplate_imagePullSecretsListWithOneNonEmptyValueAndOneEmptyValue() {
    var mock = mockCronJobFromTemplate();
    String secretName = "test_secret_name";
    V1CronJob v1CronJob =
        mock.v1CronJobFromTemplate(
            "",
            "",
            true,
            null,
            null,
            null,
            Collections.emptyMap(),
            Collections.emptyMap(),
            Collections.emptyMap(),
            List.of("", secretName));

    List<V1LocalObjectReference> actualImagePullSecrets =
        v1CronJob
            .getSpec()
            .getJobTemplate()
            .getSpec()
            .getTemplate()
            .getSpec()
            .getImagePullSecrets();

    Assertions.assertNotNull(actualImagePullSecrets);
    Assertions.assertEquals(1, actualImagePullSecrets.size());
    Assertions.assertEquals(secretName, actualImagePullSecrets.get(0).getName());
  }

  public void testQuantityToMbConversion(int expectedMb, String providedResources)
      throws Exception {
    var q = Quantity.fromString(providedResources);
    var actual = KubernetesService.convertMemoryToMBs(q);
    Assertions.assertEquals(expectedMb, actual);
  }

  private KubernetesService mockCronJobFromTemplate() {
    var mock = Mockito.mock(KubernetesService.class);
    Mockito.when(mock.getK8sSupportsV1CronJob()).thenReturn(false);
    Mockito.when(
            mock.v1beta1CronJobFromTemplate(
                anyString(),
                anyString(),
                anyBoolean(),
                any(),
                any(),
                any(),
                any(),
                any(),
                any(),
                anyList()))
        .thenCallRealMethod();
    Mockito.when(
            mock.v1CronJobFromTemplate(
                anyString(),
                anyString(),
                anyBoolean(),
                any(),
                any(),
                any(),
                any(),
                any(),
                any(),
                anyList()))
        .thenCallRealMethod();

    ReflectionTestUtils.setField(
        mock, // inject into this object
        "log", // assign to this field
        Mockito.mock(Logger.class)); // object to be injected

    return mock;
  }
}
