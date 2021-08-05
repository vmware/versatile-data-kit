/*
 * Copyright (c) 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.kubernetes;

import com.vmware.taurus.service.KubernetesService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;

/**
 * Kubernetes service used for serving data jobs deployments.
 * All deployed data jobs are executed in this environment and all other necessary resources that are used
 * only during the execution of a data job should be create in this kubernetes.
 */
@Service
@Slf4j
public class DataJobsKubernetesService extends KubernetesService {

   public DataJobsKubernetesService(@Value("${datajobs.deployment.k8s.namespace:}") String namespace,
                                    @Value("${datajobs.deployment.k8s.kubeconfig:}") String kubeconfig) {
      super(namespace, kubeconfig, log);
      if (StringUtils.isBlank(kubeconfig) && !new File(kubeconfig).isFile()) {
         log.warn("Data Jobs (Deployment) Kubernetes service may not have been correctly bootstrapped. {} file is missing " +
                         "Will try to use same cluster as control Plane. But this is not recommended in production.",
                 kubeconfig);
      }
   }
}
