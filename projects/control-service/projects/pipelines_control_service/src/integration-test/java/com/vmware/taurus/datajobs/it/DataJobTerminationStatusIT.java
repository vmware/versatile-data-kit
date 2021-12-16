/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
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
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import com.vmware.taurus.datajobs.it.common.BaseDataJobDeploymentIT;
import com.vmware.taurus.service.JobsRepository;

@AutoConfigureMetrics
public class DataJobTerminationStatusIT extends BaseDataJobDeploymentIT {

    public static final String INFO_METRICS = "taurus_datajob_info";
    public static final String TERMINATION_STATUS_METRICS = "taurus_datajob_termination_status";
    public static final String HEADER_X_OP_ID = "X-OPID";

    private static final Logger log = LoggerFactory.getLogger(DataJobTerminationStatusIT.class);
    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

    @Autowired
    JobsRepository jobsRepository;

    // TODO split this test into job termination status test and data job execution test
    /**
     * This test aims to validate the data job execution and termination status monitoring logic in TPCS. For the purpose it does the following:
     * <ul>
     *     <li>Creates a new data job (simple_job.zip), configured with:</li>
     *     <ul>
     *         <li>schedule (e.g. *&#47;2 * * * *)</li>
     *         <li>notification emails</li>
     *         <li>enable_execution_notifications set to false</li>
     *     </ul>
     *     <li>Deploys the data job</li>
     *     <li>Wait for the deployment to complete</li>
     *     <li>Executes the data job</li>
     *     <li>Checks data job execution status</li>
     *     <li>Wait until a single data job execution to complete (using the awaitility for this)</li>
     *     <li>Checks data job execution status</li>
     *     <li>Make a rest call to the (/data-jobs/debug/prometheus)</li>
     *     <li>Parse the result and validate that:</li>
     *     <ul>
     *         <li>there is a taurus_datajob_info metrics for the data job used for testing and that it has the
     *         appropriate email labels (they should be empty because enable_execution_notifications is false)</li>
     *         <li>there is a taurus_datajob_termination_status metrics for the data job used for testing and it
     *         has the appropriate value (0.0 in this case; i.e. the job should have succeeded)</li>
     *     </ul>
     *     <li>Finally, delete the job deployment and the leftover K8s jobs.</li>
     * </ul>
     */
    @Test
    public void testDataJobTerminationStatus(String jobName, String teamName, String username) throws Exception {
        // Execute data job
        String opId = jobName + UUID.randomUUID().toString().toLowerCase();
        DataJobExecutionRequest dataJobExecutionRequest = new DataJobExecutionRequest()
              .startedBy(username);

        String triggerDataJobExecutionUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
              teamName,
              jobName,
              "release");
        MvcResult dataJobExecutionResponse = mockMvc.perform(post(triggerDataJobExecutionUrl)
              .with(user(username))
              .header(HEADER_X_OP_ID, opId)
              .content(mapper.writeValueAsString(dataJobExecutionRequest))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().is(202))
              .andReturn();

        // Check the data job execution status
        String location = dataJobExecutionResponse.getResponse().getHeader("location");
        String executionId = location.substring(location.lastIndexOf("/") + 1);
        checkDataJobExecutionStatus(executionId, DataJobExecution.StatusEnum.SUCCEEDED, opId, jobName, teamName, username);

        // Wait for the job execution to complete, polling every 5 seconds
        // See: https://github.com/awaitility/awaitility/wiki/Usage
        await().atMost(10, TimeUnit.MINUTES).with().pollInterval(15, TimeUnit.SECONDS).until(terminationMetricsAreAvailable());

        String scrape = scrapeMetrics();

        // Validate that all metrics for the executed data job are correctly exposed
        // First, validate that there is a taurus_datajob_info metrics for the data job
        var match = findMetricsWithLabel(scrape, INFO_METRICS, "data_job", jobName);
        assertTrue(match.isPresent(),
                String.format("Could not find %s metrics for the data job %s",
                        INFO_METRICS, jobName));

        // Validate the labels of the taurus_datajob_info metrics
        String line = match.get();
        assertLabelEquals(INFO_METRICS, teamName, "team", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_success", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_platform_error", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_user_error", line);

        // Validate that there is a taurus_datajob_info metrics for the data job
        match = findMetricsWithLabel(scrape, TERMINATION_STATUS_METRICS, "data_job", jobName);
        assertTrue(match.isPresent(),
                String.format("Could not find %s metrics for the data job %s",
                        TERMINATION_STATUS_METRICS, jobName));

        // Validate that the metrics has a value of 0.0 (i.e. Success)
        System.out.println(match.get().trim());
        assertTrue(match.get().trim().endsWith("0.0"), "The value of the taurus_datajob_termination_status metrics does not match");

        // Check the data job execution status
        checkDataJobExecutionStatus(executionId, DataJobExecution.StatusEnum.SUCCEEDED, opId, jobName, teamName, username);
    }

    private String scrapeMetrics() throws Exception {
        return mockMvc.perform(get("/data-jobs/debug/prometheus"))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();
    }

    private Callable<Boolean> terminationMetricsAreAvailable() {
        return () -> scrapeMetrics().contains(TERMINATION_STATUS_METRICS);
    }

    private static Optional<String> findMetricsWithLabel(CharSequence input, String metrics, String label, String labelValue) {
        Pattern pattern = Pattern.compile(String.format("%s\\{.*%s=\"%s\"[^\\}]*\\} (.*)", metrics, label, labelValue),
                Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(input);
        if (!matcher.find()) {
            return Optional.empty();
        }
        return Optional.of(matcher.group());
    }

    private static void assertLabelEquals(String metrics, String expectedValue, String label, String line) {
        // Label value is captured in the first regex group
        Matcher matcher = Pattern.compile(String.format(".*%s=\"([^\"]*)\".*", label), Pattern.CASE_INSENSITIVE).matcher(line);
        assertTrue(matcher.find(), String.format("The metrics %s does not have a matching label %s", metrics, label));
        String actualValue = matcher.group(1);
        assertEquals(expectedValue, actualValue,
                String.format("The metrics %s does not have correct value for label %s. Expected: %s, Actual: %s",
                        metrics, label, expectedValue, actualValue));
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
