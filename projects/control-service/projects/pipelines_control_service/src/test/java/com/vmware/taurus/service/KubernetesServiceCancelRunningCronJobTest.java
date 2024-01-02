/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service;

import com.vmware.taurus.service.deploy.JobCommandProvider;
import com.vmware.taurus.service.kubernetes.DataJobsKubernetesService;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.ApiResponse;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import io.kubernetes.client.openapi.models.V1Status;
import io.kubernetes.client.openapi.models.V1StatusDetails;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import com.vmware.taurus.exception.DataJobExecutionCannotBeCancelledException;
import com.vmware.taurus.exception.KubernetesException;

public class KubernetesServiceCancelRunningCronJobTest {

  @Test
  public void testIsRunningJob_nullResponse_shouldThrowDataJobExecutionCannotBeCancelledException()
      throws ApiException {
    var kubernetesService = mockKubernetesService(null);

    Assertions.assertThrows(
        DataJobExecutionCannotBeCancelledException.class,
        () ->
            kubernetesService.cancelRunningCronJob(
                "test-team", "test-job-name", "test-execution-id"));
  }

  @Test
  public void
      testIsRunningJob_notNullResponseAndNullStatus_shouldThrowDataJobExecutionCannotBeCancelledException()
          throws ApiException {
    var kubernetesService = mockKubernetesService(new V1Status().status(null).code(404));

    Assertions.assertThrows(
        DataJobExecutionCannotBeCancelledException.class,
        () ->
            kubernetesService.cancelRunningCronJob(
                "test-team", "test-job-name", "test-execution-id"));
  }

  @Test
  public void testIsRunningJob_notNullResponseAndStatusSuccess_shouldNotThrowException()
      throws ApiException {
    var kubernetesService = mockKubernetesService(new V1Status().code(200));

    Assertions.assertDoesNotThrow(
        () ->
            kubernetesService.cancelRunningCronJob(
                "test-team", "test-job-name", "test-execution-id"));
  }

  @Test
  public void testIsRunningJob_notNullResponseAndStatusFailure_shouldThrowKubernetesException()
      throws ApiException {
    V1Status v1Status =
        new V1Status()
            .status("Failure")
            .reason("test-reason")
            .code(1)
            .message("test-message")
            .details(new V1StatusDetails());
    var kubernetesService = mockKubernetesService(v1Status);

    Assertions.assertThrows(
        KubernetesException.class,
        () ->
            kubernetesService.cancelRunningCronJob(
                "test-team", "test-job-name", "test-execution-id"));
  }

  private DataJobsKubernetesService mockKubernetesService(V1Status v1Status) throws ApiException {
    ApiResponse<V1Status> response = Mockito.mock(ApiResponse.class);
    Mockito.when(response.getData()).thenReturn(v1Status);
    Mockito.when(response.getStatusCode()).thenReturn(v1Status == null ? 404 : v1Status.getCode());

    BatchV1Api batchV1Api = Mockito.mock(BatchV1Api.class);
    Mockito.when(
            batchV1Api.deleteNamespacedJobWithHttpInfo(
                Mockito.anyString(),
                Mockito.anyString(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.isNull(),
                Mockito.anyString(),
                Mockito.isNull()))
        .thenReturn(response);

    return new DataJobsKubernetesService(
        "default",
        false,
        new ApiClient(),
        batchV1Api,
        new BatchV1beta1Api(),
        new JobCommandProvider());
  }
}
