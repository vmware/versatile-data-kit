/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import com.vmware.taurus.service.model.converter.ExecutionStatusConverter;
import com.vmware.taurus.service.model.converter.ExecutionTerminationStatusConverter;
import lombok.*;

import javax.persistence.*;
import java.time.OffsetDateTime;
import java.util.Set;

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
