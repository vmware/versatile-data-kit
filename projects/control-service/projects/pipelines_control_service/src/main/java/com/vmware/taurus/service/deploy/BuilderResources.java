/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.deploy;

import lombok.Getter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component
@Getter
public class BuilderResources {
  @Value("${datajob.builder.cpu.requests:250m}")
  private String dataJobBuilderCpuRequests;

  @Value("${datajob.builder.memory.requests:250Mi}")
  private String dataJobBuilderMemoryRequests;

  @Value("${datajob.builder.cpu.limits:1000m}")
  private String dataJobBuilderCpuLimits;

  @Value("${datajob.builder.memory.limits:1000Mi}")
  private String dataJobBuilderMemoryLimits;
}
