/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Component
@AllArgsConstructor
public class KubernetesResources {
   // TODO: clients may need to configure those - consider making them configurable.

   // Data jobs Default resource configuration for the init container only.
   public static final String DATA_JOB_INIT_CONTAINER_CPU_REQUESTS = "100m";
   public static final String DATA_JOB_INIT_CONTAINER_MEMORY_REQUESTS = "100M";

   public static final String DATA_JOB_INIT_CONTAINER_CPU_LIMITS = "100m";
   public static final String DATA_JOB_INIT_CONTAINER_MEMORY_LIMITS = "100M";

   @Autowired
   private final BuilderResources builderResources;

   public KubernetesService.Resources dataJobInitContainerRequests() {
      return new KubernetesService.Resources(DATA_JOB_INIT_CONTAINER_CPU_REQUESTS, DATA_JOB_INIT_CONTAINER_MEMORY_REQUESTS);
   }

   public KubernetesService.Resources dataJobInitContainerLimits() {
      return new KubernetesService.Resources(DATA_JOB_INIT_CONTAINER_CPU_LIMITS, DATA_JOB_INIT_CONTAINER_MEMORY_LIMITS);
   }

   public KubernetesService.Resources builderRequests() {
      return new KubernetesService.Resources(builderResources.getDataJobBuilderCpuRequests(), builderResources.getDataJobBuilderMemoryRequests());
   }

   public KubernetesService.Resources builderLimits() {
      return new KubernetesService.Resources(builderResources.getDataJobBuilderCpuLimits(), builderResources.getDataJobBuilderMemoryLimits());
   }
}
