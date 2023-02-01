/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.DataJobDeploymentExtension;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.boot.test.context.SpringBootTest;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobOOMIT extends BaseIT {

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension =
      DataJobDeploymentExtension.builder().jobSource("oom_job.zip").build();

  private final ObjectMapper objectMapper =
      new ObjectMapper()
          .registerModule(new JavaTimeModule()); // Used for converting to OffsetDateTime;

  @Test
  public void testJobCancellation_createDeployExecuteAndCancelJob(
      String jobName, String username, String deploymentId, String teamName) throws Exception {
    // manually start job execution
    ImmutablePair<String, String> executeDataJobResult =
        JobExecutionUtil.executeDataJob(jobName, teamName, username, deploymentId, mockMvc);
    String opId = executeDataJobResult.getLeft();
    String executionId = executeDataJobResult.getRight();

    // Check the data job execution status
    JobExecutionUtil.checkDataJobExecutionStatus(
        executionId,
        DataJobExecution.StatusEnum.USER_ERROR,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);

    JobExecutionUtil.checkDataJobExecutionStatus(
        executionId,
        DataJobExecution.StatusEnum.PLATFORM_ERROR,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
  }
}
