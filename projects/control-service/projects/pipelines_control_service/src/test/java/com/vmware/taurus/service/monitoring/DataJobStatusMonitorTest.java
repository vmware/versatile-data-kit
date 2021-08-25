/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.monitoring;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.KubernetesService.JobExecution;
import com.vmware.taurus.service.KubernetesService.PodTerminationMessage;
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
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doThrow;


@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT, classes = ControlplaneApplication.class)
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class DataJobStatusMonitorTest {

    @Autowired
    private MeterRegistry meterRegistry;

    @Autowired
    private JobsRepository jobsRepository;

    @Autowired
    private JobExecutionRepository jobExecutionRepository;

    @MockBean
    private DataJobsKubernetesService dataJobsKubernetesService;

    @Autowired
    private DataJobStatusMonitor dataJobStatusMonitor;

    @Test
    @Order(1)
    public void testUpdateDataJobTerminationStatusSuccess() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, TerminationStatus.SUCCESS, randomId("data-job-"));

        dataJobStatusMonitor.updateDataJobTerminationStatus(() -> jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(TerminationStatus.SUCCESS.getValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(TerminationStatus.SUCCESS, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(2)
    public void testUpdateDataJobTerminationStatusPlatformError() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, TerminationStatus.PLATFORM_ERROR, randomId("data-job-"));

        dataJobStatusMonitor.updateDataJobTerminationStatus(() -> jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(TerminationStatus.PLATFORM_ERROR.getValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(TerminationStatus.PLATFORM_ERROR, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(3)
    public void testUpdateDataJobTerminationStatusSkipped() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, TerminationStatus.SKIPPED, randomId("data-job-"));

        dataJobStatusMonitor.updateDataJobTerminationStatus(() -> jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(TerminationStatus.SKIPPED.getValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(TerminationStatus.SKIPPED, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(4)
    public void testUpdateDataJobTerminationStatusStatusUserError() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, TerminationStatus.USER_ERROR, randomId("data-job-"));

        dataJobStatusMonitor.updateDataJobTerminationStatus(() -> jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
        Assertions.assertEquals(TerminationStatus.USER_ERROR.getValue(), gauges.stream().findFirst().get().value());

        var expectedJob = jobsRepository.findById(dataJob.getName());
        Assertions.assertTrue(expectedJob.isPresent());
        Assertions.assertEquals(TerminationStatus.USER_ERROR, expectedJob.get().getLatestJobTerminationStatus());
    }

    @Test
    @Order(5)
    public void testUpdateDataJobsTerminationStatusWithoutJobs() {
        dataJobStatusMonitor.updateDataJobsTerminationStatus(Collections::emptyList);

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(1, gauges.size());
    }

    @Test
    @Order(6)
    public void testWatchJobs() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), PodTerminationMessage.SUCCESS.getValue()),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), PodTerminationMessage.USER_ERROR.getValue()),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), PodTerminationMessage.PLATFORM_ERROR.getValue()),
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), PodTerminationMessage.SKIPPED.getValue())
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(new DataJob(s.getJobName(), new JobConfig())));

        dataJobStatusMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(5, gauges.size());
        jobStatuses.forEach(s -> {
            var expectedJob = jobsRepository.findById(s.getJobName());
            Assertions.assertTrue(expectedJob.isPresent());
            Assertions.assertEquals(getTerminationStatus(s), expectedJob.get().getLatestJobTerminationStatus());
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
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());

        dataJobStatusMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(5, gauges.size());
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
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());

        dataJobStatusMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(5, gauges.size());
        Assertions.assertEquals(5, jobsRepository.count());
    }

    @Test
    @Order(9)
    public void testWatchJobsWithTheSameStatus() throws IOException, ApiException {
        var jobStatuses = List.of(
              buildJobExecutionStatus(randomId("datajob-"), randomId("job-"), PodTerminationMessage.SUCCESS.getValue())
        );
        doAnswer(inv -> {
            jobStatuses.forEach(inv.getArgument(1));
            return null;
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(
                new DataJob(s.getJobName(), new JobConfig(), DeploymentStatus.NONE, getTerminationStatus(s), null)));

        dataJobStatusMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(6, gauges.size());
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
        }).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());
        jobStatuses.forEach(s -> jobsRepository.save(
                new DataJob(s.getJobName(), new JobConfig(), DeploymentStatus.NONE, getTerminationStatus(s), null)));

        dataJobStatusMonitor.watchJobs();

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(7, gauges.size());
        jobStatuses.forEach(s -> {
            var expectedJob = jobsRepository.findById(s.getJobName());
            Assertions.assertTrue(expectedJob.isPresent());
            Assertions.assertEquals(TerminationStatus.NONE, expectedJob.get().getLatestJobTerminationStatus());
        });
    }

    @Test
    @Order(11)
    public void testUpdateDataJobTerminationStatusWithoutExecutionId() {
        var dataJob = new DataJob("data-job", new JobConfig(),
                DeploymentStatus.NONE, TerminationStatus.SUCCESS, randomId("data-job-"));

        dataJobStatusMonitor.updateDataJobTerminationStatus(() -> jobsRepository.save(dataJob));

        var gauges = meterRegistry.find(DataJobStatusMonitor.GAUGE_METRIC_NAME).gauges();
        Assertions.assertEquals(7, gauges.size());
    }

    @Test
    @Order(12)
    public void testWatchJobsWhenExceptionIsThrown() throws IOException, ApiException {
        doThrow(new ApiException()).when(dataJobsKubernetesService).watchJobs(anyMap(), any(), anyLong());

        Assertions.assertDoesNotThrow(() -> dataJobStatusMonitor.watchJobs());
    }

    @Test
    @Order(13)
    public void testRecordJobExecutionStatus_nullDataJobName_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus(null, randomId("job-"), PodTerminationMessage.SUCCESS.getValue());
        dataJobStatusMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    @Test
    @Order(14)
    public void testRecordJobExecutionStatus_emptyDataJobName_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus("", randomId("job-"), PodTerminationMessage.SUCCESS.getValue());
        dataJobStatusMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    @Test
    @Order(15)
    public void testRecordJobExecutionStatus_existingDataJobAndNonExistingExecution_shouldRecordExecution() {
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "execution-id", PodTerminationMessage.SUCCESS.getValue(), JobExecution.Status.RUNNING);
        dataJobStatusMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(16)
    public void testRecordJobExecutionStatus_existingDataJobAndExistingExecution_shouldUpdateExecution() {
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "execution-id", PodTerminationMessage.SUCCESS.getValue(), JobExecution.Status.FINISHED);
        dataJobStatusMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(17)
    public void testRecordJobExecutionStatusSkipped_existingDataJobAndExistingExecution_shouldRecordExecution() {
        var expectedTerminationMessage = "Skipping job execution due to another parallel running execution.";
        JobExecution expectedJobExecution = buildJobExecutionStatus("data-job", "execution-id", expectedTerminationMessage, JobExecution.Status.RUNNING);
        dataJobStatusMonitor.recordJobExecutionStatus(expectedJobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(expectedJobExecution.getExecutionId());

        assertDataJobExecutionValid(expectedJobExecution, actualJobExecution);
    }

    @Test
    @Order(18)
    public void testRecordJobExecutionStatus_nonExistingDataJobAndNonExistingExecution_shouldNotRecordExecution() {
        JobExecution jobExecution = buildJobExecutionStatus(randomId("data-job-"), randomId("job-"), PodTerminationMessage.SUCCESS.getValue());
        dataJobStatusMonitor.recordJobExecutionStatus(jobExecution);
        Optional<DataJobExecution> actualJobExecution = jobExecutionRepository.findById(jobExecution.getExecutionId());

        Assertions.assertTrue(actualJobExecution.isEmpty());
    }

    private static String randomId(String prefix) {
        return prefix + UUID.randomUUID();
    }

    private static TerminationStatus getTerminationStatus(JobExecution jobExecution) {
        return DataJobStatusMonitor.getTerminationStatus(jobExecution.getTerminationMessage());
    }

    private static JobExecution buildJobExecutionStatus(String jobName, String executionId, String terminationMessage) {
        return buildJobExecutionStatus(jobName, executionId, terminationMessage, JobExecution.Status.FINISHED);
    }

    private static JobExecution buildJobExecutionStatus(
          String jobName,
          String executionId,
          String terminationMessage,
          JobExecution.Status status) {
        return JobExecution.builder()
              .jobName(jobName)
              .executionId(executionId)
              .terminationMessage(terminationMessage)
              .executionType("scheduled")
              .opId("opId")
              .startTime(OffsetDateTime.now())
              .endTime(OffsetDateTime.now())
              .jobVersion("jobVersion")
              .jobSchedule("jobSchedule")
              .resourcesCpuRequest(1F)
              .resourcesCpuLimit(2F)
              .resourcesMemoryRequest(500)
              .resourcesMemoryLimit(1000)
              .deployedDate(OffsetDateTime.now())
              .deployedBy("lastDeployedBy")
              .status(status)
              .build();
    }

    private void assertDataJobExecutionValid(JobExecution expectedJobExecution, Optional<DataJobExecution> actualJobExecution) {
        Assertions.assertTrue(actualJobExecution.isPresent());

        DataJobExecution actualDataJobExecution = actualJobExecution.get();
        Assertions.assertEquals(expectedJobExecution.getExecutionId(), actualDataJobExecution.getId());
        Assertions.assertEquals(expectedJobExecution.getJobName(), actualDataJobExecution.getDataJob().getName());
        MatcherAssert.assertThat(expectedJobExecution.getExecutionType(), IsEqualIgnoringCase.equalToIgnoringCase(actualDataJobExecution.getType().name()));
        Assertions.assertEquals(expectedJobExecution.getJobVersion(), actualDataJobExecution.getJobVersion());
        Assertions.assertEquals(expectedJobExecution.getJobSchedule(), actualDataJobExecution.getJobSchedule());
        Assertions.assertEquals(expectedJobExecution.getStartTime(), actualDataJobExecution.getStartTime());
        Assertions.assertEquals(expectedJobExecution.getEndTime(), actualDataJobExecution.getEndTime());
        Assertions.assertEquals(expectedJobExecution.getOpId(), actualDataJobExecution.getOpId());
        Assertions.assertEquals(expectedJobExecution.getResourcesCpuRequest(), actualDataJobExecution.getResourcesCpuRequest());
        Assertions.assertEquals(expectedJobExecution.getResourcesCpuLimit(), actualDataJobExecution.getResourcesCpuLimit());
        Assertions.assertEquals(expectedJobExecution.getResourcesMemoryRequest(), actualDataJobExecution.getResourcesMemoryRequest());
        Assertions.assertEquals(expectedJobExecution.getResourcesMemoryLimit(), actualDataJobExecution.getResourcesMemoryLimit());
        Assertions.assertEquals(expectedJobExecution.getTerminationMessage(), actualDataJobExecution.getMessage());
        Assertions.assertEquals(expectedJobExecution.getDeployedBy(), actualDataJobExecution.getLastDeployedBy());
        Assertions.assertEquals(expectedJobExecution.getDeployedDate(), actualDataJobExecution.getLastDeployedDate());
    }
}
