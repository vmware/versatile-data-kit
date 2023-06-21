/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.text.MessageFormat;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

import org.hamcrest.Matchers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
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

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class GraphQLExecutionsLogsUrlIT extends BaseIT {

  @Autowired JobExecutionRepository jobExecutionRepository;

  @Autowired JobsRepository jobsRepository;

  private static final String LOGS_URL_TEMPLATE =
      "https://log-insight-base-url/li/query/stream?query=%C2%A7%C2%A7%C2%A7AND%C"
          + "2%A7%C2%A7%C2%A7%C2%A7{0}%C2%A7{1}%C2%A7true%C2%A7COUNT%C2%A7*%C2%A7"
          + "timestamp%C2%A7pageSortPreference:%7B%22sortBy%22%3A%22-{2}-{3}-"
          + "ingest_timestamp%22%2C%22sortOrder%22%3A%22DESC%22%7D%C2%A7"
          + "alertDefList:%5B%5D%C2%A7partitions:%C2%A7%C2%A7text:CONTAINS:{4}*";

  private static final String TEST_JOB_NAME_1 = "TEST-JOB-NAME-1";
  private static final String TEST_JOB_NAME_2 = "TEST-JOB-NAME-2";
  private static final String TEST_JOB_NAME_3 = "TEST-JOB-NAME-3";

  private static final long TEST_START_TIME_OFFSET_SECONDS = 1000;
  private static final long TEST_END_TIME_OFFSET_SECONDS = -1000;

  private DataJobExecution dataJobExecution1;
  private DataJobExecution dataJobExecution2;
  private DataJobExecution dataJobExecution3;

  @DynamicPropertySource
  static void dynamicProperties(DynamicPropertyRegistry registry) {
    String logsUrlTemplate =
        MessageFormat.format(
            LOGS_URL_TEMPLATE,
            "{{start_time}}",
            "{{end_time}}",
            "{{job_name}}",
            "{{op_id}}",
            "{{execution_id}}");
    registry.add("datajobs.executions.logsUrl.template", () -> logsUrlTemplate);
    registry.add("datajobs.executions.logsUrl.dateFormat", () -> "unix");
    registry.add(
        "datajobs.executions.logsUrl.startTimeOffsetSeconds", () -> TEST_START_TIME_OFFSET_SECONDS);
    registry.add(
        "datajobs.executions.logsUrl.endTimeOffsetSeconds", () -> TEST_END_TIME_OFFSET_SECONDS);
  }

  @BeforeEach
  public void setup() {
    cleanup();

    DataJob dataJob1 = jobsRepository.save(new DataJob(TEST_JOB_NAME_1, new JobConfig()));
    DataJob dataJob2 = jobsRepository.save(new DataJob(TEST_JOB_NAME_2, new JobConfig()));
    DataJob dataJob3 = jobsRepository.save(new DataJob(TEST_JOB_NAME_3, new JobConfig()));

    OffsetDateTime now = OffsetDateTime.now();
    this.dataJobExecution1 =
        JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository, "testId1", dataJob1, now, now, ExecutionStatus.SUCCEEDED);
    this.dataJobExecution2 =
        JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository,
            "testId2",
            dataJob2,
            now.minusSeconds(1),
            now.minusSeconds(1),
            ExecutionStatus.RUNNING);
    this.dataJobExecution3 =
        JobExecutionUtil.createDataJobExecution(
            jobExecutionRepository,
            "testId3",
            dataJob3,
            now.minusSeconds(10),
            now.minusSeconds(10),
            ExecutionStatus.SUBMITTED);
  }

  private static String getQuery() {
    return "query($filter: DataJobExecutionFilter, $order: DataJobExecutionOrder, $pageNumber: Int,"
        + " $pageSize: Int) {  executions(pageNumber: $pageNumber, pageSize: $pageSize,"
        + " filter: $filter, order: $order) {    content {      id      logsUrl    }   "
        + " totalPages    totalItems  }}";
  }

  private void cleanup() {
    jobsRepository
        .findAllById(List.of(TEST_JOB_NAME_1, TEST_JOB_NAME_2, TEST_JOB_NAME_3))
        .forEach(dataJob -> jobsRepository.delete(dataJob));
  }

  @Test
  public void testExecutions_filterByStartTimeGte() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"startTimeGte\": \""
                        + dataJobExecution3.getStartTime().truncatedTo(ChronoUnit.MICROS)
                        + "\""
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user(TEST_USERNAME)))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.contains(
                    dataJobExecution1.getId(),
                    dataJobExecution2.getId(),
                    dataJobExecution3.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].logsUrl",
                Matchers.contains(
                    buildLogsUrl(dataJobExecution1),
                    buildLogsUrl(dataJobExecution2),
                    buildLogsUrl(dataJobExecution3))));
  }

  private static String buildLogsUrl(DataJobExecution dataJobExecution) {
    return MessageFormat.format(
        LOGS_URL_TEMPLATE,
        String.valueOf(
            dataJobExecution
                .getStartTime()
                .toInstant()
                .plusSeconds(TEST_START_TIME_OFFSET_SECONDS)
                .toEpochMilli()),
        String.valueOf(
            dataJobExecution
                .getEndTime()
                .toInstant()
                .plusSeconds(TEST_END_TIME_OFFSET_SECONDS)
                .toEpochMilli()),
        dataJobExecution.getDataJob().getName(),
        dataJobExecution.getOpId(),
        dataJobExecution.getId());
  }
}
