/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.vmware.taurus.service.CronJobDeployer;
import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.JobCommandProvider;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

/**
 * Kubernetes service used for serving data jobs deployments. All deployed data jobs are executed in
 * this environment and all other necessary resources that are used only during the execution of a
 * data job should be create in this kubernetes.
 */
@Service
@Slf4j
public class DataJobsKubernetesService extends KubernetesService {

  public DataJobsKubernetesService(
      @Value("${datajobs.deployment.k8s.namespace:}") String namespace,
      @Value("${datajobs.control.k8s.k8sSupportsV1CronJob}") boolean k8sSupportsV1CronJob,
      @Qualifier("deploymentApiClient") ApiClient client,
      @Qualifier("controlBatchV1Api") BatchV1Api batchV1Api,
      @Qualifier("controlBatchV1beta1Api") BatchV1beta1Api batchV1beta1Api,
      CronJobDeployer cronJobDeployer,
      JobCommandProvider jobCommandProvider) {
    super(
        namespace,
        k8sSupportsV1CronJob,
        log,
        client,
        batchV1Api,
        batchV1beta1Api,
        cronJobDeployer,
        jobCommandProvider);
  }
}
