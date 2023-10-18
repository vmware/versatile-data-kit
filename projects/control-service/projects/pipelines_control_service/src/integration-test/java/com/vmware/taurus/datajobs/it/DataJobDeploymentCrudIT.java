/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;

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

  @Override
  protected void beforeDeploymentDeletion() throws Exception {
    // Execute set vdk version for deployment
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

    // Execute reset back vdk version for deployment
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

    // verify vdk version is reset correctly
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
}
