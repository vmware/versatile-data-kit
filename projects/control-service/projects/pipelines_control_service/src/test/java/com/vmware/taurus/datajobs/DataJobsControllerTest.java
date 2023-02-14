/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.controlplane.model.data.DataJob;
import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.controlplane.model.data.DataJobSchedule;
import com.vmware.taurus.exception.ApiConstraintError;
import com.vmware.taurus.service.JobOperationResult;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.model.DeploymentStatus;
import com.vmware.taurus.service.model.JobConfig;
import graphql.ExecutionInput;
import graphql.GraphQL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.springframework.http.HttpHeaders;
import org.springframework.web.util.UriBuilder;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class DataJobsControllerTest {

  private JobsService jobsService = mock(JobsService.class);
  private GraphQL graphQL = mock(GraphQL.class);
  @Captor private ArgumentCaptor<ExecutionInput> queryCaptor;

  @Test
  public void testDataJobCreate() {
    when(jobsService.createJob(any()))
        .thenReturn(JobOperationResult.builder().completed(true).build());
    UriBuilder builder = UriComponentsBuilder.fromHttpUrl("http://test.com/");
    var testInst = new DataJobsController(jobsService, null, null, null, () -> builder);
    DataJob dataJob = newJob("test-job");
    var response = testInst.dataJobCreate("team", dataJob, "");
    var location = response.getHeaders().get(HttpHeaders.LOCATION).get(0);
    assertEquals("http://test.com/data-jobs/for-team/team/jobs/test-job", location);
  }

  @Test
  public void testDataJobCreateNameValidity() {
    when(jobsService.createJob(any()))
        .thenReturn(JobOperationResult.builder().completed(true).build());
    UriBuilder builder = UriComponentsBuilder.fromHttpUrl("http://test.com/");
    var testInst = new DataJobsController(jobsService, null, null, null, () -> builder);

    Assertions.assertThrows(
        ApiConstraintError.class,
        () -> testInst.dataJobCreate("team", newJob("1_job_with_starting_number"), ""));
    Assertions.assertThrows(
        ApiConstraintError.class,
        () -> testInst.dataJobCreate("team", newJob("NameWithCapitalLetters"), ""));
    Assertions.assertThrows(
        ApiConstraintError.class,
        () -> testInst.dataJobCreate("team", newJob("job name with spaces"), ""));
    Assertions.assertThrows(
        ApiConstraintError.class,
        () -> testInst.dataJobCreate("team", newJob("job_name_with_underscore"), ""));
    Assertions.assertThrows(
        ApiConstraintError.class, () -> testInst.dataJobCreate("team", newJob("a".repeat(51)), ""));
    Assertions.assertThrows(
        ApiConstraintError.class, () -> testInst.dataJobCreate("team", newJob("a".repeat(5)), ""));

    testInst.dataJobCreate("team", newJob("a".repeat(6)), "");
    testInst.dataJobCreate("team", newJob("a".repeat(45)), "");
    testInst.dataJobCreate("team", newJob("a".repeat(50)), "");
    testInst.dataJobCreate("team", newJob("job-name-with-dash"), "");
  }

  @Test
  public void testDataJobUpdateTeamChange() {
    when(jobsService.updateJob(any())).thenReturn(true);
    when(jobsService.getByName(any()))
        .thenReturn(Optional.of(getServiceModelDataJob("test-job", "team")));
    when(jobsService.jobWithTeamExists("test-job", "team")).thenReturn(true);
    UriBuilder builder = UriComponentsBuilder.fromHttpUrl("http://test.com/");
    var testInst = new DataJobsController(jobsService, null, null, null, () -> builder);

    Assertions.assertThrows(
        ApiConstraintError.class,
        () -> testInst.dataJobUpdate("team", "test-job", newJob("test-job", "team2", "* * * * *")));

    testInst.dataJobUpdate("team", "test-job", newJob("test-job", "team", "* * * * *"));
  }

  private static com.vmware.taurus.service.model.DataJob getServiceModelDataJob(
      String name, String team) {
    JobConfig jobConfig = new JobConfig();
    jobConfig.setJobName(name);
    jobConfig.setTeam(team);
    return new com.vmware.taurus.service.model.DataJob(name, jobConfig, DeploymentStatus.NONE);
  }

  private static DataJob newJob(String s) {
    return newJob(s, "team", "* * * * *");
  }

  private static DataJob newJob(String s, String team, String cron) {
    DataJob dataJob = new DataJob();
    DataJobSchedule schedule = new DataJobSchedule().scheduleCron(cron);
    DataJobConfig config = new DataJobConfig().schedule(schedule);
    return dataJob.jobName(s).config(config).team(team);
  }
}
