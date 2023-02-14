/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.webhook;

import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.datajobs.ToApiModelConverter;
import com.vmware.taurus.service.model.DataJob;
import com.vmware.taurus.service.model.ExecutionStatus;
import com.vmware.taurus.service.model.ExecutionType;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.OffsetDateTime;

public class ToApiModelConverterJobExecutionTest {

  private static final String TEST_LOGS_URL = "http://logs/jobs?filter=job-name";

  private DataJobExecution expected;

  private com.vmware.taurus.service.model.DataJobExecution toConvert;

  @BeforeEach
  public void setUp() {
    DataJobDeployment dataJobDeployment = new DataJobDeployment();
    var schedule = new DataJobSchedule();
    schedule.setScheduleCron("cron schedule string");

    var resources = new DataJobResources();
    resources.setMemoryRequest(100);
    resources.setMemoryLimit(150);
    resources.setCpuRequest(1.4f);
    resources.setCpuLimit(2.5f);

    dataJobDeployment.setSchedule(schedule);
    dataJobDeployment.setResources(resources);
    dataJobDeployment.setId(DataJobMode.RELEASE.getValue());
    dataJobDeployment.setMode(DataJobMode.RELEASE);
    dataJobDeployment.enabled(true);
    dataJobDeployment.setDeployedBy("test-user");
    dataJobDeployment.setDeployedDate(OffsetDateTime.MAX);

    expected = new DataJobExecution();
    expected.setDeployment(dataJobDeployment);
    expected.setType(DataJobExecution.TypeEnum.SCHEDULED);
    expected.setMessage("Message");
    expected.setStartedBy("Started");
    expected.setId("1234");
    expected.setOpId("1234");
    expected.setStartTime(OffsetDateTime.MIN);
    expected.setEndTime(OffsetDateTime.MAX);
    expected.setJobName("Job");
    expected.setStatus(DataJobExecution.StatusEnum.RUNNING);
    expected.setLogsUrl(TEST_LOGS_URL);

    toConvert = new com.vmware.taurus.service.model.DataJobExecution();
    toConvert.setEndTime(OffsetDateTime.MAX);
    toConvert.setStartTime(OffsetDateTime.MIN);
    toConvert.setType(ExecutionType.SCHEDULED);
    toConvert.setMessage("Message");
    toConvert.setStartedBy("Started");
    toConvert.setId("1234");
    toConvert.setOpId("1234");
    toConvert.setDataJob(new DataJob());
    toConvert.getDataJob().setName("Job");
    toConvert.setLastDeployedBy("test-user");
    toConvert.setLastDeployedDate(OffsetDateTime.MAX);
    toConvert.setStatus(ExecutionStatus.RUNNING);
    toConvert.setJobSchedule("cron schedule string");
    toConvert.setResourcesCpuLimit(2.5f);
    toConvert.setResourcesCpuRequest(1.4f);
    toConvert.setResourcesMemoryRequest(100);
    toConvert.setResourcesMemoryLimit(150);
  }

  @Test
  public void testConvertDataJobExecution() {
    var actual = ToApiModelConverter.jobExecutionToConvert(toConvert, TEST_LOGS_URL);
    Assertions.assertEquals(expected, actual);
  }

  @Test
  public void testDifferentStatus() {
    expected.setStatus(DataJobExecution.StatusEnum.PLATFORM_ERROR);
    toConvert.setStatus(ExecutionStatus.PLATFORM_ERROR);
    var actual = ToApiModelConverter.jobExecutionToConvert(toConvert, TEST_LOGS_URL);

    Assertions.assertEquals(expected, actual);
  }

  @Test
  public void testDifferentType() {
    expected.setType(DataJobExecution.TypeEnum.MANUAL);
    toConvert.setType(ExecutionType.MANUAL);
    var actual = ToApiModelConverter.jobExecutionToConvert(toConvert, TEST_LOGS_URL);

    Assertions.assertEquals(expected, actual);
  }

  @Test
  public void testSomeNullablePropertiesNull() {
    expected.setEndTime(null);
    expected.setMessage(null);

    toConvert.setEndTime(null);
    toConvert.setMessage(null);
    var actual = ToApiModelConverter.jobExecutionToConvert(toConvert, TEST_LOGS_URL);

    Assertions.assertEquals(expected, actual);
  }
}
