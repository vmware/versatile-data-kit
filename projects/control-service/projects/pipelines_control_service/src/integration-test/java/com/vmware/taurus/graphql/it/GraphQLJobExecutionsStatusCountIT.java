/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.OffsetDateTime;

import org.hamcrest.core.IsNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;

public class GraphQLJobExecutionsStatusCountIT extends BaseDataJobDeploymentIT {

   @Autowired
   JobExecutionRepository jobExecutionRepository;

   @Autowired
   JobsRepository jobsRepository;

   @AfterEach
   public void cleanup() {
      jobExecutionRepository.deleteAll();
   }

   private static String getQuery(String jobName) {
      return "{\n" +
            "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"jobName\", pattern: \"" + jobName + "\"}]) {\n" +
            "    content {\n" +
            "      jobName\n" +
            "      deployments {\n" +
            "        successfulExecutions\n " +
            "        failedExecutions\n " +
            "      }\n" +
            "    }\n" +
            "  }\n" +
            "}";
   }

   @Test
   public void testExecutionStatusCountFieldsPresent(String jobName, String username) throws Exception {
      var expectedEndTimeLarger = OffsetDateTime.now();
      var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

      createDataJobExecution("testId", jobName, expectedEndTimeLarger);
      createDataJobExecution("testId2", jobName, expectedEndTimeSmaller);

      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery(jobName))
                  .with(user(username)))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(IsNull.nullValue()))
            .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(IsNull.nullValue()));

   }

   private void createDataJobExecution(
         String executionId,
         String jobName,
         OffsetDateTime endTime) {

      DataJob dataJob = jobsRepository.findById(jobName).get();
      var jobExecution = DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .startTime(OffsetDateTime.now())
            .endTime(endTime)
            .type(ExecutionType.MANUAL)
            .status(ExecutionStatus.FINISHED)
            .resourcesCpuRequest(1F)
            .resourcesCpuLimit(2F)
            .resourcesMemoryRequest(500)
            .resourcesMemoryLimit(1000)
            .message("message")
            .lastDeployedBy("test_user")
            .lastDeployedDate(OffsetDateTime.now())
            .jobVersion("test_version")
            .jobSchedule("*/5 * * * *")
            .opId("test_op_id")
            .vdkVersion("test_vdk_version")
            .build();

      jobExecutionRepository.save(jobExecution);
   }
}
