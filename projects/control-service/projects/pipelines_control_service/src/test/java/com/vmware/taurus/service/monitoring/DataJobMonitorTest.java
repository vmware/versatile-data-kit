/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService.JobExecution;
import com.vmware.taurus.service.execution.JobExecutionResultManager;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import com.vmware.taurus.service.model.*;
import io.kubernetes.client.ApiException;
import io.micrometer.core.instrument.MeterRegistry;
import org.hamcrest.MatcherAssert;
import org.hamcrest.text.IsEqualIgnoringCase;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.io.IOException;
import java.time.Duration;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doThrow;


@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DataJobMonitorTest {

    @Autowired
    private MeterRegistry meterRegistry;

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @MockBean
    private DataJobsKubernetesService dataJobsKubernetesService;

    @Autowired
    private DataJobMonitor dataJobMonitor;

    @Test
    @Order(1)
    public void testUpdateDataJobTerminationStatusSuccess() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.SUCCEEDED, randomId("data-job-"));

        dataJobMonitor.updateDataJobTerminationStatusGauge(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED.getAlertValue().doubleValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(2)
    public void testUpdateDataJobTerminationStatusPlatformError() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.PLATFORM_ERROR, randomId("data-job-"));

        dataJobMonitor.updateDataJobTerminationStatusGauge(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR.getAlertValue().doubleValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(3)
    public void testUpdateDataJobTerminationStatusSkipped() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.SKIPPED, randomId("data-job-"));

        dataJobMonitor.updateDataJobTerminationStatusGauge(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(ExecutionStatus.SKIPPED.getAlertValue().doubleValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(ExecutionStatus.SKIPPED, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(4)
    public void testUpdateDataJobTerminationStatusStatusUserError() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.USER_ERROR, randomId("data-job-"));

        dataJobMonitor.updateDataJobTerminationStatusGauge(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(ExecutionStatus.USER_ERROR.getAlertValue().doubleValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(ExecutionStatus.USER_ERROR, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(5)
    public void testUpdateDataJobsGaugesWithoutJobs() {
        dataJobMonitor.updateDataJobsGauges(Collections.emptyList());

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
    }

    @Test
    @Order(6)
    public void testWatchJobs() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), ExecutionStatus.SUCCEEDED.getPodStatus()),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), ExecutionStatus.USER_ERROR.getPodStatus(), false),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), ExecutionStatus.PLATFORM_ERROR.getPodStatus(), false),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), ExecutionStatus.SKIPPED.getPodStatus())
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(new DataJob(s.getJobName(), new JobConfig())));

        dataJobMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        // We had 1 gauge from previous tests and added 4 more; but data jobs with last termination status SKIPPED
        // have no metrics exposed; so effectively the expected number of gauges is 4
        Assertions.assertEquals(4, gauges.size());
        jobStatuses.forEach(s -> {
            var expectedJob = jobsRepository.findById(s.getJobName());
            Assertions.assertTrue(expectedJob.isPresent());
            ExecutionStatus expectedStatus = getTerminationStatus(s);
            if (expectedStatus != ExecutionStatus.SKIPPED) {
                Assertions.assertEquals(expectedStatus, expectedJob.get().getLatestJobTerminationStatus());
            }
        });
    }

    // NOTE: The below two test cases may throw assertion errors if the data_job table in the
    // database used is not empty. In such case, delete all entries in the data_jobs table, and
    // re-run the tests.
    @Test
    @Order(7)
    public void testWatchJobsWithEmptyJobName() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), "", "")
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());

        dataJobMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(4, gauges.size());
        Assertions.assertEquals(5, jobsRepository.count());
    }

    @Test
    @Order(8)
    public void testWatchJobsWithMissingJob() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), "missing-id", "")
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());

        dataJobMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(4, gauges.size());
        Assertions.assertEquals(5, jobsRepository.count());
    }

    @Test
    @Order(9)
    public void testWatchJobsWithTheSameStatus() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), ExecutionStatus.SUCCEEDED.getPodStatus())
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(
                new DataJob(s.getJobName(), new JobConfig(), DeploymentStatus.NONE, getTerminationStatus(s), s.getExecutionId())));

        dataJobMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(4, gauges.size());
        jobStatuses.forEach(s -> {
            var expectedJob = jobsRepository.findById(s.getJobName());
            Assertions.assertTrue(expectedJob.isPresent());
            Assertions.assertEquals(getTerminationStatus(s), expectedJob.get().getLatestJobTerminationStatus());
        });
    }

    @Test
    @Order(10)
    void testWatchJobsWithoutTerminationMessage() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), null)
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(
                new DataJob(s.getJobName(), new JobConfig(), DeploymentStatus.NONE, getTerminationStatus(s), null)));

        dataJobMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(5, gauges.size());
        jobStatuses.forEach(s -> {
            var expectedJob = jobsRepository.findById(s.getJobName());
            Assertions.assertTrue(expectedJob.isPresent());
            Assertions.assertEquals(ExecutionStatus.SUCCEEDED, expectedJob.get().getLatestJobTerminationStatus());
        });
    }

    @Test
    @Order(11)
    public void testUpdateDataJobTerminationStatusWithoutExecutionId() {
        var dataJob = new DataJob("data-job", new JobConfig(), DeploymentStatus.NONE);

        dataJobMonitor.updateDataJobTerminationStatusGauge(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(5, gauges.size());
    }

    @Test
    @Order(12)
    public void testWatchJobsWhenExceptionIsThrown() throws IOException, ApiException {
        doThrow(new ApiException()).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), any(), anyLong());

        Assertions.assertDoesNotThrow(() -> dataJobMonitor.watchJobs());
    }

    @Test
    @Order(13)
    public void testRecordJobExecutionStatus_nullDataJobName_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus(null, randomId("job-"), ExecutionStatus.SUCCEEDED.getPodStatus());
        dataJobMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    @Test
    @Order(14)
    public void testRecordJobExecutionStatus_emptyDataJobName_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("", randomId("job-"), ExecutionStatus.SUCCEEDED.getPodStatus());
        dataJobMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    @Test
    @Order(15)
    public void testRecordJobExecutionStatus_existingDataJobAndNonExistingExecution_shouldRecordExecution() {
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "execution-id", ExecutionStatus.SUCCEEDED.getPodStatus(), true);
        dataJobMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(16)
    public void testRecordJobExecutionStatus_existingDataJobAndExistingExecution_shouldUpdateExecution() {
        DataJobExecution jobExecutionBeforeUpdate = jobExecutionRepository.findById("execution-id").get();
        JobExecution expectedJobExecution = JobExecution.builder()
              .jobName(jobExecutionBeforeUpdate.getDataJob().getName())
              .executionId(jobExecutionBeforeUpdate.getId())
              .podTerminationMessage(ExecutionStatus.SUCCEEDED.getPodStatus())
              .executionType("scheduled")
              .opId("opId")
              .startTime(jobExecutionBeforeUpdate.getStartTime())
              .endTime(jobExecutionBeforeUpdate.getEndTime())
              .jobVersion("jobVersion")
              .jobSchedule("jobSchedule")
              .resourcesCpuRequest(1F)
              .resourcesCpuLimit(2F)
              .resourcesMemoryRequest(500)
              .resourcesMemoryLimit(1000)
              .deployedDate(jobExecutionBeforeUpdate.getLastDeployedDate())
              .deployedBy("lastDeployedBy")
              .succeeded(true)
              .build();

        dataJobMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(17)
    public void testRecordJobExecutionStatusSkipped_existingDataJobAndNonExistingExecution_shouldRecordExecution() {
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "different-execution-id", ExecutionStatus.RUNNING.getPodStatus(), null);
        dataJobMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(18)
    public void testRecordJobExecutionStatusSkipped_existingDataJobAndExistingExecution_shouldRecordExecution() {
        var expectedExecutionMessage = "Skipping job execution due to another parallel running execution.";
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "different-execution-id", ExecutionStatus.SKIPPED.getPodStatus(), true);
        Optional<DataJobExecution> jobExecutionBeforeUpdate = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());
        dataJobMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution, expectedExecutionMessage, jobExecutionBeforeUpdate.get().getStartTime());
    }

    @Test
    @Order(19)
    public void testRecordJobExecutionStatus_nonExistingDataJobAndNonExistingExecution_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus(randomId("data-job-"), randomId("job-"), ExecutionStatus.SUCCEEDED.getPodStatus());
        dataJobMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    @Test
    @Order(20)
    void testUpdateDataJobInfoGauges() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.SUCCEEDED, randomId("data-job-"));

        dataJobMonitor.updateDataJobInfoGauges(jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
    }

    @Test
    @Order(21)
    void testUpdateDataJobInfoGauges_withNullDataJob_throwsException() {
        Assertions.assertThrows(NullPointerException.class, () -> dataJobMonitor.updateDataJobInfoGauges(null));
    }

    @Test
    @Order(22)
    void testClearDataJobsGaugesNotIn() {
        var dataJobs = Arrays.asList(
                new DataJob("data-job1", new JobConfig(), DeploymentStatus.NONE, ExecutionStatus.SUCCEEDED, randomId("data-job1-")),
                new DataJob("data-job2", new JobConfig(), DeploymentStatus.NONE, ExecutionStatus.SUCCEEDED, randomId("data-job2-")),
                new DataJob("data-job3", new JobConfig(), DeploymentStatus.NONE, ExecutionStatus.SUCCEEDED, randomId("data-job3-")));

        // Clean up from previous tests
        jobsRepository.deleteAll();
        dataJobMonitor.clearDataJobsGaugesNotIn(Collections.emptyList());

        // Add some more gauges
        dataJobMonitor.updateDataJobsGauges(jobsRepository.saveAll(dataJobs));

        var gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
        Assertions.assertEquals(3, gauges.size());
        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
        Assertions.assertEquals(3, gauges.size());
        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(3, gauges.size());

        // Delete a data job and verify that its gauges are removed as a result
        jobsRepository.deleteById(dataJobs.get(0).getName());
        dataJobMonitor.clearDataJobsGaugesNotIn(Arrays.asList(dataJobs.get(1), dataJobs.get(2)));

        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_INFO_METRIC_NAME).gauges();
        Assertions.assertEquals(2, gauges.size());
        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_NOTIFICATION_DELAY_METRIC_NAME).gauges();
        Assertions.assertEquals(2, gauges.size());
        gauges = meterRegistry.find(DataJobMetrics.TAURUS_DATAJOB_TERMINATION_STATUS_METRIC_NAME).gauges();
        Assertions.assertEquals(2, gauges.size());
    }

    @Test
    @Order(23)
    void testRecordJobExecutionStatus_withStatusSkipped_shouldNotUpdateTerminationStatus() {
        // Clean up from previous tests
        jobsRepository.deleteAll();
        dataJobMonitor.clearDataJobsGaugesNotIn(Collections.emptyList());

        var dataJob = new DataJob("new-job", new JobConfig(),
                DeploymentStatus.NONE, null, "old-execution-id");
        jobsRepository.save(dataJob);

        JobExecution jobExecution = buildJobExecutionStatus("new-job", "new-execution-id", ExecutionStatus.SKIPPED.getPodStatus(), true);
        dataJobMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJob> actualJob = jobsRepository.findById(dataJob.getName());

        Assertions.assertTrue(actualJob.isPresent());
        Assertions.assertEquals("old-execution-id", actualJob.get().getLatestJobExecutionId());
    }

    @Test
    @Order(24)
    void testRecordJobExecutionStatus_withDifferentStatus_shouldUpdateTerminationStatus() {
        // Clean up from previous tests
        jobsRepository.deleteAll();
        dataJobMonitor.clearDataJobsGaugesNotIn(Collections.emptyList());

        var dataJob = new DataJob("new-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.PLATFORM_ERROR, "old-execution-id");
        jobsRepository.save(dataJob);

        JobExecution jobExecution = buildJobExecutionStatus("new-job", "old-execution-id", ExecutionStatus.SUCCEEDED.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(actualJob.isPresent());
        Assertions.assertEquals("old-execution-id", actualJob.get().getLatestJobExecutionId());
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(25)
    void testRecordJobExecutionStatus_withDifferentExecutionId_shouldUpdateTerminationStatus() {
        // Clean up from previous tests
        jobsRepository.deleteAll();
        dataJobMonitor.clearDataJobsGaugesNotIn(Collections.emptyList());

        var dataJob = new DataJob("new-job", new JobConfig(),
                DeploymentStatus.NONE, null, "old-execution-id");
        jobsRepository.save(dataJob);

        JobExecution jobExecution = buildJobExecutionStatus("new-job", "new-execution-id", ExecutionStatus.USER_ERROR.getPodStatus(), true);

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(actualJob.isPresent());
        Assertions.assertEquals("new-execution-id", actualJob.get().getLatestJobExecutionId());
        Assertions.assertEquals(ExecutionStatus.USER_ERROR, actualJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(26)
    void testRecordJobExecutionStatus_shouldUpdateLastExecution() {
        // Clean up from previous tests
        jobsRepository.deleteAll();
        dataJobMonitor.clearDataJobsGaugesNotIn(Collections.emptyList());

        var dataJob = new DataJob("new-job", new JobConfig(),
                DeploymentStatus.NONE, ExecutionStatus.PLATFORM_ERROR, "old-execution-id");
        dataJob.setLastExecutionStatus(ExecutionStatus.PLATFORM_ERROR);
        dataJob.setLastExecutionEndTime(OffsetDateTime.of(2000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC));
        dataJob.setLastExecutionDuration(1000);
        jobsRepository.save(dataJob);

        JobExecution jobExecution = buildJobExecutionStatus("new-job", "old-execution-id", ExecutionStatus.PLATFORM_ERROR.getPodStatus(), false);

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualJob.get().getLastExecutionStatus());
    }

    @Test
    @Order(27)
    void testRecordJobExecutionStatus_withNullExecutionId_shouldNotUpdateLastExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", null, ExecutionStatus.SUCCEEDED.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualJob.get().getLastExecutionStatus());
    }

    @Test
    @Order(28)
    void testRecordJobExecutionStatus_withEmptyExecutionId_shouldNotUpdateLastExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", "", ExecutionStatus.SUCCEEDED.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualJob.get().getLastExecutionStatus());
    }


    @Test
    @Order(29)
    void testRecordJobExecutionStatus_withSameExecutionIdAndNewStatus_shouldNotUpdateLastExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", "old-execution-id", ExecutionStatus.SUCCEEDED.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        Assertions.assertEquals(ExecutionStatus.PLATFORM_ERROR, actualJob.get().getLastExecutionStatus());
    }

    @Test
    @Order(30)
    void testRecordJobExecutionStatus_withNewExecutionIdAndNewStatus_shouldUpdateLastExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", "new-execution-id", ExecutionStatus.SUCCEEDED.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualJob.get().getLastExecutionStatus());
        Assertions.assertEquals(jobExecution.getEndTime(), actualJob.get().getLastExecutionEndTime());
    }

    @Test
    @Order(31)
    void testRecordJobExecutionStatus_withSameExecutionIdAndOldStatusIsFinal_shouldNotUpdateTerminationStatus() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", "new-execution-id", ExecutionStatus.USER_ERROR.getPodStatus());

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        // The termination status should not have changed from SUCCESS to USER_ERROR because SUCCESS is a final status
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(32)
    void testRecordJobExecutionStatus_withAnOlderExecution_shouldNotUpdateLastExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("new-job", "newer-execution-id",
                ExecutionStatus.USER_ERROR.getPodStatus(), false,
                OffsetDateTime.now().minus(Duration.ofDays(2)),
                OffsetDateTime.now().minus(Duration.ofDays(1)));

        dataJobMonitor.recordJobExecutionStatus(jobExecution);

        Optional<DataJob> actualJob = jobsRepository.findById(jobExecution.getJobName());
        Assertions.assertFalse(actualJob.isEmpty());
        // The last execution status should not have changed from SUCCEEDED to USER_ERROR because the execution is not recent
        Assertions.assertEquals(ExecutionStatus.SUCCEEDED, actualJob.get().getLastExecutionStatus());
    }

    private static String randomId(String prefix) {
        return prefix + UUID.randomUUID();
    }

    private static ExecutionStatus getTerminationStatus(JobExecution jobExecution) {
        return JobExecutionResultManager.getResult(jobExecution).getExecutionStatus();
    }

    private static JobExecution buildJobExecutionStatus(String jobName, String executionId, String terminationMessage) {
        return buildJobExecutionStatus(jobName, executionId, terminationMessage, true);
    }

    private static JobExecution buildJobExecutionStatus(
            String jobName,
            String executionId,
            String terminationMessage,
            Boolean executionSucceeded) {
        return buildJobExecutionStatus(jobName, executionId, terminationMessage,
                executionSucceeded, OffsetDateTime.now(), OffsetDateTime.now());
    }

    private static JobExecution buildJobExecutionStatus(
          String jobName,
          String executionId,
          String terminationMessage,
          Boolean executionSucceeded,
          OffsetDateTime startTime,
          OffsetDateTime endTime) {
        return JobExecution.builder()
              .jobName(jobName)
              .executionId(executionId)
              .podTerminationMessage(terminationMessage)
              .executionType("scheduled")
              .opId("opId")
              .startTime(startTime)
              .endTime(endTime)
              .jobVersion("jobVersion")
              .jobSchedule("jobSchedule")
              .resourcesCpuRequest(1F)
              .resourcesCpuLimit(2F)
              .resourcesMemoryRequest(500)
              .resourcesMemoryLimit(1000)
              .deployedDate(OffsetDateTime.now())
              .deployedBy("lastDeployedBy")
              .succeeded(executionSucceeded)
              .build();
    }

    private void assertDataJobExecutionValid(JobExecution expectedJobExecution, Optional<DataJobExecution> actualJobExecution) {
        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution, null, null);
    }

    private void assertDataJobExecutionValid(JobExecution expectedJobExecution, Optional<DataJobExecution> actualJobExecution, OffsetDateTime startTime) {
        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution, null, startTime);
    }

    private void assertDataJobExecutionValid(JobExecution expectedJobExecution, Optional<DataJobExecution> actualJobExecution, String expectedExecutionMessage, OffsetDateTime startTime) {
        Assertions.assertTrue(actualJobExecution.isPresent());

        DataJobExecution actualDataJobExecution = actualJobExecution.get();
        Assertions.assertEquals(expectedJobExecution.getExecutionId(), actualDataJobExecution.getId());
        Assertions.assertEquals(expectedJobExecution.getJobName(), actualDataJobExecution.getDataJob().getName());
        MatcherAssert.assertThat(expectedJobExecution.getExecutionType(), IsEqualIgnoringCase.equalToIgnoringCase(actualDataJobExecution.getType().name()));
        Assertions.assertEquals(expectedJobExecution.getJobVersion(), actualDataJobExecution.getJobVersion());
        Assertions.assertEquals(expectedJobExecution.getJobSchedule(), actualDataJobExecution.getJobSchedule());
        Assertions.assertEquals(startTime == null ? expectedJobExecution.getStartTime() : startTime, actualDataJobExecution.getStartTime());
        Assertions.assertEquals(expectedJobExecution.getEndTime(), actualDataJobExecution.getEndTime());
        Assertions.assertEquals(expectedJobExecution.getOpId(), actualDataJobExecution.getOpId());
        Assertions.assertEquals(expectedJobExecution.getResourcesCpuRequest(), actualDataJobExecution.getResourcesCpuRequest());
        Assertions.assertEquals(expectedJobExecution.getResourcesCpuLimit(), actualDataJobExecution.getResourcesCpuLimit());
        Assertions.assertEquals(expectedJobExecution.getResourcesMemoryRequest(), actualDataJobExecution.getResourcesMemoryRequest());
        Assertions.assertEquals(expectedJobExecution.getResourcesMemoryLimit(), actualDataJobExecution.getResourcesMemoryLimit());
        Assertions.assertEquals(expectedExecutionMessage == null ? expectedJobExecution.getPodTerminationMessage() : expectedExecutionMessage, actualDataJobExecution.getMessage());
        Assertions.assertEquals(expectedJobExecution.getDeployedBy(), actualDataJobExecution.getLastDeployedBy());
        Assertions.assertEquals(expectedJobExecution.getDeployedDate(), actualDataJobExecution.getLastDeployedDate());
    }
}
