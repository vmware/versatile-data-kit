/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobConfig;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.OffsetDateTime;
import java.util.List;

import static com.vmware.taurus.datajobs.it.common.JobExecutionUtil.getTimeAccurateToMicroSecond;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class GraphQLExecutionsIT extends BaseIT {

  @Autowired JobExecutionRepository jobExecutionRepository;

  @Autowired JobsRepository jobsRepository;

  private static final String TEST_JOB_NAME_1 = "TEST-JOB-NAME-1";
  private static final String TEST_JOB_NAME_2 = "TEST-JOB-NAME-2";
  private static final String TEST_JOB_NAME_3 = "TEST-JOB-NAME-3";

  private DataJob dataJob1;
  private DataJob dataJob2;
  private DataJob dataJob3;

  private DataJobExecution dataJobExecution1;
  private DataJobExecution dataJobExecution2;
  private DataJobExecution dataJobExecution3;

  @BeforeEach
  public void setup() {
    cleanup();

    var config1 = new JobConfig();
    config1.setTeam("test-team1");

    var config2 = new JobConfig();
    config2.setTeam("test-team2");

    var config3 = new JobConfig();
    config3.setTeam("test-team3");

    this.dataJob1 = jobsRepository.save(new DataJob(TEST_JOB_NAME_1, config1));
    this.dataJob2 = jobsRepository.save(new DataJob(TEST_JOB_NAME_2, config2));
    this.dataJob3 = jobsRepository.save(new DataJob(TEST_JOB_NAME_3, config3));

    OffsetDateTime now = getTimeAccurateToMicroSecond();
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
            ExecutionStatus.USER_ERROR);
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
        + " filter: $filter, order: $order) {    content {      id      jobName     "
        + " startTime      endTime      status      deployment {        id        enabled   "
        + "     jobVersion        deployedDate        deployedBy        resources {         "
        + "  cpuLimit           cpuRequest           memoryLimit           memoryRequest    "
        + "    }        schedule {           scheduleCron        }        vdkVersion      } "
        + "   }    totalPages    totalItems  }}";
  }

  private void cleanup() {
    jobsRepository.deleteAll(
        jobsRepository.findAllById(List.of(TEST_JOB_NAME_1, TEST_JOB_NAME_2, TEST_JOB_NAME_3)));
  }

  @Test
  public void testExecutions_filterByStartTimeGte_shouldReturnAllProperties() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"startTimeGte\": \""
                        + dataJobExecution2.getStartTime()
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
                Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].jobName",
                Matchers.contains(dataJob1.getName(), dataJob2.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(
                    dataJobExecution1.getStatus().toString(),
                    dataJobExecution2.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.jobVersion",
                Matchers.contains(
                    dataJobExecution1.getJobVersion(), dataJobExecution2.getJobVersion())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.deployedDate",
                Matchers.contains(
                    dataJobExecution1.getLastDeployedDate().toString(),
                    dataJobExecution2.getLastDeployedDate().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.deployedBy",
                Matchers.contains(
                    dataJobExecution1.getLastDeployedBy(), dataJobExecution2.getLastDeployedBy())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.vdkVersion",
                Matchers.contains(
                    dataJobExecution1.getVdkVersion(), dataJobExecution2.getVdkVersion())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.resources.cpuRequest",
                Matchers.contains(
                    convertFloatToDouble(dataJobExecution1.getResourcesCpuRequest()),
                    convertFloatToDouble(dataJobExecution2.getResourcesCpuRequest()))))
        .andExpect(jsonPath(
            "$.data.content[*].deployment.resources.cpuLimit",
            Matchers.contains(
                    convertFloatToDouble(dataJobExecution1.getResourcesCpuLimit()),
                    convertFloatToDouble(dataJobExecution2.getResourcesCpuLimit()))))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.resources.memoryRequest",
                Matchers.contains(
                    dataJobExecution1.getResourcesMemoryRequest(),
                    dataJobExecution2.getResourcesMemoryRequest())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.resources.memoryLimit",
                Matchers.contains(
                    dataJobExecution1.getResourcesMemoryLimit(),
                    dataJobExecution2.getResourcesMemoryLimit())))
        .andExpect(
            jsonPath(
                "$.data.content[*].deployment.schedule.scheduleCron",
                Matchers.contains(
                    dataJobExecution1.getJobSchedule(), dataJobExecution2.getJobSchedule())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
  }

  @Test
  public void testExecutions_filterByStartTimeLte() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"startTimeLte\": \""
                        + dataJobExecution2.getStartTime()
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
                Matchers.contains(dataJobExecution2.getId(), dataJobExecution3.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].jobName",
                Matchers.contains(dataJob2.getName(), dataJob3.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(
                    dataJobExecution2.getStatus().toString(),
                    dataJobExecution3.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution1.getId()))));
  }

  @Test
  public void testExecutions_filterByEndTimeGte() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"endTimeGte\": \""
                        + dataJobExecution2.getEndTime()
                        + "\""
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user("user")))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].jobName",
                Matchers.contains(dataJob1.getName(), dataJob2.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(
                    dataJobExecution1.getStatus().toString(),
                    dataJobExecution2.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
  }

  @Test
  public void testExecutions_filterByEndTimeLte() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"endTimeLte\": \""
                        + dataJobExecution2.getEndTime()
                        + "\""
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user("user")))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.contains(dataJobExecution2.getId(), dataJobExecution3.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].jobName",
                Matchers.contains(dataJob2.getName(), dataJob3.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(
                    dataJobExecution2.getStatus().toString(),
                    dataJobExecution3.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution1.getId()))));
  }

  @Test
  public void testExecutions_filterByStatusIn() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"statusIn\": [\""
                        + dataJobExecution1.getStatus().toString()
                        + "\", \""
                        + dataJobExecution2.getStatus().toString()
                        + "\"]"
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user("user")))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.contains(dataJobExecution1.getId(), dataJobExecution2.getId())))
        .andExpect(
            jsonPath(
                "$.data.content[*].jobName",
                Matchers.contains(dataJob1.getName(), dataJob2.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(
                    dataJobExecution1.getStatus().toString(),
                    dataJobExecution2.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution3.getId()))));
  }

  @Test
  public void testExecutions_filterByJobNameIn() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"jobNameIn\": [\""
                        + dataJobExecution1.getDataJob().getName()
                        + "\"]"
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user("user")))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[*].id", Matchers.contains(dataJobExecution1.getId())))
        .andExpect(jsonPath("$.data.content[*].jobName", Matchers.contains(dataJob1.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(dataJobExecution1.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id", Matchers.not(Matchers.contains(dataJobExecution3.getId()))))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution2.getId()))));
  }

  @Test
  public void testExecutions_filterByTeamNameIn() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery())
                .param(
                    "variables",
                    "{"
                        + "\"filter\": {"
                        + "      \"teamNameIn\": [\""
                        + dataJobExecution1.getDataJob().getJobConfig().getTeam()
                        + "\"]"
                        + "    },"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .with(user("user")))
        .andExpect(status().is(200))
        .andExpect(content().contentType("application/json"))
        .andExpect(jsonPath("$.data.content[*].id", Matchers.contains(dataJobExecution1.getId())))
        .andExpect(jsonPath("$.data.content[*].jobName", Matchers.contains(dataJob1.getName())))
        .andExpect(
            jsonPath(
                "$.data.content[*].status",
                Matchers.contains(dataJobExecution1.getStatus().toString())))
        .andExpect(
            jsonPath(
                "$.data.content[*].id", Matchers.not(Matchers.contains(dataJobExecution3.getId()))))
        .andExpect(
            jsonPath(
                "$.data.content[*].id",
                Matchers.not(Matchers.contains(dataJobExecution2.getId()))));
  }


  /**
   * Helper method that converts Float to Double and rounds it as scale 2.
   * It is necessary because tests' checks resolved Float to <0.1F> but it should be <0.1>.
   */
  private static Double convertFloatToDouble(Float value) {
    return BigDecimal.valueOf(value).setScale(2, RoundingMode.HALF_UP).doubleValue();
  }
}
