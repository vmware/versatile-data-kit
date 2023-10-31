/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import org.junit.jupiter.api.Assertions;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.hamcrest.Matchers.is;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.deployment.configuration.persistence.writeTos=K8S",
      "datajobs.deployment.configuration.persistence.readDataSource=K8S",
      "datajobs.deployment.configuration.synchronization.task.enabled=false"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudIT extends BaseDataJobDeploymentCrudIT {

  private void setVdkVersionForDeployment() throws Exception {
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentVdkVersionRequestBody("new_vdk_version_tag"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isBadRequest());
  }

  private void disableDeployment() throws Exception {
    // Execute disable deployment again to check that the version is not overwritten
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentEnableRequestBody(false))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isAccepted());
  }

  private void verifyVersion() throws Exception {
    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.vdk_version", is("release")));
  }

  private void resetVdkDeploymentVersion() throws Exception {
    mockMvc
        .perform(
            patch(
                    String.format(
                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                        TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .content(getDataJobDeploymentVdkVersionRequestBody(""))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isBadRequest());
  }

  private MvcResult getDeployment() throws Exception {
    return mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isOk())
        .andReturn();
  }

  private void checkDeployment() throws Exception {

    MvcResult result = getDeployment();

    DataJobDeploymentStatus jobDeployment =
        mapper.readValue(result.getResponse().getContentAsString(), DataJobDeploymentStatus.class);

    Assertions.assertEquals("user", jobDeployment.getLastDeployedBy());
    Assertions.assertEquals("3.9", jobDeployment.getPythonVersion());
    Assertions.assertFalse(jobDeployment.getEnabled());
    Assertions.assertEquals("release", jobDeployment.getVdkVersion());
    Assertions.assertNotNull(jobDeployment.getJobVersion());
    Assertions.assertNotNull(jobDeployment.getVdkVersion());
  }

  @Override
  protected void beforeDeploymentDeletion() throws Exception {
    setVdkVersionForDeployment();

    disableDeployment();

    resetVdkDeploymentVersion();

    verifyVersion();

    checkDeployment();
  }
}
