/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ServiceApp;
import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.time.OffsetDateTime;

import static org.apache.commons.lang3.RandomStringUtils.random;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(classes = ServiceApp.class)
@AutoConfigureMockMvc
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class GraphQLJobExecutionsStatusCountIT extends BaseDataJobDeploymentIT {

   @Autowired
   JobExecutionRepository jobExecutionRepository;

   @Autowired
   JobsRepository jobsRepository;

   @BeforeEach
   public void cleanup() {
      jobExecutionRepository.deleteAll();
   }

   private void addJobExecution(OffsetDateTime endTime, String executionId, ExecutionStatus executionStatus, String jobName) {
      var execution = createDataJobExecution(executionId, jobName, executionStatus,
              "message", OffsetDateTime.now());
      execution.setEndTime(endTime);
      jobExecutionRepository.save(execution);
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
   public void testExecutionStatusCount_expectTwoSuccessful(String jobName, String username) throws Exception {
      var expectedEndTimeLarger = OffsetDateTime.now();
      var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

      addJobExecution(expectedEndTimeLarger, random(10), ExecutionStatus.FINISHED, jobName);
      addJobExecution(expectedEndTimeSmaller, random(11), ExecutionStatus.FINISHED, jobName);

      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI).queryParam("query", getQuery(jobName)).with(user(username)))
              .andExpect(status().is(200))
              .andExpect(content().contentType("application/json"))
              .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(2))
              .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(0));

   }

   @Test
   public void testExecutionStatusCount_expectNoCounts(String jobName, String username) throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI).queryParam("query", getQuery(jobName)).with(user(username)))
              .andExpect(status().is(200))
              .andExpect(content().contentType("application/json"))
              .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(0))
              .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(0));
   }

   @Test
   public void testExecutionStatusCount_expectTwoSuccessfulTwoFailed(String jobName, String username) throws Exception {
      var expectedEndTimeLarger = OffsetDateTime.now();
      var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

      addJobExecution(expectedEndTimeLarger, random(10), ExecutionStatus.FINISHED, jobName);
      addJobExecution(expectedEndTimeSmaller, random(11), ExecutionStatus.FINISHED, jobName);
      addJobExecution(expectedEndTimeLarger, random(12), ExecutionStatus.FAILED, jobName);
      addJobExecution(expectedEndTimeSmaller, random(13), ExecutionStatus.FAILED, jobName);

      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI).queryParam("query", getQuery(jobName)).with(user(username)))
              .andExpect(status().is(200))
              .andExpect(content().contentType("application/json"))
              .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(2))
              .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(2));

   }

   @Test
   public void testExecutionStatusCount_expectOneSuccessfulOneFailed(String jobName, String username) throws Exception {
      var expectedEndTimeLarger = OffsetDateTime.now();

      addJobExecution(expectedEndTimeLarger, random(10), ExecutionStatus.FINISHED, jobName);
      addJobExecution(expectedEndTimeLarger, random(11), ExecutionStatus.FAILED, jobName);

      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI).queryParam("query", getQuery(jobName)).with(user(username)))
              .andExpect(status().is(200))
              .andExpect(content().contentType("application/json"))
              .andExpect(jsonPath("$.data.content[0].deployments[0].successfulExecutions").value(1))
              .andExpect(jsonPath("$.data.content[0].deployments[0].failedExecutions").value(1));

   }

   private DataJobExecution createDataJobExecution(
           String executionId,
           String jobName,
           ExecutionStatus executionStatus,
           String message,
           OffsetDateTime startTime) {

      DataJob dataJob = jobsRepository.findById(jobName).get();

      var jobExecution = DataJobExecution.builder()
              .id(executionId)
              .dataJob(dataJob)
              .startTime(startTime)
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

      return jobExecution;
   }
}
