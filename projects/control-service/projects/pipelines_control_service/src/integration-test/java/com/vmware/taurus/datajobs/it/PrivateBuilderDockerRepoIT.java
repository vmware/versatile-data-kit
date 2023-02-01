/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.datajobs.it;

import com.vmware.taurus.ControlplaneApplication;
import com.vmware.taurus.controlplane.model.data.DataJobExecution;
import com.vmware.taurus.datajobs.it.common.BaseIT;
import com.vmware.taurus.datajobs.it.common.DockerConfigJsonUtils;
import com.vmware.taurus.datajobs.it.common.JobExecutionUtil;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.CoreV1Api;
import io.kubernetes.client.openapi.models.V1SecretBuilder;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.TestPropertySource;

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

  /**
   * This test exists to make sure that the builder image can be pulled from a private repo. We
   * create, build, deploy a data job and manually start execution to test this. We don't wait for
   * the job to complete because that is irrelevant.
   *
   * <p>Within this test we assert only that the data job execution is started and has an execution
   * id. We don't wait for the job to be completed as successful as that takes too long
   */
  @Test
  public void testPrivateDockerBuildJob(
      String jobName, String teamName, String username, String deploymentId) throws Exception {
    createBuilderImagePullSecret(controlNamespace);
    // manually start job execution
    ImmutablePair<String, String> executeDataJobResult =
        JobExecutionUtil.executeDataJob(jobName, teamName, username, deploymentId, mockMvc);
    String opId = executeDataJobResult.getLeft();
    String executionId = executeDataJobResult.getRight();

    // Check the data job execution status
    JobExecutionUtil.checkDataJobExecutionStatus(
        executionId,
        DataJobExecution.StatusEnum.SUCCEEDED,
        opId,
        jobName,
        teamName,
        username,
        mockMvc);
  }
}
