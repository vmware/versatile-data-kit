/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.service.JobExecutionRepository;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.annotation.DirtiesContext;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ActiveProfiles({"MockKubernetes", "MockKerberos", "unittest", "MockTelemetry"})
@ExtendWith(SpringExtension.class)
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.MOCK,
    classes = ControlplaneApplication.class)
@AutoConfigureMockMvc
public class DataJobsExecutionControllerIT {

  private static final String TEST_TEAM_NAME = "test-team";
  private static final String TEST_JOB_NAME = "test-job";

  @Autowired private MockMvc mockMvc;
  @Autowired private DataJobsKubernetesService dataJobsKubernetesService;

  @Autowired private JobExecutionRepository jobExecutionRepository;

  @Test
  @WithMockUser
  @DirtiesContext
  public void testDataJobExecutionStartNotFound() throws Exception {
    ResultActions mockExecution =
        TestUtils.startMockExecution(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    mockExecution.andExpect(status().isNotFound());
  }

  // TODO: test all methods
  @Test
  @WithMockUser
  @DirtiesContext
  public void testWhenADeploymentFailsNoEntryIsSavedInTheDatabase() throws Exception {
    // arrange
    doThrow(new RuntimeException("Expected failure"))
        .when(dataJobsKubernetesService)
        .startNewCronJobExecution(any(), any(), any(), any(), any(), any());
    // act
    TestUtils.createDataJob(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    TestUtils.createDeployment(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    assertEquals(
        TestUtils.startMockExecution(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME)
            .andReturn()
            .getResponse()
            .getStatus(),
        500);

    // assert
    assertTrue(jobExecutionRepository.findAll().isEmpty());
  }

  @Test
  @WithMockUser
  @DirtiesContext
  public void testDataJobExecutionLogs() throws Exception {
    TestUtils.createDataJob(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    TestUtils.createDeployment(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    ResultActions mockExecution =
        TestUtils.startMockExecution(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    var location = mockExecution.andReturn().getResponse().getHeader("Location");
    String id = location.substring(location.lastIndexOf('/') + 1);

    String url =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs", TEST_TEAM_NAME, TEST_JOB_NAME, id);
    mockMvc.perform(get(url)).andExpect(status().isOk());
  }

  @Test
  @WithMockUser
  @DirtiesContext
  public void testDataJobExecutionLogsNoExecution() throws Exception {
    TestUtils.createDataJob(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);
    TestUtils.createDeployment(mockMvc, TEST_TEAM_NAME, TEST_JOB_NAME);

    String url =
        String.format(
            "/data-jobs/for-team/%s/jobs/%s/executions/%s/logs",
            TEST_TEAM_NAME, TEST_JOB_NAME, "no-exec");
    mockMvc.perform(get(url)).andExpect(status().isNotFound());
  }
}
