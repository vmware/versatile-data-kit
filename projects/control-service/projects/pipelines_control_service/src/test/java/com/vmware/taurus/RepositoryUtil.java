/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.JobsRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import com.vmware.taurus.service.model.JobConfig;
import org.junit.jupiter.api.Assertions;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;

public final class RepositoryUtil {

  public static DataJob createDataJob(JobsRepository jobsRepository) {
    return createDataJob(jobsRepository, "test-job");
  }

  public static DataJob createDataJob(JobsRepository jobsRepository, String jobName) {
    return createDataJob(jobsRepository, jobName, "test-team");
  }

  public static DataJob createDataJob(
      JobsRepository jobsRepository, String jobName, String jobTeam) {
    JobConfig config = new JobConfig();
    config.setSchedule("schedule");
    config.setTeam(jobTeam);
    var expectedJob = new DataJob(jobName, config, DeploymentStatus.NONE);
    var actualJob = jobsRepository.save(expectedJob);
    Assertions.assertEquals(expectedJob, actualJob);

    return actualJob;
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus) {

    return createDataJobExecution(
        jobExecutionRepository, executionId, dataJob, executionStatus, "test_message");
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus,
      OffsetDateTime startTime,
      OffsetDateTime endTime) {

    return createDataJobExecution(
        jobExecutionRepository,
        executionId,
        dataJob,
        executionStatus,
        "test_message",
        startTime,
        endTime);
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus,
      String message,
      OffsetDateTime startTime) {

    return createDataJobExecution(
        jobExecutionRepository,
        executionId,
        dataJob,
        executionStatus,
        message,
        startTime,
        getTimeAccurateToMicroSecond());
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus,
      OffsetDateTime startTime) {

    return createDataJobExecution(
        jobExecutionRepository,
        executionId,
        dataJob,
        executionStatus,
        "test_message",
        startTime,
        getTimeAccurateToMicroSecond());
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus,
      String message) {

    return createDataJobExecution(
        jobExecutionRepository,
        executionId,
        dataJob,
        executionStatus,
        message,
        getTimeAccurateToMicroSecond(),
        getTimeAccurateToMicroSecond());
  }

  public static DataJobExecution createDataJobExecution(
      JobExecutionRepository jobExecutionRepository,
      String executionId,
      DataJob dataJob,
      ExecutionStatus executionStatus,
      String message,
      OffsetDateTime startTime,
      OffsetDateTime endTime) {

    var expectedJobExecution =
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
            .message(message)
            .lastDeployedBy("test_user")
            .lastDeployedDate(getTimeAccurateToMicroSecond())
            .jobVersion("test_version")
            .jobSchedule("*/5 * * * *")
            .opId("test_op_id")
            .vdkVersion("test_vdk_version")
            .build();

    return jobExecutionRepository.save(expectedJobExecution);
  }

  /**
   * at the database level we only store date-times accurate to the microsecond. Like wise in older
   * versions of java .now() returned timestamps accurate to micro-seconds. In newer versions of
   * java .now() gives nano-second precision and it causes tests written before we adopted that java
   * version to fail.
   */
  public static OffsetDateTime getTimeAccurateToMicroSecond() {
    return OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS);
  }
}
