/*
 * Copyright 2023-2025 Broadcom
 * SPDX-License-Identifier: Apache-2.0
 */

package com.vmware.taurus.service.model;

public interface DataJobExecutionStatusCount {
  ExecutionStatus getStatus();

  int getStatusCount();

  String getJobName();
}
