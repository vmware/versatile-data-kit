/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.JobAnnotation;
import com.vmware.taurus.service.model.JobLabel;
import io.kubernetes.client.custom.Quantity;
import io.kubernetes.client.models.*;
import org.joda.time.DateTime;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;

import java.lang.reflect.Method;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.*;

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

      Assert.assertEquals(expectedVDKContainer, actualVDKContainer);
   }

   @Test
   public void testGetJobExecutionStatus_emptyJob_shouldReturnEmptyJobExecutionStatus() {
      V1Job v1Job = new V1Job();
      KubernetesService mock = Mockito.mock(KubernetesService.class);
      Mockito.when(mock.getTerminationStatus(v1Job)).thenReturn(Optional.empty());
      Mockito.when(mock.getJobExecutionStatus(v1Job, null)).thenCallRealMethod();
      Optional<KubernetesService.JobExecution> actualJobExecutionStatusOptional = mock.getJobExecutionStatus(v1Job, null);

      Assert.assertTrue(actualJobExecutionStatusOptional.isPresent());

      KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
      Assert.assertNull(actualJobExecution.getExecutionId());
      Assert.assertNull(actualJobExecution.getJobName());
      Assert.assertNull(actualJobExecution.getJobVersion());
      Assert.assertNull(actualJobExecution.getDeployedDate());
      Assert.assertNull(actualJobExecution.getExecutionType());
      Assert.assertNull(actualJobExecution.getOpId());
      Assert.assertNull(actualJobExecution.getResourcesCpuRequest());
      Assert.assertNull(actualJobExecution.getResourcesCpuLimit());
      Assert.assertNull(actualJobExecution.getResourcesMemoryRequest());
      Assert.assertNull(actualJobExecution.getResourcesMemoryLimit());
      Assert.assertNull(actualJobExecution.getStartTime());
      Assert.assertNull(actualJobExecution.getEndTime());
      Assert.assertEquals(KubernetesService.JobExecution.Status.RUNNING, actualJobExecution.getStatus());
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

      Assert.assertTrue(actualJobExecutionStatusOptional.isPresent());

      KubernetesService.JobExecution actualJobExecution = actualJobExecutionStatusOptional.get();
      Assert.assertEquals(kubernetesJobName, actualJobExecution.getExecutionId());
      Assert.assertEquals(dataJobName, actualJobExecution.getJobName());
      Assert.assertEquals(jobVersion, actualJobExecution.getJobVersion());
      Assert.assertEquals(OffsetDateTime.parse(deployedDate), actualJobExecution.getDeployedDate());
      Assert.assertEquals(executionType, actualJobExecution.getExecutionType());
      Assert.assertEquals(opId, actualJobExecution.getOpId());
      Assert.assertEquals(Float.valueOf(cpuRequest), actualJobExecution.getResourcesCpuRequest());
      Assert.assertEquals(Float.valueOf(cpuLimit), actualJobExecution.getResourcesCpuLimit());
      Assert.assertEquals(memoryRequest, actualJobExecution.getResourcesMemoryRequest());
      Assert.assertEquals(memoryLimit, actualJobExecution.getResourcesMemoryLimit());
      Assert.assertEquals(OffsetDateTime.ofInstant(Instant.ofEpochMilli(startTime.getMillis()), ZoneOffset.UTC), actualJobExecution.getStartTime());
      Assert.assertEquals(OffsetDateTime.ofInstant(Instant.ofEpochMilli(endTime.getMillis()), ZoneOffset.UTC), actualJobExecution.getEndTime());
      Assert.assertEquals(KubernetesService.JobExecution.Status.FINISHED, actualJobExecution.getStatus());
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
                Assert.fail("The method 'loadInternalCronjobTemplate' does not exist.");
            }
            loadInternalCronjobTemplate.setAccessible(true);
            V1beta1CronJob internalCronjobTemplate = (V1beta1CronJob) loadInternalCronjobTemplate.invoke(service);
            // Prepare the 'checkForMissingEntries' method.
            Method checkForMissingEntries = KubernetesService.class.getDeclaredMethod("checkForMissingEntries", V1beta1CronJob.class);
            if(checkForMissingEntries == null) {
                Assert.fail("The method 'checkForMissingEntries' does not exist.");
            }
            checkForMissingEntries.setAccessible(true);
            V1beta1CronJob emptyCronjobToBeFixed = new V1beta1CronJob(); // Worst case scenario to test - empty cronjob.
            checkForMissingEntries.invoke(service, emptyCronjobToBeFixed);
            // We can't rely on equality check on root metadata/spec level, because if the internal template
            // has missing elements, the equality check will miss them. Instead, we will check the most
            // important elements one by one.
            Assert.assertNotNull(emptyCronjobToBeFixed.getMetadata());
            Assert.assertNotNull(emptyCronjobToBeFixed.getMetadata().getAnnotations());
            Assert.assertEquals(internalCronjobTemplate.getMetadata().getAnnotations(),
                    emptyCronjobToBeFixed.getMetadata().getAnnotations());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getSpec());
            Assert.assertNotNull(emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata());
            Assert.assertEquals(internalCronjobTemplate.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata().getLabels(),
                    emptyCronjobToBeFixed.getSpec().getJobTemplate().getSpec().getTemplate().getMetadata().getLabels());

            Assert.assertNotNull(internalCronjobTemplate.getSpec().getJobTemplate().getMetadata());
            // Step 3 - create and check the actual cronjob.
            Method[] methods = KubernetesService.class.getDeclaredMethods();
            // This is much easier than describing the whole method signature.
            Optional<Method> method = Arrays.stream(methods).filter(m -> m.getName().equals("cronJobFromTemplate")).findFirst();
            if(method.isEmpty()) {
                Assert.fail("The method 'cronJobFromTemplate' does not exist.");
            }
            method.get().setAccessible(true);
            V1beta1CronJob cronjob = (V1beta1CronJob) method.get().invoke(service, "test-job-name", "test-job-schedule", true, null, null, null, Collections.EMPTY_MAP, Collections.EMPTY_MAP, Collections.EMPTY_MAP, Collections.EMPTY_MAP);
            Assert.assertEquals("test-job-name", cronjob.getMetadata().getName());
            Assert.assertEquals("test-job-schedule", cronjob.getSpec().getSchedule());
            Assert.assertEquals(true, cronjob.getSpec().isSuspend());
            Assert.assertEquals(Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getLabels());
            Assert.assertEquals(Collections.EMPTY_MAP, cronjob.getSpec().getJobTemplate().getMetadata().getAnnotations());

        } catch(Exception e) {
            e.printStackTrace();
            Assert.fail(e.getMessage());
        }
    }
}
