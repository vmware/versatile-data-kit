/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.NEW_TEST_TEAM_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_1;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_2;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_3;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_4;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_5;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_6;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobGraphQLIT extends BaseIT {

  private static final String DEFAULT_QUERY_WITH_VARS =
      "query($filter: [Predicate], $search: String, $pageNumber: Int, $pageSize: Int) { "
          + " jobs(pageNumber: $pageNumber, pageSize: $pageSize, filter: $filter, search: $search)"
          + " {    content {      jobName      config {        team        description       "
          + " schedule {          scheduleCron        }      }    }    totalPages    totalItems  }"
          + "}";

  @Test
  public void testGraphQLPagination() throws Exception {
    createDummyJobs();

    // Test listing of team jobs by filtering with team property
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param(
                    "variables",
                    "{"
                        + "\"filter\": ["
                        + "    {"
                        + "      \"property\": \"config.team\","
                        + "      \"pattern\": \""
                        + TEST_TEAM_NAME
                        + "\""
                        + "    }"
                        + "  ],"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (s.contains(TEST_JOB_1))
                                && (s.contains(TEST_JOB_2))
                                && (s.contains(TEST_JOB_6))
                                && (!s.contains(TEST_JOB_3))
                                && (!s.contains(TEST_JOB_4))
                                && (!s.contains(TEST_JOB_5)))));

    // Test listing of team jobs by searching for team name
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param(
                    "variables",
                    "{"
                        + "\"search\": \""
                        + NEW_TEST_TEAM_NAME
                        + "\","
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 10"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (!s.contains(TEST_JOB_1))
                                && (!s.contains(TEST_JOB_2))
                                && (!s.contains(TEST_JOB_6))
                                && (s.contains(TEST_JOB_3))
                                && (s.contains(TEST_JOB_4))
                                && (s.contains(TEST_JOB_5)))));

    // Test showing only first page
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param("variables", "{" + "\"pageNumber\": 1," + "\"pageSize\": 2" + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (s.contains(TEST_JOB_1))
                                && (s.contains(TEST_JOB_2))
                                && (!s.contains(TEST_JOB_3))
                                && (!s.contains(TEST_JOB_4))
                                && (!s.contains(TEST_JOB_5))
                                && (!s.contains(TEST_JOB_6)))));

    // Test showing only middle page
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param("variables", "{" + "\"pageNumber\": 2," + "\"pageSize\": 2" + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (!s.contains(TEST_JOB_1))
                                && (!s.contains(TEST_JOB_2))
                                && (s.contains(TEST_JOB_3))
                                && (s.contains(TEST_JOB_4))
                                && (!s.contains(TEST_JOB_5))
                                && (!s.contains(TEST_JOB_6)))));

    // Test showing only last page
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param("variables", "{" + "\"pageNumber\": 3," + "\"pageSize\": 2" + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (!s.contains(TEST_JOB_1))
                                && (!s.contains(TEST_JOB_2))
                                && (!s.contains(TEST_JOB_3))
                                && (!s.contains(TEST_JOB_4))
                                && (s.contains(TEST_JOB_5))
                                && (s.contains(TEST_JOB_6)))));

    // Test showing only first page sorted DESC by jobName
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param(
                    "variables",
                    "{"
                        + "\"filter\": ["
                        + "    {"
                        + "      \"property\": \"jobName\","
                        + "      \"sort\": \"DESC\""
                        + "    }"
                        + "  ],"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 2"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (!s.contains(TEST_JOB_1))
                                && (!s.contains(TEST_JOB_2))
                                && (!s.contains(TEST_JOB_3))
                                && (!s.contains(TEST_JOB_4))
                                && (s.contains(TEST_JOB_5))
                                && (s.contains(TEST_JOB_6)))));

    // Test showing custom filtered, sorted and paged data jobs by multiple parameters
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .param("query", DEFAULT_QUERY_WITH_VARS)
                .param(
                    "variables",
                    "{"
                        + "\"filter\": ["
                        + "    {"
                        + "      \"property\": \"config.team\","
                        + "      \"pattern\": \""
                        + TEST_TEAM_NAME
                        + "\""
                        + "    },"
                        + "    {"
                        + "      \"property\": \"jobName\","
                        + "      \"sort\": \"DESC\""
                        + "    }"
                        + "  ],"
                        + "\"pageNumber\": 1,"
                        + "\"pageSize\": 2"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s ->
                            (!s.contains(TEST_JOB_1))
                                && (s.contains(TEST_JOB_2))
                                && (!s.contains(TEST_JOB_3))
                                && (!s.contains(TEST_JOB_4))
                                && (!s.contains(TEST_JOB_5))
                                && (s.contains(TEST_JOB_6)))));

    deleteDummyJobs();
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
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", teamName))
                .with(user("user"))
                .content(body)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());
  }

  private void deleteJob(String jobName, String teamName) throws Exception {
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", teamName, jobName))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
  }
}
