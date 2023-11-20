/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import com.vmware.taurus.service.KubernetesService;
import java.text.NumberFormat;
import java.text.ParseException;
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

  public float getCpuRequests() throws ParseException {
    return NumberFormat.getInstance().parse(cpuRequests).floatValue();
  }

  public float getCpuLimits() throws ParseException {
    return NumberFormat.getInstance().parse(cpuLimits).floatValue();
  }

  public int getMemoryRequests() throws ParseException {
    var memoryAmount = NumberFormat.getInstance().parse(memoryRequests).intValue();
    return K8SMemoryConversionUtils.getMemoryInMi(memoryRequests, memoryAmount);
  }

  public int getMemoryLimits() throws ParseException {
    var memoryAmount = NumberFormat.getInstance().parse(memoryLimits).intValue();
    return K8SMemoryConversionUtils.getMemoryInMi(memoryLimits, memoryAmount);
  }
}
