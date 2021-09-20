/*
 * Copyright 2021 VMware, Inc.
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum ExecutionStatus {
   SUBMITTED(0),
   RUNNING(1),
   FINISHED(2),
   FAILED(3),
   CANCELLED(4),
   SKIPPED(5);

   @Getter
   private final int value;

}
