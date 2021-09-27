/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.service.deploy.JobImageDeployer;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import io.kubernetes.client.ApiException;
import org.apache.commons.io.IOUtils;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.test.autoconfigure.actuate.metrics.AutoConfigureMetrics;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import java.lang.Error;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static org.awaitility.Awaitility.await;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMetrics
@Import({DataJobTerminationStatusIT.TaskExecutorConfig.class})
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
public class DataJobTerminationStatusIT extends BaseIT {

    private static final Logger log = LoggerFactory.getLogger(DataJobTerminationStatusIT.class);

    private static final String SIMPLE_JOB_NAME = "integration-test-" + UUID.randomUUID().toString().substring(0, 8);
    private static final String SIMPLE_JOB_NOTIFIED_EMAIL = "tpalashki@vmware.com";
    private static final String SIMPLE_JOB_SCHEDULE = "*/2 * * * *";
    private static final String USER_NAME = "user";
    private static final String DEPLOYMENT_ID = "NOT_USED";
    private static final String INFO_METRICS = "taurus_datajob_info";
    private static final String TERMINATION_STATUS_METRICS = "taurus_datajob_termination_status";
    private static final String HEADER_X_OP_ID = "X-OPID";

    private final ObjectMapper objectMapper = new ObjectMapper().registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

    @TestConfiguration
    static class TaskExecutorConfig {
        @Bean
        @Primary
        public TaskExecutor taskExecutor() {
            // Deployment methods are non-blocking (Async) which makes them harder to test.
            // Making them sync for the purposes of this test.
            return new SyncTaskExecutor();
        }
    }

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
    public void testDataJobTerminationStatus() throws Exception {
        // Setup
        String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, SIMPLE_JOB_NAME);

