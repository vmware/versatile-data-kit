/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.*;

import javax.persistence.*;

@Getter
@Setter
@NoArgsConstructor
@EqualsAndHashCode
@ToString
@Embeddable
@AllArgsConstructor
public class DataJobDeploymentResources {

  @Column(name = "resources_cpu_request_cores")
  private Float cpuRequestCores;

  @Column(name = "resources_cpu_limit_cores")
  private Float cpuLimitCores;

  @Column(name = "resources_memory_request_mi")
  private Integer memoryRequestMi;

  @Column(name = "resources_memory_limit_mi")
  private Integer memoryLimitMi;
}
