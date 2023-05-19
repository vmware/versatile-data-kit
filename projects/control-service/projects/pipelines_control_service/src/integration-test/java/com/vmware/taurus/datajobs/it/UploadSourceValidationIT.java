/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;


import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@TestPropertySource(
    properties = {
      "upload.validation.fileTypes.allowlist=text/x-sql,application/json",
    })
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class UploadSourceValidationIT extends BaseIT {
  protected static final String TEST_JOB_NAME =
      JobExecutionUtil.generateJobName(UploadSourceValidationIT.class.getSimpleName());

  @BeforeEach
  public void setup() throws Exception {
    String dataJobRequestBody = getDataJobRequestBody(TEST_TEAM_NAME, TEST_JOB_NAME);
    // Execute create job
    mockMvc
        .perform(
            post(String.format("/data-jobs/for-team/%s/jobs", TEST_TEAM_NAME))
                .with(user("user"))
                .content(dataJobRequestBody)
                .contentType(MediaType.APPLICATION_JSON))
        .andExpect(status().isCreated());
  }

  @Test
  public void testDataJobUploadSource() throws Exception {
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("data_jobs/simple_job.zip"));

    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                .with(user("user"))
                .content(jobZipBinary)
                .contentType(MediaType.APPLICATION_OCTET_STREAM))
        .andExpect(status().isBadRequest());
  }
}
