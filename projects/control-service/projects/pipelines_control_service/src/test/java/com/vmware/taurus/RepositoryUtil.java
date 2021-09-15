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
import java.util.Random;

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
         String message) {

      var expectedJobExecution = DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .startTime(OffsetDateTime.now())
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
