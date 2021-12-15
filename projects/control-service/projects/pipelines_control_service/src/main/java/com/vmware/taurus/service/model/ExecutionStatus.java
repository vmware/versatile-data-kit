/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum ExecutionStatus {
   SUBMITTED(0, "Submitted", 2),
   RUNNING(1, "Running", 5),
   SUCCEEDED(2, "Success", 0),
   CANCELLED(4, "Cancelled", 6),
   SKIPPED(5, "Skipped", 4),
   USER_ERROR(6, "User error", 3),
   PLATFORM_ERROR(7, "Platform error", 1);

   @Getter
   private final Integer dbValue;

   @Getter
   private final String podStatus;

   @Getter
   private final Integer alertValue;
}
