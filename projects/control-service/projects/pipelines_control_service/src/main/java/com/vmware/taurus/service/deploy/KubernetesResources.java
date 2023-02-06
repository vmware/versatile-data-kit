/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import lombok.AllArgsConstructor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
@AllArgsConstructor
public class KubernetesResources {
  @Value("${datajobs.deployment.initContainer.resources.requests.cpu}")
  private String dataJobInitContainerCpuRequests;

  @Value("${datajobs.deployment.initContainer.resources.requests.memory}")
  private String dataJobInitContainerMemoryRequests;

  @Value("${datajobs.deployment.initContainer.resources.limits.cpu}")
  private String dataJobInitContainerCpuLimits;

  @Value("${datajobs.deployment.initContainer.resources.limits.memory}")
  private String dataJobInitContainerMemoryLimits;

  @Autowired private final BuilderResources builderResources;

  public KubernetesService.Resources dataJobInitContainerRequests() {
    return new KubernetesService.Resources(
        dataJobInitContainerCpuRequests, dataJobInitContainerMemoryRequests);
  }

  public KubernetesService.Resources dataJobInitContainerLimits() {
    return new KubernetesService.Resources(
        dataJobInitContainerCpuLimits, dataJobInitContainerMemoryLimits);
  }

  public KubernetesService.Resources builderRequests() {
    return new KubernetesService.Resources(
        builderResources.getDataJobBuilderCpuRequests(),
        builderResources.getDataJobBuilderMemoryRequests());
  }

  public KubernetesService.Resources builderLimits() {
    return new KubernetesService.Resources(
        builderResources.getDataJobBuilderCpuLimits(),
        builderResources.getDataJobBuilderMemoryLimits());
  }
}
