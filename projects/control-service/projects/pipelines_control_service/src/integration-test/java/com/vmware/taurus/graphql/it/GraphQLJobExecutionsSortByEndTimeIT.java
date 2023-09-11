/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.UUID;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.DataJobDeploymentExtension;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class GraphQLJobExecutionsSortByEndTimeIT extends BaseIT {

  @Autowired JobExecutionRepository jobExecutionRepository;

  @Autowired JobsRepository jobsRepository;

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension = new DataJobDeploymentExtension();

  @BeforeEach
  public void cleanup() {
    jobExecutionRepository.deleteAll();
  }

  private static String getQuery(String jobName, String executionsSortOrder) {
    return "{\n"
        + "  jobs(pageNumber: 1, pageSize: 100, filter: [{property: \"jobName\", pattern: \""
        + jobName
        + "\", sort: ASC}]) {\n"
        + "    content {\n"
        + "      jobName\n"
        + "      deployments {\n"
        + "        executions(pageNumber: 1, pageSize: 10, order: {property: \"endTime\","
        + " direction: "
        + executionsSortOrder
        + "}) {\n"
        + "          id\n"
        + "          endTime\n"
        + "        }\n"
        + "      }\n"
        + "    }\n"
        + "  }\n"
        + "}";
  }

  @Test
  public void testEmptyCallAsc(String jobName, String username) throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "ASC"))
                .with(user(username)))
        .andExpect(status().is(200));
  }

  @Test
  public void testEmptyCallDesc(String jobName, String username) throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "DESC"))
                .with(user(username)))
        .andExpect(status().is(200));
  }

  @Test
  public void testCallWithSingleExecution(String jobName, String username) throws Exception {
    var expectedId = "testId1";
    var expectedEndTime = OffsetDateTime.now();

    createDataJobExecution(expectedId, jobName, expectedEndTime);
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "DESC"))
                .with(user(username)))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].id").value(expectedId))
        .andExpect(
            jsonPath("$.data.content[0].deployments[0].executions[0].endTime")
                .value(roundDateTimeToMicros(expectedEndTime)));
  }

  @Test
  public void testCallTwoExecutionsSortAsc(String jobName, String username) throws Exception {
    var expectedId1 = "testId1";
    var expectedId2 = "testId2";
    var expectedEndTimeLarger = OffsetDateTime.now();
    var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

    createDataJobExecution(expectedId1, jobName, expectedEndTimeLarger);
    createDataJobExecution(expectedId2, jobName, expectedEndTimeSmaller);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "ASC"))
                .with(user(username)))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].id").value(expectedId2))
        .andExpect(
            jsonPath("$.data.content[0].deployments[0].executions[0].endTime")
                .value(roundDateTimeToMicros(expectedEndTimeSmaller)))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1].id").value(expectedId1))
        .andExpect(
            jsonPath("$.data.content[0].deployments[0].executions[1].endTime")
                .value(roundDateTimeToMicros(expectedEndTimeLarger)));
  }

  @Test
  public void testCallTwoExecutionsSortDesc(String jobName, String username) throws Exception {
    var expectedId1 = "testId1";
    var expectedId2 = "testId2";
    var expectedEndTimeLarger = OffsetDateTime.now();
    var expectedEndTimeSmaller = OffsetDateTime.now().minusDays(1);

    createDataJobExecution(expectedId1, jobName, expectedEndTimeLarger);
    createDataJobExecution(expectedId2, jobName, expectedEndTimeSmaller);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "DESC"))
                .with(user(username)))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0].id").value(expectedId1))
        .andExpect(
            jsonPath("$.data.content[0].deployments[0].executions[0].endTime")
                .value(roundDateTimeToMicros(expectedEndTimeLarger)))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[1].id").value(expectedId2))
        .andExpect(
            jsonPath("$.data.content[0].deployments[0].executions[1].endTime")
                .value(roundDateTimeToMicros(expectedEndTimeSmaller)));
  }

  @Test
  public void testCallPagination(String jobName, String username) throws Exception {
    for (int i = 0; i < 15; i++) {
      createDataJobExecution(UUID.randomUUID().toString(), jobName, OffsetDateTime.now());
    }
    // Query pagination is set to 10 items per page.
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery(jobName, "DESC"))
                .with(user(username)))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[0]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[9]").exists())
        .andExpect(jsonPath("$.data.content[0].deployments[0].executions[10]").doesNotExist());
  }

  private void createDataJobExecution(String executionId, String jobName, OffsetDateTime endTime) {

    DataJob dataJob = jobsRepository.findById(jobName).get();
    var jobExecution =
        DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .startTime(OffsetDateTime.now())
            .endTime(endTime)
            .type(ExecutionType.MANUAL)
            .status(ExecutionStatus.SUCCEEDED)
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

  private static String roundDateTimeToMicros(OffsetDateTime dateTime) {
    return dateTime.plusNanos(500).truncatedTo(ChronoUnit.MICROS).toString();
  }
}
