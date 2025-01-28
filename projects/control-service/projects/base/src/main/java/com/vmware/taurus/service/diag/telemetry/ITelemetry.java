/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.diag.telemetry;

public interface ITelemetry {
  /**
   * @param payload json to be sent as payload.
   */
  void sendAsync(String payload);
}
