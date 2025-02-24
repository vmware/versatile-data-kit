/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import java.time.OffsetDateTime;

public interface DataJobExecutionIdAndEndTime {
  String getId();

  OffsetDateTime getEndTime();
}
