/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobLabel;
import io.kubernetes.client.apis.BatchV1beta1Api;
import io.kubernetes.client.custom.Quantity;
import io.kubernetes.client.models.*;
import org.joda.time.DateTime;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mockito;

import java.lang.reflect.Method;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.*;

import static org.mockito.ArgumentMatchers.any;

public class KubernetesServiceTest {

   @Test
   public void testCreateVDKContainer() {

      var vdkCommand = List.of(
            "/bin/bash",
            "-c",
            "cp -r /usr/local/lib/python3.7/site-packages /vdk/. && cp /usr/local/bin/vdk /vdk/.");

      var volumeMount = KubernetesService.volumeMount("vdk-volume", "/vdk", false);

      var expectedVDKContainer = new V1ContainerBuilder()
            .withName("vdk")
            .withImage("vdk:latest")
            .withVolumeMounts(new V1VolumeMount()
                  .name("vdk-volume")
                  .mountPath("/vdk")
                  .readOnly(false))
            .withImagePullPolicy("Always")
            .withSecurityContext(new V1SecurityContextBuilder()
                  .withPrivileged(false)
                  .build())
            .withCommand(vdkCommand)
            .withArgs(List.of())
            .withEnv(List.of())
            .withResources(new V1ResourceRequirementsBuilder()
                  .withRequests(Map.of("cpu", new Quantity("500m"), "memory", new Quantity("1G")))
                  .withLimits(Map.of("cpu", new Quantity("2000m"), "memory", new Quantity("1G")))
                  .build())
            .build();

      var actualVDKContainer = KubernetesService.container("vdk", "vdk:latest", false, Map.of(), List.of(),
            List.of(volumeMount), "Always", new KubernetesService.Resources("500m", "1G"),
            new KubernetesService.Resources("2000m", "1G"), null, vdkCommand);

      Assertions.assertEquals(expectedVDKContainer, actualVDKContainer);
   }

   @Test
   public void testGetJobExecutionStatus_emptyJob_shouldReturnEmptyJobExecutionStatus() {
      V1Job v1Job = new V1Job();
      KubernetesService mock = Mockito.mock(KubernetesService.class);
      Mockito.when(mock.getTerminationStatus(v1Job)).thenReturn(Optional.empty());
      Mockito.when(mock.getJobExecutionStatus(v1Job, null)).thenCallRealMethod();
      Optional<KubernetesService.JobExecution> actualJobExecutionStatusOptional = mock.getJobExecutionStatus(v1Job, null);

      Assertions.assertTrue(actualJobExecutionStatusOptional.isPresent());

      KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
      Assertions.assertNull(actualJobExecution.getExecutionId());
      Assertions.assertNull(actualJobExecution.getJobName());
      Assertions.assertNull(actualJobExecution.getJobVersion());
      Assertions.assertNull(actualJobExecution.getDeployedDate());
      Assertions.assertNull(actualJobExecution.getExecutionType());
      Assertions.assertNull(actualJobExecution.getOpId());
      Assertions.assertNull(actualJobExecution.getResourcesCpuRequest());
      Assertions.assertNull(actualJobExecution.getResourcesCpuLimit());
      Assertions.assertNull(actualJobExecution.getResourcesMemoryRequest());
      Assertions.assertNull(actualJobExecution.getResourcesMemoryLimit());
      Assertions.assertNull(actualJobExecution.getStartTime());
      Assertions.assertNull(actualJobExecution.getEndTime());
      Assertions.assertEquals(KubernetesService.JobExecution.Status.RUNNING, actualJobExecution.getStatus());
   }

