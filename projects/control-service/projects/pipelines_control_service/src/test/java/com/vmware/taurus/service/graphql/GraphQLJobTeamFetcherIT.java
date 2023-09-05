/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import com.vmware.taurus.ControlplaneApplication;
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
public class GraphQLJobTeamFetcherIT {

  @Autowired JobsRepository jobsRepository;

  @Autowired private MockMvc mockMvc;

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  private static String getJobsUri(String teamName) {
    return "/data-jobs/for-team/" + teamName + "/jobs";
  }

  private static String getQuery(String jobTeam) {
    return "{\n"
        + "  jobs(\n"
        + "    pageNumber: 1\n"
        + "    pageSize: 100\n"
        + "    filter: [\n"
        + "      { property: \"config.team\", pattern: \""
        + jobTeam
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
  public void testRetrieveJobNameWithParentheses() throws Exception {
    testJobApiRetrievalWithTeamName_retrieveExpected("VIDA (Eco-system)");
  }

  @Test
  public void testRetrieveJobNameWithoutParentheses() throws Exception {
    testJobApiRetrievalWithTeamName_retrieveExpected("VIDA");
  }

  /**
   * Re-usable test that creates a data job with a given team name and attempts to retrieve it via
   * the graphQL API, expecting to find it.
   *
   * @param jobTeam - the team name.
   * @param searchString - the graphQl search string.
   * @throws Exception
   */
  private void testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(
      String jobTeam, String searchString) throws Exception {
    createJobWithTeam(jobTeam);
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(getJobsUri(jobTeam))
                .queryParam("query", getQuery(searchString))
                .with(user("test")))
        .andExpect(status().is(200))
        .andExpect(jsonPath("$.data.content[0].jobName").value("test-job"))
        .andExpect(jsonPath("$.data.content[0].config.team").value(jobTeam));
  }

  private void testJobApiRetrievalWithTeamName_retrieveExpected(String jobTeam) throws Exception {
    testJobApiRetrievalWithTeamNameAndSearchString_retrieveExpected(jobTeam, jobTeam);
  }

  private void createJobWithTeam(String jobTeam) {
    DataJob dataJob = new DataJob();
    JobConfig jobConfig = new JobConfig();
    jobConfig.setTeam(jobTeam);
    dataJob.setName("test-job");
    dataJob.setJobConfig(jobConfig);
    jobsRepository.save(dataJob);
  }
}
