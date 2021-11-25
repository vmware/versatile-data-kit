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
import java.util.List;

import org.hamcrest.Matchers;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class GraphQLExecutionsIT extends BaseIT {

   @Autowired
   JobExecutionRepository jobExecutionRepository;

   @Autowired
   JobsRepository jobsRepository;

   private static final String TEST_JOB_NAME_1 = "TEST-JOB-NAME-1";
   private static final String TEST_JOB_NAME_2 = "TEST-JOB-NAME-2";
   private static final String TEST_JOB_NAME_3 = "TEST-JOB-NAME-3";

   private DataJob dataJob1;
   private DataJob dataJob2;
   private DataJob dataJob3;

   private DataJobExecution dataJobExecution1;
   private DataJobExecution dataJobExecution2;
   private DataJobExecution dataJobExecution3;

   @AfterEach
   public void cleanup() {
      jobsRepository.deleteAllById(List.of(TEST_JOB_NAME_1, TEST_JOB_NAME_2, TEST_JOB_NAME_3));
   }

   @BeforeEach
   public void setup() {
      this.dataJob1 = jobsRepository.save(new DataJob(TEST_JOB_NAME_1, new JobConfig()));
      this.dataJob2 = jobsRepository.save(new DataJob(TEST_JOB_NAME_2, new JobConfig()));
      this.dataJob3 = jobsRepository.save(new DataJob(TEST_JOB_NAME_3, new JobConfig()));

      OffsetDateTime now = OffsetDateTime.now();
      this.dataJobExecution1 = JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository, "testId1", dataJob1, now, now, ExecutionStatus.FINISHED);
      this.dataJobExecution2 = JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository, "testId2", dataJob2, now.minusSeconds(1), now.minusSeconds(1), ExecutionStatus.RUNNING);
      this.dataJobExecution3 = JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository, "testId3", dataJob3, now.minusSeconds(10), now.minusSeconds(10), ExecutionStatus.SUBMITTED);
   }

   private static String getQuery() {
      return "query($filter: DataJobExecutionFilter, $order: DataJobExecutionOrder, $pageNumber: Int, $pageSize: Int) {" +
            "  executions(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, order: $order) {" +
            "    content {" +
            "      id" +
            "      jobName" +
            "      startTime" +
            "      endTime" +
            "      status" +
            "    }" +
            "    totalPages" +
            "    totalItems" +
            "  }" +
            "}";
   }

   @Test
   public void testExecutions_filterByStartTimeGte() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"startTimeGte\": \"" + dataJobExecution2.getStartTime() + "\"" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user(TEST_USERNAME)))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

   @Test
   public void testExecutions_filterByStartTimeLte() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"startTimeLte\": \"" + dataJobExecution2.getStartTime() + "\"" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user(TEST_USERNAME)))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

   @Test
   public void testExecutions_filterByEndTimeGte() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"endTimeGte\": \"" + dataJobExecution2.getEndTime() + "\"" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user("user")))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

   @Test
   public void testExecutions_filterByEndTimeLte() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"endTimeLte\": \"" + dataJobExecution2.getEndTime() + "\"" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user("user")))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

   @Test
   public void testExecutions_filterByStatusIn() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"statusIn\": [\"" + dataJobExecution1.getStatus().toString() + "\", \"" + dataJobExecution2.getStatus().toString() + "\"]" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user("user")))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath("$.data.content[*].id", Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

   @Test
   public void testExecutions_filterByJobNameIn() throws Exception {
      mockMvc.perform(MockMvcRequestBuilders.get(JOBS_URI)
                  .queryParam("query", getQuery())
                  .param("variables", "{" +
                        "\"filter\": {" +
                        "      \"jobNameIn\": [\"" + dataJobExecution1.getDataJob().getName() + "\"]" +
                        "    }," +
                        "\"pageNumber\": 1," +
                        "\"pageSize\": 10" +
                        "}")
                  .with(user("user")))
            .andExpect(status().is(200))
            .andExpect(content().contentType("application/json"))
            .andExpect(jsonPath(
                  "$.data.content[*].id",
                  Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
            .andExpect(jsonPath(
                  "$.data.content[*].jobName",
                  Matchers.contains(dataJob1.getName(), dataJob2.getName())))
            .andExpect(jsonPath(
                  "$.data.content[*].status",
                  Matchers.contains(dataJobExecution1.getStatus().toString(), dataJobExecution2.getStatus().toString())))
            .andExpect(jsonPath("$.data.content[*].id", Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
   }

}
