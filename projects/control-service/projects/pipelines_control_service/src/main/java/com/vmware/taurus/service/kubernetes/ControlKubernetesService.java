/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.JobCommandProvider;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;

/**
 * Kubernetes service used for serving system tasks of the Control Service. For example helper jobs
 * to deploy data jobs. Generally it's fine if it's the same as where the Control service runs.
 */
@Service
@Slf4j
public class ControlKubernetesService extends KubernetesService {

  // those should be null/empty when Control service is deployed in k8s hence default is empty
  public ControlKubernetesService(
      @Qualifier("controlNamespace") String namespace,
      @Qualifier("controlApiClient") ApiClient client,
      @Qualifier("controlBatchV1Api") BatchV1Api batchV1Api,
      JobCommandProvider jobCommandProvider) {
    super(namespace, log, client, batchV1Api, jobCommandProvider);
  }
}
