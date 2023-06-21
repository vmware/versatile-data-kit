/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.vmware.taurus.service.KubernetesService;
import com.vmware.taurus.service.deploy.JobCommandProvider;
import io.kubernetes.client.openapi.ApiClient;
import io.kubernetes.client.openapi.ApiException;
import io.kubernetes.client.openapi.apis.BatchV1Api;
import io.kubernetes.client.openapi.apis.BatchV1beta1Api;
import io.kubernetes.client.openapi.models.V1Container;
import io.kubernetes.client.openapi.models.V1Volume;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * Kubernetes service used for serving data jobs deployments. All deployed data jobs are executed in
 * this environment and all other necessary resources that are used only during the execution of a
 * data job should be create in this kubernetes.
 */
@Service
@Slf4j
public class DataJobsKubernetesService extends KubernetesService {

  public DataJobsKubernetesService(
      @Qualifier("dataJobsNamespace") String namespace,
      @Value("${datajobs.control.k8s.k8sSupportsV1CronJob}") boolean k8sSupportsV1CronJob,
      @Qualifier("deploymentApiClient") ApiClient client,
      @Qualifier("deploymentBatchV1Api") BatchV1Api batchV1Api,
      @Qualifier("deploymentBatchV1beta1Api") BatchV1beta1Api batchV1beta1Api,
      JobCommandProvider jobCommandProvider) {
    super(
        namespace,
        k8sSupportsV1CronJob,
        log,
        client,
        batchV1Api,
        batchV1beta1Api,
        jobCommandProvider);
  }


  public void createCronJob(
          String name,
          String image,
          String schedule,
          boolean enable,
          V1Container jobContainer,
          V1Container initContainer,
          List<V1Volume> volumes,
          Map<String, String> jobAnnotations,
          Map<String, String> jobLabels,
          List<String> imagePullSecrets)
          throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      createV1CronJob(
              name,
              image,
              schedule,
              enable,
              jobContainer,
              initContainer,
              volumes,
              jobAnnotations,
              jobLabels,
              imagePullSecrets);
    } else {
      createV1beta1CronJob(
              name,
              image,
              schedule,
              enable,
              jobContainer,
              initContainer,
              volumes,
              jobAnnotations,
              jobLabels,
              imagePullSecrets);
    }
  }


  public void updateCronJob(
          String name,
          String image,
          String schedule,
          boolean enable,
          V1Container jobContainer,
          V1Container initContainer,
          List<V1Volume> volumes,
          Map<String, String> jobAnnotations,
          Map<String, String> jobLabels,
          List<String> imagePullSecrets)
          throws ApiException {
    if (getK8sSupportsV1CronJob()) {
      updateV1CronJob(
              name,
              image,
              schedule,
              enable,
              jobContainer,
              initContainer,
              volumes,
              jobAnnotations,
              jobLabels,
              imagePullSecrets);
    } else {
      updateV1beta1CronJob(
              name,
              image,
              schedule,
              enable,
              jobContainer,
              initContainer,
              volumes,
              jobAnnotations,
              jobLabels,
              imagePullSecrets);
    }
  }


}
