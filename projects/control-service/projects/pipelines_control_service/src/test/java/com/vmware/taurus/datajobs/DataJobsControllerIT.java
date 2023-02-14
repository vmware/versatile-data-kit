/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJob;
import org.hamcrest.BaseMatcher;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.net.URLDecoder;
import java.nio.charset.Charset;
import java.util.UUID;
import java.util.function.Predicate;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ActiveProfiles({"MockKubernetes", "MockKerberos", "unittest", "MockGit", "MockTelemetry"})
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.MOCK,
    classes = ControlplaneApplication.class)
@AutoConfigureMockMvc
public class DataJobsControllerIT {

  // team name can have spaces in it so we are purposefully using one with space
  private static final String TEST_TEAM_NAME = "test team";
  private static final String TEST_JOB_NAME = "test-job";
  private static final String TEST_TEAM_WRONG_NAME = "test-example-team";

  @Autowired private MockMvc mockMvc;

  private final ObjectMapper mapper = new ObjectMapper();

  private Matcher<String> lambdaMatcher(Predicate<String> predicate) {
    return new BaseMatcher<>() {
      @Override
      public boolean matches(Object actual) {
        return predicate.test((String) actual);
      }

      @Override
      public void describeTo(Description description) {
        description.appendText("failed to match predicate");
      }
    };
  }

  @Test
  @WithMockUser
  public void testDataJobCrud() throws Exception {
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, TEST_JOB_NAME);

    String body = mapper.writeValueAsString(job);
    String expectedLocationPath =
        String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .content(body)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated())
        .andExpect(
            header()
                .string(
                    HttpHeaders.LOCATION,
                    lambdaMatcher(
                        s ->
                            URLDecoder.decode(s, Charset.defaultCharset())
                                .endsWith(expectedLocationPath))));
    // deprecated jobsList in favour of jobsQuery
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .param(
                    "query",
                    "query($filter: [Predicate], $pageNumber: Int) {"
                        + "  jobs(pageNumber: $pageNumber, filter: $filter) {"
                        + "    content {"
                        + "      jobName"
                        + "    }"
                        + "  }"
                        + "}")
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
                        + "\"pageNumber\": 1"
                        + "}")
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(content().string(lambdaMatcher(s -> (s.contains(TEST_JOB_NAME)))));
    mockMvc
        .perform(
            get(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME)))
        .andExpect(status().isOk())
        .andExpect(content().string(lambdaMatcher(s -> s.contains(TEST_JOB_NAME))))
        .andExpect(
            content()
                .string(
                    lambdaMatcher(
                        s -> s.contains(job.getConfig().getSchedule().getScheduleCron()))));
    mockMvc
        .perform(
            delete(String.format("/data-jobs/for-team/%s/jobs/%s", TEST_TEAM_NAME, TEST_JOB_NAME))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
  }

  @Test
  @WithMockUser
  public void testDataJobDeployTelemetry() throws Exception {
    MockTelemetry.payloads.clear();
    var job = TestUtils.getDataJob(TEST_TEAM_NAME, "deployment-job");

    String body = mapper.writeValueAsString(job);
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .content(body)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());

    var jobDeployment = TestUtils.getDataJobDeployment("prod", "1");

    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, "deployment-job"))
                .content(mapper.writeValueAsString(jobDeployment))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());
    // checking if httptrace table is updated correctly with http trace info
    var httpTraceTelemetry =
        MockTelemetry.payloads.stream()
            .filter(
                p ->
                    p.contains("taurus_httptrace")
                        && p.contains(
                            "/data-jobs/for-team/{team_name}/jobs/{job_name}/deployments"))
            .findFirst();
    // checking if taurus_api_call is updated with DeploymentProgress as specified by Measurable
    // annotation
    var deployProgressTelemetry =
        MockTelemetry.payloads.stream()
            .filter(
                p ->
                    p.contains("taurus_api_call")
                        && p.contains("DeploymentProgress")
                        && p.contains("completed"))
            .findFirst();

    assertTrue(
        httpTraceTelemetry.isPresent(),
        "Did not find expected http trace telemetry. See all payloads: " + MockTelemetry.payloads);
    assertTrue(
        deployProgressTelemetry.isPresent(),
        "Did not find expected deploy progress telemetry. See all payloads: "
            + MockTelemetry.payloads);
  }

  @Test
  @WithMockUser
  public void testDownloadKeytab() throws Exception {
    DataJob job =
        TestUtils.getDataJob(TEST_TEAM_NAME, "job-" + UUID.randomUUID().toString().toLowerCase());
    String downloadKeytabPath =
        String.format("/data-jobs/for-team/%s/jobs/%s/keytab", TEST_TEAM_NAME, job.getJobName());
    mockMvc.perform(get(downloadKeytabPath)).andExpect(status().isNotFound());

    String body = mapper.writeValueAsString(job);
    mockMvc.perform(
        post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
            .content(body)
            .contentType(MediaType.APPLICATION_JSON));

    mockMvc
        .perform(
            get(
                String.format(
                    "/data-jobs/for-team/%s/jobs/%s/keytab",
                    TEST_TEAM_WRONG_NAME, job.getJobName())))
        .andExpect(status().isNotFound());

    byte[] keytab = downloadPath(downloadKeytabPath);
    byte[] keytabAgain = downloadPath(downloadKeytabPath);

    assertArrayEquals(keytab, keytabAgain);
  }

  private byte[] downloadPath(String path) throws Exception {
    return mockMvc
        .perform(get(path))
        .andExpect(status().isOk())
        .andReturn()
        .getResponse()
        .getContentAsByteArray();
  }
}
