/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import static org.awaitility.Awaitility.await;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;
import java.util.concurrent.TimeUnit;
import java.util.List;
import com.fasterxml.jackson.core.type.TypeReference;
import java.util.stream.Collectors;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.UUID;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Slf4j
@Import({DataJobDeploymentCrudIT.TaskExecutorConfig.class})
@TestPropertySource(
    properties = {
      "dataJob.readOnlyRootFileSystem=true",
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobEphemeralStorageIT extends BaseIT {

  private static final String TEST_JOB_NAME =
      "ephemeral-storage-test-" + UUID.randomUUID().toString().substring(0, 8);
  private static final Object DEPLOYMENT_ID = "testing-ephemeral-storage";
  private final ObjectMapper objectMapper =
      new ObjectMapper()
          .registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

  @AfterEach
  public void cleanUp() throws Exception {
    // delete job
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user")))
        .andExpect(status().isOk());

    // Execute delete deployment
    mockMvc
        .perform(
            delete(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, TEST_JOB_NAME, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());
  }

  @BeforeEach
  public void setup() throws Exception {
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

    // Execute create job
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());
  }

  @Test
  public void testEphemeralStorageJob() throws Exception {
    // Take the job zip as byte array
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("job_ephemeral_storage.zip"));

    // Execute job upload with user
    MvcResult jobUploadResult =
        mockMvc
            .perform(
                post(String.format(
                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                    .with(user("user"))
                    .content(jobZipBinary)
                    .contentType(MediaType.APPLICATION_OCTET_STREAM))
            .andExpect(status().isOk())
            .andReturn();

    DataJobVersion testDataJobVersion =
        new ObjectMapper()
            .readValue(jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
    Assertions.assertNotNull(testDataJobVersion);

    String testJobVersionSha = testDataJobVersion.getVersionSha();
    Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

    // Setup
    String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

    // Execute build and deploy job
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .content(dataJobDeploymentRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted())
        .andReturn();

    String opId = TEST_JOB_NAME + UUID.randomUUID().toString().toLowerCase();

    // manually start job execution
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_JOB_DEPLOYMENT_ID))
                .with(user("user"))
                .header(HEADER_X_OP_ID, opId)
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
                        TEST_TEAM_NAME, TEST_JOB_NAME, TEST_JOB_DEPLOYMENT_ID))
                    .with(user("user"))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    var gson = new Gson();
    ArrayList<LinkedTreeMap> parsed =
        gson.fromJson(exc.getResponse().getContentAsString(), ArrayList.class);
    String executionId = (String) parsed.get(0).get("id");

    // Check the data job execution status
    checkDataJobExecutionStatus(
        executionId,
        DataJobExecution.StatusEnum.SUCCEEDED,
        opId,
        TEST_JOB_NAME,
        TEST_TEAM_NAME,
        "user");
  }

  private void checkDataJobExecutionStatus(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    try {
      testDataJobExecutionRead(executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobExecutionList(executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobDeploymentExecutionList(
          executionId, executionStatus, opId, jobName, teamName, username);
      testDataJobExecutionLogs(executionId, jobName, teamName, username);
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
      String opId,
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

    assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecution[0], jobName);
  }

  private void testDataJobExecutionList(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    String dataJobExecutionListUrl =
        String.format("/data-jobs/for-team/%s/jobs/%s/executions", teamName, jobName);
    MvcResult dataJobExecutionResult =
        mockMvc
            .perform(
                get(dataJobExecutionListUrl)
                    .with(user(username))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    List<DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    Assertions.assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    Assertions.assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName);
  }

  private void testDataJobDeploymentExecutionList(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username)
      throws Exception {

    String dataJobDeploymentExecutionListUrl =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
            teamName, jobName, "release");
    MvcResult dataJobExecutionResult =
        mockMvc
            .perform(
                get(dataJobDeploymentExecutionListUrl)
                    .with(user(username))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    List<DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    Assertions.assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    Assertions.assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName);
  }

  private void testDataJobExecutionLogs(
      String executionId, String jobName, String teamName, String username) throws Exception {
    MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId, jobName, teamName, username);
    Assertions.assertFalse(dataJobExecutionLogsResult.getResponse().getContentAsString().isEmpty());
  }

  @NotNull
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

  private void assertDataJobExecutionValid(
      String executionId,
      DataJobExecution.StatusEnum executionStatus,
      String opId,
      DataJobExecution dataJobExecution,
      String jobName) {

    Assertions.assertNotNull(dataJobExecution);
    Assertions.assertEquals(executionId, dataJobExecution.getId());
    Assertions.assertEquals(jobName, dataJobExecution.getJobName());
    Assertions.assertEquals(executionStatus, dataJobExecution.getStatus());
    Assertions.assertEquals(DataJobExecution.TypeEnum.MANUAL, dataJobExecution.getType());
    Assertions.assertEquals(opId, dataJobExecution.getOpId());
  }
}
