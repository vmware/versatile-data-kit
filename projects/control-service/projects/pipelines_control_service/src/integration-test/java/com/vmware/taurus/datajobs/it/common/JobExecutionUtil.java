/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import static com.vmware.taurus.datajobs.it.common.BaseIT.HEADER_X_OP_ID;
import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class JobExecutionUtil {

  public static final String JOB_NAME_PREFIX = "integration-test-";

  private static final ObjectMapper objectMapper =
      new ObjectMapper()
          .registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

  private static final Logger log = LoggerFactory.getLogger(JobExecutionUtil.class);

  /**
   * at the database level we only store date-times accurate to the microsecond. Like wise in older
   * versions of java .now() returned timestamps accurate to micro-seconds. In newer versions of
   * java .now() gives nano-second precision and it causes tests written before we adopted that java
   * version to fail.
   */
  public static OffsetDateTime getTimeAccurateToMicroSecond() {
    return OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS);
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      OffsetDateTime startTime,
      OffsetDateTime endTime,
      ExecutionStatus executionStatus) {

    var jobExecution =
        DataJobExecution.builder()
            .id(executionId)
            .dataJob(dataJob)
            .startTime(startTime)
            .endTime(endTime)
            .type(ExecutionType.MANUAL)
            .status(executionStatus)
            .resourcesCpuRequest(1F)
            .resourcesCpuLimit(2F)
            .resourcesMemoryRequest(500)
            .resourcesMemoryLimit(1000)
            .message("message")
            .lastDeployedBy("test_user")
            .lastDeployedDate(getTimeAccurateToMicroSecond())
            .jobVersion("test_version")
            .jobSchedule("*/5 * * * *")
            .opId("test_op_id")
            .vdkVersion("test_vdk_version")
            .build();

    return jobExecutionRepository.save(jobExecution);
  }

  public static void checkDataJobExecutionStatus(
      String executionId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username,
      MockMvc mockMvc)
      throws Exception {

    try {
      testDataJobExecutionRead(
          executionId, executionStatus, opId, jobName, teamName, username, mockMvc);
      testDataJobExecutionList(
          executionId, executionStatus, opId, jobName, teamName, username, mockMvc);
      testDataJobDeploymentExecutionList(
          executionId, executionStatus, opId, jobName, teamName, username, mockMvc);
      testDataJobExecutionLogs(executionId, jobName, teamName, username, mockMvc);
    } catch (Error e) {
      try {
        // print logs in case execution has failed
        MvcResult dataJobExecutionLogsResult =
            getExecuteLogs(executionId, jobName, teamName, username, mockMvc);
        log.info(
            "Job Execution {} logs:\n{}",
            executionId,
            dataJobExecutionLogsResult.getResponse().getContentAsString());
      } catch (Error ignore) {
      }
      throw e;
    }
  }

  public static ImmutablePair<String, String> executeDataJob(
      String jobName, String teamName, String username, String deploymentId, MockMvc mockMvc)
      throws Exception {
    String opId = jobName + UUID.randomUUID().toString().toLowerCase();

    String triggerDataJobExecutionUrl =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
            teamName, jobName, deploymentId);
    MvcResult dataJobExecutionResponse =
        mockMvc
            .perform(
                post(triggerDataJobExecutionUrl)
                    .with(user(username))
                    .header(HEADER_X_OP_ID, opId)
                    .content(
                        objectMapper.writeValueAsString(
                            new DataJobExecutionRequest().startedBy(username)))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().is(202))
            .andReturn();

    // Check the data job execution status
    String location = dataJobExecutionResponse.getResponse().getHeader("location");
    String executionId = location.substring(location.lastIndexOf("/") + 1);
    return ImmutablePair.of(opId, executionId);
  }

  public static void testDataJobExecutionRead(
      String executionId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username,
      MockMvc mockMvc) {

    com.vmware.taurus.controlplane.model.data.DataJobExecution[] dataJobExecution =
        new com.vmware.taurus.controlplane.model.data.DataJobExecution[1];

    Callable<com.vmware.taurus.controlplane.model.data.DataJobExecution> dataJobExecutionCallable =
        () -> {
          String dataJobExecutionReadUrl =
              String.format(
                  "/data-jobs/for-team/%s/jobs/%s/executions/%s", teamName, jobName, executionId);
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
                  com.vmware.taurus.controlplane.model.data.DataJobExecution.class);
          return dataJobExecution[0];
        };
    await()
        .atMost(11, TimeUnit.MINUTES)
        .with()
        .pollInterval(15, TimeUnit.SECONDS)
        .failFast(
            () -> {
              com.vmware.taurus.controlplane.model.data.DataJobExecution status =
                  dataJobExecutionCallable.call();
              return status != null
                  && !status
                      .getStatus()
                      .equals(
                          com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum
                              .RUNNING)
                  && !executionStatus.equals(status.getStatus());
            })
        .until(
            dataJobExecutionCallable,
            statusEnum -> statusEnum != null && executionStatus.equals(statusEnum.getStatus()));

    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecution[0], jobName, username);
  }

  public static void testDataJobExecutionList(
      String executionId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username,
      MockMvc mockMvc)
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

    List<com.vmware.taurus.controlplane.model.data.DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
  }

  public static void testDataJobDeploymentExecutionList(
      String executionId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum executionStatus,
      String opId,
      String jobName,
      String teamName,
      String username,
      MockMvc mockMvc)
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

    List<com.vmware.taurus.controlplane.model.data.DataJobExecution> dataJobExecutions =
        objectMapper.readValue(
            dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
    assertNotNull(dataJobExecutions);
    dataJobExecutions =
        dataJobExecutions.stream()
            .filter(e -> e.getId().equals(executionId))
            .collect(Collectors.toList());
    assertEquals(1, dataJobExecutions.size());
    assertDataJobExecutionValid(
        executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
  }

  private static void testDataJobExecutionLogs(
      String executionId, String jobName, String teamName, String username, MockMvc mockMvc)
      throws Exception {
    MvcResult dataJobExecutionLogsResult =
        getExecuteLogs(executionId, jobName, teamName, username, mockMvc);
    assertFalse(dataJobExecutionLogsResult.getResponse().getContentAsString().isEmpty());
  }

  private static MvcResult getExecuteLogs(
      String executionId, String jobName, String teamName, String username, MockMvc mockMvc)
      throws Exception {
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

  private static void assertDataJobExecutionValid(
      String executionId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution.StatusEnum executionStatus,
      String opId,
      com.vmware.taurus.controlplane.model.data.DataJobExecution dataJobExecution,
      String jobName,
      String username) {

    assertNotNull(dataJobExecution);
    assertEquals(executionId, dataJobExecution.getId());
    assertEquals(jobName, dataJobExecution.getJobName());
    assertEquals(executionStatus, dataJobExecution.getStatus());
    assertEquals(
        com.vmware.taurus.controlplane.model.data.DataJobExecution.TypeEnum.MANUAL,
        dataJobExecution.getType());
    assertEquals(username + "/" + "user", dataJobExecution.getStartedBy());
    assertEquals(opId, dataJobExecution.getOpId());
  }
}
