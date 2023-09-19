/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.repository.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@AutoConfigureMockMvc(addFilters = false)
public class GraphQLJobTeamAndNameFilterMatcherIT extends BaseIT {

  @Autowired JobsRepository jobsRepository;

  @Autowired private MockMvc mockMvc;

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  private static String getJobsUri(String teamName) {
    return "/data-jobs/for-team/" + teamName + "/jobs";
  }

  private static String getQuery(String searchPattern, String searchProperty) {
    return "{\n"
        + "  jobs(\n"
        + "    pageNumber: 1\n"
        + "    pageSize: 100\n"
        + "    filter: [\n"
        + "      { property: "
        + searchProperty
        + ", pattern: \""
        + searchPattern
        + "\", sort: ASC }\n"
        + "      { property: \"jobName\", sort: ASC }\n"
        + "    ]\n"
        + "  ) {\n"
        + "    content {\n"
        + "      jobName\n"
        + "      config {\n"
        + "        team\n"
        + "        description\n"
        + "        schedule {\n"
        + "          scheduleCron\n"
        + "        }\n"
        + "      }\n"
        + "      deployments {\n"
        + "        enabled\n"
        + "        status\n"
        + "      }\n"
        + "    }\n"
        + "  }\n"
        + "}";
  }

  @Test
  public void testFilterByJobTeamExactMatch_shouldRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
        "test-team", "test-team", "\"config.team\"");
  }

  @Test
  public void testFilterByJobNameExactMatch_shouldRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
        "test-team", "test-job", "\"jobName\"");
  }

  @Test
  public void testFilterByJobTeamExactMatch_shouldNotRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveNotExpected(
        "test-team", "test-team1", "\"config.team\"");
  }

  @Test
  public void testFilterByJobNameExactMatch_shouldNotRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveNotExpected(
        "test-team", "test-job1", "\"jobName\"");
  }

  @Test
  public void testFilterByJobNameExactMatch_multipleJobs_shouldRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    createJobWithTeam("another-team", "another-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
        "test-team", "test-job", "\"jobName\"");
  }

  @Test
  public void testFilterByJobNameExactMatch_multipleJobs_shouldNotRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    createJobWithTeam("another-team", "another-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveNotExpected(
        "test-team", "test-job1", "\"jobName\"");
  }

  @Test
  public void testFilterByJobNameWildcardMatch_multipleJobs_shouldRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    createJobWithTeam("another-team", "another-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
        "test-team", "test-*", "\"jobName\"");
  }

  @Test
  public void testFilterByJobNameWildcardMatch_multipleJobs_shouldNotRetrieve() throws Exception {
    createJobWithTeam("test-team", "test-job");
    createJobWithTeam("another-team", "another-job");
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveNotExpected(
        "test-team", "unrelated-*", "\"jobName\"");
  }

  private void testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
      String jobTeam, String searchString, String searchProperty) throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(getJobsUri(jobTeam))
                .queryParam("query", getQuery(searchString, searchProperty))
                .with(user("test")))
        .andExpect(status().is(200))
        .andExpect(jsonPath("$.data.content[0].jobName").value("test-job"))
        .andExpect(jsonPath("$.data.content[0].config.team").value(jobTeam));
  }

  private void testJobApiRetrievalWithTeamNameAndSearchString_retrieveNotExpected(
      String jobTeam, String searchString, String searchProperty) throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(getJobsUri(jobTeam))
                .queryParam("query", getQuery(searchString, searchProperty))
                .with(user("test")))
        .andExpect(status().is(200))
        .andExpect(jsonPath("$.data.content").isEmpty());
  }

  private void createJobWithTeam(String jobTeam, String jobName) {
    DataJob dataJob = new DataJob();
    JobConfig jobConfig = new JobConfig();
    jobConfig.setTeam(jobTeam);
    dataJob.setName(jobName);
    dataJob.setJobConfig(jobConfig);
    jobsRepository.save(dataJob);
  }
}
