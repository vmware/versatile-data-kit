/*
 * Copyright 2021-2023 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

/** Used for setting of Kubernetes Job Container environment variables */
@AllArgsConstructor
public enum JobEnvVar {
  VDK_OP_ID("VDK_OP_ID");

  @Getter private String value;
}
