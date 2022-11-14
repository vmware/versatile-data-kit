/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MvcResult;

import java.util.ArrayList;
import java.util.UUID;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Slf4j
@Import({DataJobDeploymentCrudIT.TaskExecutorConfig.class})
@SpringBootTest(
        webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
        classes = ControlplaneApplication.class)
public class DataJobEphemeralStorageIT extends BaseIT {

    private static final String TEST_JOB_NAME =
            "ephemeral-storage-test-" + UUID.randomUUID().toString().substring(0, 8);
    private static final Object DEPLOYMENT_ID = "testing-ephemeral-storage";

    @AfterEach
    public void cleanUp() throws Exception {
        // delete job
        mockMvc
                .perform(
                        delete(
                                String.format(
                                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                                .with(user("user")))
                .andExpect(status().isOk());

        // Execute delete deployment
        mockMvc
                .perform(
                        delete(
                                String.format(
                                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s",
                                        TEST_TEAM_NAME, TEST_JOB_NAME, DEPLOYMENT_ID))
                                .with(user("user"))
                                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isAccepted());
    }

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
    }

    @Test
    public void testJobCancellation_createDeployExecuteAndCancelJob() throws Exception {
        // Take the job zip as byte array
        byte[] jobZipBinary =
                IOUtils.toByteArray(
                        getClass().getClassLoader().getResourceAsStream("simple_job_ephemeral_storage.zip"));

        // Execute job upload with user
        MvcResult jobUploadResult =
                mockMvc
                        .perform(
                                post(String.format(
                                        "/data-jobs/for-team/%s/jobs/%s/sources", TEST_TEAM_NAME, TEST_JOB_NAME))
                                        .with(user("user"))
                                        .content(jobZipBinary)
                                        .contentType(MediaType.APPLICATION_OCTET_STREAM))
                        .andExpect(status().isOk())
                        .andReturn();

        DataJobVersion testDataJobVersion =
                new ObjectMapper()
                        .readValue(jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
        Assertions.assertNotNull(testDataJobVersion);

        String testJobVersionSha = testDataJobVersion.getVersionSha();
        Assertions.assertFalse(StringUtils.isBlank(testJobVersionSha));

        // Setup
        String dataJobDeploymentRequestBody = getDataJobDeploymentRequestBody(testJobVersionSha);

        // Execute build and deploy job
        mockMvc
                .perform(
                        post(String.format(
                                "/data-jobs/for-team/%s/jobs/%s/deployments", TEST_TEAM_NAME, TEST_JOB_NAME))
                                .with(user("user"))
                                .content(dataJobDeploymentRequestBody)
                                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isAccepted())
                .andReturn();

        // manually start job execution
        mockMvc
                .perform(
                        post(String.format(
                                "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                                TEST_TEAM_NAME, TEST_JOB_NAME, TEST_JOB_DEPLOYMENT_ID))
                                .with(user("user"))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(
                                        "{\n"
                                                + "  \"args\": {\n"
                                                + "    \"key\": \"value\"\n"
                                                + "  },\n"
                                                + "  \"started_by\": \"schedule/runtime\"\n"
                                                + "}"))
                .andExpect(status().is(202))
                .andReturn();

        // wait for pod to initialize
        Thread.sleep(10000);

        // retrieve running job execution id.
        var exc =
                mockMvc
                        .perform(
                                get(String.format(
                                        "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                                        TEST_TEAM_NAME, TEST_JOB_NAME, TEST_JOB_DEPLOYMENT_ID))
                                        .with(user("user"))
                                        .contentType(MediaType.APPLICATION_JSON))
                        .andExpect(status().isOk())
                        .andReturn();

        var gson = new Gson();
        ArrayList<LinkedTreeMap> parsed =
                gson.fromJson(exc.getResponse().getContentAsString(), ArrayList.class);
        String executionId = (String) parsed.get(0).get("id");

        // cancel running execution
        mockMvc
                .perform(
                        delete(
                                String.format(
                                        "/data-jobs/for-team/%s/jobs/%s/executions/%s",
                                        TEST_TEAM_NAME, TEST_JOB_NAME, executionId))
                                .with(user("user"))
                                .contentType(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk());
    }
}
