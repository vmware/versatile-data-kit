/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.controlplane.model.data.*;
import com.vmware.taurus.service.model.JobDeployment;
import com.vmware.taurus.service.model.JobDeploymentStatus;
import org.jetbrains.annotations.NotNull;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

public class TestUtils {

  public static final String TEST_TEAM_NAME = "test-team-name";

  private static final ObjectMapper mapper = new ObjectMapper();

  // @NotNull
  public static DataJob getDataJob(String teamName, String name) {
    var job = new DataJob();
    job.setJobName(name);
    job.setTeam(teamName);
    var dataJobConfig = new DataJobConfig();
    dataJobConfig.setGenerateKeytab(true);
    dataJobConfig.setSchedule(new DataJobSchedule());
    dataJobConfig.getSchedule().setScheduleCron("15 10 * * *");
    dataJobConfig.setContacts(new DataJobContacts());
    dataJobConfig.setDbDefaultType("");
    job.setConfig(dataJobConfig);
    return job;
  }

  public static DataJobDeployment getDataJobDeployment(String deploymentId, String jobVersion) {
    var jobDeployment = new DataJobDeployment();
    jobDeployment.setVdkVersion("");
    jobDeployment.setJobVersion(jobVersion);
    jobDeployment.setMode(DataJobMode.RELEASE);
    jobDeployment.setEnabled(true);
    jobDeployment.setResources(new DataJobResources());
    jobDeployment.setSchedule(new DataJobSchedule());
    jobDeployment.setId(deploymentId);

    return jobDeployment;
  }

  public static ResultActions createDataJob(MockMvc mockMvc, String teamName, String jobName)
      throws Exception {
    var job = TestUtils.getDataJob(teamName, jobName);

    String body = mapper.writeValueAsString(job);
    var result =
        mockMvc
            .perform(
                post(String.format("/data-jobs/for-team/%s/jobs", teamName))
                    .content(body)
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isCreated());
    return result;
  }

  public static ResultActions createDeployment(MockMvc mockMvc, String teamName, String jobName)
      throws Exception {
    var jobDeployment = TestUtils.getDataJobDeployment(jobName, "1");

    var result =
        mockMvc.perform(
            post(String.format("/data-jobs/for-team/%s/jobs/%s/deployments", teamName, jobName))
                .content(mapper.writeValueAsString(jobDeployment))
                .contentType(MediaType.APPLICATION_JSON));
    return result;
  }

  @NotNull
  public static ResultActions startMockExecution(MockMvc mockMvc, String teamName, String jobName)
      throws Exception {
    DataJobExecutionRequest executionRequest = new DataJobExecutionRequest();
    executionRequest.setStartedBy("unit-test");
    String body = mapper.writeValueAsString(executionRequest);

    String url =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions", teamName, jobName, jobName);
    var mockExecution =
        mockMvc.perform(post(url).content(body).contentType(MediaType.APPLICATION_JSON));
    return mockExecution;
  }

  public static JobDeploymentStatus getJobDeploymentStatus() {
    JobDeploymentStatus jobDeploymentStatus = new JobDeploymentStatus();
    jobDeploymentStatus.setGitCommitSha("version");
    jobDeploymentStatus.setEnabled(true);
    jobDeploymentStatus.setImageName("test-job-image-name");
    jobDeploymentStatus.setMode("mode");
    jobDeploymentStatus.setCronJobName("cron");
    return jobDeploymentStatus;
  }

  public static JobDeployment getJobDeployment() {
    JobDeployment jobDeployment = new JobDeployment();
    jobDeployment.setDataJobTeam(TestUtils.TEST_TEAM_NAME);
    jobDeployment.setGitCommitSha("version");
    jobDeployment.setEnabled(true);
    jobDeployment.setImageName("test-job-image-name");
    jobDeployment.setMode("mode");
    jobDeployment.setCronJobName("cron");
    return jobDeployment;
  }
}