   @Test
   public void testGetJobExecutionStatus_notEmptyJob_shouldReturnNotEmptyJobExecutionStatus() {
      String dataJobName = "test-data-job";
      String kubernetesJobName = "test-job";
      String jobVersion = "1234";
      String deployedDate = "2021-06-15T08:04:33.534787Z";
      String deployedBy = "test-user";
      String executionType = "manual";
      String opId = "test-op-id";
      String cpuRequest = "1";
      String cpuLimit = "2";
      Integer memoryRequest = 500;
      Integer memoryLimit = 1000;
      DateTime startTime = DateTime.now();
      DateTime endTime = DateTime.now();
      Integer succeeded = 1;

      V1Job expectedJob = new V1Job()
            .metadata(new V1ObjectMeta()
                  .name(kubernetesJobName)
                  .putLabelsItem(JobLabel.VERSION.getValue(), jobVersion)
                  .putLabelsItem(JobLabel.NAME.getValue(), dataJobName)
                  .putAnnotationsItem(JobAnnotation.DEPLOYED_DATE.getValue(), deployedDate)
                  .putAnnotationsItem(JobAnnotation.DEPLOYED_BY.getValue(), deployedBy)
                  .putAnnotationsItem(JobAnnotation.EXECUTION_TYPE.getValue(), executionType)
                  .putAnnotationsItem(JobAnnotation.OP_ID.getValue(), opId))
            .spec(new V1JobSpec()
                  .template(new V1PodTemplateSpec()
                        .spec(new V1PodSpec()
                              .addContainersItem(new V1Container()
                                    .name(dataJobName)
                                    .resources(new V1ResourceRequirements()
                                          .putRequestsItem("cpu", new Quantity(cpuRequest))
                                          .putRequestsItem("memory", new Quantity(Integer.toString(memoryRequest * 1000 * 1000)))
                                          .putLimitsItem("cpu", new Quantity(cpuLimit))
                                          .putLimitsItem("memory", new Quantity(Integer.toString(memoryLimit * 1000 * 1000)))
                                    )))))
            .status(new V1JobStatus()
                  .startTime(startTime)
                  .completionTime(endTime)
                  .succeeded(succeeded));
      KubernetesService.JobStatusCondition condition = new KubernetesService.JobStatusCondition(true, "type", "reason", "message", endTime.getMillis());

      KubernetesService mock = Mockito.mock(KubernetesService.class);
      Mockito.when(mock.getTerminationStatus(expectedJob)).thenReturn(Optional.empty());
      Mockito.when(mock.getJobExecutionStatus(expectedJob, condition)).thenCallRealMethod();
      Optional<KubernetesService.JobExecution> actualJobExecutionStatusOptional = mock.getJobExecutionStatus(expectedJob, condition);

      Assertions.assertTrue(actualJobExecutionStatusOptional.isPresent());

      KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
      Assertions.assertEquals(kubernetesJobName, actualJobExecution.getExecutionId());
      Assertions.assertEquals(dataJobName, actualJobExecution.getJobName());
      Assertions.assertEquals(jobVersion, actualJobExecution.getJobVersion());
      Assertions.assertEquals(OffsetDateTime.parse(deployedDate), actualJobExecution.getDeployedDate());
      Assertions.assertEquals(executionType, actualJobExecution.getExecutionType());
      Assertions.assertEquals(opId, actualJobExecution.getOpId());
      Assertions.assertEquals(Float.valueOf(cpuRequest), actualJobExecution.getResourcesCpuRequest());
      Assertions.assertEquals(Float.valueOf(cpuLimit), actualJobExecution.getResourcesCpuLimit());
      Assertions.assertEquals(memoryRequest, actualJobExecution.getResourcesMemoryRequest());
      Assertions.assertEquals(memoryLimit, actualJobExecution.getResourcesMemoryLimit());
      Assertions.assertEquals(OffsetDateTime.ofInstant(Instant.ofEpochMilli(startTime.getMillis()), ZoneOffset.UTC), actualJobExecution.getStartTime());
      Assertions.assertEquals(OffsetDateTime.ofInstant(Instant.ofEpochMilli(endTime.getMillis()), ZoneOffset.UTC), actualJobExecution.getEndTime());
      Assertions.assertEquals(KubernetesService.JobExecution.Status.FINISHED, actualJobExecution.getStatus());
   }

