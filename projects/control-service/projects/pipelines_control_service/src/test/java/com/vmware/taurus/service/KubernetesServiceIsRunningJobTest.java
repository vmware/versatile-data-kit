/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import java.util.Collections;

import com.vmware.taurus.service.deploy.JobCommandProvider;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import io.kubernetes.client.openapi.models.V1Job;
import io.kubernetes.client.openapi.models.V1JobCondition;
import io.kubernetes.client.openapi.models.V1JobList;
import io.kubernetes.client.openapi.models.V1JobStatus;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class KubernetesServiceIsRunningJobTest {

  @Test
  public void testIsRunningJob_nullResponse_shouldReturnFalse() throws ApiException {
    assertResponseValid(null, false);
  }

  @Test
  public void testIsRunningJob_emptyResponse_shouldReturnFalse() throws ApiException {
    assertResponseValid(new V1JobList(), false);
  }

  @Test
  public void testIsRunningJob_oneJobWithConditionsNull_shouldReturnTrue() throws ApiException {
    V1JobList response =
        new V1JobList().addItemsItem(new V1Job().status(new V1JobStatus().conditions(null)));

    assertResponseValid(response, true);
  }

  @Test
  public void testIsRunningJob_oneJobWithConditionsNotNullAndEmpty_shouldReturnTrue()
      throws ApiException {
    V1JobList response =
        new V1JobList()
            .addItemsItem(
                new V1Job().status(new V1JobStatus().conditions(Collections.emptyList())));

    assertResponseValid(response, true);
  }

  @Test
  public void testIsRunningJob_oneJobWithConditionsNotNullAndNotEmpty_shouldReturnFalse()
      throws ApiException {
    V1JobList response =
        new V1JobList()
            .addItemsItem(
                new V1Job().status(new V1JobStatus().addConditionsItem(new V1JobCondition())));

    assertResponseValid(response, false);
  }

  @Test
  public void
      testIsRunningJob_oneJobWithConditionsNullAndOneJobWithConditionsNotNull_shouldReturnTrue()
          throws ApiException {
    V1JobList response =
        new V1JobList()
            .addItemsItem(new V1Job().status(new V1JobStatus().conditions(null)))
            .addItemsItem(
                new V1Job().status(new V1JobStatus().addConditionsItem(new V1JobCondition())));

    assertResponseValid(response, true);
  }

  private void assertResponseValid(V1JobList response, boolean expectedResult) throws ApiException {

    BatchV1Api batchV1Api = Mockito.mock(BatchV1Api.class);
    Mockito.when(
            batchV1Api.listNamespacedJob(
                Mockito.anyString(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.anyString(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull()))
        .thenReturn(response);

    KubernetesService kubernetesService =
            new DataJobsKubernetesService(
                    "default",
                    true,
                    new ApiClient(),
                    batchV1Api,
                    new BatchV1beta1Api(),
                    new JobCommandProvider());
    boolean actualResult = kubernetesService.isRunningJob("test-job");

    Assertions.assertEquals(expectedResult, actualResult);
  }
}
