/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.graphql.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobContacts;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.JobConfig;
import org.hamcrest.Matchers;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

import java.util.List;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class GraphQLDataJobsSortContactsIT extends BaseIT {

  @Autowired private JobsRepository jobsRepository;

  @AfterEach
  public void cleanup() {
    jobsRepository.deleteAll();
  }

  private String getQuery(String sortOrder) {
    return "{\n"
        + "  jobs(\n"
        + "    pageNumber: 1\n"
        + "    pageSize: 5\n"
        + "    filter: [{ property: \"config.contacts.present\", sort:"
        + sortOrder
        + "}]\n"
        + "  ) {\n"
        + "    content {\n"
        + "      jobName\n"
        + "      config {\n"
        + "        contacts{"
        + "           notifiedOnJobFailureUserError "
        + "           notifiedOnJobSuccess"
        + "        }\n"
        + "      }\n"
        + "    }\n"
        + "  }\n"
        + "}";
  }

  @Test
  public void testEmptyCall_shouldBeEmpty() throws Exception {
    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("DESC"))
                .with(user(TEST_USERNAME)))
        .andExpect(jsonPath("$.data.content").isEmpty());
  }

  @Test
  public void testSingleJob_shouldReturnOne() throws Exception {
    var contacts = new DataJobContacts();
    contacts.setNotifiedOnJobFailureUserError(List.of("test-notified"));
    var job = createDummyJob(contacts, "test-job");
    jobsRepository.save(job);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("DESC"))
                .with(user(TEST_USERNAME)))
        .andExpect(
            jsonPath("$.data.content[0].config.contacts.notifiedOnJobFailureUserError")
                .value("test-notified"));
  }

  @Test
  public void testSortingTwoJobs_shouldReturnDescOrder() throws Exception {
    var contacts = new DataJobContacts();
    contacts.setNotifiedOnJobFailureUserError(List.of("test-notified"));
    var job = createDummyJob(contacts, "test-job");

    var contacts2 = new DataJobContacts();
    var job2 = createDummyJob(contacts2, "test-job2");

    jobsRepository.save(job);
    jobsRepository.save(job2);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("DESC"))
                .with(user(TEST_USERNAME)))
        .andExpect(
            jsonPath("$.data.content[0].config.contacts.notifiedOnJobFailureUserError")
                .value("test-notified"))
        .andExpect(
            jsonPath("$.data.content[1].config.contacts.notifiedOnJobFailureUserError").isEmpty());
  }

  @Test
  public void testSortingTwoJobs_shouldReturnAscOrder() throws Exception {
    var contacts = new DataJobContacts();
    contacts.setNotifiedOnJobSuccess(List.of("test-notified"));
    var job = createDummyJob(contacts, "test-job");

    var contacts2 = new DataJobContacts();
    var job2 = createDummyJob(contacts2, "test-job2");

    jobsRepository.save(job);
    jobsRepository.save(job2);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("ASC"))
                .with(user(TEST_USERNAME)))
        .andExpect(
            jsonPath("$.data.content[1].config.contacts.notifiedOnJobSuccess")
                .value("test-notified"))
        .andExpect(jsonPath("$.data.content[0].config.contacts.notifiedOnJobSuccess").isEmpty());
  }

  @Test
  public void testSortingTwoJobsNoContacts_shouldReturnTwo() throws Exception {
    var contacts = new DataJobContacts();
    var job = createDummyJob(contacts, "test-job");

    var contacts2 = new DataJobContacts();
    var job2 = createDummyJob(contacts2, "test-job2");

    jobsRepository.save(job);
    jobsRepository.save(job2);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("ASC"))
                .with(user(TEST_USERNAME)))
        .andExpect(jsonPath("$.data.content.length()").value(2))
        .andExpect(
            jsonPath("$.data.content[*].jobName", Matchers.contains("test-job", "test-job2")));
  }

  @Test
  public void testSortingTwoJobsWithContacts_shouldReturnTwo() throws Exception {
    var contacts = new DataJobContacts();
    contacts.setNotifiedOnJobDeploy(List.of("test"));
    var job = createDummyJob(contacts, "test-job");

    var contacts2 = new DataJobContacts();
    contacts2.setNotifiedOnJobFailurePlatformError(List.of("test"));
    var job2 = createDummyJob(contacts2, "test-job2");

    jobsRepository.save(job);
    jobsRepository.save(job2);

    mockMvc
        .perform(
            MockMvcRequestBuilders.get(JOBS_URI)
                .queryParam("query", getQuery("ASC"))
                .with(user(TEST_USERNAME)))
        .andExpect(jsonPath("$.data.content.length()").value(2))
        .andExpect(
            jsonPath("$.data.content[*].jobName", Matchers.contains("test-job", "test-job2")));
  }

  private DataJob createDummyJob(DataJobContacts contacts, String id) {
    DataJob job = new DataJob();
    job.setName(id);
    JobConfig config = new JobConfig();
    config.setSchedule("test-schedule");
    config.setNotifiedOnJobFailureUserError(contacts.getNotifiedOnJobFailureUserError());
    config.setNotifiedOnJobDeploy(contacts.getNotifiedOnJobDeploy());
    config.setNotifiedOnJobSuccess(contacts.getNotifiedOnJobSuccess());
    config.setNotifiedOnJobFailurePlatformError(contacts.getNotifiedOnJobFailurePlatformError());
    job.setJobConfig(config);
    return job;
  }
}
