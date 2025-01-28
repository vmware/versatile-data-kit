/*
 * Copyright 2023-2024 Broadcom
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

@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@TestPropertySource(
    properties = {
      "datajobs.job.resources.requests.memory=6Mi",
      "datajobs.job.resources.limits.memory=6Mi",
      // This is a standard cron job template except restartPolicy is set to never so that when a
      // job runs out of memory it is
      // not retied but instead reports more quickly that it is a platform error
      "datajobs.control.k8s.data.job.template.file=data_job_templates/fast_failing_cron_job.yaml"
    })
public class DataJobMainContainerOOMIT extends BaseIT {

  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension =
      new DataJobDeploymentExtension("oom_job.zip");

  @Test
  public void testDataJob_causesOOM_shouldCompleteWithUserError(
      String jobName, String teamName, String username, String deploymentId) throws Exception {
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
  }
}
