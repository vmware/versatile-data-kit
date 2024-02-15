/*
 * Copyright 2023-2024 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

/*
 * Copyright 2021-2024 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.telemetry;

public interface ITelemetry {
  /**
   * @param payload json to be sent as payload.
   */
  void sendAsync(String payload);
}
