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
import com.vmware.taurus.service.execution.JobExecutionService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.shaded.org.awaitility.Awaitility;

import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import static com.vmware.taurus.datajobs.it.common.JobExecutionUtil.testDataJobExecutionRead;

@Slf4j
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobViewLogsIT extends BaseIT {

  @Autowired private JobExecutionService executionService;

  // simple_job_read_logs.zip contains a job that would run for more than 30 minutes if allowed
  @RegisterExtension
  static DataJobDeploymentExtension dataJobDeploymentExtension =
      new DataJobDeploymentExtension("simple_job_read_logs.zip");

  @Test
  public void testJobLogsViewing(
      String jobName, String username, String deploymentId, String teamName) throws Exception {
    // manually start job execution
    ImmutablePair<String, String> executeDataJobResult =
        JobExecutionUtil.executeDataJob(jobName, teamName, username, deploymentId, mockMvc);
    String executionId = executeDataJobResult.getRight();
    String opId = executeDataJobResult.getLeft();
    testDataJobExecutionRead(
        executionId,
        DataJobExecution.StatusEnum.RUNNING,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
    Awaitility.await()
        .atMost(6, TimeUnit.MINUTES)
        .ignoreExceptionsMatching(
            (e) ->
                // It is only by looking 3 exceptions deep that we can tell the reason the logs read
                // failed.
                e.getCause()
                    .getCause()
                    // If 400 is in the error message then the pod is not up yet and we should keep
                    // trying to poll for the logs.
                    .getMessage()
                    .contains("400"))
        .until(
            () -> {
              getLogsFast(jobName, teamName, executionId);
              return true;
            });
  }

  /** We are testing that the server returns logs quickly. */
  private void getLogsFast(String jobName, String teamName, String executionId)
      throws InterruptedException, ExecutionException, TimeoutException {
    Executors.newSingleThreadExecutor()
        .submit(
            () -> {
              executionService.getJobExecutionLogs(teamName, jobName, executionId, 0);
            })
        .get(5, TimeUnit.SECONDS);
  }
}
