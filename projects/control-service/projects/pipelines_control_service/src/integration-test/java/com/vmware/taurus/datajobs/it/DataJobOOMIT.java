/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
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

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobOOMIT extends BaseIT {

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension = DataJobDeploymentExtension.builder()
          .jobSource("oom_job.zip")
          .build();

  private final ObjectMapper objectMapper =
          new ObjectMapper()
                  .registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

  @Test
  public void testJobCancellation_createDeployExecuteAndCancelJob(String jobName, String username, String deploymentId, String teamName) throws Exception {
    // manually start job execution
    var dataJobExecutionResponse = mockMvc
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
                        + "  \"started_by\": \"java/integration-test\"\n"
                        + "}"))
        .andExpect(status().is(202))
        .andReturn();

    // Check the data job execution status
    String location = dataJobExecutionResponse.getResponse().getHeader("location");
    String executionId = location.substring(location.lastIndexOf("/") + 1);
    checkDataJobExecutionStatus(
            executionId, DataJobExecution.StatusEnum.USER_ERROR, jobName, teamName, username);

    checkDataJobExecutionStatus(
            executionId, DataJobExecution.StatusEnum.PLATFORM_ERROR, jobName, teamName, username);
  }

  private void checkDataJobExecutionStatus(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String jobName,
          String teamName,
          String username)
          throws Exception {

    try {
      testDataJobExecutionRead(executionId, executionStatus, jobName, teamName, username);
    } catch (Error e) {
      try {
        // print logs in case execution has failed
        MvcResult dataJobExecutionLogsResult =
                getExecuteLogs(executionId, jobName, teamName, username);
        log.info(
                "Job Execution {} logs:\n{}",
                executionId,
                dataJobExecutionLogsResult.getResponse().getContentAsString());
      } catch (Error ignore) {
      }
      throw e;
    }
  }

  private void testDataJobExecutionRead(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String jobName,
          String teamName,
          String username) {

    DataJobExecution[] dataJobExecution = new DataJobExecution[1];

    await()
            .atMost(5, TimeUnit.MINUTES)
            .with()
            .pollInterval(15, TimeUnit.SECONDS)
            .until(
                    () -> {
                      String dataJobExecutionReadUrl =
                              String.format(
                                      "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                                      teamName, jobName, executionId);
                      MvcResult dataJobExecutionResult =
                              mockMvc
                                      .perform(
                                              get(dataJobExecutionReadUrl)
                                                      .with(user(username))
                                                      .contentType(MediaType.APPLICATION_JSON))
                                      .andExpect(status().isOk())
                                      .andReturn();

                      dataJobExecution[0] =
                              objectMapper.readValue(
                                      dataJobExecutionResult.getResponse().getContentAsString(),
                                      DataJobExecution.class);
                      if (dataJobExecution[0] == null) {
                        log.info("No response from server");
                      } else {
                        log.info("Response from server  " + dataJobExecution[0].getStatus());
                      }
                      return dataJobExecution[0] != null
                              && executionStatus.equals(dataJobExecution[0].getStatus());
                    });

    assertEquals(executionStatus, dataJobExecution[0].getStatus());
  }

  private MvcResult getExecuteLogs(
          String executionId, String jobName, String teamName, String username) throws Exception {
    String dataJobExecutionListUrl =
            String.format(
                    "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs", teamName, jobName, executionId);
    MvcResult dataJobExecutionLogsResult =
            mockMvc
                    .perform(get(dataJobExecutionListUrl).with(user(username)))
                    .andExpect(status().isOk())
                    .andReturn();
    return dataJobExecutionLogsResult;
  }
}
