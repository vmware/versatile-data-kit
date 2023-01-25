/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;

import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.DataJobExecution;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;

public class JobExecutionUtil {

  /** at the database level we only store date-times accurate to the microsecond. Like wise in older versions of java .now() returned timestamps accurate to micro-seconds.
   * In newer versions of java .now() gives nano-second precision and it causes tests written before we adopted that java version to fail.
   */
  public static OffsetDateTime getTimeAccurateToMicroSecond(){
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
            .lastDeployedDate(OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS))
            .jobVersion("test_version")
            .jobSchedule("*/5 * * * *")
            .opId("test_op_id")
            .vdkVersion("test_vdk_version")
            .build();

    return jobExecutionRepository.save(jobExecution);
  }
}
