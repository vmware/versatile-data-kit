/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.graphql;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import com.vmware.taurus.service.model.JobConfig;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.JobExecutionRepository;
import com.vmware.taurus.service.repository.JobsRepository;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@AutoConfigureMockMvc(addFilters = false)
public class FindAllDataJobsTest {

  @Autowired JobsRepository jobsRepository;

  @Autowired ActualJobDeploymentRepository actualJobDeploymentRepository;

  @Autowired JobExecutionRepository jobExecutionRepository;

  @Autowired private MockMvc mockMvc;

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
    actualJobDeploymentRepository.deleteAll();
    jobExecutionRepository.deleteAll();
  }

  private static String getJobsUri(String teamName) {
    return "/data-jobs/for-team/" + teamName + "/jobs";
  }

  private static String getQuery(int pageNumber) {
    return "{ jobs(pageNumber: "
        + pageNumber
        + ", pageSize: 100, filter: [{ property: \"config.team\", sort: ASC },"
        + " { property: \"jobName\", sort: ASC }]) { content { jobName config { team description "
        + "schedule { scheduleCron }  }  deployments { enabled status }  }  }  }";
  }

  @Test
  public void testJsonReturnOrder_expectNoChanges() throws Exception {
    populateThreePagesOfDummyJobs();

    var firstPage = getResponseAsString("unspecified", 1);
    var secondPage = getResponseAsString("unspecified", 2);
    var thirdPage = getResponseAsString("unspecified", 3);

    for (int i = 0; i < 100; i++) {
      // we test if the returned json has a changed sort order
      var firstPageInALoop = getResponseAsString("unspecified", 1);
      var secondPageInALoop = getResponseAsString("unspecified", 2);
      var thirdPageInALoop = getResponseAsString("unspecified", 3);

      Assertions.assertEquals(firstPage, firstPageInALoop);
      Assertions.assertEquals(secondPage, secondPageInALoop);
      Assertions.assertEquals(thirdPage, thirdPageInALoop);
    }
  }

  @Test
  public void testNumberOfReturnedJobs() throws Exception {
    populateThreePagesOfDummyJobs();
    getAllJobs("unspecified", 1)
        .andExpect(jsonPath("$.data.content[99].jobName").exists())
        .andExpect(jsonPath("$.data.content[101].jobName").doesNotExist());
    getAllJobs("unspecified", 2)
        .andExpect(jsonPath("$.data.content[99].jobName").exists())
        .andExpect(jsonPath("$.data.content[101].jobName").doesNotExist());
    getAllJobs("unspecified", 3)
        .andExpect(jsonPath("$.data.content[1].jobName").exists())
        .andExpect(jsonPath("$.data.content[2].jobName").doesNotExist());
  }

  private String getResponseAsString(String team, int pageNumber) throws Exception {
    return getAllJobs(team, pageNumber)
        .andExpect(status().is(200))
        .andReturn()
        .getResponse()
        .getContentAsString();
  }

  private ResultActions getAllJobs(String jobTeam, int pageNumber) throws Exception {
    var response =
        mockMvc.perform(
            MockMvcRequestBuilders.get(getJobsUri(jobTeam))
                .queryParam("query", getQuery(pageNumber))
                .with(user("test")));

    return response;
  }

  private void populateThreePagesOfDummyJobs() {
    // create 202 jobs to have 3 pages of results
    for (int i = 0; i < 101; i++) {
      saveTestJob(i + "bar", "AAAA");
      saveTestJob(i + "foo", "BBBB");
    }
  }

  private void saveTestJob(String jobName, String jobTeam) {
    var job = new DataJob();
    var config = new JobConfig();
    config.setTeam(jobTeam);
    job.setJobConfig(config);
    job.setName(jobName);
    job.setEnabled(true);
    jobsRepository.save(job);
    var execution = new DataJobExecution();
    execution.setStatus(ExecutionStatus.SUCCEEDED);
    execution.setDataJob(job);
    execution.setId(job.getName());
    execution.setType(ExecutionType.MANUAL);
    execution.setOpId(UUID.randomUUID().toString());
    jobExecutionRepository.save(execution);
    var deployment = new ActualDataJobDeployment();
    deployment.setDataJobName(job.getName());
    deployment.setEnabled(true);
    deployment.setLastDeployedDate(OffsetDateTime.now());
    actualJobDeploymentRepository.save(deployment);
  }
}
