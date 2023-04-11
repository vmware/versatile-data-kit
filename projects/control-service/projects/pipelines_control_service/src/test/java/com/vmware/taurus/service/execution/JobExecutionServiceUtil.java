/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.execution;

import com.vmware.taurus.controlplane.model.data.DataJobDeployment;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.controlplane.model.data.DataJobResources;
import com.vmware.taurus.datajobs.ToApiModelConverter;
import org.junit.jupiter.api.Assertions;

import java.util.List;

public class JobExecutionServiceUtil {

  public static void assertDataJobExecutionListValid(
      com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution,
      List<DataJobExecution> actualDataJobExecutions) {
    Assertions.assertNotNull(actualDataJobExecutions);
    Assertions.assertFalse(actualDataJobExecutions.isEmpty());

    DataJobExecution actualDataJobExecution = actualDataJobExecutions.get(0);
    assertDataJobExecutionValid(expectedDataJobExecution, actualDataJobExecution);
  }

  public static void assertDataJobExecutionValid(
      com.vmware.taurus.service.model.DataJobExecution expectedDataJobExecution,
      DataJobExecution actualDataJobExecution) {
    Assertions.assertEquals(expectedDataJobExecution.getId(), actualDataJobExecution.getId());
    Assertions.assertEquals(
        expectedDataJobExecution.getDataJob().getName(), actualDataJobExecution.getJobName());
    Assertions.assertEquals(
        ToApiModelConverter.convertTypeEnum(expectedDataJobExecution.getType()),
        actualDataJobExecution.getType());
    Assertions.assertEquals(
        ToApiModelConverter.convertStatusEnum(expectedDataJobExecution.getStatus()),
        actualDataJobExecution.getStatus());
    Assertions.assertEquals(expectedDataJobExecution.getOpId(), actualDataJobExecution.getOpId());
    Assertions.assertEquals(
        expectedDataJobExecution.getMessage(), actualDataJobExecution.getMessage());
    Assertions.assertEquals(
        expectedDataJobExecution.getStartedBy(), actualDataJobExecution.getStartedBy());
    Assertions.assertEquals(
        expectedDataJobExecution.getStartTime(), actualDataJobExecution.getStartTime());
    Assertions.assertEquals(
        expectedDataJobExecution.getEndTime(), actualDataJobExecution.getEndTime());

    DataJobDeployment actualDeployment = actualDataJobExecution.getDeployment();
    Assertions.assertNotNull(actualDeployment);
    Assertions.assertEquals(
        expectedDataJobExecution.getJobSchedule(),
        actualDeployment.getSchedule().getScheduleCron());
    Assertions.assertEquals(
        expectedDataJobExecution.getVdkVersion(), actualDeployment.getVdkVersion());
    Assertions.assertEquals(
        expectedDataJobExecution.getJobVersion(), actualDeployment.getJobVersion());
    Assertions.assertEquals(
        expectedDataJobExecution.getJobPythonVersion(), actualDeployment.getPythonVersion());

    DataJobResources actualDeploymentResources = actualDeployment.getResources();
    Assertions.assertNotNull(actualDeploymentResources);
    Assertions.assertEquals(
        expectedDataJobExecution.getResourcesCpuRequest(),
        actualDeploymentResources.getCpuRequest());
    Assertions.assertEquals(
        expectedDataJobExecution.getResourcesCpuLimit(), actualDeploymentResources.getCpuLimit());
    Assertions.assertEquals(
        expectedDataJobExecution.getResourcesMemoryRequest(),
        actualDeploymentResources.getMemoryRequest());
    Assertions.assertEquals(
        expectedDataJobExecution.getResourcesMemoryLimit(),
        actualDeploymentResources.getMemoryLimit());
  }
}