    // Note that we are testing private functionality and mocking the surrounding methods
    // won't do us any good. Better approach is to rely on integration tests where we can
    // check the final outcome directly in the K8s environment.
    @Test
    public void testCreateV1beta1CronJobFromInternalResource() {
        KubernetesService service = new DataJobsKubernetesService("default", "someConfig");
        try {
            // Step 1 - load and check the internal cronjob template.
            service.afterPropertiesSet();
            // At this point we know that the cronjob template is loaded successfully.

            // Step 2 - check whether an empty V1beta1CronJob object is properly populated
            //          with corresponding entries from the internal cronjob template.
            // First we load the internal cronjob template.
            Method loadInternalCronjobTemplate = KubernetesService.class.getDeclaredMethod("loadInternalCronjobTemplate");
            if(loadInternalCronjobTemplate == null) {
                Assertions.fail("The method 'loadInternalCronjobTemplate' does not exist.");
            }
            loadInternalCronjobTemplate.setAccessible(true);
            V1beta1CronJob internalCronjobTemplate = (V1beta1CronJob) loadInternalCronjobTemplate.invoke(service);
            // Prepare the 'checkForMissingEntries' method.
            Method checkForMissingEntries = KubernetesService.class.getDeclaredMethod("checkForMissingEntries", V1beta1CronJob.class);
            if(checkForMissingEntries == null) {
                Assertions.fail("The method 'checkForMissingEntries' does not exist.");
            }
            checkForMissingEntries.setAccessible(true);
            V1beta1CronJob emptyCronjobToBeFixed = new V1beta1CronJob(); // Worst case scenario to test - empty cronjob.
            checkForMissingEntries.invoke(service, emptyCronjobToBeFixed);
            // We can't rely on equality check on root metadata/spec level, because if the internal template
            // has missing elements, the equality check will miss them. Instead, we will check the most
            // important elements one by one.
            Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getMetadata().getAnnotations());
            Assertions.assertEquals(internalCronjobTemplate.getMetadata().getAnnotations(),
                    emptyCronjobToBeFixed.getMetadata().getAnnotations());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
            Assertions.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata());
            Assertions.assertEquals(internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata().getLabels(),
                    emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata().getLabels());

