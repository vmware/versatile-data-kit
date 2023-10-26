/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobDeploymentStatus;
import com.vmware.taurus.service.model.ActualDataJobDeployment;
import com.vmware.taurus.service.repository.ActualJobDeploymentRepository;
import com.vmware.taurus.service.repository.DesiredJobDeploymentRepository;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;

@TestPropertySource(
    properties = {
      "datajobs.control.k8s.k8sSupportsV1CronJob=true",
      "datajobs.deployment.configuration.persistence.writeTos=DB",
      "datajobs.deployment.configuration.persistence.readDataSource=DB",
      "datajobs.deployment.configuration.synchronization.task.enabled=true",
      "datajobs.deployment.configuration.synchronization.task.interval.ms=1000",
      "datajobs.deployment.configuration.synchronization.task.initial.delay.ms=0"
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobDeploymentCrudAsyncIT extends BaseDataJobDeploymentCrudIT {

  @Override
  protected void beforeDeploymentDeletion() throws Exception {
    checkDeployment();
  }

  @Override
  protected void afterDeploymentDeletion() throws Exception {
    checkDesiredDeploymentDeleted();
  }

  private void checkDeployment()
      throws Exception {

    MvcResult result =
        mockMvc
            .perform(
                get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                    TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                    .with(user("user"))
                    .contentType(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andReturn();

    DataJobDeploymentStatus jobDeployment =
        mapper.readValue(result.getResponse().getContentAsString(), DataJobDeploymentStatus.class);

    Assertions.assertEquals(TEST_JOB_SCHEDULE, jobDeployment.getSchedule().getScheduleCron());
    Assertions.assertEquals(testJobName, jobDeployment.getId());
    Assertions.assertEquals("user", jobDeployment.getLastDeployedBy());
    Assertions.assertEquals("3.9", jobDeployment.getPythonVersion());
    Assertions.assertFalse(jobDeployment.getEnabled());
    Assertions.assertNotNull(jobDeployment.getResources());
    Assertions.assertNotNull(jobDeployment.getJobVersion());
    Assertions.assertNotNull(jobDeployment.getVdkVersion());
    Assertions.assertNotNull(jobDeployment.getContacts());
  }

  private void checkDesiredDeploymentDeleted() throws Exception {
    mockMvc
        .perform(
            get(String.format(
                "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                TEST_TEAM_NAME, testJobName, DEPLOYMENT_ID))
                .with(user("user"))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNotFound());
  }
}
