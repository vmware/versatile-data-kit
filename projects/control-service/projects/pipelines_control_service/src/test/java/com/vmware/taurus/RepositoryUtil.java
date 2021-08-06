/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.*;
import org.junit.Assert;

import java.time.OffsetDateTime;

public class RepositoryUtil {

   public static DataJob createDataJob(JobsRepository jobsRepository) {
      JobConfig config = new JobConfig();
      config.setSchedule("schedule");
      config.setTeam("test-team");
      var expectedJob = new DataJob("test-job", config, DeploymentStatus.NONE);
      var actualJob = jobsRepository.save(expectedJob);
      Assert.assertEquals(expectedJob, actualJob);

      return actualJob;
   }

   public static DataJobExecution createDataJobExecution(
         JobExecutionRepository jobExecutionRepository,
         String executionId,
         DataJob dataJob,
         ExecutionStatus executionStatus) {

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
            .message("test_message")
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
