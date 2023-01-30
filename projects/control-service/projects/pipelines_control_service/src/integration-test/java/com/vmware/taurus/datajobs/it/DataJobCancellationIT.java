/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.DataJobDeploymentExtension;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import java.util.ArrayList;
import java.util.UUID;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobCancellationIT extends BaseIT {

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension = DataJobDeploymentExtension.builder()
          .jobSource("simple_job_cancel.zip")
          .jobGlobal(false)
          .build();

  @Test
  public void testJobCancellation_createDeployExecuteAndCancelJob(String jobName, String username, String deploymentId, String teamName) throws Exception {
    // manually start job execution
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                    teamName, jobName, deploymentId))
                .with(user(username))
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    "{\n"
                        + "  \"args\": {\n"
                        + "    \"key\": \"value\"\n"
                        + "  },\n"
                        + "  \"started_by\": \"schedule/runtime\"\n"
                        + "}"))
        .andExpect(status().is(202))
        .andReturn();

    // wait for pod to initialize
    Thread.sleep(10000);

    // retrieve running job execution id.
    var exc =
        mockMvc
            .perform(
                get(String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                        teamName, jobName, deploymentId))
                    .with(user("user"))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    var gson = new Gson();
    ArrayList<LinkedTreeMap> parsed =
        gson.fromJson(exc.getResponse().getContentAsString(), ArrayList.class);
    String executionId = (String) parsed.get(0).get("id");

    // cancel running execution
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                            teamName, jobName, executionId))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk());
  }

  @Test
  public void testJobCancellation_nonExistingJob(String jobName, String username, String deploymentId, String teamName) throws Exception {

    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                            teamName, jobName, "executionId"))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }
}
