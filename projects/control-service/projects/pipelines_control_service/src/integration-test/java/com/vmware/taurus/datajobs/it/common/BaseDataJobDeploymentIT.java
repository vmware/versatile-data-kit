/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it.common;

import static org.awaitility.Awaitility.await;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.core.task.SyncTaskExecutor;
import org.springframework.core.task.TaskExecutor;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;

/**
 * It combines all necessary annotations and constants for tests that need an already deployed data
 * job.
 *
 * <p>The test just needs to extend this class, and it will have access to the already deployed data
 * job.
 */
@Import({BaseDataJobDeploymentIT.TaskExecutorConfig.class})
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
@ExtendWith(DataJobDeploymentExtension.class)
public abstract class BaseDataJobDeploymentIT extends BaseIT {

  @TestConfiguration
  public static class TaskExecutorConfig {
    @Bean
    @Primary
    public TaskExecutor taskExecutor() {
      // Deployment methods are non-blocking (Async) which makes them harder to test.
      // Making them sync for the purposes of this test.
      return new SyncTaskExecutor();
    }
  }

  protected MvcResult executeDataJob(
      String jobName, String teamName, String username, String opId) {
    // Execute data job
    if (opId == null) {
      opId = jobName + UUID.randomUUID().toString().toLowerCase();
    }

    DataJobExecutionRequest dataJobExecutionRequest =
        new DataJobExecutionRequest().startedBy(username);

    String triggerDataJobExecutionUrl =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
            teamName, jobName, "release");

    // Wait for the job execution to complete, polling every 15 seconds
    // See: https://github.com/awaitility/awaitility/wiki/Usage
    String finalOpId = opId;
    return await()
        .atMost(5, TimeUnit.MINUTES)
        .with()
        .pollInterval(15, TimeUnit.SECONDS)
        .until(
            () ->
                mockMvc
                    .perform(
                        post(triggerDataJobExecutionUrl)
                            .with(user(username))
                            .header(HEADER_X_OP_ID, finalOpId)
                            .content(mapper.writeValueAsString(dataJobExecutionRequest))
                            .contentType(MediaType.APPLICATION_JSON))
                    .andReturn(),
            mvcResult -> mvcResult.getResponse().getStatus() == 202);
  }
}
