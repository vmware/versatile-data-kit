/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecutionRequest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ActiveProfiles({"MockKubernetes", "MockKerberos", "unittest", "MockTelemetry"})
@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK, classes = ControlplaneApplication.class)
@AutoConfigureMockMvc
public class DataJobsExecutionControllerIT {

   private static final String TEST_TEAM_NAME = "test-team";

   @Autowired
   private MockMvc mockMvc;

   private final ObjectMapper mapper = new ObjectMapper();

   @Test
   @WithMockUser
   public void testDataJobExecutionStartNotFound() throws Exception {
      String jobName = "test-job";
      String deploymentId = "dummy";
      DataJobExecutionRequest executionRequest = new DataJobExecutionRequest();
      executionRequest.setStartedBy("unit-test");
      String body = mapper.writeValueAsString(executionRequest);

      String url = String.format("/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
              TEST_TEAM_NAME, jobName, deploymentId);
      mockMvc.perform(post(url).content(body).contentType(MediaType.APPLICATION_JSON))
              .andExpect(status().isNotFound());

   }

   // TODO: test all methods

}
