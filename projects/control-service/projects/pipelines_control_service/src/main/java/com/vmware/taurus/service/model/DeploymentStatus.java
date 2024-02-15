/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum DeploymentStatus {
  NONE(-1),
  SUCCESS(0),
  PLATFORM_ERROR(1),
  USER_ERROR(3);

  @Getter private int value;
}
