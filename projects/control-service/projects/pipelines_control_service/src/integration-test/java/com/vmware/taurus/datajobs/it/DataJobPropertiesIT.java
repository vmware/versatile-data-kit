/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.properties.service.PropertiesRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;

import java.util.HashMap;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_JOB_NAME;
import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class DataJobPropertiesIT extends BaseIT {

  @Test
  public void testDataJobProperties() throws Exception {
    // Setup
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);

    // Execute create job (Post Create WebHook will return success for this call)
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated())
        .andExpect(
            header()
                .string(
                    HttpHeaders.LOCATION,
                    lambdaMatcher(
                        s ->
                            s.endsWith(
                                String.format(
                                    "/data-jobs/for-team/%s/jobs/%s",
                                    TEST_TEAM_NAME, TEST_JOB_NAME)))));

    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/properties",
                    TEST_TEAM_NAME, TEST_JOB_NAME, "dev"))
                .with(user("user")))
        .andExpect(status().isOk())
        .andExpect(content().string("{}"));

    var props = new HashMap<String, Object>();
    props.put("string_key", "string_value");
    props.put("int_key", 123);
    props.put("bool_key", true);
    mockMvc
        .perform(
            put(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/properties",
                    TEST_TEAM_NAME, TEST_JOB_NAME, "dev"))
                .with(user("user"))
                .content(mapper.writeValueAsString(props))
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isNoContent());

    mockMvc
        .perform(
            get(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/properties",
                    TEST_TEAM_NAME, TEST_JOB_NAME, "dev"))
                .with(user("user")))
        .andExpect(status().isOk())
        .andExpect(content().json(mapper.writeValueAsString(props)));
  }
}
