/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.ResultActions;

import static org.hamcrest.Matchers.greaterThan;
import static org.hamcrest.Matchers.is;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

// TODO: move to junit 5
@RunWith(SpringRunner.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobGraphQLIT extends BaseIT {

   private static final Logger LOG = LoggerFactory.getLogger(DataJobGraphQLIT.class);
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
   public void testGraphQLPagination() throws Exception

   {
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
   public void testGraphQLFields() throws Exception {
      String dataJobTestBodyOne = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_1);
      createJob(dataJobTestBodyOne, TEST_TEAM_NAME);

      // Test requesting of fields that are computed
      String contentAsString = mockMvc.perform(get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .with(user("user"))
            .param("query", "query($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) {" +
                  "  jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search) {" +
                  "    content {" +
                  "      jobName" +
                  "      deployments {" +
                  "        id" +
                  "        enabled" +
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
                  "\"pageSize\": 10" +
                  "}")
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.content[0].config.team", is(TEST_TEAM_NAME)))
            .andExpect(jsonPath("$.data.content[0].config.schedule.scheduleCron", is(TEST_JOB_SCHEDULE)))
            .andExpect(jsonPath("$.data.content[0].config.schedule.nextRunEpochSeconds", greaterThan(1)))
            .andReturn().getResponse().getContentAsString();

      deleteJob(TEST_JOB_1, TEST_TEAM_NAME);
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

   private void deleteJob(String jobName, String teamName) throws Exception {
      ResultActions resultActions = mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s", teamName, jobName))
            .with(user("user"))
            .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk());
   }
}
