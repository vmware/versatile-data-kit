/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.*;
import org.junit.jupiter.api.Assertions;

import java.time.OffsetDateTime;

public final class RepositoryUtil {

   public static DataJob createDataJob(JobsRepository jobsRepository) {
      JobConfig config = new JobConfig();
      config.setSchedule("schedule");
      config.setTeam("test-team");
      var expectedJob = new DataJob("test-job", config, DeploymentStatus.NONE);
      var actualJob = jobsRepository.save(expectedJob);
      Assertions.assertEquals(expectedJob, actualJob);

      return actualJob;
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus) {

      return createDataJobExecution(jobExecutionRepository, executionId, dataJob, executionStatus, "test_message");
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus,
         OffsetDateTime startTime,
         OffsetDateTime endTime) {

      return createDataJobExecution(jobExecutionRepository, executionId, dataJob, executionStatus, "test_message", startTime, endTime);
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus,
         String message,
         OffsetDateTime startTime) {

      return createDataJobExecution(jobExecutionRepository, executionId, dataJob, executionStatus, message, startTime, OffsetDateTime.now());
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus,
         OffsetDateTime startTime) {

      return createDataJobExecution(jobExecutionRepository, executionId, dataJob, executionStatus, "test_message", startTime, OffsetDateTime.now());
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus,
         String message) {

      return createDataJobExecution(jobExecutionRepository, executionId, dataJob, executionStatus, message, OffsetDateTime.now(), OffsetDateTime.now());
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus,
         String message,
         OffsetDateTime startTime,
         OffsetDateTime endTime) {

      var expectedJobExecution = DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .startTime(startTime)
            .endTime(endTime)
            .type(ExecutionType.MANUAL)
            .status(executionStatus)
            .resourcesCpuRequest(1F)
            .resourcesCpuLimit(2F)
            .resourcesMemoryRequest(500)
            .resourcesMemoryLimit(1000)
            .message(message)
            .lastDeployedBy("test_user")
            .lastDeployedDate(OffsetDateTime.now())
            .jobVersion("test_version")
            .jobSchedule("*/5 * * * *")
            .opId("test_op_id")
            .vdkVersion("test_vdk_version")
            .build();

      return jobExecutionRepository.save(expectedJobExecution);
   }
}