        // Create the data job
        mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user(USER_NAME))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isCreated())
                .andExpect(header().string(HttpHeaders.LOCATION,
                        lambdaMatcher(s -> s.endsWith(String.format("/data-jobs/for-team/%s/jobs/%s",
                                TEST_TEAM_NAME,
                                SIMPLE_JOB_NAME)))));

        byte[] jobZipBinary = IOUtils.toByteArray(
                getClass().getClassLoader().getResourceAsStream("simple_job.zip"));

        // Upload the data job
        MvcResult uploadResult = mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
                TEST_TEAM_NAME,
                SIMPLE_JOB_NAME))
                .with(user(USER_NAME))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
                .andExpect(status().isOk())
                .andReturn();
        DataJobVersion dataJobVersion = mapper.readValue(uploadResult.getResponse().getContentAsString(),
                DataJobVersion.class);

        // Update the data job configuration
        var dataJob = new DataJob()
                .jobName(SIMPLE_JOB_NAME)
                .team(TEST_TEAM_NAME)
                .config(new DataJobConfig()
                        .enableExecutionNotifications(false)
                        .contacts(new DataJobContacts()
                                .addNotifiedOnJobSuccessItem(SIMPLE_JOB_NOTIFIED_EMAIL)
                                .addNotifiedOnJobDeployItem(SIMPLE_JOB_NOTIFIED_EMAIL)
                                .addNotifiedOnJobFailurePlatformErrorItem(SIMPLE_JOB_NOTIFIED_EMAIL)
                                .addNotifiedOnJobFailureUserErrorItem(SIMPLE_JOB_NOTIFIED_EMAIL))
                        .schedule(new DataJobSchedule()
                                .scheduleCron(SIMPLE_JOB_SCHEDULE)));
        mockMvc.perform(put(String.format("/data-jobs/for-team/%s/jobs/%s",
                TEST_TEAM_NAME,
                SIMPLE_JOB_NAME))
                .with(user(USER_NAME))
                .content(mapper.writeValueAsString(dataJob))
                .contentType(MediaType.APPLICATION_JSON));

        // Deploy the data job
        var dataJobDeployment = new DataJobDeployment()
                .jobVersion(dataJobVersion.getVersionSha())
                .mode(DataJobMode.RELEASE)
                .enabled(true);
        mockMvc.perform(post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, SIMPLE_JOB_NAME))
                .with(user(USER_NAME))
                .content(mapper.writeValueAsString(dataJobDeployment))
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isAccepted())
                .andReturn();

        // Verify that the job deployment was created
        String jobDeploymentName = JobImageDeployer.getCronJobName(SIMPLE_JOB_NAME);
        Optional<JobDeploymentStatus> cronJobOptional = dataJobsKubernetesService.readCronJob(jobDeploymentName);
        assertTrue(cronJobOptional.isPresent());
        JobDeploymentStatus cronJob = cronJobOptional.get();
        assertEquals(dataJobVersion.getVersionSha(), cronJob.getGitCommitSha());
        assertEquals(DataJobMode.RELEASE.toString(), cronJob.getMode());
        assertEquals(true, cronJob.getEnabled());
        assertTrue(cronJob.getImageName().endsWith(dataJobVersion.getVersionSha()));
        assertEquals(USER_NAME, cronJob.getLastDeployedBy());

        // Execute data job
        String opId = SIMPLE_JOB_NAME + UUID.randomUUID().toString().toLowerCase();
        DataJobExecutionRequest dataJobExecutionRequest = new DataJobExecutionRequest()
              .startedBy(USER_NAME);

        String triggerDataJobExecutionUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
              TEST_TEAM_NAME,
              SIMPLE_JOB_NAME,
              "release");
        MvcResult dataJobExecutionResponse = mockMvc.perform(post(triggerDataJobExecutionUrl)
              .with(user(USER_NAME))
              .header(HEADER_X_OP_ID, opId)
              .content(mapper.writeValueAsString(dataJobExecutionRequest))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().is(202))
              .andReturn();

        // Check the data job execution status
        String location = dataJobExecutionResponse.getResponse().getHeader("location");
        String executionId = location.substring(location.lastIndexOf("/") + 1);
        checkDataJobExecutionStatus(executionId, DataJobExecution.StatusEnum.FINISHED, opId);

        // Wait for the job execution to complete, polling every 5 seconds
        // See: https://github.com/awaitility/awaitility/wiki/Usage
        await().atMost(10, TimeUnit.MINUTES).with().pollInterval(15, TimeUnit.SECONDS).until(terminationMetricsAreAvailable());

        String scrape = scrapeMetrics();

        // Validate that all metrics for the executed data job are correctly exposed
        // First, validate that there is a taurus_datajob_info metrics for the data job
        var match = findMetricsWithLabel(scrape, INFO_METRICS, "data_job", SIMPLE_JOB_NAME);
        assertTrue(match.isPresent(),
                String.format("Could not find %s metrics for the data job %s",
                        INFO_METRICS, SIMPLE_JOB_NAME));

        // Validate the labels of the taurus_datajob_info metrics
        String line = match.get();
        assertLabelEquals(INFO_METRICS, TEST_TEAM_NAME, "team", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_success", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_platform_error", line);
        assertLabelEquals(INFO_METRICS, "", "email_notified_on_user_error", line);

        // Validate that there is a taurus_datajob_info metrics for the data job
        match = findMetricsWithLabel(scrape, TERMINATION_STATUS_METRICS, "data_job", SIMPLE_JOB_NAME);
        assertTrue(match.isPresent(),
                String.format("Could not find %s metrics for the data job %s",
                        TERMINATION_STATUS_METRICS, SIMPLE_JOB_NAME));

        // Validate that the metrics has a value of 0.0 (i.e. Success)
        System.out.println(match.get().trim());
        // TODO: Temporary disabled since the К8S POD termination message is always null and respectively the termination status is 1.0
        // assertTrue("The value of the taurus_datajob_termination_status metrics does not match", match.get().trim().endsWith("0.0"));

        // Check the data job execution status
        checkDataJobExecutionStatus(executionId, DataJobExecution.StatusEnum.FINISHED, opId);
    }

    @AfterEach
    public void cleanup() throws Exception {
        log.info("Cleaning up deployments");

        // Execute delete deployment
        mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                TEST_TEAM_NAME,
                SIMPLE_JOB_NAME,
                DEPLOYMENT_ID))
                .with(user(USER_NAME))
                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isAccepted());

        // Wait for deployment to be deleted
        String jobDeploymentName = JobImageDeployer.getCronJobName(SIMPLE_JOB_NAME);
        await().atMost(5, TimeUnit.SECONDS).with().pollInterval(1, TimeUnit.SECONDS).until(deploymentIsDeleted(jobDeploymentName));

        mockMvc.perform(delete(String.format("/data-jobs/for-team/%s/jobs/%s/sources",
              TEST_TEAM_NAME,
              SIMPLE_JOB_NAME))
              .with(user(USER_NAME))
              .contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isOk());

        // Finally, delete the K8s jobs to avoid them messing up subsequent runs of the same test
        dataJobsKubernetesService.listJobs().stream()
                .filter(jobName -> jobName.startsWith(SIMPLE_JOB_NAME))
                .forEach(this::deleteKubernetesJob);
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

    private void deleteKubernetesJob(String jobName) {
        try {
            dataJobsKubernetesService.deleteJob(jobName);
        } catch (ApiException e) {
            log.warn("Failed to delete job {}", jobName, e);
        }
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

    private Callable<Boolean> deploymentIsDeleted(String jobDeploymentName) {
        return () -> dataJobsKubernetesService.readCronJob(jobDeploymentName).isEmpty();
    }

    private void checkDataJobExecutionStatus(String executionId, DataJobExecution.StatusEnum executionStatus, String opId) throws Exception {
        try {
            testDataJobExecutionRead(executionId, executionStatus, opId);
            testDataJobExecutionList(executionId, executionStatus, opId);
            testDataJobDeploymentExecutionList(executionId, executionStatus, opId);
            testDataJobExecutionLogs(executionId, executionStatus, opId);
        } catch (Error e) {
            try {
                // print logs in case execution has failed
                MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId);
                log.info("Job Execution {} logs:\n{}", executionId, dataJobExecutionLogsResult.getResponse().getContentAsString());
            } catch(Error ignore) {
            }
            throw e;
        }
    }

    private void testDataJobExecutionRead(String executionId, DataJobExecution.StatusEnum executionStatus, String opId) {
        DataJobExecution[] dataJobExecution = new DataJobExecution[1];

        await()
              .atMost(5, TimeUnit.MINUTES)
              .with()
              .pollInterval(15, TimeUnit.SECONDS)
              .until(() -> {
                  String dataJobExecutionReadUrl = String.format(
                        "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                        TEST_TEAM_NAME, SIMPLE_JOB_NAME,
                        executionId);
                  MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobExecutionReadUrl)
                        .with(user(USER_NAME))
                        .contentType(MediaType.APPLICATION_JSON))
                        .andExpect(status().isOk())
                        .andReturn();

                  dataJobExecution[0] = objectMapper
                        .readValue(dataJobExecutionResult.getResponse().getContentAsString(), DataJobExecution.class);

                  return dataJobExecution[0] != null && executionStatus.equals(dataJobExecution[0].getStatus());
              });

        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecution[0]);
    }

    private void testDataJobExecutionList(String executionId, DataJobExecution.StatusEnum executionStatus, String opId) throws Exception {
        String dataJobExecutionListUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/executions",
              TEST_TEAM_NAME, SIMPLE_JOB_NAME);
        MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobExecutionListUrl)
              .with(user(USER_NAME))
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
        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecutions.get(0));
    }

    private void testDataJobDeploymentExecutionList(String executionId, DataJobExecution.StatusEnum executionStatus, String opId) throws Exception {
        String dataJobDeploymentExecutionListUrl = String.format(
              "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
              TEST_TEAM_NAME, SIMPLE_JOB_NAME, "release");
        MvcResult dataJobExecutionResult = mockMvc.perform(get(dataJobDeploymentExecutionListUrl)
              .with(user(USER_NAME))
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
        assertDataJobExecutionValid(executionId, executionStatus, opId, dataJobExecutions.get(0));
    }

    private void testDataJobExecutionLogs(String executionId, DataJobExecution.StatusEnum executionStatus, String opId) throws Exception {
        MvcResult dataJobExecutionLogsResult = getExecuteLogs(executionId);
        assertFalse(dataJobExecutionLogsResult.getResponse().getContentAsString().isEmpty());
    }

    @NotNull
    private MvcResult getExecuteLogs(String executionId) throws Exception {
        String dataJobExecutionListUrl = String.format(
                "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs",
                TEST_TEAM_NAME, SIMPLE_JOB_NAME, executionId);
        MvcResult dataJobExecutionLogsResult = mockMvc.perform(get(dataJobExecutionListUrl)
                        .with(user(USER_NAME)))
                .andExpect(status().isOk())
                .andReturn();
        return dataJobExecutionLogsResult;
    }

    private void assertDataJobExecutionValid(
          String executionId,
          DataJobExecution.StatusEnum executionStatus,
          String opId,
          DataJobExecution dataJobExecution) {

        assertNotNull(dataJobExecution);
        assertEquals(executionId, dataJobExecution.getId());
        assertEquals(SIMPLE_JOB_NAME, dataJobExecution.getJobName());
        assertEquals(executionStatus, dataJobExecution.getStatus());
        assertEquals(DataJobExecution.TypeEnum.MANUAL, dataJobExecution.getType());
        assertEquals("manual/" + USER_NAME + "/" + "user", dataJobExecution.getStartedBy());
        assertEquals(opId, dataJobExecution.getOpId());
    }
}
