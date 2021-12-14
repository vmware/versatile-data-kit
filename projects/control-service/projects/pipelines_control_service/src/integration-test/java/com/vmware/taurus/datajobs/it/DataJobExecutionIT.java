/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.actuate.metrics.AutoConfigureMetrics;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobExecutionRepository;

public class DataJobExecutionIT extends BaseDataJobDeploymentIT {

    private static final Logger log = LoggerFactory.getLogger(DataJobExecutionIT.class);
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

    @Autowired
    JobExecutionRepository jobExecutionRepository;

    /**
     * This test aims to validate the data job execution .For the purpose it does the following:
     * <ul>
     *     <li>Executes the data job</li>
     *     <li>Wait until a single data job execution to complete (using the awaitility for this)</li>
     *     <li>Checks data job execution status</li>
     * </ul>
     */
    @Test
    public void testDataJobExecution(String jobName, String teamName, String username) throws Exception {
        // cleanup
        List<com.vmware.taurus.service.model.DataJobExecution> dataJobExecutions = jobExecutionRepository.findDataJobExecutionsByDataJobName(jobName);
        jobExecutionRepository.deleteAll(dataJobExecutions);

        // Execute data job
        String opId = jobName + UUID.randomUUID().toString().toLowerCase();
        MvcResult dataJobExecutionResponse = executeDataJob(jobName, teamName, username, opId);

        // Check the data job execution status
        String location = dataJobExecutionResponse.getResponse().getHeader("location");
        String executionId = location.substring(location.lastIndexOf("/") + 1);
        checkDataJobExecutionStatus(executionId, DataJobExecution.StatusEnum.SUCCEEDED, opId, jobName, teamName, username);
    }

    private void checkDataJobExecutionStatus(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String opId,
          String jobName,
          String teamName,
          String username) throws Exception {

        try {
            testDataJobExecutionRead(executionId, executionStatus, opId, jobName, teamName, username);
            testDataJobExecutionList(executionId, executionStatus, opId, jobName, teamName, username);
            testDataJobDeploymentExecutionList(executionId, executionStatus, opId, jobName, teamName, username);
            testDataJobExecutionLogs(executionId, jobName, teamName, username);
        } catch (Error e) {
            try {
                // print logs in case execution has failed
                MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId, jobName, teamName, username);
                log.info("Job Execution {} logs:\n{}", executionId, dataJobExecutionLogsResult.getResponse().getContentAsString());
            } catch(Error ignore) {
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
              .until(() -> {
                  String dataJobExecutionReadUrl = String.format(
                        "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                        teamName, jobName,
                        executionId);
                  MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobExecutionReadUrl)
                        .with(user(username))
                        .contentType(MediaType.APPLICATION_JSON))
                        .andExpect(status().isOk())
                        .andReturn();

                  dataJobExecution[0] = objectMapper
                        .readValue(dataJobExecutionResult.getResponse().getContentAsString(), DataJobExecution.class);

                  return dataJobExecution[0] != null && executionStatus.equals(dataJobExecution[0].getStatus());
              });

        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecution[0], jobName, username);
    }

    private void testDataJobExecutionList(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String opId,
          String jobName,
          String teamName,
          String username) throws Exception {

        String dataJobExecutionListUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/executions",
              teamName, jobName);
        MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobExecutionListUrl)
              .with(user(username))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andReturn();

        List<DataJobExecution> dataJobExecutions = objectMapper
              .readValue(dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertNotNull(dataJobExecutions);
        dataJobExecutions = dataJobExecutions
              .stream()
              .filter(e -> e.getId().equals(executionId))
              .collect(Collectors.toList());
        assertEquals(1, dataJobExecutions.size());
        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
    }

    private void testDataJobDeploymentExecutionList(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String opId,
          String jobName,
          String teamName,
          String username) throws Exception {

        String dataJobDeploymentExecutionListUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
              teamName, jobName, "release");
        MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobDeploymentExecutionListUrl)
              .with(user(username))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk())
              .andReturn();

        List<DataJobExecution> dataJobExecutions = objectMapper
              .readValue(dataJobExecutionResult.getResponse().getContentAsString(), new TypeReference<>() {});
        assertNotNull(dataJobExecutions);
        dataJobExecutions = dataJobExecutions
              .stream()
              .filter(e -> e.getId().equals(executionId))
              .collect(Collectors.toList());
        assertEquals(1, dataJobExecutions.size());
        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecutions.get(0), jobName, username);
    }

    private void testDataJobExecutionLogs(String executionId, String jobName, String teamName, String username) throws Exception {
        MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId, jobName, teamName, username);
        assertFalse(dataJobExecutionLogsResult.getResponse().getContentAsString().isEmpty());
    }

    @NotNull
    private MvcResult getExecuteLogs(String executionId, String jobName, String teamName, String username) throws Exception {
        String dataJobExecutionListUrl = String.format(
                "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs",
                teamName, jobName, executionId);
        MvcResult dataJobExecutionLogsResult = mockMvc.perform(get(dataJobExecutionListUrl)
                        .with(user(username)))
                .andExpect(status().isOk())
                .andReturn();
        return dataJobExecutionLogsResult;
    }

    private void assertDataJobExecutionValid(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String opId,
          DataJobExecution dataJobExecution,
          String jobName,
          String username) {

        assertNotNull(dataJobExecution);
        assertEquals(executionId, dataJobExecution.getId());
        assertEquals(jobName, dataJobExecution.getJobName());
        assertEquals(executionStatus, dataJobExecution.getStatus());
        assertEquals(DataJobExecution.TypeEnum.MANUAL, dataJobExecution.getType());
        assertEquals(username + "/" + "user", dataJobExecution.getStartedBy());
        assertEquals(opId, dataJobExecution.getOpId());
    }
}
