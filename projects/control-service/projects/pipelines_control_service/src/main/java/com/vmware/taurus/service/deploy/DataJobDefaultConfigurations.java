/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
public class DataJobDefaultConfigurations {

  @Value("${datajobs.job.resources.limits.memory:1G}")
  private String memoryLimits;

  @Value("${datajobs.job.resources.limits.cpu:2000m}")
  private String cpuLimits;

  @Value("${datajobs.job.resources.requests.memory:500Mi}")
  private String memoryRequests;

  @Value("${datajobs.job.resources.requests.cpu:1000m}")
  private String cpuRequests;

  public KubernetesService.Resources dataJobRequests() {
    return new KubernetesService.Resources(cpuRequests, memoryRequests);
  }

  public KubernetesService.Resources dataJobLimits() {
    return new KubernetesService.Resources(cpuLimits, memoryLimits);
  }
}
