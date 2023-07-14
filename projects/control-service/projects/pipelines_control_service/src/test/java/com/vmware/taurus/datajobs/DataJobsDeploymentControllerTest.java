/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJob;
import com.vmware.taurus.controlplane.model.data.DataJobConfig;
import com.vmware.taurus.service.JobsService;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.BatchV1Api;

import static org.mockito.ArgumentMatchers.any;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.boot.test.mock.mockito.SpyBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;

@AutoConfigureMockMvc
@ExtendWith(MockitoExtension.class)
@SpringBootTest(
    classes = {ControlplaneApplication.class},
    properties = {"datajobs.control.k8s.k8sSupportsV1CronJob=true"})
@MockitoSettings(strictness = Strictness.LENIENT)
public class DataJobsDeploymentControllerTest {

  @Autowired protected MockMvc mockMvc;
  @Autowired protected JobsService jobService;

  @MockBean(name = "deploymentBatchV1Api")
  private BatchV1Api batchV1Api;

  @SpyBean private DataJobsKubernetesService dataJobsKubernetesService;

  @Test
  public void whenKubernetesIsUnavailableTheControlPlaneShouldReturnAnErrorInsteadOfSayingNoJobs()
      throws Exception {
    Mockito.doNothing().when(dataJobsKubernetesService).saveSecretData(any(), any());
//   This exception encompasses random exceptions from k8s but also version incompatibility issues.
    Mockito.when(batchV1Api.readNamespacedCronJob(Mockito.any(), Mockito.any(), Mockito.any()))
        .thenThrow(new ApiException("", null, 500, null, ""));

    mockMvc
        .perform(
            post("/data-jobs/for-team/team-name/jobs")
                .contentType(MediaType.APPLICATION_JSON)
                .content(
                    new ObjectMapper()
                        .writeValueAsString(new DataJob("job-name", "desc", new DataJobConfig()))))
        .andExpect(status().is(201));
    mockMvc
        .perform(get("/data-jobs/for-team/team-name/jobs/job-name/deployments"))
        .andExpect(status().is(503));
  }
}
