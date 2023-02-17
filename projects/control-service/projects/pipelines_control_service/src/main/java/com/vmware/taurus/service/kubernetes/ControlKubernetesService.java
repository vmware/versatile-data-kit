/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.vmware.taurus.service.KubernetesService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
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
      @Value("${datajobs.control.k8s.namespace:}") String namespace,
      @Value("${datajobs.control.k8s.kubeconfig:}") String kubeconfig,
      @Value("${datajobs.control.k8s.k8sSupportsV1CronJob}") boolean k8sSupportsV1CronJob) {
    super(namespace, kubeconfig, k8sSupportsV1CronJob, log);
  }
}
