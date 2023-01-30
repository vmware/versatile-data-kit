/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobVersion;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.DockerConfigJsonUtils;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.CoreV1Api;
import io.kubernetes.client.openapi.models.V1SecretBuilder;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.awaitility.Awaitility;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.platform.commons.util.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MvcResult;

import java.util.ArrayList;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static com.vmware.taurus.datajobs.it.common.WebHookServerMockExtension.TEST_TEAM_NAME;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@Slf4j
@TestPropertySource(
    properties = {
      "dataJob.readOnlyRootFileSystem=true",
    })
@ActiveProfiles({"test", "private-builder"})
@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    classes = ControlplaneApplication.class)
public class PrivateBuilderDockerRepoIT extends BaseIT {

  private static final String TEST_JOB_NAME =
      "private-docker-builder-test-" + UUID.randomUUID().toString().substring(0, 8);
  private static final Object DEPLOYMENT_ID = "private-docker-builder";

  @Value("${datajobs.builder.registrySecret.content.testOnly:}")
  private String dataJobsBuilderRegistrySecretContent;

  @Value("${datajobs.builder.image}")
  private String builderImage;

  private void createBuilderImagePullSecret(String namespaceName) throws Exception {
    try {
      new CoreV1Api(controlKubernetesService.getClient())
          .createNamespacedSecret(
              namespaceName,
              new V1SecretBuilder()
                  .withNewMetadata()
                  .withName("integration-test-docker-pull-secret")
                  .withNamespace(namespaceName)
                  .endMetadata()
                  .withStringData(
                      DockerConfigJsonUtils.create(
                          builderImage.substring(0, builderImage.lastIndexOf("/")),
                          dataJobsBuilderRegistrySecretContent))
                  .withType("kubernetes.io/dockerconfigjson")
                  .build(),
              null,
              null,
              null,
              null);
    } catch (ApiException e) {
      if (e.getCode() == 409) { // Value already exists in k8s.
        return;
      }
      throw e;
    }
  }

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
        .andExpect(status().isCreated());
  }

  /**
   * This test exists to make sure that the builder image can be pulled from a private repo. We
   * create, build, deploy a data job and manually start execution to test this. We don't wait for
   * the job to complete because that is irrelevant.
   *
   * <p>Within this test we assert only that the data job execution is started and has an execution
   * id. We don't wait for the job to be completed as successful as that takes too long
   */
  @Test
  public void testPrivateDockerBuildJob() throws Exception {
    createBuilderImagePullSecret(controlNamespace);
    // Take the job zip as byte array
    byte[] jobZipBinary =
        IOUtils.toByteArray(
            getClass().getClassLoader().getResourceAsStream("job_ephemeral_storage.zip"));

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
        BaseIT.mapper.readValue(
            jobUploadResult.getResponse().getContentAsString(), DataJobVersion.class);
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

    String opId = TEST_JOB_NAME + UUID.randomUUID().toString().toLowerCase();

    // manually start job execution
    mockMvc
        .perform(
            post(String.format(
                    "/data-jobs/for-team/%s/jobs/%s/deployments/%s/executions",
                    TEST_TEAM_NAME, TEST_JOB_NAME, TEST_JOB_DEPLOYMENT_ID))
                .with(user("user"))
                .header(HEADER_X_OP_ID, opId)
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
    Awaitility.await()
        .atMost(10, TimeUnit.SECONDS)
        .until(
            () -> {
              try {
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
                return StringUtils.isNotBlank(
                    (String)
                        parsed
                            .get(0)
                            .get("id")); // simply check there is an exeution id. We don't care the
                // status of the job
              } catch (Exception e) {
                return false;
              }
            });
  }
}
