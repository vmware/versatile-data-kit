/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.jayway.jsonpath.JsonPath;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.deploy.DeploymentService;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;

import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobGraphQLIT extends BaseIT {

   @Autowired
   private JobsRepository jobsRepository;

   @MockBean
   private DeploymentService deploymentService;

   private static final String DEFAULT_QUERY_WITH_VARS =
         "query($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
               "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
               "    content {" +
               "      jobName" +
               "      config {" +
               "        team" +
               "        description" +
               "        schedule {" +
               "          scheduleCron" +
               "        }" +
               "      }" +
               "    }" +
               "    totalPages" +
               "    totalItems" +
               "  }" +
               "}";

   @Test
   public void testPagination() throws Exception {
      createDummyJobs();

      // Test listing of team jobs by filtering with team property
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"filter\": [" +
                  "    {" +
                  "      \"property\": \"config.team\"," +
                  "      \"pattern\": \"" + TEST_TEAM_NAME + "\"" +
                  "    }" +
                  "  ]," +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 10" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (s.contains(TEST_JOB_1))
                  && (s.contains(TEST_JOB_2))
                  && (s.contains(TEST_JOB_6))
                  && (!s.contains(TEST_JOB_3))
                  && (!s.contains(TEST_JOB_4))
                  && (!s.contains(TEST_JOB_5)))));

      // Test listing of team jobs by searching for team name
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"search\": \""+NEW_TEST_TEAM_NAME+"\"," +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 10" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (!s.contains(TEST_JOB_1))
                  && (!s.contains(TEST_JOB_2))
                  && (!s.contains(TEST_JOB_6))
                  && (s.contains(TEST_JOB_3))
                  && (s.contains(TEST_JOB_4))
                  && (s.contains(TEST_JOB_5)))));

      // Test showing only first page
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 2" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (s.contains(TEST_JOB_1))
                  && (s.contains(TEST_JOB_2))
                  && (!s.contains(TEST_JOB_3))
                  && (!s.contains(TEST_JOB_4))
                  && (!s.contains(TEST_JOB_5))
                  && (!s.contains(TEST_JOB_6)))));

      // Test showing only middle page
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"pageNumber\": 2," +
                  "\"pageSize\": 2" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (!s.contains(TEST_JOB_1))
                  && (!s.contains(TEST_JOB_2))
                  && (s.contains(TEST_JOB_3))
                  && (s.contains(TEST_JOB_4))
                  && (!s.contains(TEST_JOB_5))
                  && (!s.contains(TEST_JOB_6)))));

      // Test showing only last page
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"pageNumber\": 3," +
                  "\"pageSize\": 2" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (!s.contains(TEST_JOB_1))
                  && (!s.contains(TEST_JOB_2))
                  && (!s.contains(TEST_JOB_3))
                  && (!s.contains(TEST_JOB_4))
                  && (s.contains(TEST_JOB_5))
                  && (s.contains(TEST_JOB_6)))));

      // Test showing only first page sorted DESC by jobName
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"filter\": [" +
                  "    {" +
                  "      \"property\": \"jobName\"," +
                  "      \"sort\": \"DESC\"" +
                  "    }" +
                  "  ]," +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 2" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (!s.contains(TEST_JOB_1))
                  && (!s.contains(TEST_JOB_2))
                  && (!s.contains(TEST_JOB_3))
                  && (!s.contains(TEST_JOB_4))
                  && (s.contains(TEST_JOB_5))
                  && (s.contains(TEST_JOB_6)))));

      // Test showing custom filtered, sorted and paged data jobs by multiple parameters
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", DEFAULT_QUERY_WITH_VARS)
            .param("variables", "{" +
                  "\"filter\": [" +
                  "    {" +
                  "      \"property\": \"config.team\"," +
                  "      \"pattern\": \"" + TEST_TEAM_NAME + "\"" +
                  "    }," +
                  "    {" +
                  "      \"property\": \"jobName\"," +
                  "      \"sort\": \"DESC\"" +
                  "    }" +
                  "  ]," +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 2" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(content().string(lambdaMatcher(s -> (!s.contains(TEST_JOB_1))
                  && (s.contains(TEST_JOB_2))
                  && (!s.contains(TEST_JOB_3))
                  && (!s.contains(TEST_JOB_4))
                  && (!s.contains(TEST_JOB_5))
                  && (s.contains(TEST_JOB_6)))));

      deleteDummyJobs();
   }

   @Test
   void testFields() throws Exception {
      var dataJob = createJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);

      // Test requesting of fields that are computed
      mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query",
                  "query($filter: [Predicate], $executionFilter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
                  "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                  "    content {" +
                  "      jobName" +
                  "      deployments {" +
                  "        id" +
                  "        enabled" +
                  "        lastExecutionStatus" +
                  "        lastExecutionTime" +
                  "        lastExecutionDuration" +
                  "        executions(pageNumber: 1, pageSize: 5, filter: $executionFilter) {" +
                  "          id" +
                  "          status" +
                  "        }" +
                  "      }" +
                  "      config {" +
                  "        team" +
                  "        description" +
                  "        schedule {" +
                  "          scheduleCron" +
                  "          nextRunEpochSeconds" +
                  "        }" +
                  "      }" +
                  "    }" +
                  "    totalPages" +
                  "    totalItems" +
                  "  }" +
                  "}")
            .param("variables", "{" +
                  "\"search\": \"" + TEST_JOB_1 + "\"," +
                  "\"pageNumber\": 1," +
                  "\"pageSize\": 10," +
                  "\"executionFilter\": [" +
                  "    {" +
                  "      \"sort\": \"DESC\"," +
                  "      \"property\": \"deployments.executions.status\"" +
                  "    }" +
                  "  ]" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.content[0].config.team", is(TEST_TEAM_NAME)))
            .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron", is(TEST_JOB_SCHEDULE)))
            .andExpect(jsonPath("$.data.content[0].config.schedule.nextRunEpochSeconds", greaterThan(1)))
            .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionStatus", is(dataJob.getLastExecutionStatus().name())))
            .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionTime", isDate(dataJob.getLastExecutionEndTime())))
            .andExpect(jsonPath("$.data.content[0].deployments[0].lastExecutionDuration", is(dataJob.getLastExecutionDuration())))
            .andReturn().getResponse().getContentAsString();

      deleteJob(TEST_JOB_1, TEST_TEAM_NAME);
   }

   @Test
   void testFilteringByLastExecutionStatus() throws Exception {
      createJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);
      createJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME,
              ExecutionStatus.FAILED, OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC), null);
      createJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, null, 0);
      createJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME,
              null, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);

      String resultAsString = mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                      .with(user("user"))
                      .param("query",
                              "query($filter: [Predicate], $executionFilter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
                                      "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                                      "    content {" +
                                      "      jobName" +
                                      "      deployments {" +
                                      "        id" +
                                      "        enabled" +
                                      "        lastExecutionStatus" +
                                      "        lastExecutionTime" +
                                      "        lastExecutionDuration" +
                                      "        executions(pageNumber: 1, pageSize: 5, filter: $executionFilter) {" +
                                      "          id" +
                                      "          status" +
                                      "        }" +
                                      "      }" +
                                      "      config {" +
                                      "        team" +
                                      "        description" +
                                      "        schedule {" +
                                      "          scheduleCron" +
                                      "          nextRunEpochSeconds" +
                                      "        }" +
                                      "      }" +
                                      "    }" +
                                      "    totalPages" +
                                      "    totalItems" +
                                      "  }" +
                                      "}")
                      .param("variables", "{" +
                              "\"pageNumber\":1," +
                              "\"pageSize\":25," +
                              "\"filter\":[" +
                              "  {" +
                              "     \"property\":\"deployments.lastExecution.status\"," +
                              "     \"pattern\":\"finished\"," +
                              "     \"sort\":null" +
                              "  }]," +
                              "  \"search\":\"\"" +
                              "}")
                      .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andExpect(jsonPath("$.data.content", hasSize(2))) // There are 2 jobs with status "finished"
              .andReturn().getResponse().getContentAsString();

      deleteJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME);
   }

   @Test
   void testSortingByLastExecutionTime() throws Exception {
      createJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);
      createJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME,
              ExecutionStatus.FAILED, OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC), null);
      createJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, null, 0);
      createJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME,
              null, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);

      String resultAsString = mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                      .with(user("user"))
                      .param("query",
                              "query($filter: [Predicate], $executionFilter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
                                      "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                                      "    content {" +
                                      "      jobName" +
                                      "      deployments {" +
                                      "        id" +
                                      "        enabled" +
                                      "        lastExecutionStatus" +
                                      "        lastExecutionTime" +
                                      "        lastExecutionDuration" +
                                      "        executions(pageNumber: 1, pageSize: 5, filter: $executionFilter) {" +
                                      "          id" +
                                      "          status" +
                                      "        }" +
                                      "      }" +
                                      "      config {" +
                                      "        team" +
                                      "        description" +
                                      "        schedule {" +
                                      "          scheduleCron" +
                                      "          nextRunEpochSeconds" +
                                      "        }" +
                                      "      }" +
                                      "    }" +
                                      "    totalPages" +
                                      "    totalItems" +
                                      "  }" +
                                      "}")
                      .param("variables", "{" +
                              "\"pageNumber\":1," +
                              "\"pageSize\":25," +
                              "\"filter\":[" +
                              "  {" +
                              "     \"property\":\"deployments.lastExecution.time\"," +
                              "     \"pattern\":null," +
                              "     \"sort\":\"ASC\"" +
                              "  }]," +
                              "  \"search\":\"\"" +
                              "}")
                      .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andReturn().getResponse().getContentAsString();

      // Check that jobs are sorted in descending order by the last execution duration
      var times = new OffsetDateTime[] {
              parseUtcDateTimeOrNull(JsonPath.read(resultAsString, "$.data.content[0].deployments[0].lastExecutionTime")),
              parseUtcDateTimeOrNull(JsonPath.read(resultAsString, "$.data.content[1].deployments[0].lastExecutionTime")),
              parseUtcDateTimeOrNull(JsonPath.read(resultAsString, "$.data.content[2].deployments[0].lastExecutionTime")),
              parseUtcDateTimeOrNull(JsonPath.read(resultAsString, "$.data.content[3].deployments[0].lastExecutionTime"))
      };
      assertThat(times).isEqualTo(
              new OffsetDateTime[] {
                      OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC),
                      OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC),
                      OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC),
                     null
              });

      deleteJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME);
   }

   @Test
   void testSortingByLastExecutionDuration() throws Exception {
      createJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);
      createJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME,
              ExecutionStatus.FAILED, OffsetDateTime.of(2000, 1, 3, 0, 0, 0, 0, ZoneOffset.UTC), null);
      createJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME,
              ExecutionStatus.FINISHED, null, 0);
      createJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME,
              null, OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC), 1000);

      String resultAsString = mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                      .with(user("user"))
                      .param("query",
                              "query($filter: [Predicate], $executionFilter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
                                      "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                                      "    content {" +
                                      "      jobName" +
                                      "      deployments {" +
                                      "        id" +
                                      "        enabled" +
                                      "        lastExecutionStatus" +
                                      "        lastExecutionTime" +
                                      "        lastExecutionDuration" +
                                      "        executions(pageNumber: 1, pageSize: 5, filter: $executionFilter) {" +
                                      "          id" +
                                      "          status" +
                                      "        }" +
                                      "      }" +
                                      "      config {" +
                                      "        team" +
                                      "        description" +
                                      "        schedule {" +
                                      "          scheduleCron" +
                                      "          nextRunEpochSeconds" +
                                      "        }" +
                                      "      }" +
                                      "    }" +
                                      "    totalPages" +
                                      "    totalItems" +
                                      "  }" +
                                      "}")
                      .param("variables", "{" +
                              "\"pageNumber\":1," +
                              "\"pageSize\":25," +
                              "\"filter\":[" +
                              "  {" +
                              "     \"property\":\"deployments.lastExecution.duration\"," +
                              "     \"pattern\":null," +
                              "     \"sort\":\"DESC\"" +
                              "  }]," +
                              "  \"search\":\"\"" +
                              "}")
                      .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andReturn().getResponse().getContentAsString();

      // Check that jobs are sorted in descending order by the last execution duration
      var durations = new Integer[] {
              JsonPath.read(resultAsString, "$.data.content[0].deployments[0].lastExecutionDuration"),
              JsonPath.read(resultAsString, "$.data.content[1].deployments[0].lastExecutionDuration"),
              JsonPath.read(resultAsString, "$.data.content[2].deployments[0].lastExecutionDuration"),
              JsonPath.read(resultAsString, "$.data.content[3].deployments[0].lastExecutionDuration")
      };
      assertThat(durations).isEqualTo(new Integer[] {null, 1000, 1000, 0});

      deleteJobWithDeployment(TEST_JOB_1, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_2, TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_3, NEW_TEST_TEAM_NAME);
      deleteJobWithDeployment(TEST_JOB_4, NEW_TEST_TEAM_NAME);
   }

   private OffsetDateTime parseUtcDateTimeOrNull(String value) {
      if (value == null) {
         return null;
      }
      return OffsetDateTime.parse(value).toInstant().atOffset(ZoneOffset.UTC);
   }

   private void createDummyJobs() throws Exception {
      // Setup by creating 3 jobs in 2 separate teams (6 jobs total)
      String dataJobTestBodyOne = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_1);
      createJob(dataJobTestBodyOne, TEST_TEAM_NAME);

      String dataJobTestBodyTwo = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_2);
      createJob(dataJobTestBodyTwo, TEST_TEAM_NAME);

      String dataJobTestBodyThree = getDataJobRequestBody(NEW_TEST_TEAM_NAME, TEST_JOB_3);
      createJob(dataJobTestBodyThree, NEW_TEST_TEAM_NAME);

      String dataJobTestBodyFour = getDataJobRequestBody(NEW_TEST_TEAM_NAME, TEST_JOB_4);
      createJob(dataJobTestBodyFour, NEW_TEST_TEAM_NAME);

      String dataJobTestBodyFive = getDataJobRequestBody(NEW_TEST_TEAM_NAME, TEST_JOB_5);
      createJob(dataJobTestBodyFive, NEW_TEST_TEAM_NAME);

      String dataJobTestBodySix = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_6);
      createJob(dataJobTestBodySix, TEST_TEAM_NAME);
   }

   private void deleteDummyJobs() throws Exception {
      // Clean up
      deleteJob(TEST_JOB_1, TEST_TEAM_NAME);
      deleteJob(TEST_JOB_2, TEST_TEAM_NAME);
      deleteJob(TEST_JOB_3, NEW_TEST_TEAM_NAME);
      deleteJob(TEST_JOB_4, NEW_TEST_TEAM_NAME);
      deleteJob(TEST_JOB_5, NEW_TEST_TEAM_NAME);
      deleteJob(TEST_JOB_6, TEST_TEAM_NAME);
   }

   private void createJob(String body, String teamName) throws Exception {
      mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs", teamName))
            .with(user("user"))
            .content(body)
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isCreated());
   }

   private final List<JobDeploymentStatus> deploymentStatuses = new ArrayList<>();

   private DataJob createJobWithDeployment(String jobName,
                                           String teamName,
                                           ExecutionStatus lastExecutionStatus,
                                           OffsetDateTime lastExecutionTime,
                                           Integer lastExecutionDuration) throws Exception {

      String body = getDataJobRequestBody(teamName, jobName);
      createJob(body, teamName);

      var deploymentStatus = new JobDeploymentStatus();
      deploymentStatus.setDataJobName(jobName);
      deploymentStatus.setEnabled(true);
      deploymentStatus.setLastDeployedBy("auserov");
      deploymentStatus.setLastDeployedDate("today");
      deploymentStatus.setMode("testing");
      deploymentStatus.setGitCommitSha("de3c104");
      deploymentStatus.setImageName("image");
      deploymentStatus.setCronJobName(String.format("%s-cron", jobName));
      deploymentStatuses.add(deploymentStatus);
      when(deploymentService.readDeployments()).thenReturn(deploymentStatuses);

      var dataJob = jobsRepository.findById(jobName). get();
      dataJob.setLastExecutionStatus(lastExecutionStatus);
      dataJob.setLastExecutionEndTime(lastExecutionTime);
      dataJob.setLastExecutionDuration(lastExecutionDuration);
      return jobsRepository.save(dataJob);
   }

   private void deleteJob(String jobName, String teamName) throws Exception {
      mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s", teamName, jobName))
            .with(user("user"))
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk());
   }

   private void deleteJobWithDeployment(String jobName, String teamName) throws Exception {
      deleteJob(jobName, teamName);
      var deploymentStatus = deploymentStatuses.stream()
              .filter(s -> s.getDataJobName().equals(jobName))
              .findFirst()
              .orElse(null);
      deploymentStatuses.remove(deploymentStatus);
      when(deploymentService.readDeployments()).thenReturn(deploymentStatuses);
   }
}
