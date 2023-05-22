/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

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
import org.springframework.test.context.TestPropertySource;

import static com.vmware.taurus.datajobs.it.common.JobExecutionUtil.*;

@Slf4j
@TestPropertySource(
    properties = {
      // This is a standard cron job template except activeDeadlineSeconds is set to 1
      "datajobs.control.k8s.data.job.template.file=data_job_templates/backoff_limit_exceeded_cron_job.yaml"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobBackoffLimitExceededIT extends BaseIT {

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension = new DataJobDeploymentExtension();

  @Test
  public void testDataJob_causesOOM_shouldCompleteWithUserError(
      String jobName, String teamName, String username, String deploymentId) throws Exception {
    // manually start job execution
    ImmutablePair<String, String> executeDataJobResult =
        JobExecutionUtil.executeDataJob(jobName, teamName, username, deploymentId, mockMvc);
    String opId = executeDataJobResult.getLeft();
    String executionId = executeDataJobResult.getRight();

    // Check the data job execution status
    testDataJobExecutionRead(
        executionId,
        DataJobExecution.StatusEnum.USER_ERROR,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
    testDataJobExecutionList(
        executionId,
        DataJobExecution.StatusEnum.USER_ERROR,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
    testDataJobDeploymentExecutionList(
        executionId,
        DataJobExecution.StatusEnum.USER_ERROR,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
  }
}
