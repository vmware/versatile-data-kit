/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.ServiceApp;
import io.kubernetes.client.openapi.ApiException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mockito;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.context.junit.jupiter.SpringExtension;

import java.util.Collections;

@ExtendWith(SpringExtension.class)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.MOCK, classes = ServiceApp.class)
public class DataJobsSynchronizerTest {

  @Autowired private DataJobsSynchronizer dataJobsSynchronizer;

  @MockBean private DeploymentServiceV2 deploymentService;

  @Test
  void
      synchronizeDataJobs_loadDeploymentNamesFromKubernetesReturnsValue_shouldFinishSynchronization()
          throws ApiException {
    Mockito.when(deploymentService.findAllActualDeploymentNamesFromKubernetes())
        .thenReturn(Collections.emptySet());

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(1))
        .findAllActualDeploymentNamesFromKubernetes();

    Mockito.verify(deploymentService, Mockito.times(1)).findAllActualDataJobDeployments();
  }

  @Test
  void
      synchronizeDataJobs_loadDeploymentNamesFromKubernetesThrowsApiException_shouldSkipSynchronization()
          throws ApiException {
    Mockito.when(deploymentService.findAllActualDeploymentNamesFromKubernetes())
        .thenThrow(new ApiException());

    dataJobsSynchronizer.synchronizeDataJobs();

    Mockito.verify(deploymentService, Mockito.times(1))
        .findAllActualDeploymentNamesFromKubernetes();

    Mockito.verify(deploymentService, Mockito.times(0)).findAllActualDataJobDeployments();
  }
}