            Assertions.assertNotNull(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
            // Step 3 - create and check the actual cronjob.
            Method[] methods = KubernetesService.class.getDeclaredMethods();
            // This is much easier than describing the whole method signature.
            Optional<Method> method = Arrays.stream(methods).filter(m -> m.getName().equals("cronJobFromTemplate")).findFirst();
            if(method.isEmpty()) {
                Assertions.fail("The method 'cronJobFromTemplate' does not exist.");
            }
            method.get().setAccessible(true);
            V1beta1CronJob cronjob = (V1beta1CronJob) method.get().invoke(service, "test-job-name", "test-job-schedule", true, null, null, null, Collections.EMPTY_MAP, Collections.EMPTY_MAP, Collections.EMPTY_MAP, Collections.EMPTY_MAP);
            Assertions.assertEquals("test-job-name", cronjob.getMetadata().getName());
            Assertions.assertEquals("test-job-schedule", cronjob.getSpec().getSchedule());
            Assertions.assertEquals(true, cronjob.getSpec().isSuspend());
            Assertions.assertEquals(Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getLabels());
            Assertions.assertEquals(Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations());

        } catch(Exception e) {
            e.printStackTrace();
            Assertions.fail(e.getMessage());
        }
    }

    @Test
    public void testStartCronJobWithExtraArgumentForVdkRun() {

        try {
            ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
            var testService = getMockKubernetesServiceForVdkRunExtraArgsTests();
            Map<String, Object> extraArgs = Map.of("argument1", "value1");
            testService.startNewCronJobExecution("test-job", "test-id", new HashMap<>(), new HashMap<>(), extraArgs, "test-job");
            Mockito.verify(testService).createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
            var capturedSpec = specCaptor.getValue();
            var capturedCommand = capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
            //check if command arg starts correctly
            Assertions.assertEquals("export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/" +
                    "site-packages/ && /vdk/vdk run ./test-job --arguments '{\"argument1\":\"value1\"}'", capturedCommand);

        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail(e.getMessage());
        }
    }

    @Test
    public void testStartCronJobWithExtraArgumentsForVdkRun() {

        try {
            ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
            var testService = getMockKubernetesServiceForVdkRunExtraArgsTests();
            Map<String, Object> extraArgs = Map.of("argument1", "value1", "argument2", "value2");
            testService.startNewCronJobExecution("test-job", "test-id", new HashMap<>(), new HashMap<>(), extraArgs, "test-job");
            Mockito.verify(testService).createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
            var capturedSpec = specCaptor.getValue();
            var capturedCommand = capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
            //check if command arg starts correctly
            Assertions.assertTrue(capturedCommand.startsWith("export PYTHONPATH=/usr/local/lib/python3.7/si" +
                    "te-packages:/vdk/site-packages/ && /vdk/vdk run ./test-job --arguments '{"), "Vdk run command string invalid.");
            //extra arguments passed as a map, print order might be different.
            Assertions.assertTrue(capturedCommand.contains("\"argument2\":\"value2\""), "Second argument not present.");
            Assertions.assertTrue(capturedCommand.contains("\"argument1\":\"value1\""), "First argument not present.");

        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail(e.getMessage());
        }
    }

    @Test
    public void testStartCronJobWithNullArgumentsForVdkRun() {

        try {
            ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
            var testService = getMockKubernetesServiceForVdkRunExtraArgsTests();
            testService.startNewCronJobExecution("test-job", "test-id", new HashMap<>(), new HashMap<>(), null, "test-job");

            Mockito.verify(testService).createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
            var capturedSpec = specCaptor.getValue();
            var capturedCommand = capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
            //check if command arg hasn't changed.
            Assertions.assertEquals("export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/" +
                            "site-packages/ && /vdk/vdk run ./test-job", capturedCommand);

        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail(e.getMessage());
        }
    }

    @Test
    public void testStartCronJobWithEmptyArgumentsForVdkRun() {

        try {
            ArgumentCaptor<V1JobSpec> specCaptor = ArgumentCaptor.forClass(V1JobSpec.class);
            var testService = getMockKubernetesServiceForVdkRunExtraArgsTests();
            testService.startNewCronJobExecution("test-job", "test-id", new HashMap<>(), new HashMap<>(), Map.of(), "test-job");

            Mockito.verify(testService).createNewJob(Mockito.any(), specCaptor.capture(), Mockito.any(), Mockito.any());
            var capturedSpec = specCaptor.getValue();
            var capturedCommand = capturedSpec.getTemplate().getSpec().getContainers().get(0).getCommand().get(2);
            //check if command arg hasn't changed.
            Assertions.assertEquals("export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/" +
                    "site-packages/ && /vdk/vdk run ./test-job", capturedCommand);

        } catch (Exception e) {
            e.printStackTrace();
            Assertions.fail(e.getMessage());
        }
    }

    private KubernetesService getMockKubernetesServiceForVdkRunExtraArgsTests() throws Exception {

        V1beta1CronJob internalCronjobTemplate = getValidCronJobForVdkRunExtraArgsTests();
        KubernetesService testService = Mockito.mock(KubernetesService.class);
        BatchV1beta1Api mockBatch = Mockito.mock(BatchV1beta1Api.class);
        Mockito.when(testService.initBatchV1beta1Api()).thenReturn(mockBatch);
        Mockito.when(mockBatch.readNamespacedCronJob(any(), any(), any(), any(), any())).thenReturn(internalCronjobTemplate);
        Mockito.doNothing().when(testService).createNewJob(any(), any(), any(), any());
        Mockito.doCallRealMethod().when(testService).startNewCronJobExecution(any(), any(), any(), any(), any(), any());

        return testService;
    }

    private V1beta1CronJob getValidCronJobForVdkRunExtraArgsTests() throws Exception {
        KubernetesService service = new DataJobsKubernetesService("default", "someConfig");
        // V1betaCronJob initializing snippet copied from tests above, using reflection
        service.afterPropertiesSet();
        Method loadInternalCronjobTemplate = KubernetesService.class.getDeclaredMethod("loadInternalCronjobTemplate");
        if(loadInternalCronjobTemplate == null) {
            Assertions.fail("The method 'loadInternalCronjobTemplate' does not exist.");
        }
        loadInternalCronjobTemplate.setAccessible(true);
        V1beta1CronJob internalCronjobTemplate = (V1beta1CronJob) loadInternalCronjobTemplate.invoke(service);
        var container = internalCronjobTemplate.getSpec()
                                                           .getJobTemplate()
                                                           .getSpec()
                                                           .getTemplate()
                                                           .getSpec()
                                                           .getContainers()
                                                           .get(0);

        var newCommand = new ArrayList<String>(container.getCommand());
        newCommand.set(2, "export PYTHONPATH=/usr/local/lib/python3.7/site-packages:/vdk/site-packages/ && /vdk/vdk run ./test-job");
        container.setCommand(newCommand);
        return internalCronjobTemplate;
    }

}
