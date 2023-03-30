/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.RepositoryUtil;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.exception.DataJobAlreadyRunningException;
import com.vmware.taurus.exception.DataJobDeploymentNotFoundException;
import com.vmware.taurus.exception.DataJobNotFoundException;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.diag.OperationContext;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

@SpringBootTest(classes = ControlplaneApplication.class)
public class JobExecutionServiceStartExecutionIT {

  @Autowired private JobsRepository jobsRepository;

  @Autowired private JobExecutionRepository jobExecutionRepository;

  @Autowired private JobExecutionService jobExecutionService;

  @MockBean private DataJobsKubernetesService dataJobsKubernetesService;

  @MockBean private DeploymentService deploymentService;

  @MockBean private OperationContext operationContext;

  @Test
  public void testStartDataJobExecution_nonExistingDataJob_shouldThrowException() {
    Assertions.assertThrows(
        DataJobNotFoundException.class,
        () ->
            jobExecutionService.startDataJobExecution(
                "test-team", "test-job", "", new DataJobExecutionRequest()));
  }

  @Test
  public void testStartDataJobExecution_nonExistingDataJobDeployment_shouldThrowException() {
    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

    Mockito.when(deploymentService.readDeployment(Mockito.eq(actualDataJob.getName())))
        .thenReturn(Optional.empty());

    Assertions.assertThrows(
        DataJobDeploymentNotFoundException.class,
        () ->
            jobExecutionService.startDataJobExecution(
                actualDataJob.getJobConfig().getTeam(),
                actualDataJob.getName(),
                "",
                new DataJobExecutionRequest()));
  }

  @Test
  public void testStartDataJobExecution_alreadyRunningDataJob_shouldThrowException()
      throws ApiException {
    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

    Mockito.when(deploymentService.readDeployment(Mockito.eq(actualDataJob.getName())))
        .thenReturn(Optional.of(new JobDeploymentStatus()));
    Mockito.when(dataJobsKubernetesService.isRunningJob(Mockito.eq(actualDataJob.getName())))
        .thenReturn(true);

    Assertions.assertThrows(
        DataJobAlreadyRunningException.class,
        () ->
            jobExecutionService.startDataJobExecution(
                actualDataJob.getJobConfig().getTeam(),
                actualDataJob.getName(),
                "",
                new DataJobExecutionRequest()));
  }

  @Test
  public void testStartDataJobExecution_correctDataJobDeployment_shouldStartDataJobExecution()
      throws ApiException {
    String opId = "test-op-id";
    String startedBy = "manual/vdk-control-cli" + "/" + operationContext.getUser();
    String cronJobName = "test-cron-job";

    DataJob actualDataJob = RepositoryUtil.createDataJob(jobsRepository);

    JobDeploymentStatus jobDeploymentStatus = new JobDeploymentStatus();
    jobDeploymentStatus.setCronJobName(cronJobName);
    Mockito.when(deploymentService.readDeployment(Mockito.eq(actualDataJob.getName())))
        .thenReturn(Optional.of(jobDeploymentStatus));
    Mockito.when(operationContext.getOpId()).thenReturn(opId);
    Mockito.when(dataJobsKubernetesService.isRunningJob(Mockito.eq(actualDataJob.getName())))
        .thenReturn(false);

    final Map<String, String> annotations = new LinkedHashMap<>();
    annotations.put(JobAnnotation.OP_ID.getValue(), opId);
    annotations.put(JobAnnotation.STARTED_BY.getValue(), startedBy);
    annotations.put(
        JobAnnotation.EXECUTION_TYPE.getValue(),
        JobExecutionService.ExecutionType.MANUAL.getValue());

    Map<String, String> envs = Map.of(JobEnvVar.VDK_OP_ID.getValue(), opId);

    String executionId =
        jobExecutionService.startDataJobExecution(
            actualDataJob.getJobConfig().getTeam(),
            actualDataJob.getName(),
            "",
            new DataJobExecutionRequest().startedBy("manual/vdk-control-cli"));
    Mockito.verify(dataJobsKubernetesService)
        .startNewCronJobExecution(
            Mockito.eq(cronJobName),
            Mockito.eq(executionId),
            Mockito.eq(annotations),
            Mockito.eq(envs),
            Mockito.any(),
            Mockito.any());

    Optional<DataJobExecution> actualDataJobExecutionOptional =
        jobExecutionRepository.findById(executionId);
    Assertions.assertTrue(actualDataJobExecutionOptional.isPresent());
    DataJobExecution actualDataJobExecution = actualDataJobExecutionOptional.get();
    Assertions.assertEquals(executionId, actualDataJobExecution.getId());
    Assertions.assertEquals(actualDataJob, actualDataJobExecution.getDataJob());
    Assertions.assertEquals(ExecutionStatus.SUBMITTED, actualDataJobExecution.getStatus());
    Assertions.assertEquals(ExecutionType.MANUAL, actualDataJobExecution.getType());
    Assertions.assertEquals(opId, actualDataJobExecution.getOpId());
    Assertions.assertEquals(startedBy, actualDataJobExecution.getStartedBy());
  }
}
